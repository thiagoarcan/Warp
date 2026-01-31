"""
Downsampling algorithms for time series data - Platform Base v2.0

Implements efficient downsampling methods to handle large datasets:
- LTTB (Largest Triangle Three Buckets) - preserves visual characteristics
- MinMax - preserves extrema for each interval
- Adaptive - variable density based on data variance
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Literal

import numpy as np


try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from platform_base.core.models import DownsampleResult, QualityMetrics, ResultMetadata
from platform_base.profiling.decorators import performance_critical, profile
from platform_base.utils.errors import DownsampleError
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)

SUPPORTED_METHODS = {
    "lttb",           # Largest Triangle Three Buckets
    "minmax",         # Min-Max downsampling
    "adaptive",       # Adaptive downsampling
    "uniform",        # Uniform spacing
    "peak_aware",     # Peak-aware downsampling
}


def _build_metadata(method: str, params: dict, duration_ms: float = 0.0) -> ResultMetadata:
    """Build result metadata"""
    return ResultMetadata(
        operation=f"downsample_{method}",
        parameters=params,
        platform_version="2.0.0",
        timestamp=datetime.now(UTC),
        duration_ms=duration_ms,
    )


# Numba-optimized functions for critical performance
def _create_numba_functions():
    """Create numba-optimized downsampling functions if available."""
    if not NUMBA_AVAILABLE:
        logger.info("numba_downsampling_not_available",
                   message="Using standard numpy implementations")
        return None, None, None

    @numba.jit(nopython=True, cache=True)
    def _triangle_area_numba(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
        """Calculate triangle area using numba"""
        return abs((p1_x * (p2_y - p3_y) + p2_x * (p3_y - p1_y) + p3_x * (p1_y - p2_y)) / 2.0)

    @numba.jit(nopython=True, cache=True)
    def _lttb_bucket_numba(t_bucket, v_bucket, prev_point, next_avg_point):
        """LTTB bucket processing with numba"""
        max_area = -1.0
        max_idx = 0

        for i in range(len(t_bucket)):
            area = _triangle_area_numba(
                prev_point[0], prev_point[1],
                t_bucket[i], v_bucket[i],
                next_avg_point[0], next_avg_point[1],
            )
            if area > max_area:
                max_area = area
                max_idx = i

        return max_idx, max_area

    @numba.jit(nopython=True, cache=True)
    def _minmax_bucket_numba(v_bucket):
        """MinMax bucket processing with numba"""
        min_val = v_bucket[0]
        max_val = v_bucket[0]
        min_idx = 0
        max_idx = 0

        for i in range(1, len(v_bucket)):
            if v_bucket[i] < min_val:
                min_val = v_bucket[i]
                min_idx = i
            elif v_bucket[i] > max_val:
                max_val = v_bucket[i]
                max_idx = i

        return min_idx, max_idx

    logger.info("numba_downsampling_compiled",
               message="Numba downsampling functions compiled successfully")
    return _triangle_area_numba, _lttb_bucket_numba, _minmax_bucket_numba


# Initialize numba functions
_triangle_area_numba, _lttb_bucket_numba, _minmax_bucket_numba = _create_numba_functions()


def _lttb_downsample(
    t: np.ndarray,
    values: np.ndarray,
    n_points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Largest Triangle Three Buckets (LTTB) downsampling.

    Preserves visual characteristics by selecting points that form
    the largest triangular areas, maintaining the overall shape.

    Args:
        t: Time array
        values: Value array
        n_points: Target number of points

    Returns:
        Tuple of (downsampled_t, downsampled_values, selected_indices)
    """
    n_data = len(t)

    if n_points >= n_data:
        return t.copy(), values.copy(), np.arange(n_data)

    if n_points < 3:
        # For very few points, just take first, middle, last
        indices = [0, n_data // 2, n_data - 1]
        indices = indices[:n_points]
        return t[indices], values[indices], np.array(indices)

    # Calculate bucket size
    bucket_size = (n_data - 2) / (n_points - 2)

    # Always include first and last points
    selected_indices = [0]
    selected_t = [t[0]]
    selected_values = [values[0]]

    # Process intermediate buckets
    prev_point = (t[0], values[0])

    for i in range(n_points - 2):
        # Current bucket range
        bucket_start = int(i * bucket_size) + 1
        bucket_end = int((i + 1) * bucket_size) + 1

        bucket_end = min(n_data - 1, bucket_end)

        if bucket_start >= bucket_end:
            continue

        # Calculate average point for next bucket (for triangle area calculation)
        if i < n_points - 3:  # Not the last bucket
            next_bucket_start = bucket_end
            next_bucket_end = int((i + 2) * bucket_size) + 1
            next_bucket_end = min(n_data, next_bucket_end)

            if next_bucket_start < next_bucket_end:
                next_avg_t = np.mean(t[next_bucket_start:next_bucket_end])
                next_avg_val = np.mean(values[next_bucket_start:next_bucket_end])
            else:
                next_avg_t = t[-1]
                next_avg_val = values[-1]
        else:
            # For last bucket, use last point
            next_avg_t = t[-1]
            next_avg_val = values[-1]

        next_avg_point = (next_avg_t, next_avg_val)

        # Find point in bucket that creates largest triangle
        t_bucket = t[bucket_start:bucket_end]
        v_bucket = values[bucket_start:bucket_end]

        if len(t_bucket) == 0:
            continue

        # Use numba optimization if available
        if NUMBA_AVAILABLE and _lttb_bucket_numba is not None and len(t_bucket) > 10:
            max_idx, _ = _lttb_bucket_numba(t_bucket, v_bucket, prev_point, next_avg_point)
        else:
            # Standard implementation
            max_area = -1
            max_idx = 0

            for j, (t_val, v_val) in enumerate(zip(t_bucket, v_bucket, strict=False)):
                # Calculate triangle area
                area = abs((prev_point[0] * (v_val - next_avg_point[1]) +
                           t_val * (next_avg_point[1] - prev_point[1]) +
                           next_avg_point[0] * (prev_point[1] - v_val)) / 2.0)

                if area > max_area:
                    max_area = area
                    max_idx = j

        # Select point
        actual_idx = bucket_start + max_idx
        selected_indices.append(actual_idx)
        selected_t.append(t[actual_idx])
        selected_values.append(values[actual_idx])

        prev_point = (t[actual_idx], values[actual_idx])

    # Always include last point
    if selected_indices[-1] != n_data - 1:
        selected_indices.append(n_data - 1)
        selected_t.append(t[-1])
        selected_values.append(values[-1])

    return (np.array(selected_t),
            np.array(selected_values),
            np.array(selected_indices))


def _minmax_downsample(
    t: np.ndarray,
    values: np.ndarray,
    n_points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    MinMax downsampling - preserves extrema.

    Divides data into buckets and selects min/max values from each bucket,
    ensuring all peaks and valleys are preserved.

    Args:
        t: Time array
        values: Value array
        n_points: Target number of points (will be adjusted to even number)

    Returns:
        Tuple of (downsampled_t, downsampled_values, selected_indices)
    """
    n_data = len(t)

    if n_points >= n_data:
        return t.copy(), values.copy(), np.arange(n_data)

    # Ensure even number of points (min/max pairs)
    n_buckets = max(1, n_points // 2)
    bucket_size = n_data / n_buckets

    selected_indices = []
    selected_t = []
    selected_values = []

    for i in range(n_buckets):
        bucket_start = int(i * bucket_size)
        bucket_end = int((i + 1) * bucket_size)

        if i == n_buckets - 1:  # Last bucket
            bucket_end = n_data

        if bucket_start >= bucket_end:
            continue

        # Get bucket data
        t[bucket_start:bucket_end]
        v_bucket = values[bucket_start:bucket_end]

        if len(v_bucket) == 0:
            continue

        # Find min and max indices
        if NUMBA_AVAILABLE and _minmax_bucket_numba is not None and len(v_bucket) > 10:
            min_idx_local, max_idx_local = _minmax_bucket_numba(v_bucket)
        else:
            min_idx_local = np.argmin(v_bucket)
            max_idx_local = np.argmax(v_bucket)

        # Convert to global indices
        min_idx = bucket_start + min_idx_local
        max_idx = bucket_start + max_idx_local

        # Add points in time order
        indices_to_add = sorted([min_idx, max_idx])
        for idx in indices_to_add:
            if idx not in selected_indices:  # Avoid duplicates
                selected_indices.append(idx)
                selected_t.append(t[idx])
                selected_values.append(values[idx])

    # Sort by time order
    if selected_indices:
        sort_order = np.argsort(selected_t)
        selected_indices = np.array(selected_indices)[sort_order]
        selected_t = np.array(selected_t)[sort_order]
        selected_values = np.array(selected_values)[sort_order]
    else:
        # Fallback: select first and last points
        selected_indices = np.array([0, n_data - 1])
        selected_t = np.array([t[0], t[-1]])
        selected_values = np.array([values[0], values[-1]])

    return selected_t, selected_values, selected_indices


def _adaptive_downsample(
    t: np.ndarray,
    values: np.ndarray,
    n_points: int,
    variance_threshold: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Adaptive downsampling based on local variance.

    Allocates more points to regions with higher variance,
    fewer points to stable regions.

    Args:
        t: Time array
        values: Value array
        n_points: Target number of points
        variance_threshold: Minimum variance threshold

    Returns:
        Tuple of (downsampled_t, downsampled_values, selected_indices)
    """
    n_data = len(t)

    if n_points >= n_data:
        return t.copy(), values.copy(), np.arange(n_data)

    # Calculate local variance using sliding window
    window_size = max(3, n_data // 100)  # Adaptive window size
    variances = np.zeros(n_data)

    for i in range(n_data):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(n_data, i + window_size // 2 + 1)
        window_values = values[start_idx:end_idx]
        variances[i] = np.var(window_values) if len(window_values) > 1 else 0.0

    # Normalize variances
    max_variance = np.max(variances)
    if max_variance > 0:
        variances = variances / max_variance

    # Apply threshold
    variances = np.maximum(variances, variance_threshold)

    # Calculate cumulative importance
    importance = variances / np.sum(variances)
    cumulative_importance = np.cumsum(importance)

    # Select points based on importance distribution
    selected_indices = []
    target_spacing = 1.0 / n_points

    # Always include first point
    selected_indices.append(0)

    # Select intermediate points
    for i in range(1, n_points - 1):
        target_cumulative = i * target_spacing

        # Find closest point in cumulative importance
        closest_idx = np.argmin(np.abs(cumulative_importance - target_cumulative))

        # Avoid duplicates
        if closest_idx not in selected_indices:
            selected_indices.append(closest_idx)

    # Always include last point
    if (n_data - 1) not in selected_indices:
        selected_indices.append(n_data - 1)

    # Sort indices
    selected_indices = sorted(set(selected_indices))
    selected_indices = np.array(selected_indices)

    return t[selected_indices], values[selected_indices], selected_indices


def _uniform_downsample(
    t: np.ndarray,
    values: np.ndarray,
    n_points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Uniform downsampling - evenly spaced points.

    Simple downsampling that selects points at uniform intervals.

    Args:
        t: Time array
        values: Value array
        n_points: Target number of points

    Returns:
        Tuple of (downsampled_t, downsampled_values, selected_indices)
    """
    n_data = len(t)

    if n_points >= n_data:
        return t.copy(), values.copy(), np.arange(n_data)

    # Generate uniform indices
    indices = np.linspace(0, n_data - 1, n_points, dtype=int)

    return t[indices], values[indices], indices


def _peak_aware_downsample(
    t: np.ndarray,
    values: np.ndarray,
    n_points: int,
    peak_threshold_percentile: float = 95.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Peak-aware downsampling - preserves significant peaks.

    Identifies peaks above a threshold and ensures they are preserved,
    then fills remaining points uniformly.

    Args:
        t: Time array
        values: Value array
        n_points: Target number of points
        peak_threshold_percentile: Percentile threshold for peak detection

    Returns:
        Tuple of (downsampled_t, downsampled_values, selected_indices)
    """
    n_data = len(t)

    if n_points >= n_data:
        return t.copy(), values.copy(), np.arange(n_data)

    # Detect peaks
    from scipy.signal import find_peaks

    # Calculate threshold based on percentile
    threshold = np.percentile(np.abs(values), peak_threshold_percentile)

    # Find peaks above threshold
    peak_indices, _ = find_peaks(np.abs(values), height=threshold)

    # Start with peaks
    selected_indices = list(peak_indices)

    # Always include first and last points
    if 0 not in selected_indices:
        selected_indices.append(0)
    if (n_data - 1) not in selected_indices:
        selected_indices.append(n_data - 1)

    # If we have too many peaks, select the most significant ones
    if len(selected_indices) > n_points:
        peak_values = np.abs(values[peak_indices])
        top_peak_indices = peak_indices[np.argsort(peak_values)[-n_points+2:]]  # Keep room for first/last
        selected_indices = [0, *list(top_peak_indices), n_data - 1]

    # If we need more points, add uniformly distributed ones
    if len(selected_indices) < n_points:
        remaining_points = n_points - len(selected_indices)

        # Create mask of available indices
        available_mask = np.ones(n_data, dtype=bool)
        available_mask[selected_indices] = False
        available_indices = np.where(available_mask)[0]

        if len(available_indices) > 0:
            # Select uniformly from available indices
            step = max(1, len(available_indices) // remaining_points)
            additional_indices = available_indices[::step][:remaining_points]
            selected_indices.extend(additional_indices)

    # Sort indices
    selected_indices = sorted(set(selected_indices))
    selected_indices = np.array(selected_indices)

    return t[selected_indices], values[selected_indices], selected_indices


@profile(target_name="downsample_1m")
@performance_critical(max_time_seconds=1.0, operation_name="downsampling")
def downsample(
    values: np.ndarray,
    t_seconds: np.ndarray,
    n_points: int,
    method: Literal["lttb", "minmax", "adaptive", "uniform", "peak_aware"] = "lttb",
    params: dict | None = None,
) -> DownsampleResult:
    """
    Downsample time series data using various algorithms.

    Args:
        values: Value array to downsample
        t_seconds: Time array in seconds
        n_points: Target number of points
        method: Downsampling method
        params: Method-specific parameters

    Returns:
        DownsampleResult with downsampled data and metadata

    Raises:
        DownsampleError: If method not supported or insufficient data
    """
    start_time = time.perf_counter()

    if params is None:
        params = {}

    if method not in SUPPORTED_METHODS:
        raise DownsampleError(
            f"Downsampling method '{method}' not supported",
            {"method": method, "supported": sorted(SUPPORTED_METHODS)},
        )

    values = values.astype(float)
    t_seconds = t_seconds.astype(float)
    n_data = len(values)

    if n_data != len(t_seconds):
        raise DownsampleError(
            "Values and time arrays must have same length",
            {"values_len": len(values), "time_len": len(t_seconds)},
        )

    if n_data < 2:
        raise DownsampleError(
            "Insufficient data for downsampling",
            {"n_data": n_data, "minimum": 2},
        )

    if n_points <= 0:
        raise DownsampleError(
            "Target points must be positive",
            {"n_points": n_points},
        )

    # Sort by time if needed
    if not np.all(np.diff(t_seconds) >= 0):
        sort_order = np.argsort(t_seconds)
        t_seconds = t_seconds[sort_order]
        values = values[sort_order]
        logger.debug("data_sorted_by_time")

    # Apply downsampling method
    try:
        if method == "lttb":
            downsampled_t, downsampled_values, selected_indices = _lttb_downsample(
                t_seconds, values, n_points)

        elif method == "minmax":
            downsampled_t, downsampled_values, selected_indices = _minmax_downsample(
                t_seconds, values, n_points)

        elif method == "adaptive":
            variance_threshold = params.get("variance_threshold", 0.1)
            downsampled_t, downsampled_values, selected_indices = _adaptive_downsample(
                t_seconds, values, n_points, variance_threshold)

        elif method == "uniform":
            downsampled_t, downsampled_values, selected_indices = _uniform_downsample(
                t_seconds, values, n_points)

        elif method == "peak_aware":
            peak_threshold_percentile = params.get("peak_threshold_percentile", 95.0)
            downsampled_t, downsampled_values, selected_indices = _peak_aware_downsample(
                t_seconds, values, n_points, peak_threshold_percentile)

        else:
            raise DownsampleError(f"Method {method} not implemented")

    except Exception as e:
        raise DownsampleError(f"Downsampling failed: {e!s}", {"method": method}) from e

    # Calculate metrics
    duration_ms = (time.perf_counter() - start_time) * 1000
    reduction_ratio = len(downsampled_values) / n_data

    quality_metrics = QualityMetrics(
        n_valid=len(downsampled_values),
        n_interpolated=0,
        n_nan=np.sum(~np.isfinite(downsampled_values)),
    )

    # Enhanced metadata
    result_params = {
        **params,
        "original_points": int(n_data),
        "target_points": int(n_points),
        "actual_points": len(downsampled_values),
        "reduction_ratio": float(reduction_ratio),
        "compression_ratio": float(n_data / len(downsampled_values)),
        "time_span_preserved": float(downsampled_t[-1] - downsampled_t[0]) if len(downsampled_t) > 1 else 0.0,
    }

    logger.info("downsampling_completed",
               method=method,
               original_points=n_data,
               downsampled_points=len(downsampled_values),
               reduction_ratio=reduction_ratio,
               duration_ms=duration_ms)

    return DownsampleResult(
        values=downsampled_values,
        t_seconds=downsampled_t,
        selected_indices=selected_indices,
        metadata=_build_metadata(method, result_params, duration_ms),
        quality_metrics=quality_metrics,
    )


# Convenience functions
def lttb_downsample(values: np.ndarray, t_seconds: np.ndarray,
                   n_points: int, **kwargs) -> DownsampleResult:
    """LTTB downsampling convenience function"""
    return downsample(values, t_seconds, n_points, method="lttb", params=kwargs)


def minmax_downsample(values: np.ndarray, t_seconds: np.ndarray,
                     n_points: int, **kwargs) -> DownsampleResult:
    """MinMax downsampling convenience function"""
    return downsample(values, t_seconds, n_points, method="minmax", params=kwargs)


def adaptive_downsample(values: np.ndarray, t_seconds: np.ndarray,
                       n_points: int, **kwargs) -> DownsampleResult:
    """Adaptive downsampling convenience function"""
    return downsample(values, t_seconds, n_points, method="adaptive", params=kwargs)
