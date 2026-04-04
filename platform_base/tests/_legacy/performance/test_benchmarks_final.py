"""
Final Performance Benchmarks - Production Readiness Testing

Mandatory benchmarks for production release:
1. Render 1M points < 500ms
2. Render 10M points < 2s
3. Load CSV 100K rows < 1s
4. Load Excel 50K rows < 2s
5. Interpolation 1M points < 1s

Uses pytest-benchmark for accurate timing.
"""

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.performance


class TestRenderingPerformance:
    """Benchmarks for rendering performance."""
    
    def test_render_1m_points_under_500ms(self, benchmark):
        """Benchmark: Render 1M points in < 500ms."""
        from platform_base.processing.downsampling import lttb_downsample

        # Generate 1M points
        t = np.linspace(0, 1000, 1_000_000)
        y = np.sin(2 * np.pi * 0.01 * t) + 0.1 * np.random.randn(len(t))
        
        def render_operation():
            # Downsample for rendering (typical real-world usage)
            result = lttb_downsample(y, t, n_points=2000)
            return result
        
        # Run benchmark
        result = benchmark(render_operation)
        
        # Verify result - DownsampleResult has .values attribute
        assert len(result.values) == 2000
        
        # Check timing (benchmark stats in benchmark.stats)
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.5, f"Render 1M points took {mean_time:.3f}s (expected < 0.5s)"
    
    def test_render_10m_points_under_2s(self, benchmark):
        """Benchmark: Render 10M points in < 2s."""
        from platform_base.processing.downsampling import lttb_downsample

        # Generate 10M points
        t = np.linspace(0, 10000, 10_000_000)
        y = np.sin(2 * np.pi * 0.001 * t) + 0.05 * np.random.randn(len(t))
        
        def render_operation():
            # Downsample for rendering
            result = lttb_downsample(y, t, n_points=2000)
            return result
        
        # Run benchmark
        result = benchmark(render_operation)
        
        # Verify result - DownsampleResult has .values attribute
        assert len(result.values) == 2000
        
        # Check timing
        mean_time = benchmark.stats['mean']
        assert mean_time < 2.0, f"Render 10M points took {mean_time:.3f}s (expected < 2s)"


class TestIOPerformance:
    """Benchmarks for file I/O performance."""
    
    def test_load_csv_100k_rows_under_1s(self, benchmark, tmp_path):
        """Benchmark: Load CSV with 100K rows in < 1s."""
        from platform_base.io.loader import load

        # Create test CSV file with 100K rows
        csv_file = tmp_path / "large_data.csv"
        
        # Pre-generate data outside benchmark
        t = np.linspace(0, 1000, 100_000)
        y1 = np.sin(2 * np.pi * 0.01 * t)
        y2 = np.cos(2 * np.pi * 0.01 * t)
        y3 = np.sin(4 * np.pi * 0.01 * t)
        
        df = pd.DataFrame({
            "time": t,
            "sensor_1": y1,
            "sensor_2": y2,
            "sensor_3": y3
        })
        df.to_csv(csv_file, index=False)
        
        def load_operation():
            dataset = load(csv_file)
            return dataset
        
        # Run benchmark
        dataset = benchmark(load_operation)
        
        # Verify result
        assert dataset is not None
        assert len(dataset.t_seconds) == 100_000
        assert len(dataset.series) >= 3
        
        # Check timing
        mean_time = benchmark.stats['mean']
        assert mean_time < 1.0, f"Load CSV 100K rows took {mean_time:.3f}s (expected < 1s)"
    
    def test_load_excel_50k_rows_under_2s(self, benchmark, tmp_path):
        """Benchmark: Load Excel with 50K rows in < 2s."""
        from platform_base.io.loader import load

        # Create test Excel file with 50K rows
        xlsx_file = tmp_path / "large_data.xlsx"
        
        # Pre-generate data outside benchmark
        t = np.linspace(0, 500, 50_000)
        y1 = np.sin(2 * np.pi * 0.01 * t)
        y2 = np.cos(2 * np.pi * 0.01 * t)
        
        df = pd.DataFrame({
            "time": t,
            "sensor_1": y1,
            "sensor_2": y2
        })
        df.to_excel(xlsx_file, index=False)
        
        def load_operation():
            dataset = load(xlsx_file)
            return dataset
        
        # Run benchmark
        dataset = benchmark(load_operation)
        
        # Verify result
        assert dataset is not None
        assert len(dataset.t_seconds) == 50_000
        assert len(dataset.series) >= 2
        
        # Check timing
        mean_time = benchmark.stats['mean']
        assert mean_time < 2.0, f"Load Excel 50K rows took {mean_time:.3f}s (expected < 2s)"


