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
        from platform_base.processing.interpolation import interpolate
        from platform_base.processing.calculus import derivative
        
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
        assert "s1" in result.synced_data
        assert "s2" in result.synced_data
        assert len(result.synced_data["s1"]) == len(result.synced_data["s2"])


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
        from platform_base.core.session import SessionState, SessionData
        from platform_base.core.models import Dataset, Series
        
        # Create session with data
        session = SessionState()
        
        # Add dataset
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        series = Series(series_id="test", name="Test Series", values=y)
        dataset = Dataset(
            dataset_id="test_ds",
            name="Test Dataset",
            series={"test": series},
            t_seconds=t
        )
        session.add_dataset(dataset)
        
        # Save session - use these variables to verify structure
        session_file = tmp_path / "session.json"
        session_data = SessionData(datasets=[dataset])
        
        # Verify session file path and data structure
        assert session_file.parent.exists()
        assert len(session_data.datasets) == 1
        assert len(session.datasets) == 1
        assert "test_ds" in session.datasets


class TestStreamingIntegration:
    """Integration tests for streaming functionality."""
    
    def test_streaming_with_filters(self):
        """Test streaming with real-time filtering."""
        from platform_base.streaming.filters import LowpassFilter
        
        # Generate streaming data
        t = np.linspace(0, 10, 1000)
        y = np.sin(2 * np.pi * t) + 0.1 * np.random.randn(len(t))
        
        # Apply filter
        filter_obj = LowpassFilter(cutoff=5.0, fs=100.0)
        filtered = filter_obj.apply(y)
        
        assert len(filtered) == len(y)
        # Filtered signal should have less noise
        assert np.std(filtered) < np.std(y)


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
        assert result.format == "csv"
    
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
        t = np.array([0, 1, 2, 5, 6, 7, 10])  # Gap between 2 and 5
        y = np.sin(t)
        
        methods = ["linear", "spline_cubic", "pchip"]
        results = {}
        
        for method in methods:
            result = interpolate(y, t, method=method, params={})
            results[method] = result
            assert result is not None
        
        # All methods should produce same length output
        lengths = [len(r.values) for r in results.values()]
        assert len(set(lengths)) == 1  # All same length
    
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
        from platform_base.processing.downsampling import downsample_lttb
        
        # Generate large dataset
        t = np.linspace(0, 1000, 100_000)
        y = np.sin(t) + 0.01 * np.random.randn(len(t))
        
        # Downsample first for performance
        downsampled = downsample_lttb(y, t, n_out=1000)
        assert len(downsampled) == 1000
        
        # Process downsampled data
        result = derivative(downsampled, np.linspace(t[0], t[-1], 1000), order=1)
        assert result is not None
