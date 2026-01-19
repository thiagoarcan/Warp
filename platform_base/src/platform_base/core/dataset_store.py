from __future__ import annotations

from typing import Iterable

import numpy as np

from platform_base.core.models import (
    Dataset,
    DatasetID,
    Series,
    SeriesID,
    TimeWindow,
    ViewData,
)
from platform_base.utils.errors import ValidationError


class DatasetSummary:
    def __init__(self, dataset_id: DatasetID, n_series: int, n_points: int):
        self.dataset_id = dataset_id
        self.n_series = n_series
        self.n_points = n_points


class SeriesSummary:
    def __init__(self, series_id: SeriesID, name: str, n_points: int):
        self.series_id = series_id
        self.name = name
        self.n_points = n_points


class DatasetStore:
    """In-memory dataset store with basic versioning support."""

    def __init__(self):
        self._datasets: dict[DatasetID, Dataset] = {}

    def add_dataset(self, dataset: Dataset) -> DatasetID:
        dataset_id = dataset.dataset_id
        self._datasets[dataset_id] = dataset
        return dataset_id

    def get_dataset(self, dataset_id: DatasetID) -> Dataset:
        if dataset_id not in self._datasets:
            raise ValidationError("Dataset not found", {"dataset_id": dataset_id})
        return self._datasets[dataset_id]

    def list_datasets(self) -> list[DatasetSummary]:
        return [
            DatasetSummary(dataset_id=ds.dataset_id, n_series=len(ds.series), n_points=len(ds.t_seconds))
            for ds in self._datasets.values()
        ]

    def add_series(self, dataset_id: DatasetID, series: Series) -> SeriesID:
        dataset = self.get_dataset(dataset_id)
        dataset.series[series.series_id] = series
        return series.series_id

    def get_series(self, dataset_id: DatasetID, series_id: SeriesID) -> Series:
        dataset = self.get_dataset(dataset_id)
        if series_id not in dataset.series:
            raise ValidationError("Series not found", {"series_id": series_id})
        return dataset.series[series_id]

    def list_series(self, dataset_id: DatasetID) -> list[SeriesSummary]:
        dataset = self.get_dataset(dataset_id)
        return [
            SeriesSummary(series_id=s.series_id, name=s.name, n_points=len(s.values))
            for s in dataset.series.values()
        ]

    def create_view(
        self,
        dataset_id: DatasetID,
        series_ids: Iterable[SeriesID],
        time_window: TimeWindow,
    ) -> ViewData:
        dataset = self.get_dataset(dataset_id)
        t_seconds = dataset.t_seconds
        mask = (t_seconds >= time_window.start_seconds) & (t_seconds <= time_window.end_seconds)
        if not np.any(mask):
            raise ValidationError("Time window has no data", {"dataset_id": dataset_id})
        t_seconds_view = dataset.t_seconds[mask]
        t_datetime_view = dataset.t_datetime[mask]
        series_view = {
            series_id: dataset.series[series_id].values[mask] for series_id in series_ids
        }
        return ViewData(
            dataset_id=dataset_id,
            series=series_view,
            t_seconds=t_seconds_view,
            t_datetime=t_datetime_view,
            window=time_window,
        )
