"""
Testes completos para core/dataset_store.py - Platform Base v2.0

Cobertura 100% do DatasetStore com threading, cache e operações.
"""

import time
from datetime import datetime
from threading import Thread
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest


class TestDatasetSummary:
    """Testes para DatasetSummary"""
    
    def test_dataset_summary_creation(self):
        """Testa criação de DatasetSummary"""
        from platform_base.core.dataset_store import DatasetSummary
        
        summary = DatasetSummary(
            dataset_id="ds_001",
            n_series=5,
            n_points=1000
        )
        
        assert summary.dataset_id == "ds_001"
        assert summary.n_series == 5
        assert summary.n_points == 1000


class TestDatasetStoreBasic:
    """Testes básicos do DatasetStore"""
    
    @pytest.fixture
    def mock_dataset(self):
        """Cria dataset mock para testes"""
        from pint import UnitRegistry

        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        
        ureg = UnitRegistry()
        
        source = SourceInfo(
            filepath="/data/test.csv",
            filename="test.csv",
            format="csv",
            size_bytes=1024,
            checksum="abc123"
        )
        
        meta = DatasetMetadata(description="Test dataset")
        
        n_points = 100
        t_seconds = np.linspace(0, 10, n_points)
        t_datetime = np.array([
            np.datetime64('2024-01-01') + np.timedelta64(int(t * 1000), 'ms')
            for t in t_seconds
        ])
        
        series_meta = SeriesMetadata(original_name="Temp", source_column="temp")
        series = Series(
            series_id="temp_001",
            name="Temperature",
            unit=ureg.degC,
            values=np.random.randn(n_points) * 10 + 25,
            metadata=series_meta
        )
        
        dataset = Dataset(
            dataset_id="ds_001",
            version=1,
            parent_id=None,
            source=source,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series={"temp_001": series},
            metadata=meta,
            created_at=datetime.now()
        )
        
        return dataset
    
    def test_store_creation_without_cache(self):
        """Testa criação do store sem cache"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        
        assert store._disk_cache is None
        assert len(store._datasets) == 0
    
    def test_store_creation_with_cache(self):
        """Testa criação do store com cache"""
        import tempfile

        from platform_base.core.dataset_store import DatasetStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"path": tmpdir, "ttl_seconds": 3600}
            store = DatasetStore(cache_config=config)
            
            assert store._disk_cache is not None
    
    def test_add_dataset(self, mock_dataset):
        """Testa adição de dataset"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        dataset_id = store.add_dataset(mock_dataset)
        
        assert dataset_id == "ds_001"
        assert "ds_001" in store._datasets
    
    def test_get_dataset(self, mock_dataset):
        """Testa obtenção de dataset"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        store.add_dataset(mock_dataset)
        
        result = store.get_dataset("ds_001")
        
        assert result.dataset_id == "ds_001"
        assert len(result.series) == 1
    
    def test_get_dataset_not_found(self):
        """Testa obtenção de dataset inexistente"""
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.utils.errors import ValidationError
        
        store = DatasetStore()
        
        with pytest.raises(ValidationError):
            store.get_dataset("nonexistent")
    
    def test_list_datasets(self, mock_dataset):
        """Testa listagem de datasets"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        store.add_dataset(mock_dataset)
        
        summaries = store.list_datasets()
        
        assert len(summaries) == 1
        assert summaries[0].dataset_id == "ds_001"
        assert summaries[0].n_series == 1
        assert summaries[0].n_points == 100


