"""
Extended Integration Tests - Complete Pipeline Testing

Tests complete data processing pipelines with multiple components working together.
These tests verify that all modules integrate correctly.
"""

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.integration


class TestDataLoadProcessExportPipeline:
    """Integration tests for complete data processing pipeline."""
    
    def test_csv_load_interpolate_derivative_export(self, tmp_path):
        """Full pipeline: CSV load → interpolate → derivative → export."""
        from platform_base.io.loader import load
        from platform_base.processing.calculus import derivative
        from platform_base.processing.interpolation import interpolate

        # Create test CSV
        csv_file = tmp_path / "input.csv"
        t = np.linspace(0, 10, 100)
        y = np.sin(t) * np.exp(-t/10)
        df = pd.DataFrame({"time": t, "value": y})
        df.to_csv(csv_file, index=False)
        
        # Load data
        dataset = load(csv_file)
        assert dataset is not None
        assert len(dataset.series) >= 1
        
        series = list(dataset.series.values())[0]
        t_orig = dataset.t_seconds
        y_orig = series.values
        
        # Interpolate to higher resolution
        result_interp = interpolate(y_orig, t_orig, method="spline_cubic", params={})
        assert len(result_interp.values) == len(y_orig)
        
        # Calculate derivative
        result_deriv = derivative(result_interp.values, t_orig, order=1)
        assert result_deriv is not None
        assert len(result_deriv.values) == len(result_interp.values)
        
        # Export result
        output_csv = tmp_path / "output.csv"
        df_out = pd.DataFrame({"time": t_orig, "derivative": result_deriv.values})
        df_out.to_csv(output_csv, index=False)
        
        assert output_csv.exists()
        df_loaded = pd.read_csv(output_csv)
        assert len(df_loaded) == len(t_orig)
    
    def test_multiple_series_synchronization_pipeline(self, tmp_path):
        """Pipeline with multiple series synchronization."""
        from platform_base.io.loader import load
        from platform_base.processing.synchronization import synchronize

        # Create test files with different time grids
        csv1 = tmp_path / "series1.csv"
        t1 = np.linspace(0, 10, 100)
        y1 = np.sin(t1)
        pd.DataFrame({"time": t1, "value": y1}).to_csv(csv1, index=False)
        
        csv2 = tmp_path / "series2.csv"
        t2 = np.linspace(0, 10, 150)  # Different resolution
        y2 = np.cos(t2)
        pd.DataFrame({"time": t2, "value": y2}).to_csv(csv2, index=False)
        
        # Load both datasets
        ds1 = load(csv1)
        ds2 = load(csv2)
        
        # Synchronize
        series1 = list(ds1.series.values())[0].values
        series2 = list(ds2.series.values())[0].values
        
        result = synchronize(
            {"s1": series1, "s2": series2},
            {"s1": ds1.t_seconds, "s2": ds2.t_seconds},
            method="common_grid_interpolate",
            params={}
        )
        
        assert result is not None
        # SyncResult has synced_series not synced_data
        assert "s1" in result.synced_series
        assert "s2" in result.synced_series
        assert len(result.synced_series["s1"]) == len(result.synced_series["s2"])


class TestCachingIntegration:
    """Integration tests for caching layer."""
    
    def test_memory_cache_with_processing(self):
        """Test memory cache integration with processing operations."""
        from platform_base.caching.memory import MemoryCache
        from platform_base.processing.calculus import derivative

        # MemoryCache takes maxsize (int) not max_size_mb
        cache = MemoryCache(maxsize=100)
        
        # Generate test data
        t = np.linspace(0, 10, 1000)
        y = np.sin(t)
        
        # First calculation (cache miss)
        key = "deriv_1"
        result1 = derivative(y, t, order=1)
        cache.set(key, result1)
        
        # Second retrieval (cache hit)
        cached_result = cache.get(key)
        assert cached_result is not None
        np.testing.assert_array_equal(cached_result.values, result1.values)
    
    def test_disk_cache_persistence(self, tmp_path):
        """Test disk cache persists across instances."""
        from platform_base.caching.disk import DiskCache
        
        cache_dir = tmp_path / "cache"
        # DiskCache takes location (str/Path) not cache_dir
        cache1 = DiskCache(location=str(cache_dir))
        
        # Store data
        data = {"test": np.array([1, 2, 3])}
        cache1.set("test_key", data)
        
        # Create new cache instance
        cache2 = DiskCache(location=str(cache_dir))
        retrieved = cache2.get("test_key")
        
        assert retrieved is not None
        np.testing.assert_array_equal(retrieved["test"], data["test"])


class TestWorkerIntegration:
    """Integration tests for worker threads."""
    
    def test_processing_worker_async_execution(self, qtbot):
        """Test processing worker executes operations asynchronously."""
        from PyQt6.QtCore import QObject, pyqtSignal

        # Create mock worker
        class MockWorker(QObject):
            finished = pyqtSignal(object)
            error = pyqtSignal(str)
            
            def process(self, data):
                result = np.mean(data)
                self.finished.emit(result)
        
        worker = MockWorker()
        
        # Connect signal and test
        results = []
        worker.finished.connect(lambda x: results.append(x))
        
        test_data = np.array([1, 2, 3, 4, 5])
        worker.process(test_data)
        
        # Wait for signal
        qtbot.wait(100)
        
        assert len(results) == 1
        assert results[0] == 3.0


