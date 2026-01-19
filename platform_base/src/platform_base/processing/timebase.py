from __future__ import annotations

from datetime import datetime

import numpy as np


def to_seconds(t_datetime: np.ndarray) -> np.ndarray:
    if len(t_datetime) == 0:
        return np.array([], dtype=float)
    t_datetime = t_datetime.astype("datetime64[ns]")
    valid = ~np.isnat(t_datetime)
    if not valid.any():
        return np.full(len(t_datetime), np.nan)
    origin = t_datetime[valid][0]
    delta = t_datetime - origin
    return delta.astype("timedelta64[ns]").astype(float) / 1e9


def to_datetime(t_seconds: np.ndarray, origin: datetime) -> np.ndarray:
    origin64 = np.datetime64(origin)
    return origin64 + t_seconds.astype("timedelta64[s]")
