"""
Testes completos para core/models.py - Platform Base v2.0

Cobertura 100% de todos os modelos Pydantic do core.
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from pint import Unit


class TestSourceInfo:
    """Testes para SourceInfo"""
    
    def test_source_info_creation(self):
        """Testa criação básica de SourceInfo"""
        from platform_base.core.models import SourceInfo
        
        info = SourceInfo(
            filepath="/path/to/file.csv",
            filename="file.csv",
            format="csv",
            size_bytes=1024,
            checksum="abc123"
        )
        
        assert info.filepath == "/path/to/file.csv"
        assert info.filename == "file.csv"
        assert info.format == "csv"
        assert info.size_bytes == 1024
        assert info.checksum == "abc123"
        assert info.loaded_at is not None
    
    def test_source_info_from_file(self):
        """Testa criação de SourceInfo a partir de arquivo"""
        from platform_base.core.models import SourceInfo

        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            f.write("2024-01-01,100\n")
            temp_file = f.name
        
        try:
            info = SourceInfo.from_file(temp_file)
            
            assert info.filename.endswith('.csv')
            assert info.format == 'csv'
            assert info.size_bytes > 0
            assert len(info.checksum) == 64  # SHA256
        finally:
            os.unlink(temp_file)
    
    def test_source_info_formats(self):
        """Testa diferentes formatos de arquivo"""
        from platform_base.core.models import SourceInfo
        
        for ext, fmt in [('.xlsx', 'xlsx'), ('.parquet', 'parquet'), ('.hdf5', 'hdf5')]:
            info = SourceInfo(
                filepath=f"/path/file{ext}",
                filename=f"file{ext}",
                format=fmt,
                size_bytes=2048,
                checksum="def456"
            )
            assert info.format == fmt


class TestDatasetMetadata:
    """Testes para DatasetMetadata"""
    
    def test_metadata_defaults(self):
        """Testa valores default do metadata"""
        from platform_base.core.models import DatasetMetadata
        
        meta = DatasetMetadata()
        
        assert meta.description is None
        assert meta.tags == []
        assert meta.custom == {}
        assert meta.schema_confidence == 1.0
        assert meta.validation_warnings == []
        assert meta.validation_errors == []
        assert meta.timezone == "UTC"
    
    def test_metadata_with_values(self):
        """Testa metadata com valores customizados"""
        from platform_base.core.models import DatasetMetadata
        
        meta = DatasetMetadata(
            description="Test dataset",
            tags=["test", "sensor"],
            custom={"source": "lab"},
            schema_confidence=0.95,
            validation_warnings=["Warning 1"],
            timezone="America/Sao_Paulo"
        )
        
        assert meta.description == "Test dataset"
        assert "test" in meta.tags
        assert meta.custom["source"] == "lab"
        assert meta.schema_confidence == 0.95


class TestSeriesMetadata:
    """Testes para SeriesMetadata"""
    
    def test_series_metadata_basic(self):
        """Testa criação básica de SeriesMetadata"""
        from platform_base.core.models import SeriesMetadata
        
        meta = SeriesMetadata(
            original_name="Temperature",
            source_column="temp_c"
        )
        
        assert meta.original_name == "Temperature"
        assert meta.source_column == "temp_c"
        assert meta.original_unit is None
        assert meta.description is None
        assert meta.tags == []
    
    def test_series_metadata_full(self):
        """Testa SeriesMetadata completo"""
        from platform_base.core.models import SeriesMetadata
        
        meta = SeriesMetadata(
            original_name="Pressure",
            source_column="pressure_psi",
            original_unit="psi",
            description="Pipe pressure sensor",
            tags=["pressure", "sensor"],
            custom={"calibration_date": "2024-01-15"}
        )
        
        assert meta.original_unit == "psi"
        assert "pressure" in meta.tags


class TestInterpolationInfo:
    """Testes para InterpolationInfo"""
    
    def test_interpolation_info_creation(self):
        """Testa criação de InterpolationInfo"""
        from platform_base.core.models import InterpolationInfo
        
        n_points = 10
        info = InterpolationInfo(
            is_interpolated=np.array([False, False, True, True, False, False, True, False, False, False]),
            method_used=np.array(['original', 'original', 'linear', 'linear', 'original', 
                                 'original', 'cubic', 'original', 'original', 'original'])
        )
        
        assert len(info.is_interpolated_mask) == n_points
        assert info.is_interpolated_mask[2] == True
        assert info.method_used[2] == 'linear'
    
    def test_interpolation_info_with_confidence(self):
        """Testa InterpolationInfo com confidence"""
        from platform_base.core.models import InterpolationInfo
        
        info = InterpolationInfo(
            is_interpolated=np.array([False, True, True, False]),
            method_used=np.array(['original', 'linear', 'linear', 'original']),
            confidence=np.array([1.0, 0.95, 0.90, 1.0])
        )
        
        assert info.confidence is not None
        assert info.confidence[1] == 0.95
    
    def test_interpolation_info_alias(self):
        """Testa alias is_interpolated"""
        from platform_base.core.models import InterpolationInfo
        
        info = InterpolationInfo(
            is_interpolated=np.array([True, False]),
            method_used=np.array(['linear', 'original'])
        )
        
        # Property should work
        assert info.is_interpolated[0] == True


class TestResultMetadata:
    """Testes para ResultMetadata"""
    
    def test_result_metadata_basic(self):
        """Testa criação básica de ResultMetadata"""
        from platform_base.core.models import ResultMetadata
        
        meta = ResultMetadata(
            operation="interpolation"
        )
        
        assert meta.operation == "interpolation"
        assert meta.parameters == {}
        assert meta.duration_ms == 0.0
        assert meta.platform_version == "2.0.0"
    
    def test_result_metadata_with_params(self):
        """Testa ResultMetadata com parâmetros"""
        from platform_base.core.models import ResultMetadata
        
        meta = ResultMetadata(
            operation="derivative",
            params={"order": 1, "method": "central"},
            duration_ms=15.5,
            seed=42
        )
        
        assert meta.params["order"] == 1
        assert meta.duration_ms == 15.5
        assert meta.seed == 42
    
    def test_result_metadata_params_alias(self):
        """Testa alias params -> parameters"""
        from platform_base.core.models import ResultMetadata
        
        meta = ResultMetadata(
            operation="test",
            parameters={"key": "value"}
        )
        
        assert meta.params["key"] == "value"


class TestQualityMetrics:
    """Testes para QualityMetrics"""
    
    def test_quality_metrics_basic(self):
        """Testa criação de QualityMetrics"""
        from platform_base.core.models import QualityMetrics
        
        metrics = QualityMetrics(
            n_valid=950,
            n_interpolated=45,
            n_nan=5
        )
        
        assert metrics.n_valid == 950
        assert metrics.n_interpolated == 45
        assert metrics.n_nan == 5
        assert metrics.error_estimate is None
    
    def test_quality_metrics_full(self):
        """Testa QualityMetrics com todas as métricas"""
        from platform_base.core.models import QualityMetrics
        
        metrics = QualityMetrics(
            n_valid=900,
            n_interpolated=80,
            n_nan=20,
            error_estimate=0.05,
            rmse=0.023,
            mae=0.018
        )
        
        assert metrics.rmse == 0.023
        assert metrics.mae == 0.018


class TestLineage:
    """Testes para Lineage"""
    
    def test_lineage_creation(self):
        """Testa criação de Lineage"""
        from platform_base.core.models import Lineage
        
        now = datetime.now()
        lineage = Lineage(
            origin_series=["series_1", "series_2"],
            operation="merge",
            parameters={"method": "concat"},
            timestamp=now,
            version="2.0.0"
        )
        
        assert "series_1" in lineage.origin_series
        assert lineage.operation == "merge"


class TestSeries:
    """Testes para Series"""
    
    def test_series_creation(self):
        """Testa criação de Series"""
        from pint import UnitRegistry

        from platform_base.core.models import Series, SeriesMetadata
        
        ureg = UnitRegistry()
        
        meta = SeriesMetadata(
            original_name="Temperature",
            source_column="temp"
        )
        
        series = Series(
            series_id="temp_001",
            name="Temperature",
            unit=ureg.degC,
            values=np.array([20.0, 21.0, 22.0, 23.0, 24.0]),
            metadata=meta
        )
        
        assert series.series_id == "temp_001"
        assert len(series.values) == 5
        assert series.interpolation_info is None
        assert series.lineage is None


class TestDataset:
    """Testes para Dataset"""
    
    def test_dataset_creation(self):
        """Testa criação de Dataset"""
        from platform_base.core.models import Dataset, DatasetMetadata, SourceInfo
        
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
        
        dataset = Dataset(
            dataset_id="ds_001",
            version=1,
            parent_id=None,
            source=source,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series={},
            metadata=meta,
            created_at=datetime.now()
        )
        
        assert dataset.dataset_id == "ds_001"
        assert dataset.version == 1
        assert len(dataset.t_seconds) == n_points


class TestTimeWindow:
    """Testes para TimeWindow"""
    
    def test_time_window_creation(self):
        """Testa criação de TimeWindow"""
        from platform_base.core.models import TimeWindow
        
        window = TimeWindow(start=0.0, end=100.0)
        
        assert window.start == 0.0
        assert window.end == 100.0
    
    def test_time_window_duration(self):
        """Testa cálculo de duração"""
        from platform_base.core.models import TimeWindow
        
        window = TimeWindow(start=10.0, end=60.0)
        
        assert window.duration == 50.0


class TestViewData:
    """Testes para ViewData"""
    
    def test_view_data_creation(self):
        """Testa criação de ViewData"""
        from platform_base.core.models import TimeWindow, ViewData
        
        window = TimeWindow(start=0.0, end=10.0)
        t_seconds = np.linspace(0, 10, 50)
        t_datetime = np.array([
            np.datetime64('2024-01-01') + np.timedelta64(int(t * 1000), 'ms')
            for t in t_seconds
        ])
        
        view = ViewData(
            dataset_id="ds_001",
            series={
                "temp": np.random.randn(50),
                "pressure": np.random.randn(50)
            },
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            window=window
        )
        
        assert view.dataset_id == "ds_001"
        assert "temp" in view.series
        assert len(view.series["temp"]) == 50


class TestDerivedResults:
    """Testes para classes de resultado derivadas"""
    
    def test_interp_result(self):
        """Testa InterpResult"""
        from platform_base.core.models import (
            InterpolationInfo,
            InterpResult,
            ResultMetadata,
        )
        
        interp_info = InterpolationInfo(
            is_interpolated=np.array([False, True, True, False]),
            method_used=np.array(['original', 'linear', 'linear', 'original'])
        )
        
        meta = ResultMetadata(operation="interpolation")
        
        result = InterpResult(
            values=np.array([1.0, 2.0, 3.0, 4.0]),
            metadata=meta,
            interpolation_info=interp_info
        )
        
        assert len(result.values) == 4
        assert result.interpolation_info is not None
    
    def test_calc_result(self):
        """Testa CalcResult"""
        from platform_base.core.models import CalcResult, ResultMetadata
        
        meta = ResultMetadata(operation="derivative")
        
        result = CalcResult(
            values=np.array([0.0, 1.0, 2.0, 3.0]),
            metadata=meta,
            operation="derivative",
            order=1
        )
        
        assert result.operation == "derivative"
        assert result.order == 1
    
    def test_sync_result(self):
        """Testa SyncResult"""
        from platform_base.core.models import ResultMetadata, SyncResult
        
        meta = ResultMetadata(operation="sync")
        
        result = SyncResult(
            values=np.array([1.0, 2.0, 3.0]),
            metadata=meta,
            t_common=np.array([0.0, 1.0, 2.0]),
            synced_series={
                "series_a": np.array([1.0, 2.0, 3.0]),
                "series_b": np.array([4.0, 5.0, 6.0])
            },
            alignment_error=0.001,
            confidence=0.98
        )
        
        assert len(result.t_common) == 3
        assert result.alignment_error < 0.01
    
    def test_downsample_result(self):
        """Testa DownsampleResult"""
        from platform_base.core.models import DownsampleResult, ResultMetadata
        
        meta = ResultMetadata(operation="downsample")
        
        result = DownsampleResult(
            values=np.array([1.0, 5.0, 9.0]),
            metadata=meta,
            t_seconds=np.array([0.0, 4.0, 8.0]),
            selected_indices=np.array([0, 4, 8])
        )
        
        assert len(result.t_seconds) == 3
        assert len(result.selected_indices) == 3


class TestSeriesSummary:
    """Testes para SeriesSummary"""
    
    def test_series_summary_basic(self):
        """Testa criação de SeriesSummary"""
        from platform_base.core.models import SeriesSummary
        
        summary = SeriesSummary(
            series_id="temp_001",
            name="Temperature",
            unit="degC",
            n_points=1000
        )
        
        assert summary.series_id == "temp_001"
        assert summary.name == "Temperature"
        assert summary.is_derived == False
    
    def test_series_summary_derived(self):
        """Testa SeriesSummary para série derivada"""
        from platform_base.core.models import SeriesSummary
        
        summary = SeriesSummary(
            series_id="temp_derivative",
            name="Temperature Rate",
            unit="degC/s",
            n_points=999,
            is_derived=True
        )
        
        assert summary.is_derived == True
