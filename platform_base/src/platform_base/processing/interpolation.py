from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Literal

import numpy as np
from scipy.interpolate import CubicSpline, UnivariateSpline

try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    from scipy.signal import lombscargle
    LOMBSCARGLE_AVAILABLE = True
except ImportError:
    LOMBSCARGLE_AVAILABLE = False

try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, WhiteKernel, Matern
    GPR_AVAILABLE = True
except ImportError:
    GPR_AVAILABLE = False

from platform_base.core.models import InterpResult, InterpolationInfo, ResultMetadata
from platform_base.utils.errors import InterpolationError
from platform_base.utils.logging import get_logger
from platform_base.profiling.decorators import profile, performance_critical

logger = get_logger(__name__)

SUPPORTED_METHODS = {
    "linear",
    "spline_cubic",
    "smoothing_spline",
    "resample_grid",
    # Advanced methods (with graceful degradation)
    "mls",                    # Moving Least Squares
    "gpr",                    # Gaussian Process Regression
    "lomb_scargle_spectral",  # Lomb-Scargle spectral interpolation
}


def _build_metadata(method: str, params: dict) -> ResultMetadata:
    return ResultMetadata(
        operation=method,
        parameters=params,
        platform_version="2.0.0",
        timestamp=datetime.now(timezone.utc),
        duration_ms=float(params.get("duration_ms", 0.0)),
        seed=params.get("seed"),
    )