class TestDatasetStoreSeriesOperations:
    """Testes de operações com séries"""
    
    @pytest.fixture
    def store_with_dataset(self):
        """Cria store com dataset para testes"""
        from pint import UnitRegistry

        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        
        ureg = UnitRegistry()
        
        source = SourceInfo(
            filepath="/data/test.csv",
            filename="test.csv",
            format="csv",
            size_bytes=1024,
            checksum="abc123"
        )
        
        n_points = 100
        t_seconds = np.linspace(0, 10, n_points)
        t_datetime = np.array([
            np.datetime64('2024-01-01') + np.timedelta64(int(t * 1000), 'ms')
            for t in t_seconds
        ])
        
        dataset = Dataset(
            dataset_id="ds_001",
            version=1,
            parent_id=None,
            source=source,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series={},
            metadata=DatasetMetadata(),
            created_at=datetime.now()
        )
        
        store = DatasetStore()
        store.add_dataset(dataset)
        
        return store, ureg
    
    def test_add_series(self, store_with_dataset):
        """Testa adição de série"""
        from platform_base.core.models import Series, SeriesMetadata
        
        store, ureg = store_with_dataset
        
        meta = SeriesMetadata(original_name="Pressure", source_column="pressure")
        series = Series(
            series_id="pressure_001",
            name="Pressure",
            unit=ureg.psi,
            values=np.random.randn(100) * 5 + 100,
            metadata=meta
        )
        
        series_id = store.add_series("ds_001", series)
        
        assert series_id == "pressure_001"
    
    def test_add_series_dataset_not_found(self, store_with_dataset):
        """Testa adição de série em dataset inexistente"""
        from platform_base.core.models import Series, SeriesMetadata
        from platform_base.utils.errors import ValidationError
        
        store, ureg = store_with_dataset
        
        meta = SeriesMetadata(original_name="Test", source_column="test")
        series = Series(
            series_id="test_001",
            name="Test",
            unit=ureg.meter,
            values=np.array([1.0, 2.0, 3.0]),
            metadata=meta
        )
        
        with pytest.raises(ValidationError):
            store.add_series("nonexistent", series)
    
    def test_get_series(self, store_with_dataset):
        """Testa obtenção de série"""
        from platform_base.core.models import Series, SeriesMetadata
        
        store, ureg = store_with_dataset
        
        meta = SeriesMetadata(original_name="Flow", source_column="flow")
        series = Series(
            series_id="flow_001",
            name="Flow",
            unit=ureg.meter**3/ureg.second,
            values=np.random.randn(100) + 50,
            metadata=meta
        )
        
        store.add_series("ds_001", series)
        
        result = store.get_series("ds_001", "flow_001")
        
        assert result.series_id == "flow_001"
        assert result.name == "Flow"
    
    def test_get_series_not_found(self, store_with_dataset):
        """Testa obtenção de série inexistente"""
        from platform_base.utils.errors import ValidationError
        
        store, _ = store_with_dataset
        
        with pytest.raises(ValidationError):
            store.get_series("ds_001", "nonexistent")
    
    def test_list_series(self, store_with_dataset):
        """Testa listagem de séries"""
        from platform_base.core.models import Series, SeriesMetadata
        
        store, ureg = store_with_dataset
        
        # Adiciona algumas séries
        for name in ["temp", "pressure", "flow"]:
            meta = SeriesMetadata(original_name=name, source_column=name)
            series = Series(
                series_id=f"{name}_001",
                name=name.capitalize(),
                unit=ureg.meter,
                values=np.random.randn(100),
                metadata=meta
            )
            store.add_series("ds_001", series)
        
        summaries = store.list_series("ds_001")
        
        assert len(summaries) == 3


class TestDatasetStoreViews:
    """Testes de operações de view"""
    
    @pytest.fixture
    def store_with_data(self):
        """Cria store com dados para testes de view"""
        from pint import UnitRegistry

        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        
        ureg = UnitRegistry()
        
        source = SourceInfo(
            filepath="/data/test.csv",
            filename="test.csv",
            format="csv",
            size_bytes=1024,
            checksum="abc123"
        )
        
        n_points = 1000
        t_seconds = np.linspace(0, 100, n_points)
        t_datetime = np.array([
            np.datetime64('2024-01-01') + np.timedelta64(int(t * 1000), 'ms')
            for t in t_seconds
        ])
        
        series = {}
        for name in ["temp", "pressure"]:
            meta = SeriesMetadata(original_name=name, source_column=name)
            series[f"{name}_001"] = Series(
                series_id=f"{name}_001",
                name=name.capitalize(),
                unit=ureg.meter,
                values=np.sin(t_seconds / 10) * 10 + np.random.randn(n_points),
                metadata=meta
            )
        
        dataset = Dataset(
            dataset_id="ds_001",
            version=1,
            parent_id=None,
            source=source,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series=series,
            metadata=DatasetMetadata(),
            created_at=datetime.now()
        )
        
        store = DatasetStore()
        store.add_dataset(dataset)
        
        return store
    
    def test_create_view(self, store_with_data):
        """Testa criação de view"""
        from platform_base.core.models import TimeWindow
        
        store = store_with_data
        
        window = TimeWindow(start=10.0, end=50.0)
        view = store.create_view("ds_001", ["temp_001"], window)
        
        assert view.dataset_id == "ds_001"
        assert "temp_001" in view.series
        assert len(view.t_seconds) > 0
        assert all(view.t_seconds >= 10.0)
        assert all(view.t_seconds <= 50.0)
    
    def test_create_view_multiple_series(self, store_with_data):
        """Testa view com múltiplas séries"""
        from platform_base.core.models import TimeWindow
        
        store = store_with_data
        
        window = TimeWindow(start=20.0, end=80.0)
        view = store.create_view("ds_001", ["temp_001", "pressure_001"], window)
        
        assert "temp_001" in view.series
        assert "pressure_001" in view.series
        assert len(view.series["temp_001"]) == len(view.series["pressure_001"])
    
    def test_create_view_empty_window(self, store_with_data):
        """Testa view com janela vazia"""
        from platform_base.core.models import TimeWindow
        from platform_base.utils.errors import ValidationError
        
        store = store_with_data
        
        # Janela fora do range de dados
        window = TimeWindow(start=500.0, end=600.0)
        
        with pytest.raises(ValidationError):
            store.create_view("ds_001", ["temp_001"], window)