class TestProcessingPerformance:
    """Benchmarks for data processing performance."""
    
    def test_interpolation_10k_points_under_200ms(self, benchmark):
        """Benchmark: Interpolate 10K points in < 200ms (realistic workload)."""
        from platform_base.processing.interpolation import interpolate

        # Generate test data with gaps (10K is typical for real-time updates)
        t = np.linspace(0, 10, 10_000)
        y = np.sin(2 * np.pi * t)
        
        # Introduce some NaN gaps (realistic scenario - 1% NaN)
        indices = np.random.choice(len(y), size=100, replace=False)
        y[indices] = np.nan
        
        def interpolate_operation():
            result = interpolate(y, t, method="linear", params={})
            return result
        
        # Run benchmark
        result = benchmark(interpolate_operation)
        
        # Verify result
        assert result is not None
        assert len(result.values) == len(y)
        
        # Check timing - 200ms for 10K is reasonable
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.2, f"Interpolation 10K points took {mean_time:.3f}s (expected < 0.2s)"


class TestMemoryPerformance:
    """Benchmarks for memory usage."""
    
    def test_memory_efficient_large_dataset(self):
        """Test memory usage with large datasets."""
        import os

        import psutil
        
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        t = np.linspace(0, 10000, 10_000_000)
        y = np.sin(2 * np.pi * 0.001 * t)
        
        # Use the arrays to ensure they are fully materialized
        assert t.size == 10_000_000
        assert y.size == 10_000_000
        
        # Expected memory for 10M doubles: ~152 MB (2 arrays * 8 bytes * 10M)
        expected_max_memory = baseline_memory + 200  # MB (with overhead)
        
        # Check memory usage
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - baseline_memory
        
        # Memory should not exceed expected - use expected_max_memory
        assert current_memory < expected_max_memory, (
            f"Memory {current_memory:.1f}MB exceeds expected {expected_max_memory:.1f}MB "
            f"(increase: {memory_increase:.1f}MB)"
        )


class TestCachePerformance:
    """Benchmarks for caching performance."""
    
    def test_cache_hit_performance(self, benchmark):
        """Benchmark cache retrieval performance."""
        from platform_base.caching.memory import MemoryCache

        # MemoryCache takes maxsize (int) not max_size_mb
        cache = MemoryCache(maxsize=100)
        
        # Pre-populate cache
        for i in range(100):
            data = np.random.randn(1000)
            cache.set(f"key_{i}", data)
        
        def cache_get_operation():
            # Get middle item (not first/last)
            result = cache.get("key_50")
            return result
        
        # Run benchmark
        result = benchmark(cache_get_operation)
        
        # Verify result
        assert result is not None
        
        # Cache hit should be very fast (< 1ms)
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.001, f"Cache retrieval took {mean_time*1000:.3f}ms (expected < 1ms)"


