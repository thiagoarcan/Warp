from __future__ import annotations

from datetime import datetime
from typing import Optional

import numpy as np
from scipy.interpolate import CubicSpline, UnivariateSpline

from platform_base.core.models import InterpResult, InterpolationInfo, ResultMetadata
from platform_base.utils.errors import InterpolationError

SUPPORTED_METHODS = {
    "linear",
    "spline_cubic",
    "smoothing_spline",
    "resample_grid",
}


def _build_metadata(method: str, params: dict) -> ResultMetadata:
    return ResultMetadata(
        method=method,
        params=params,
        version="2.0.0",
        timestamp=datetime.utcnow(),
    )


def _interp_mask(values: np.ndarray) -> np.ndarray:
    return ~np.isfinite(values)


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

    raise InterpolationError("Interpolation method not implemented", {"method": method})
