from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import savgol_filter

try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from platform_base.core.models import CalcResult, ResultMetadata
from platform_base.processing.smoothing import SmoothingConfig, smooth
from platform_base.utils.errors import CalculusError
from platform_base.utils.logging import get_logger
from platform_base.profiling.decorators import profile, performance_critical

logger = get_logger(__name__)


# Numba-optimized calculus functions
def _create_numba_calculus_functions():
    """Create numba-optimized versions of calculus functions if available."""
    if not NUMBA_AVAILABLE:
        logger.info("numba_calculus_not_available", message="Using standard numpy implementations")
        return None, None, None
    
    @numba.jit(nopython=True, cache=True)
    def _finite_diff_numba(values: np.ndarray, t: np.ndarray) -> np.ndarray:
        """Numba-optimized finite difference derivative."""
        n = len(values)
        deriv = np.empty(n)
        
        if n < 2:
            return values
        
        # Forward difference for first point
        deriv[0] = (values[1] - values[0]) / (t[1] - t[0])
        
        # Central difference for interior points
        for i in range(1, n-1):
            deriv[i] = (values[i+1] - values[i-1]) / (t[i+1] - t[i-1])
        
        # Backward difference for last point
        deriv[n-1] = (values[n-1] - values[n-2]) / (t[n-1] - t[n-2])
        
        return deriv
    
    @numba.jit(nopython=True, cache=True)
    def _trapz_numba(values: np.ndarray, t: np.ndarray) -> float:
        """Numba-optimized trapezoidal integration."""
        n = len(values)
        if n < 2:
            return 0.0
            
        integral = 0.0
        for i in range(n-1):
            dt = t[i+1] - t[i]
            integral += 0.5 * (values[i] + values[i+1]) * dt
        
        return integral
    
    @numba.jit(nopython=True, cache=True)
    def _area_between_numba(upper: np.ndarray, lower: np.ndarray, t: np.ndarray) -> float:
        """Numba-optimized area between curves."""
        diff = upper - lower
        return _trapz_numba(diff, t)
    
    logger.info("numba_calculus_compiled", message="Numba calculus functions compiled successfully")
    return _finite_diff_numba, _trapz_numba, _area_between_numba


# Initialize numba calculus functions
_finite_diff_numba, _trapz_numba, _area_between_numba = _create_numba_calculus_functions()


def _build_metadata(method: str, params: dict) -> ResultMetadata:
    return ResultMetadata(
        method=method,
        params=params,
        version="2.0.0",
        timestamp=datetime.now(timezone.utc),
    )


@profile(target_name="derivative_1m")
@performance_critical(max_time_seconds=1.0, operation_name="derivative")
def derivative(
    values: np.ndarray,
    t: np.ndarray,
    order: int,
    method: str,
    params: dict,
    smoothing: Optional[SmoothingConfig] = None,
) -> CalcResult:
    if order < 1 or order > 3:
        raise CalculusError("Order must be between 1 and 3", {"order": order})

    data = values.astype(float)
    if smoothing is not None:
        data = smooth(data, smoothing.method, smoothing.params)

    if method == "finite_diff":
        # Use Numba-optimized finite difference for large datasets and 1st order
        if (NUMBA_AVAILABLE and _finite_diff_numba is not None and 
            len(data) > 10000 and order == 1):
            logger.debug("using_numba_finite_diff", n_points=len(data), order=order)
            deriv = _finite_diff_numba(data, t)
        else:
            deriv = data
            for _ in range(order):
                deriv = np.gradient(deriv, t)
    elif method == "savitzky_golay":
        window_length = params.get("window_length", 7)
        polyorder = params.get("polyorder", 3)
        delta = params.get("delta", float(np.median(np.diff(t))))
        deriv = savgol_filter(
            data,
            window_length=window_length,
            polyorder=polyorder,
            deriv=order,
            delta=delta,
        )
    elif method == "spline_derivative":
        spline = UnivariateSpline(t, data, s=params.get("s"))
        deriv = spline.derivative(n=order)(t)
    else:
        raise CalculusError("Derivative method not available", {"method": method})

    return CalcResult(
        values=deriv,
        metadata=_build_metadata(method, params),
        operation="derivative",
        order=order,
    )


@profile(target_name="integral_500k")
@performance_critical(max_time_seconds=0.5, operation_name="integral")
def integral(values: np.ndarray, t: np.ndarray, method: str = "trapezoid") -> CalcResult:
    if method != "trapezoid":
        raise CalculusError("Integral method not available", {"method": method})
    
    # Use Numba-optimized trapezoidal integration for large datasets
    if NUMBA_AVAILABLE and _trapz_numba is not None and len(values) > 10000:
        logger.debug("using_numba_trapz", n_points=len(values))
        area = _trapz_numba(values, t)
    else:
        area = np.trapz(values, t)
    
    return CalcResult(
        values=np.array([area], dtype=float),
        metadata=_build_metadata(method, {}),
        operation="integral",
        order=None,
    )


def area_between(series_upper: np.ndarray, series_lower: np.ndarray, t: np.ndarray) -> CalcResult:
    # Use Numba-optimized area calculation for large datasets
    if NUMBA_AVAILABLE and _area_between_numba is not None and len(series_upper) > 10000:
        logger.debug("using_numba_area_between", n_points=len(series_upper))
        area = _area_between_numba(series_upper, series_lower, t)
    else:
        area = np.trapz(series_upper - series_lower, t)
    
    return CalcResult(
        values=np.array([area], dtype=float),
        metadata=_build_metadata("area_between", {}),
        operation="area_between",
        order=None,
    )