# Numba-optimized functions for critical hotspots
def _create_numba_functions():
    """Create numba-optimized versions of critical functions if available."""
    if not NUMBA_AVAILABLE:
        logger.info("numba_not_available", message="Using standard numpy implementations")
        return None, None
    
    @numba.jit(nopython=True, cache=True)
    def _linear_interp_numba(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
        """Numba-optimized linear interpolation."""
        result = np.empty_like(x)
        n = len(xp)
        
        for i in range(len(x)):
            xi = x[i]
            
            if xi <= xp[0]:
                result[i] = fp[0]
            elif xi >= xp[n-1]:
                result[i] = fp[n-1]
            else:
                # Find interpolation interval
                for j in range(n-1):
                    if xp[j] <= xi <= xp[j+1]:
                        # Linear interpolation
                        t = (xi - xp[j]) / (xp[j+1] - xp[j])
                        result[i] = fp[j] + t * (fp[j+1] - fp[j])
                        break
        
        return result
    
    @numba.jit(nopython=True, cache=True)
    def _mask_missing_numba(values: np.ndarray) -> np.ndarray:
        """Numba-optimized missing value detection."""
        result = np.empty(len(values), dtype=numba.boolean)
        for i in range(len(values)):
            result[i] = not np.isfinite(values[i])
        return result
    
    logger.info("numba_functions_compiled", message="Numba JIT functions compiled successfully")
    return _linear_interp_numba, _mask_missing_numba


# Initialize numba functions
_linear_interp_numba, _mask_missing_numba = _create_numba_functions()


def _interp_mask(values: np.ndarray) -> np.ndarray:
    """Detect missing values with optional Numba acceleration."""
    if NUMBA_AVAILABLE and _mask_missing_numba is not None:
        return _mask_missing_numba(values)
    return ~np.isfinite(values)


# ============================================================================
# Advanced Interpolation Methods
# ============================================================================

def _mls_interpolate(
    t_valid: np.ndarray,
    v_valid: np.ndarray,
    t_target: np.ndarray,
    degree: int = 2,
    weight_radius: Optional[float] = None
) -> np.ndarray:
    """
    Moving Least Squares (MLS) interpolation.
    
    Fits a local polynomial at each target point using weighted least squares,
    where weights decrease with distance from the target point.
    
    Args:
        t_valid: Known time points
        v_valid: Known values
        t_target: Target time points for interpolation
        degree: Polynomial degree (1=linear, 2=quadratic, 3=cubic)
        weight_radius: Radius for weight function (default: auto from data)
    
    Returns:
        Interpolated values at t_target
    """
    n_valid = len(t_valid)
    n_target = len(t_target)
    
    if n_valid < degree + 1:
        logger.warning("mls_insufficient_points", n_points=n_valid, degree=degree)
        return np.interp(t_target, t_valid, v_valid)
    
    # Auto-determine weight radius if not provided
    if weight_radius is None:
        weight_radius = 3.0 * np.median(np.diff(t_valid))
    
    result = np.zeros(n_target)
    
    for i, t in enumerate(t_target):
        # Compute weights (Gaussian kernel)
        distances = np.abs(t_valid - t)
        weights = np.exp(-(distances / weight_radius) ** 2)
        
        # Clamp very small weights to avoid numerical issues
        weights = np.maximum(weights, 1e-10)
        
        # Build design matrix for polynomial fitting
        A = np.column_stack([t_valid ** p for p in range(degree + 1)])
        
        # Weighted least squares: (A^T W A) c = A^T W v
        W = np.diag(weights)
        
        try:
            AtWA = A.T @ W @ A
            AtWv = A.T @ W @ v_valid
            coeffs = np.linalg.solve(AtWA, AtWv)
            
            # Evaluate polynomial at target point
            t_powers = np.array([t ** p for p in range(degree + 1)])
            result[i] = np.dot(coeffs, t_powers)
        except np.linalg.LinAlgError:
            # Fallback to linear interpolation for this point
            result[i] = np.interp([t], t_valid, v_valid)[0]
    
    return result


def _gpr_interpolate(
    t_valid: np.ndarray,
    v_valid: np.ndarray,
    t_target: np.ndarray,
    length_scale: Optional[float] = None,
    kernel_type: Literal["rbf", "matern"] = "rbf",
    noise_level: float = 0.1,
    n_restarts: int = 3
) -> tuple[np.ndarray, np.ndarray]:
    """
    Gaussian Process Regression (GPR) interpolation.
    
    Provides interpolated values with uncertainty estimates.
    
    Args:
        t_valid: Known time points
        v_valid: Known values  
        t_target: Target time points for interpolation
        length_scale: Kernel length scale (default: auto)
        kernel_type: Kernel type ("rbf" or "matern")
        noise_level: Expected noise level in data
        n_restarts: Number of optimizer restarts
    
    Returns:
        Tuple of (interpolated_values, std_deviation)
    
    Raises:
        InterpolationError: If sklearn not available
    """
    if not GPR_AVAILABLE:
        raise InterpolationError(
            "GPR interpolation requires scikit-learn. Install with: pip install scikit-learn",
            {"method": "gpr", "missing_package": "scikit-learn"}
        )
    
    # Normalize time for better numerical stability
    t_mean = np.mean(t_valid)
    t_std = np.std(t_valid) if np.std(t_valid) > 0 else 1.0
    t_valid_norm = (t_valid - t_mean) / t_std
    t_target_norm = (t_target - t_mean) / t_std
    
    # Normalize values
    v_mean = np.mean(v_valid)
    v_std = np.std(v_valid) if np.std(v_valid) > 0 else 1.0
    v_valid_norm = (v_valid - v_mean) / v_std
    
    # Auto-determine length scale
    if length_scale is None:
        length_scale = np.median(np.diff(t_valid_norm)) * 3.0
    
    # Define kernel
    if kernel_type == "matern":
        kernel = Matern(length_scale=length_scale, nu=2.5) + WhiteKernel(
            noise_level=noise_level, noise_level_bounds=(1e-10, 1e5)
        )
    else:  # rbf
        kernel = RBF(length_scale=length_scale) + WhiteKernel(
            noise_level=noise_level, noise_level_bounds=(1e-10, 1e5)
        )
    
    # Fit GPR
    gpr = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=n_restarts,
        normalize_y=False,
        alpha=1e-10  # Small regularization to improve numerical stability
    )
    
    gpr.fit(t_valid_norm.reshape(-1, 1), v_valid_norm)
    
    # Predict
    y_pred_norm, y_std_norm = gpr.predict(t_target_norm.reshape(-1, 1), return_std=True)
    
    # Denormalize
    y_pred = y_pred_norm * v_std + v_mean
    y_std = y_std_norm * v_std
    
    return y_pred, y_std


