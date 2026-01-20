from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Literal

import numpy as np
from scipy.interpolate import CubicSpline, interp1d

from platform_base.core.models import ResultMetadata, SyncResult, QualityMetrics
from platform_base.utils.errors import InterpolationError
from platform_base.utils.logging import get_logger
from platform_base.profiling.decorators import profile, performance_critical

logger = get_logger(__name__)

SUPPORTED_SYNC_METHODS = {
    "common_grid_interpolate",
    "kalman_align",
}


def _build_metadata(method: str, params: dict, duration_ms: float = 0.0) -> ResultMetadata:
    """Constrói metadata conforme especificação seção 5.6"""
    return ResultMetadata(
        operation=method,
        parameters=params,
        platform_version="2.0.0",
        timestamp=datetime.now(timezone.utc),
        duration_ms=duration_ms,
    )


def _common_grid(
    t_dict: dict[str, np.ndarray], 
    dt: float | None = None,
    grid_method: Literal["median", "min", "max", "mean"] = "median"
) -> np.ndarray:
    """
    Compute common time grid from multiple series.
    
    Args:
        t_dict: Dictionary of time arrays per series
        dt: Optional fixed time step
        grid_method: Method to compute dt from all series if not provided
    
    Returns:
        Common time grid array
    """
    starts = [float(np.nanmin(t)) for t in t_dict.values()]
    ends = [float(np.nanmax(t)) for t in t_dict.values()]
    start = max(starts)  # Latest start (ensures all series have data)
    end = min(ends)      # Earliest end (ensures all series have data)
    
    if start >= end:
        raise InterpolationError(
            "No overlapping time window", 
            {"starts": starts, "ends": ends, "overlap": (start, end)}
        )
    
    if dt is None:
        # Compute time step from all series
        all_diffs = []
        for t in t_dict.values():
            if len(t) > 1:
                diffs = np.diff(np.sort(t))
                diffs = diffs[diffs > 0]  # Filter out zero/negative diffs
                all_diffs.append(diffs)
        
        if all_diffs:
            combined_diffs = np.concatenate(all_diffs)
            if grid_method == "median":
                dt = float(np.median(combined_diffs))
            elif grid_method == "min":
                dt = float(np.min(combined_diffs))
            elif grid_method == "max":
                dt = float(np.max(combined_diffs))
            else:  # mean
                dt = float(np.mean(combined_diffs))
        else:
            dt = 1.0
            
    n_points = int((end - start) / dt) + 1
    return np.linspace(start, end, n_points)


def _interpolate_to_grid(
    t_original: np.ndarray,
    values: np.ndarray,
    t_common: np.ndarray,
    interp_method: Literal["linear", "cubic", "nearest"] = "linear"
) -> np.ndarray:
    """
    Interpolate series to common grid.
    
    Args:
        t_original: Original time array
        values: Original values array
        t_common: Target common time grid
        interp_method: Interpolation method
    
    Returns:
        Interpolated values on common grid
    """
    # Sort by time and remove duplicates
    order = np.argsort(t_original)
    t_sorted = t_original[order]
    v_sorted = values[order]
    
    # Handle duplicates by taking mean
    t_unique, unique_idx = np.unique(t_sorted, return_index=True)
    if len(t_unique) < len(t_sorted):
        # Average duplicate values
        v_unique = np.zeros(len(t_unique))
        for i, idx in enumerate(unique_idx):
            next_idx = unique_idx[i + 1] if i + 1 < len(unique_idx) else len(t_sorted)
            v_unique[i] = np.mean(v_sorted[idx:next_idx])
    else:
        v_unique = v_sorted
    
    if interp_method == "linear":
        return np.interp(t_common, t_unique, v_unique)
    elif interp_method == "cubic":
        if len(t_unique) >= 4:
            spline = CubicSpline(t_unique, v_unique, extrapolate=False)
            result = spline(t_common)
            # Handle extrapolation by using linear for out-of-bounds
            mask_nan = np.isnan(result)
            if np.any(mask_nan):
                result[mask_nan] = np.interp(t_common[mask_nan], t_unique, v_unique)
            return result
        else:
            return np.interp(t_common, t_unique, v_unique)
    elif interp_method == "nearest":
        interp_func = interp1d(t_unique, v_unique, kind='nearest', 
                               fill_value="extrapolate", bounds_error=False)
        return interp_func(t_common)
    else:
        return np.interp(t_common, t_unique, v_unique)


def _compute_alignment_error(
    synced_series: dict[str, np.ndarray],
    original_series: dict[str, np.ndarray],
    t_dict: dict[str, np.ndarray],
    t_common: np.ndarray
) -> float:
    """
    Compute alignment error as mean RMSE across all series.
    
    Compares interpolated values back to original at original time points.
    """
    total_error = 0.0
    count = 0
    
    for key in synced_series:
        if key not in original_series or key not in t_dict:
            continue
            
        t_orig = t_dict[key]
        v_orig = original_series[key]
        v_synced = synced_series[key]
        
        # Interpolate synced values back to original time points
        v_resampled = np.interp(t_orig, t_common, v_synced)
        
        # Compute RMSE for points within common grid
        mask = (t_orig >= t_common[0]) & (t_orig <= t_common[-1])
        if np.any(mask):
            rmse = np.sqrt(np.mean((v_orig[mask] - v_resampled[mask]) ** 2))
            total_error += rmse
            count += 1
    
    return total_error / count if count > 0 else 0.0