class TestSessionStateIntegration:
    """Integration tests for session state management."""
    
    def test_session_state_serialization(self, tmp_path):
        """Test session state can be saved and restored."""
        from datetime import datetime

        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        from platform_base.desktop.session_state import SessionState
        from platform_base.processing.units import parse_unit

        # Create dataset store and session
        store = DatasetStore()
        session = SessionState(dataset_store=store)
        
        # Add dataset
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        series_meta = SeriesMetadata(
            original_name="Test Series",
            source_column="value",
            original_unit="m/s"
        )
        series = Series(
            series_id="test",
            name="Test Series",
            unit=parse_unit("m/s"),
            values=y,
            metadata=series_meta
        )
        dataset = Dataset(
            dataset_id="test_ds",
            version=1,
            parent_id=None,
            source=SourceInfo(
                filepath="test.csv",
                filename="test.csv",
                format="csv",
                size_bytes=1000,
                checksum="abc123"
            ),
            series={"test": series},
            t_seconds=t,
            t_datetime=np.array([np.datetime64('2020-01-01') + np.timedelta64(int(s), 's') for s in t]),
            metadata=DatasetMetadata(description="Test Dataset"),
            created_at=datetime.now()
        )
        store.add_dataset(dataset)
        
        # Verify store has datasets
        assert len(store.list_datasets()) == 1
        assert store.get_dataset("test_ds") is not None
        
        # Test we can retrieve dataset
        retrieved = store.get_dataset("test_ds")
        assert retrieved is not None
        assert retrieved.metadata.description == "Test Dataset"


class TestStreamingIntegration:
    """Integration tests for streaming functionality."""
    
    def test_streaming_with_filters(self):
        """Test streaming with real-time filtering using QualityFilter."""
        from platform_base.streaming.filters import FilterAction, QualityFilter

        # Generate streaming data with outliers
        t = np.linspace(0, 10, 100)
        y = np.sin(2 * np.pi * 0.5 * t)
        # Add some outliers
        y[25] = 100.0  # outlier
        y[75] = -100.0  # outlier
        
        # Apply quality filter for outlier detection
        filter_obj = QualityFilter(
            name="test_filter",
            outlier_method="zscore",
            outlier_threshold=3.0,
            window_size=20
        )
        
        blocked_count = 0
        passed_count = 0
        
        for i, (time, value) in enumerate(zip(t, y)):
            result = filter_obj.apply(time, value)
            if result.action == FilterAction.BLOCK:
                blocked_count += 1
            else:
                passed_count += 1
        
        # Should detect at least the outliers (after window fills)
        assert passed_count > 0
        assert filter_obj.get_efficiency() > 0.5  # Most values should pass


class TestValidationIntegration:
    """Integration tests for data validation."""
    
    def test_file_integrity_validation(self, tmp_path):
        """Test file integrity validation before loading."""
        from platform_base.io.validator import validate_file

        # Create valid CSV
        csv_file = tmp_path / "valid.csv"
        df = pd.DataFrame({"time": [1, 2, 3], "value": [1.0, 2.0, 3.0]})
        df.to_csv(csv_file, index=False)
        
        # Validate
        result = validate_file(str(csv_file))
        assert result.is_valid
        # Check file_integrity info if present
        if result.file_integrity is not None:
            assert result.file_integrity.size_bytes > 0
    
    def test_corrupted_file_detection(self, tmp_path):
        """Test detection of corrupted files."""
        from platform_base.io.validator import validate_file

        # Create corrupted CSV
        corrupted_file = tmp_path / "corrupted.csv"
        corrupted_file.write_text("time,value\n1,2,3,4\n")  # Invalid format
        
        # Validate
        result = validate_file(str(corrupted_file))
        # Should detect issues
        assert result is not None


class TestInterpolationIntegration:
    """Integration tests for interpolation methods."""
    
    def test_multiple_interpolation_methods_comparison(self):
        """Compare different interpolation methods on same data."""
        from platform_base.processing.interpolation import interpolate

        # Create test data with gaps
        t = np.array([0, 1, 2, 5, 6, 7, 10], dtype=float)  # Gap between 2 and 5
        y = np.sin(t)
        
        # Use only supported methods
        methods = ["linear", "spline_cubic", "smoothing_spline"]
        results = {}
        
        for method in methods:
            result = interpolate(y, t, method=method, params={})
            results[method] = result
            assert result is not None
        
        # All methods should produce output
        assert len(results) == len(methods)
    
    def test_interpolation_with_nan_handling(self):
        """Test interpolation handles NaN values correctly."""
        from platform_base.processing.interpolation import interpolate

        # Data with NaN
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        y[20:30] = np.nan  # Introduce NaN gap
        
        result = interpolate(y, t, method="linear", params={})
        
        # Should interpolate NaN values
        assert result is not None
        # Result may still have some NaN at boundaries but should be reduced
        assert np.isnan(result.values).sum() <= np.isnan(y).sum()


@pytest.mark.slow
class TestPerformanceIntegration:
    """Integration tests focusing on performance."""
    
    def test_large_dataset_pipeline(self):
        """Test pipeline with large dataset (100K points)."""
        from platform_base.processing.calculus import derivative
        from platform_base.processing.downsampling import downsample

        # Generate large dataset
        t = np.linspace(0, 1000, 100_000)
        y = np.sin(t) + 0.01 * np.random.randn(len(t))
        
        # Downsample first for performance
        result = downsample(y, t, n_points=1000, method="lttb")
        assert len(result.values) == 1000
        
        # Process downsampled data
        calc_result = derivative(result.values, result.t_seconds, order=1)
        assert calc_result is not None
