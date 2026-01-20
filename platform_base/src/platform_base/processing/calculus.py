from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Literal
import time

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import savgol_filter
try:
    from scipy.integrate import cumulative_trapezoid as cumtrapz
except ImportError:
    from scipy.integrate import cumtrapz
    
try:
    from scipy.integrate import simpson
except ImportError:
    from scipy.integrate import simps as simpson

try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from platform_base.core.models import CalcResult, ResultMetadata, QualityMetrics
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


def _build_metadata(method: str, params: dict, duration_ms: float = 0.0) -> ResultMetadata:
    """Constrói metadata conforme especificação seção 5.6"""
    return ResultMetadata(
        operation=method,
        parameters=params,
        platform_version="2.0.0",
        timestamp=datetime.now(timezone.utc),
        duration_ms=duration_ms,
    )


@profile(target_name="derivative_1m")
@performance_critical(max_time_seconds=1.0, operation_name="derivative")
def derivative(
    values: np.ndarray,
    t: np.ndarray,
    order: int,
    method: Literal["finite_diff", "savitzky_golay", "spline_derivative"] = "finite_diff",
    params: Optional[dict] = None,
    smoothing: Optional[SmoothingConfig] = None,
) -> CalcResult:
    """Calcula derivadas 1ª-3ª ordem conforme especificação seção 9.1"""
    start_time = time.perf_counter()
    
    if params is None:
        params = {}
    
    if order < 1 or order > 3:
        raise CalculusError("Order must be between 1 and 3", {"order": order})

    data = values.astype(float)
    n_points = len(data)
    
    # Validação de dados
    if n_points < 2:
        raise CalculusError("Insufficient points for derivative calculation", {"n_points": n_points})
        
    # Aplica suavização se especificado
    if smoothing is not None:
        data = smooth(data, smoothing.method, smoothing.params)
        logger.debug("derivative_smoothing_applied", method=smoothing.method)

    if method == "finite_diff":
        # Use Numba-optimized finite difference for large datasets and 1st order
        if (NUMBA_AVAILABLE and _finite_diff_numba is not None and 
            n_points > 10000 and order == 1):
            logger.debug("using_numba_finite_diff", n_points=n_points, order=order)
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

    # Calcular métricas de qualidade
    n_valid = np.sum(np.isfinite(deriv))
    n_nan = np.sum(~np.isfinite(deriv))
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    quality_metrics = QualityMetrics(
        n_valid=n_valid,
        n_interpolated=0,  # Derivadas não são interpoladas
        n_nan=n_nan
    )
    
    logger.info("derivative_computed", 
               order=order, 
               method=method, 
               n_points=n_points,
               duration_ms=duration_ms)
    
    return CalcResult(
        values=deriv,
        metadata=_build_metadata(method, params, duration_ms),
        quality_metrics=quality_metrics,
        operation="derivative",
        order=order,
    )