def _compute_confidence(
    alignment_error: float,
    synced_series: dict[str, np.ndarray],
    t_common: np.ndarray
) -> float:
    """
    Compute confidence score based on alignment quality.
    
    Returns value between 0 and 1.
    """
    if len(synced_series) == 0 or len(t_common) == 0:
        return 0.0
    
    # Base confidence on alignment error and data coverage
    # Lower error = higher confidence
    error_factor = 1.0 / (1.0 + alignment_error)
    
    # Check for NaN/Inf values in synced series
    quality_factor = 1.0
    for key, values in synced_series.items():
        nan_ratio = np.sum(~np.isfinite(values)) / len(values)
        quality_factor -= nan_ratio * 0.2  # Penalize NaN values
    
    confidence = error_factor * max(0.0, quality_factor)
    return float(np.clip(confidence, 0.0, 1.0))


class KalmanFilter1D:
    """
    1D Kalman filter for time series alignment and smoothing.
    
    State: [position, velocity]
    Observation: position only
    """
    
    def __init__(
        self,
        process_noise: float = 0.01,
        measurement_noise: float = 0.1,
        initial_state: Optional[np.ndarray] = None,
        initial_covariance: Optional[np.ndarray] = None
    ):
        """
        Initialize Kalman filter.
        
        Args:
            process_noise: Process noise covariance (Q)
            measurement_noise: Measurement noise variance (R)
            initial_state: Initial state [position, velocity]
            initial_covariance: Initial state covariance
        """
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        
        # State: [position, velocity]
        self.x = initial_state if initial_state is not None else np.zeros(2)
        self.P = initial_covariance if initial_covariance is not None else np.eye(2) * 1.0
        
        # Observation matrix (we only observe position)
        self.H = np.array([[1.0, 0.0]])
        
        # Measurement noise
        self.R = np.array([[measurement_noise]])
    
    def predict(self, dt: float) -> np.ndarray:
        """
        Predict step with time delta.
        
        Args:
            dt: Time step
            
        Returns:
            Predicted state
        """
        # State transition matrix
        F = np.array([
            [1.0, dt],
            [0.0, 1.0]
        ])
        
        # Process noise covariance
        Q = np.array([
            [dt**4 / 4, dt**3 / 2],
            [dt**3 / 2, dt**2]
        ]) * self.process_noise
        
        # Predict state and covariance
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
        
        return self.x.copy()
    
    def update(self, z: float) -> np.ndarray:
        """
        Update step with measurement.
        
        Args:
            z: Measurement (observed position)
            
        Returns:
            Updated state
        """
        # Innovation
        y = z - self.H @ self.x
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state and covariance
        self.x = self.x + K.flatten() * y
        self.P = (np.eye(2) - K @ self.H) @ self.P
        
        return self.x.copy()
    
    def filter_series(
        self,
        t: np.ndarray,
        values: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Apply Kalman filter to entire series.
        
        Args:
            t: Time array
            values: Value array
            
        Returns:
            Tuple of (filtered_values, velocities)
        """
        n = len(t)
        filtered = np.zeros(n)
        velocities = np.zeros(n)
        
        # Initialize with first value
        self.x = np.array([values[0], 0.0])
        self.P = np.eye(2) * 1.0
        
        filtered[0] = values[0]
        velocities[0] = 0.0
        
        for i in range(1, n):
            dt = t[i] - t[i-1]
            if dt <= 0:
                dt = 1e-6  # Avoid zero/negative dt
                
            self.predict(dt)
            state = self.update(values[i])
            
            filtered[i] = state[0]
            velocities[i] = state[1]
        
        return filtered, velocities


def _kalman_smooth_series(
    values: np.ndarray,
    t: np.ndarray,
    process_noise: float = 0.01,
    measurement_noise: float = 0.1
) -> np.ndarray:
    """
    Apply Kalman smoothing to a series.
    
    Uses forward-backward smoothing (RTS smoother) for optimal results.
    """
    kf = KalmanFilter1D(
        process_noise=process_noise,
        measurement_noise=measurement_noise
    )
    
    n = len(values)
    
    # Forward pass - store predictions
    forward_states = np.zeros((n, 2))
    forward_covs = np.zeros((n, 2, 2))
    predicted_states = np.zeros((n, 2))
    predicted_covs = np.zeros((n, 2, 2))
    
    kf.x = np.array([values[0], 0.0])
    kf.P = np.eye(2) * 1.0
    
    forward_states[0] = kf.x.copy()
    forward_covs[0] = kf.P.copy()
    
    for i in range(1, n):
        dt = t[i] - t[i-1] if t[i] > t[i-1] else 1e-6
        
        # Predict
        predicted_states[i] = kf.predict(dt)
        predicted_covs[i] = kf.P.copy()
        
        # Update
        kf.update(values[i])
        forward_states[i] = kf.x.copy()
        forward_covs[i] = kf.P.copy()
    
    # Backward pass (RTS smoother)
    smoothed = np.zeros(n)
    smoothed[-1] = forward_states[-1, 0]
    
    xs = forward_states[-1].copy()
    
    for i in range(n - 2, -1, -1):
        dt = t[i+1] - t[i] if t[i+1] > t[i] else 1e-6
        
        F = np.array([[1.0, dt], [0.0, 1.0]])
        
        # RTS smoother gain
        try:
            C = forward_covs[i] @ F.T @ np.linalg.inv(predicted_covs[i+1])
        except np.linalg.LinAlgError:
            C = np.zeros((2, 2))
        
        # Smooth
        xs = forward_states[i] + C @ (xs - predicted_states[i+1])
        smoothed[i] = xs[0]
    
    return smoothed


@profile(target_name="synchronization_1m")
@performance_critical(max_time_seconds=5.0, operation_name="synchronization")
def synchronize(
    series_dict: dict[str, np.ndarray],
    t_dict: dict[str, np.ndarray],
    method: str,
    params: dict,
) -> SyncResult:
    """
    Synchronize multiple time series to a common time grid.
    
    Implements PRD section 8.1:
    - common_grid_interpolate: Interpolate all series to common grid
    - kalman_align: Use Kalman filtering for optimal alignment
    
    Args:
        series_dict: Dictionary mapping series names to value arrays
        t_dict: Dictionary mapping series names to time arrays
        method: Synchronization method
        params: Method-specific parameters:
            - dt: Optional fixed time step
            - grid_method: How to compute dt ("median", "min", "max", "mean")
            - interp_method: Interpolation method ("linear", "cubic", "nearest")
            - process_noise: Kalman filter process noise (kalman_align only)
            - measurement_noise: Kalman measurement noise (kalman_align only)
    
    Returns:
        SyncResult with synchronized series, alignment error, and confidence
    
    Raises:
        InterpolationError: If method is not supported or no overlapping window
    """
    logger.info("synchronize_start", 
               method=method, 
               n_series=len(series_dict),
               params=params)
    
    if method not in SUPPORTED_SYNC_METHODS:
        raise InterpolationError(
            "Sync method not available", 
            {"method": method, "supported": sorted(SUPPORTED_SYNC_METHODS)}
        )
    
    if len(series_dict) == 0:
        raise InterpolationError("No series to synchronize", {})
    
    if set(series_dict.keys()) != set(t_dict.keys()):
        raise InterpolationError(
            "Series and time dictionaries have mismatched keys",
            {"series_keys": list(series_dict.keys()), "t_keys": list(t_dict.keys())}
        )
    
    # Compute common grid
    grid_method = params.get("grid_method", "median")
    t_common = _common_grid(t_dict, dt=params.get("dt"), grid_method=grid_method)
    
    logger.debug("common_grid_computed", 
                n_points=len(t_common),
                t_start=t_common[0],
                t_end=t_common[-1])
    
    synced_series: dict[str, np.ndarray] = {}
    interp_method = params.get("interp_method", "linear")
    
    if method == "common_grid_interpolate":
        # Standard interpolation to common grid
        for key, series in series_dict.items():
            t_series = t_dict[key]
            synced = _interpolate_to_grid(t_series, series, t_common, interp_method)
            synced_series[key] = synced
            
    elif method == "kalman_align":
        # Kalman filter-based alignment
        process_noise = params.get("process_noise", 0.01)
        measurement_noise = params.get("measurement_noise", 0.1)
        
        for key, series in series_dict.items():
            t_series = t_dict[key]
            
            # First interpolate to common grid
            interpolated = _interpolate_to_grid(t_series, series, t_common, interp_method)
            
            # Then apply Kalman smoothing
            smoothed = _kalman_smooth_series(
                interpolated, 
                t_common,
                process_noise=process_noise,
                measurement_noise=measurement_noise
            )
            synced_series[key] = smoothed
    
    # Compute quality metrics
    alignment_error = _compute_alignment_error(
        synced_series, series_dict, t_dict, t_common
    )
    confidence = _compute_confidence(alignment_error, synced_series, t_common)
    
    # Create combined values array (mean of all synced series)
    all_values = np.stack(list(synced_series.values()), axis=0)
    combined_values = np.nanmean(all_values, axis=0)
    
    result = SyncResult(
        values=combined_values,
        metadata=_build_metadata(method, params),
        t_common=t_common,
        synced_series=synced_series,
        alignment_error=alignment_error,
        confidence=confidence,
        quality_metrics=QualityMetrics(rmse=alignment_error)
    )
    
    logger.info("synchronize_complete",
               method=method,
               n_series=len(synced_series),
               n_points=len(t_common),
               alignment_error=alignment_error,
               confidence=confidence)
    
    return result
