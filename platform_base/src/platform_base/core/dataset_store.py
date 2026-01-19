from __future__ import annotations

from typing import Iterable, Optional
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
from platform_base.caching.disk import DiskCache, create_disk_cache_from_config
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


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
    """
    Dataset store com cache disk integrado conforme PRD seção 9.5
    
    Features:
    - Cache multi-nível (memory + disk)
    - TTL configurável
    - Versionamento de datasets
    - Operações de view com cache
    """

    def __init__(self, cache_config: Optional[dict] = None):
        self._datasets: dict[DatasetID, Dataset] = {}
        
        # Setup disk cache se configurado
        if cache_config:
            self._disk_cache = create_disk_cache_from_config(cache_config)
            logger.info("dataset_store_cache_enabled", 
                       cache_path=cache_config.get("path", ".cache"))
        else:
            self._disk_cache = None
            logger.info("dataset_store_cache_disabled")

    def add_dataset(self, dataset: Dataset) -> DatasetID:
        dataset_id = dataset.dataset_id
        self._datasets[dataset_id] = dataset
        
        # Cache dataset se cache disponível
        if self._disk_cache:
            cache_key = f"dataset:{dataset_id}"
            self._disk_cache.set(cache_key, dataset)
            logger.debug("dataset_cached", dataset_id=dataset_id)
        
        return dataset_id

    def get_dataset(self, dataset_id: DatasetID) -> Dataset:
        # Primeiro tenta memory cache
        if dataset_id in self._datasets:
            return self._datasets[dataset_id]
        
        # Tenta disk cache se disponível
        if self._disk_cache:
            cache_key = f"dataset:{dataset_id}"
            cached_dataset = self._disk_cache.get(cache_key)
            if cached_dataset:
                # Restaura para memory cache
                self._datasets[dataset_id] = cached_dataset
                logger.debug("dataset_restored_from_cache", dataset_id=dataset_id)
                return cached_dataset
        
        raise ValidationError("Dataset not found", {"dataset_id": dataset_id})

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
        """
        Cria view com cache disk integrado conforme PRD seção 9.5
        
        Views são operações custosas que se beneficiam de cache persistente.
        """
        series_ids_list = list(series_ids)
        
        # Cria chave de cache baseada nos parâmetros
        cache_key = f"view:{dataset_id}:{hash(tuple(series_ids_list))}:{time_window.start_seconds}:{time_window.end_seconds}"
        
        # Tenta cache primeiro
        if self._disk_cache:
            cached_view = self._disk_cache.get(cache_key)
            if cached_view:
                logger.debug("view_cache_hit", 
                           dataset_id=dataset_id,
                           n_series=len(series_ids_list))
                return cached_view
        
        # Cache miss - calcula view
        dataset = self.get_dataset(dataset_id)
        t_seconds = dataset.t_seconds
        mask = (t_seconds >= time_window.start_seconds) & (t_seconds <= time_window.end_seconds)
        
        if not np.any(mask):
            raise ValidationError("Time window has no data", {"dataset_id": dataset_id})
            
        t_seconds_view = dataset.t_seconds[mask]
        t_datetime_view = dataset.t_datetime[mask]
        series_view = {
            series_id: dataset.series[series_id].values[mask] for series_id in series_ids_list
        }
        
        view_data = ViewData(
            dataset_id=dataset_id,
            series=series_view,
            t_seconds=t_seconds_view,
            t_datetime=t_datetime_view,
            window=time_window,
        )
        
        # Cache resultado se cache disponível
        if self._disk_cache:
            self._disk_cache.set(cache_key, view_data)
            logger.debug("view_cached", 
                        dataset_id=dataset_id,
                        n_series=len(series_ids_list),
                        n_points=len(t_seconds_view))
        
        return view_data
    
    def clear_cache(self) -> None:
        """Limpa cache disk se disponível"""
        if self._disk_cache:
            self._disk_cache.clear()
            logger.info("dataset_store_cache_cleared")
    
    def get_cache_stats(self) -> dict:
        """Obtém estatísticas do cache"""
        if self._disk_cache:
            return self._disk_cache.get_stats()
        return {"cache_enabled": False}