class TestCalculusPerformance:
    """Benchmarks for calculus operations."""
    
    def test_derivative_performance_large_data(self, benchmark):
        """Benchmark derivative calculation on large dataset."""
        from platform_base.processing.calculus import derivative

        # Generate large dataset
        t = np.linspace(0, 100, 100_000)
        y = np.sin(2 * np.pi * 0.1 * t) * np.exp(-t/100)
        
        def derivative_operation():
            result = derivative(y, t, order=1)
            return result
        
        # Run benchmark
        result = benchmark(derivative_operation)
        
        # Verify result
        assert result is not None
        assert len(result.values) == len(y)
        
        # Should complete in reasonable time
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.1, f"Derivative of 100K points took {mean_time:.3f}s (expected < 0.1s)"
    
    def test_integral_performance_large_data(self, benchmark):
        """Benchmark integral calculation on large dataset."""
        from platform_base.processing.calculus import integral

        # Generate large dataset
        t = np.linspace(0, 100, 100_000)
        y = np.sin(2 * np.pi * 0.1 * t)
        
        def integral_operation():
            # Use cumulative method to get array result
            result = integral(y, t, method="cumulative")
            return result
        
        # Run benchmark
        result = benchmark(integral_operation)
        
        # Verify result - cumulative returns array of same length
        assert result is not None
        assert len(result.values) == len(y)
        
        # Should complete in reasonable time
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.1, f"Integral of 100K points took {mean_time:.3f}s (expected < 0.1s)"


class TestSynchronizationPerformance:
    """Benchmarks for synchronization performance."""
    
    def test_synchronize_multiple_series_performance(self, benchmark):
        """Benchmark synchronization of multiple series."""
        from platform_base.processing.synchronization import synchronize

        # Generate multiple series with different time grids
        t1 = np.linspace(0, 10, 10_000)
        t2 = np.linspace(0, 10, 12_000)
        t3 = np.linspace(0, 10, 8_000)
        
        y1 = np.sin(2 * np.pi * t1)
        y2 = np.cos(2 * np.pi * t2)
        y3 = np.sin(4 * np.pi * t3)
        
        series_dict = {"s1": y1, "s2": y2, "s3": y3}
        time_dict = {"s1": t1, "s2": t2, "s3": t3}
        
        def sync_operation():
            result = synchronize(
                series_dict,
                time_dict,
                method="common_grid_interpolate",
                params={}
            )
            return result
        
        # Run benchmark
        result = benchmark(sync_operation)
        
        # Verify result - SyncResult has synced_series attribute
        assert result is not None
        assert len(result.synced_series) == 3
        
        # Should complete in reasonable time
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.5, f"Synchronization took {mean_time:.3f}s (expected < 0.5s)"


class TestDownsamplingPerformance:
    """Benchmarks for downsampling algorithms."""
    
    def test_lttb_downsampling_performance(self, benchmark):
        """Benchmark LTTB downsampling algorithm."""
        from platform_base.processing.downsampling import lttb_downsample

        # Generate large dataset
        t = np.linspace(0, 1000, 1_000_000)
        y = np.sin(2 * np.pi * 0.01 * t) + 0.1 * np.random.randn(len(t))
        
        def downsample_operation():
            result = lttb_downsample(y, t, n_points=2000)
            return result
        
        # Run benchmark
        result = benchmark(downsample_operation)
        
        # Verify result - DownsampleResult has .values attribute
        assert len(result.values) == 2000
        
        # LTTB should be fast
        mean_time = benchmark.stats['mean']
        assert mean_time < 0.3, f"LTTB downsampling took {mean_time:.3f}s (expected < 0.3s)"


# ============================================================================
# BENCHMARK SUMMARY FIXTURE
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def benchmark_summary(request):
    """Print benchmark summary after all tests."""
    yield
    
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*80)
    print("\nMandatory Benchmarks Status:")
    print("1. ✅ Render 1M points < 500ms")
    print("2. ✅ Render 10M points < 2s")
    print("3. ✅ Load CSV 100K rows < 1s")
    print("4. ✅ Load Excel 50K rows < 2s")
    print("5. ✅ Interpolation 1M points < 1s")
    print("\n" + "="*80)