def _lomb_scargle_interpolate(
    t_valid: np.ndarray,
    v_valid: np.ndarray,
    t_target: np.ndarray,
    n_frequencies: int = 100,
    min_freq: Optional[float] = None,
    max_freq: Optional[float] = None,
    n_components: int = 20
) -> np.ndarray:
    """
    Lomb-Scargle spectral interpolation for irregularly sampled data.
    
    Uses Lomb-Scargle periodogram to identify dominant frequencies,
    then reconstructs signal using those components.
    
    Args:
        t_valid: Known time points (can be irregular)
        v_valid: Known values
        t_target: Target time points for interpolation
        n_frequencies: Number of frequencies to analyze
        min_freq: Minimum frequency (default: 1/time_span)
        max_freq: Maximum frequency (default: Nyquist-like estimate)
        n_components: Number of frequency components to use for reconstruction
    
    Returns:
        Interpolated values at t_target
    """
    if not LOMBSCARGLE_AVAILABLE:
        raise InterpolationError(
            "Lomb-Scargle requires scipy.signal. Update scipy if needed.",
            {"method": "lomb_scargle_spectral"}
        )
    
    # Remove mean for spectral analysis
    v_mean = np.mean(v_valid)
    v_centered = v_valid - v_mean
    
    # Determine frequency range
    time_span = t_valid[-1] - t_valid[0]
    if min_freq is None:
        min_freq = 1.0 / time_span
    if max_freq is None:
        # Pseudo-Nyquist based on median sampling
        median_dt = np.median(np.diff(t_valid))
        max_freq = 0.5 / median_dt
    
    # Angular frequencies
    freqs = np.linspace(min_freq, max_freq, n_frequencies)
    angular_freqs = 2 * np.pi * freqs
    
    # Compute Lomb-Scargle periodogram
    pgram = lombscargle(t_valid, v_centered, angular_freqs, normalize=False)
    
    # Select top frequency components
    n_components = min(n_components, len(freqs))
    top_indices = np.argsort(pgram)[-n_components:]
    top_freqs = freqs[top_indices]
    top_powers = pgram[top_indices]
    
    # Estimate amplitudes and phases for each component
    result = np.full(len(t_target), v_mean)
    
    for freq, power in zip(top_freqs, top_powers):
        omega = 2 * np.pi * freq
        
        # Least squares fit for amplitude and phase: a*cos(wt) + b*sin(wt)
        cos_t = np.cos(omega * t_valid)
        sin_t = np.sin(omega * t_valid)
        
        A = np.column_stack([cos_t, sin_t])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(A, v_centered, rcond=None)
            a, b = coeffs
            
            # Reconstruct at target points
            result += a * np.cos(omega * t_target) + b * np.sin(omega * t_target)
        except np.linalg.LinAlgError:
            continue
    
    # Scale result to match original variance approximately
    result_std = np.std(result)
    original_std = np.std(v_valid)
    if result_std > 0:
        result = v_mean + (result - v_mean) * (original_std / result_std) * 0.8
    
    return result


