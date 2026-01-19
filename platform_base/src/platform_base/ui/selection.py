from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from platform_base.core.models import Dataset


@dataclass
class Selection:
    t_seconds: np.ndarray
    series: dict[str, np.ndarray]


def select_time_window(dataset: Dataset, start_seconds: float, end_seconds: float) -> Selection:
    mask = (dataset.t_seconds >= start_seconds) & (dataset.t_seconds <= end_seconds)
    series = {name: s.values[mask] for name, s in dataset.series.items()}
    return Selection(t_seconds=dataset.t_seconds[mask], series=series)


def select_by_predicate(dataset: Dataset, series_id: str, predicate) -> Selection:
    series = dataset.series[series_id].values
    mask = predicate(series)
    selected_series = {series_id: series[mask]}
    return Selection(t_seconds=dataset.t_seconds[mask], series=selected_series)