class TestDatasetStoreThreadSafety:
    """Testes de thread safety"""
    
    @pytest.fixture
    def store_and_factory(self):
        """Cria store e factory de datasets"""
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import Dataset, DatasetMetadata, SourceInfo
        
        def create_dataset(id_suffix):
            source = SourceInfo(
                filepath=f"/data/test_{id_suffix}.csv",
                filename=f"test_{id_suffix}.csv",
                format="csv",
                size_bytes=1024,
                checksum=f"abc{id_suffix}"
            )
            
            n_points = 100
            t_seconds = np.linspace(0, 10, n_points)
            t_datetime = np.array([
                np.datetime64('2024-01-01') + np.timedelta64(int(t * 1000), 'ms')
                for t in t_seconds
            ])
            
            return Dataset(
                dataset_id=f"ds_{id_suffix:03d}",
                version=1,
                parent_id=None,
                source=source,
                t_seconds=t_seconds,
                t_datetime=t_datetime,
                series={},
                metadata=DatasetMetadata(),
                created_at=datetime.now()
            )
        
        store = DatasetStore()
        return store, create_dataset
    
    def test_concurrent_adds(self, store_and_factory):
        """Testa adições concorrentes"""
        store, create_dataset = store_and_factory
        
        errors = []
        
        def add_datasets(start, count):
            try:
                for i in range(start, start + count):
                    dataset = create_dataset(i)
                    store.add_dataset(dataset)
            except Exception as e:
                errors.append(e)
        
        # Cria threads para adição concorrente
        threads = [
            Thread(target=add_datasets, args=(i * 10, 10))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(store._datasets) == 50
    
    def test_concurrent_reads(self, store_and_factory):
        """Testa leituras concorrentes"""
        store, create_dataset = store_and_factory
        
        # Adiciona datasets
        for i in range(10):
            store.add_dataset(create_dataset(i))
        
        results = []
        errors = []
        
        def read_datasets(thread_id):
            try:
                for _ in range(100):
                    summaries = store.list_datasets()
                    results.append(len(summaries))
            except Exception as e:
                errors.append(e)
        
        threads = [
            Thread(target=read_datasets, args=(i,))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert all(r == 10 for r in results)
    
    def test_concurrent_read_write(self, store_and_factory):
        """Testa leitura e escrita concorrentes"""
        store, create_dataset = store_and_factory
        
        # Adiciona alguns datasets iniciais
        for i in range(5):
            store.add_dataset(create_dataset(i))
        
        errors = []
        
        def writer(start, count):
            try:
                for i in range(start, start + count):
                    store.add_dataset(create_dataset(100 + i))
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        def reader(iterations):
            try:
                for _ in range(iterations):
                    store.list_datasets()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        threads = [
            Thread(target=writer, args=(i * 5, 5)) for i in range(3)
        ] + [
            Thread(target=reader, args=(20,)) for _ in range(3)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0


class TestDatasetStoreCacheIntegration:
    """Testes de integração com cache"""
    
    def test_add_with_cache(self):
        """Testa adição com cache ativo"""
        import tempfile

        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import Dataset, DatasetMetadata, SourceInfo
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"path": tmpdir, "ttl_seconds": 3600}
            store = DatasetStore(cache_config=config)
            
            source = SourceInfo(
                filepath="/data/test.csv",
                filename="test.csv",
                format="csv",
                size_bytes=1024,
                checksum="abc123"
            )
            
            n_points = 100
            t_seconds = np.linspace(0, 10, n_points)
            t_datetime = np.array([
                np.datetime64('2024-01-01') + np.timedelta64(int(t * 1000), 'ms')
                for t in t_seconds
            ])
            
            dataset = Dataset(
                dataset_id="ds_001",
                version=1,
                parent_id=None,
                source=source,
                t_seconds=t_seconds,
                t_datetime=t_datetime,
                series={},
                metadata=DatasetMetadata(),
                created_at=datetime.now()
            )
            
            store.add_dataset(dataset)
            
            # Verifica que foi adicionado
            result = store.get_dataset("ds_001")
            assert result.dataset_id == "ds_001"
    
    def test_clear_cache(self):
        """Testa limpeza de cache"""
        import tempfile

        from platform_base.core.dataset_store import DatasetStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"path": tmpdir, "ttl_seconds": 3600}
            store = DatasetStore(cache_config=config)
            
            # Limpa cache (não deve falhar)
            store.clear_cache()
    
    def test_get_cache_stats_with_cache(self):
        """Testa estatísticas com cache ativo"""
        import tempfile

        from platform_base.core.dataset_store import DatasetStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"path": tmpdir, "ttl_seconds": 3600}
            store = DatasetStore(cache_config=config)
            
            stats = store.get_cache_stats()
            
            assert isinstance(stats, dict)
    
    def test_get_cache_stats_without_cache(self):
        """Testa estatísticas sem cache"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        
        stats = store.get_cache_stats()
        
        assert stats["cache_enabled"] == False
