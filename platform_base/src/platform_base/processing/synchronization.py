from __future__ import annotations

from datetime import datetime

import numpy as np

from platform_base.core.models import ResultMetadata, SyncResult
from platform_base.utils.errors import InterpolationError


def _build_metadata(method: str, params: dict) -> ResultMetadata:
    return ResultMetadata(
        method=method,
        params=params,
        version="2.0.0",
        timestamp=datetime.utcnow(),
    )


def _common_grid(t_dict: dict[str, np.ndarray], dt: float | None = None) -> np.ndarray:
    starts = [float(np.nanmin(t)) for t in t_dict.values()]
    ends = [float(np.nanmax(t)) for t in t_dict.values()]
    start = max(starts)
    end = min(ends)
    if start >= end:
        raise InterpolationError("No overlapping time window", {})
    if dt is None:
        diffs = np.concatenate([np.diff(t) for t in t_dict.values() if len(t) > 1])
        dt = float(np.median(diffs)) if len(diffs) else 1.0
    return np.arange(start, end + dt, dt)


def _smooth(series: np.ndarray, alpha: float = 0.2) -> np.ndarray:
    if len(series) == 0:
        return series
    smoothed = np.empty_like(series)
    smoothed[0] = series[0]
    for i in range(1, len(series)):
        smoothed[i] = alpha * series[i] + (1.0 - alpha) * smoothed[i - 1]
    return smoothed


def synchronize(
    series_dict: dict[str, np.ndarray],
    t_dict: dict[str, np.ndarray],
    method: str,
    params: dict,
) -> SyncResult:
    if method not in {"common_grid_interpolate", "kalman_align"}:
        raise InterpolationError("Sync method not available", {"method": method})

    t_common = _common_grid(t_dict, dt=params.get("dt"))
    synced_series: dict[str, np.ndarray] = {}

    for key, series in series_dict.items():
        t_series = t_dict[key]
        order = np.argsort(t_series)
        t_sorted = t_series[order]
        s_sorted = series[order]
        synced = np.interp(t_common, t_sorted, s_sorted)
        if method == "kalman_align":
            synced = _smooth(synced, alpha=params.get("alpha", 0.2))
        synced_series[key] = synced

    alignment_error = 0.0
    confidence = 1.0
    return SyncResult(
        values=np.zeros(len(t_common)),
        metadata=_build_metadata(method, params),
        t_common=t_common,
        synced_series=synced_series,
        alignment_error=alignment_error,
        confidence=confidence,
    )
