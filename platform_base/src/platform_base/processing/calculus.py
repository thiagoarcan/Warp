from __future__ import annotations

from datetime import datetime
from typing import Optional

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import savgol_filter

from platform_base.core.models import CalcResult, ResultMetadata
from platform_base.processing.smoothing import SmoothingConfig, smooth
from platform_base.utils.errors import CalculusError


def _build_metadata(method: str, params: dict) -> ResultMetadata:
    return ResultMetadata(
        method=method,
        params=params,
        version="2.0.0",
        timestamp=datetime.utcnow(),
    )


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


def integral(values: np.ndarray, t: np.ndarray, method: str = "trapezoid") -> CalcResult:
    if method != "trapezoid":
        raise CalculusError("Integral method not available", {"method": method})
    area = np.trapz(values, t)
    return CalcResult(
        values=np.array([area], dtype=float),
        metadata=_build_metadata(method, {}),
        operation="integral",
        order=None,
    )


def area_between(series_upper: np.ndarray, series_lower: np.ndarray, t: np.ndarray) -> CalcResult:
    area = np.trapz(series_upper - series_lower, t)
    return CalcResult(
        values=np.array([area], dtype=float),
        metadata=_build_metadata("area_between", {}),
        operation="area_between",
        order=None,
    )