@profile(target_name="integral_500k")
@performance_critical(max_time_seconds=0.5, operation_name="integral")
def integral(
    values: np.ndarray, 
    t: np.ndarray, 
    method: Literal["trapezoid", "simpson", "cumulative"] = "trapezoid",
    params: Optional[dict] = None
) -> CalcResult:
    """Calcula integrais conforme especificação seção 9.2"""
    start_time = time.perf_counter()
    
    if params is None:
        params = {}
    
    n_points = len(values)
    
    if n_points < 2:
        raise CalculusError("Insufficient points for integration", {"n_points": n_points})
    
    if method == "trapezoid":
        # Use Numba-optimized trapezoidal integration for large datasets
        if NUMBA_AVAILABLE and _trapz_numba is not None and n_points > 10000:
            logger.debug("using_numba_trapz", n_points=n_points)
            area = _trapz_numba(values, t)
        else:
            area = np.trapz(values, t)
        result_values = np.array([area], dtype=float)
        
    elif method == "simpson":
        # Regra de Simpson (requer número ímpar de pontos)
        if n_points % 2 == 0:
            # Remove último ponto para ter número ímpar
            area = simpson(values[:-1], t[:-1])
        else:
            area = simpson(values, t)
        result_values = np.array([area], dtype=float)
        
    elif method == "cumulative":
        # Integral cumulativa
        cumulative = cumtrapz(values, t, initial=0.0)
        result_values = cumulative
        
    else:
        raise CalculusError("Integral method not available", {"method": method})
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    n_valid = np.sum(np.isfinite(result_values))
    n_nan = np.sum(~np.isfinite(result_values))
    
    quality_metrics = QualityMetrics(
        n_valid=n_valid,
        n_interpolated=0,
        n_nan=n_nan
    )
    
    logger.info("integral_computed", 
               method=method, 
               n_points=n_points,
               duration_ms=duration_ms)
    
    return CalcResult(
        values=result_values,
        metadata=_build_metadata(method, params, duration_ms),
        quality_metrics=quality_metrics,
        operation="integral",
        order=None,
    )


def area_between(
    series_upper: np.ndarray, 
    series_lower: np.ndarray, 
    t: np.ndarray,
    method: Literal["trapezoid", "simpson"] = "trapezoid",
    params: Optional[dict] = None
) -> CalcResult:
    """Calcula área entre curvas conforme especificação seção 9.3"""
    start_time = time.perf_counter()
    
    if params is None:
        params = {}
        
    n_points = len(series_upper)
    
    if n_points != len(series_lower) or n_points != len(t):
        raise CalculusError(
            "Array lengths must match",
            {
                "upper_len": len(series_upper),
                "lower_len": len(series_lower), 
                "t_len": len(t)
            }
        )
    
    if n_points < 2:
        raise CalculusError("Insufficient points for area calculation", {"n_points": n_points})
    
    # Calcula diferença entre curvas
    diff = series_upper - series_lower
    
    if method == "trapezoid":
        # Use Numba-optimized area calculation for large datasets
        if NUMBA_AVAILABLE and _area_between_numba is not None and n_points > 10000:
            logger.debug("using_numba_area_between", n_points=n_points)
            area = _area_between_numba(series_upper, series_lower, t)
        else:
            area = np.trapz(diff, t)
    elif method == "simpson":
        if n_points % 2 == 0:
            area = simpson(diff[:-1], t[:-1])
        else:
            area = simpson(diff, t)
    else:
        raise CalculusError("Area calculation method not available", {"method": method})
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    quality_metrics = QualityMetrics(
        n_valid=1 if np.isfinite(area) else 0,
        n_interpolated=0,
        n_nan=0 if np.isfinite(area) else 1
    )
    
    # Metadata com informações sobre as séries
    metadata_params = {
        **params,
        "n_points": n_points,
        "positive_area": bool(area >= 0),
        "abs_area": float(abs(area))
    }
    
    logger.info("area_between_computed", 
               method=method, 
               n_points=n_points,
               area=area,
               duration_ms=duration_ms)
    
    return CalcResult(
        values=np.array([area], dtype=float),
        metadata=_build_metadata("area_between", metadata_params, duration_ms),
        quality_metrics=quality_metrics,
        operation="area_between",
        order=None,
    )


# Funções de conveniência para operações comuns
def first_derivative(values: np.ndarray, t: np.ndarray, **kwargs) -> CalcResult:
    """Calcula primeira derivada"""
    return derivative(values, t, order=1, **kwargs)


def second_derivative(values: np.ndarray, t: np.ndarray, **kwargs) -> CalcResult:
    """Calcula segunda derivada"""
    return derivative(values, t, order=2, **kwargs)


def third_derivative(values: np.ndarray, t: np.ndarray, **kwargs) -> CalcResult:
    """Calcula terceira derivada"""
    return derivative(values, t, order=3, **kwargs)