@profile(target_name="interpolation_1m")
@performance_critical(max_time_seconds=2.0, operation_name="interpolation")
def interpolate(
    values: np.ndarray,
    t_seconds: np.ndarray,
    method: str,
    params: dict,
) -> InterpResult:
    if method not in SUPPORTED_METHODS:
        raise InterpolationError(
            "Interpolation method not available",
            {"method": method, "supported": sorted(SUPPORTED_METHODS)},
        )

    values = values.astype(float)
    t_seconds = t_seconds.astype(float)
    mask_missing = _interp_mask(values)
    t_valid = t_seconds[~mask_missing]
    v_valid = values[~mask_missing]

    finite_mask = np.isfinite(t_valid)
    t_valid = t_valid[finite_mask]
    v_valid = v_valid[finite_mask]

    if len(t_valid) < 2:
        raise InterpolationError("Not enough points for interpolation", {"method": method})

    order = np.argsort(t_valid)
    t_valid = t_valid[order]
    v_valid = v_valid[order]
    t_valid, unique_idx = np.unique(t_valid, return_index=True)
    v_valid = v_valid[unique_idx]

    if method == "linear":
        # Use Numba-optimized linear interpolation if available
        if NUMBA_AVAILABLE and _linear_interp_numba is not None and len(t_valid) > 1000:
            logger.debug("using_numba_linear_interpolation", n_points=len(t_seconds))
            interp_all = _linear_interp_numba(t_seconds, t_valid, v_valid)
        else:
            interp_all = np.interp(t_seconds, t_valid, v_valid)
        
        interp_values = values.copy()
        interp_values[mask_missing] = interp_all[mask_missing]
        method_used = np.where(mask_missing, method, "original")
        info = InterpolationInfo(
            is_interpolated_mask=mask_missing,
            method_used=method_used.astype("<U32"),
        )
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, params))

    if method == "spline_cubic":
        spline = CubicSpline(t_valid, v_valid)
        interp_all = spline(t_seconds)
        interp_values = values.copy()
        interp_values[mask_missing] = interp_all[mask_missing]
        method_used = np.where(mask_missing, method, "original")
        info = InterpolationInfo(
            is_interpolated_mask=mask_missing,
            method_used=method_used.astype("<U32"),
        )
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, params))

    if method == "smoothing_spline":
        smoothing = params.get("s")
        spline = UnivariateSpline(t_valid, v_valid, s=smoothing)
        interp_all = spline(t_seconds)
        interp_values = values.copy()
        interp_values[mask_missing] = interp_all[mask_missing]
        method_used = np.where(mask_missing, method, "original")
        info = InterpolationInfo(
            is_interpolated_mask=mask_missing,
            method_used=method_used.astype("<U32"),
        )
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, params))

    if method == "resample_grid":
        dt = params.get("dt")
        n_points = params.get("n_points")
        start = float(np.nanmin(t_seconds))
        end = float(np.nanmax(t_seconds))
        if dt is not None:
            t_out = np.arange(start, end + dt, dt)
        elif n_points is not None:
            t_out = np.linspace(start, end, int(n_points))
        else:
            raise InterpolationError("resample_grid requires dt or n_points", {"method": method})
        interp_values = np.interp(t_out, t_valid, v_valid)
        mask = np.ones(len(t_out), dtype=bool)
        info = InterpolationInfo(
            is_interpolated_mask=mask,
            method_used=np.full(len(t_out), method, dtype="<U32"),
        )
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, params))

    # ========================================================================
    # Advanced Methods (with graceful degradation)
    # ========================================================================
    
    if method == "mls":
        # Moving Least Squares interpolation
        logger.info("using_mls_interpolation", n_valid=len(t_valid), n_total=len(t_seconds))
        
        degree = params.get("degree", 2)
        weight_radius = params.get("weight_radius")
        
        interp_all = _mls_interpolate(t_valid, v_valid, t_seconds, 
                                      degree=degree, weight_radius=weight_radius)
        
        interp_values = values.copy()
        interp_values[mask_missing] = interp_all[mask_missing]
        method_used = np.where(mask_missing, method, "original")
        info = InterpolationInfo(
            is_interpolated_mask=mask_missing,
            method_used=method_used.astype("<U32"),
        )
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, params))
    
    if method == "gpr":
        # Gaussian Process Regression interpolation
        logger.info("using_gpr_interpolation", n_valid=len(t_valid), n_total=len(t_seconds))
        
        if not GPR_AVAILABLE:
            raise InterpolationError(
                "GPR interpolation requires scikit-learn. Install with: pip install scikit-learn",
                {"method": method, "missing_package": "scikit-learn"}
            )
        
        length_scale = params.get("length_scale")
        kernel_type = params.get("kernel_type", "rbf")
        noise_level = params.get("noise_level", 0.1)
        n_restarts = params.get("n_restarts", 3)
        
        # GPR can be slow for large datasets, subsample if needed
        max_train_points = params.get("max_train_points", 1000)
        if len(t_valid) > max_train_points:
            logger.warning("gpr_subsampling", 
                          original_points=len(t_valid), 
                          subsampled_to=max_train_points)
            indices = np.linspace(0, len(t_valid) - 1, max_train_points, dtype=int)
            t_train = t_valid[indices]
            v_train = v_valid[indices]
        else:
            t_train = t_valid
            v_train = v_valid
        
        interp_all, std_all = _gpr_interpolate(
            t_train, v_train, t_seconds,
            length_scale=length_scale,
            kernel_type=kernel_type,
            noise_level=noise_level,
            n_restarts=n_restarts
        )
        
        interp_values = values.copy()
        interp_values[mask_missing] = interp_all[mask_missing]
        method_used = np.where(mask_missing, method, "original")
        info = InterpolationInfo(
            is_interpolated_mask=mask_missing,
            method_used=method_used.astype("<U32"),
        )
        
        # Store uncertainty in params for metadata
        result_params = params.copy()
        result_params["uncertainty_std"] = float(np.mean(std_all[mask_missing])) if np.any(mask_missing) else 0.0
        
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, result_params))
    
    if method == "lomb_scargle_spectral":
        # Lomb-Scargle spectral interpolation
        logger.info("using_lomb_scargle_interpolation", n_valid=len(t_valid), n_total=len(t_seconds))
        
        if not LOMBSCARGLE_AVAILABLE:
            raise InterpolationError(
                "Lomb-Scargle requires scipy.signal. Update scipy if needed.",
                {"method": method}
            )
        
        n_frequencies = params.get("n_frequencies", 100)
        min_freq = params.get("min_freq")
        max_freq = params.get("max_freq")
        n_components = params.get("n_components", 20)
        
        interp_all = _lomb_scargle_interpolate(
            t_valid, v_valid, t_seconds,
            n_frequencies=n_frequencies,
            min_freq=min_freq,
            max_freq=max_freq,
            n_components=n_components
        )
        
        interp_values = values.copy()
        interp_values[mask_missing] = interp_all[mask_missing]
        method_used = np.where(mask_missing, method, "original")
        info = InterpolationInfo(
            is_interpolated_mask=mask_missing,
            method_used=method_used.astype("<U32"),
        )
        return InterpResult(values=interp_values, interpolation_info=info, metadata=_build_metadata(method, params))

    raise InterpolationError("Interpolation method not implemented", {"method": method})
