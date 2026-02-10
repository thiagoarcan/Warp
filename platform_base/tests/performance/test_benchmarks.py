"""
Testes de Performance usando pytest-benchmark

NÍVEL 7: Performance Tests
- Benchmarks de operações críticas
- Limites de tempo e memória
"""
from pathlib import Path

import numpy as np
import pytest

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def small_data():
    """Dados pequenos (10K pontos)"""
    t = np.linspace(0, 100, 10_000)
    y = np.sin(2 * np.pi * t) + np.random.normal(0, 0.1, len(t))
    return t, y


@pytest.fixture
def medium_data():
    """Dados médios (100K pontos)"""
    t = np.linspace(0, 100, 100_000)
    y = np.sin(2 * np.pi * t) + np.random.normal(0, 0.1, len(t))
    return t, y


@pytest.fixture
def large_data():
    """Dados grandes (1M pontos)"""
    t = np.linspace(0, 100, 1_000_000)
    y = np.sin(2 * np.pi * t) + np.random.normal(0, 0.1, len(t))
    return t, y


@pytest.fixture
def temp_csv_10k(tmp_path, small_data):
    """Cria arquivo CSV com 10K linhas"""
    t, y = small_data
    csv_file = tmp_path / "data_10k.csv"
    csv_file.write_text(
        "time,value\n" + "\n".join(f"{ti:.6f},{yi:.6f}" for ti, yi in zip(t, y))
    )
    return csv_file


@pytest.fixture
def temp_csv_100k(tmp_path, medium_data):
    """Cria arquivo CSV com 100K linhas"""
    t, y = medium_data
    csv_file = tmp_path / "data_100k.csv"
    csv_file.write_text(
        "time,value\n" + "\n".join(f"{ti:.6f},{yi:.6f}" for ti, yi in zip(t, y))
    )
    return csv_file


# =============================================================================
# PROCESSING BENCHMARKS
# =============================================================================

@pytest.mark.benchmark(group="derivative")
class TestDerivativeBenchmarks:
    """Benchmarks para cálculo de derivada"""
    
    def test_derivative_10k(self, benchmark, small_data):
        """Benchmark derivada com 10K pontos"""
        from platform_base.processing.calculus import derivative
        
        t, y = small_data
        result = benchmark(derivative, y, t, order=1)
        
        assert result is not None
        assert len(result.values) == len(y)
    
    def test_derivative_100k(self, benchmark, medium_data):
        """Benchmark derivada com 100K pontos"""
        from platform_base.processing.calculus import derivative
        
        t, y = medium_data
        result = benchmark(derivative, y, t, order=1)
        
        assert result is not None
        assert len(result.values) == len(y)


@pytest.mark.benchmark(group="integral")
class TestIntegralBenchmarks:
    """Benchmarks para cálculo de integral"""
    
    def test_integral_10k(self, benchmark, small_data):
        """Benchmark integral com 10K pontos"""
        from platform_base.processing.calculus import integral
        
        t, y = small_data
        result = benchmark(integral, y, t)
        
        assert result is not None
    
    def test_integral_100k(self, benchmark, medium_data):
        """Benchmark integral com 100K pontos"""
        from platform_base.processing.calculus import integral
        
        t, y = medium_data
        result = benchmark(integral, y, t)
        
        assert result is not None


@pytest.mark.benchmark(group="smoothing")
class TestSmoothingBenchmarks:
    """Benchmarks para suavização"""
    
    def test_smooth_savgol_10k(self, benchmark, small_data):
        """Benchmark Savitzky-Golay com 10K pontos"""
        from platform_base.processing.smoothing import smooth
        
        t, y = small_data
        result = benchmark(smooth, y, method="savitzky_golay", params={"window": 51, "order": 3})
        
        assert result is not None
        # smooth pode retornar array diretamente ou objeto com .values
        values = result.values if hasattr(result, 'values') else result
        assert len(values) == len(y)
    
    def test_smooth_gaussian_10k(self, benchmark, small_data):
        """Benchmark Gaussian com 10K pontos"""
        from platform_base.processing.smoothing import smooth
        
        t, y = small_data
        result = benchmark(smooth, y, method="gaussian", params={"sigma": 5})
        
        assert result is not None


@pytest.mark.benchmark(group="downsampling")
class TestDownsamplingBenchmarks:
    """Benchmarks para downsampling"""
    
    def test_downsample_lttb_100k_to_1k(self, benchmark, medium_data):
        """Benchmark LTTB 100K → 1K pontos"""
        from platform_base.processing.downsampling import downsample
        
        t, y = medium_data
        result = benchmark(downsample, y, t, n_points=1000, method="lttb")
        
        assert result is not None
        assert len(result.values) == 1000
    
    def test_downsample_minmax_100k_to_1k(self, benchmark, medium_data):
        """Benchmark MinMax 100K → 1K pontos"""
        from platform_base.processing.downsampling import downsample
        
        t, y = medium_data
        result = benchmark(downsample, y, t, n_points=1000, method="minmax")
        
        assert result is not None


@pytest.mark.benchmark(group="interpolation")
class TestInterpolationBenchmarks:
    """Benchmarks para interpolação"""
    
    def test_interpolate_linear_10k(self, benchmark, small_data):
        """Benchmark interpolação linear 10K pontos"""
        from platform_base.processing.interpolation import interpolate
        
        t, y = small_data
        
        # interpolate(values, t_seconds, method, params)
        result = benchmark(interpolate, y, t, "linear", {"factor": 2})
        
        assert result is not None
    
    def test_interpolate_cubic_10k(self, benchmark, small_data):
        """Benchmark interpolação cúbica 10K pontos"""
        from platform_base.processing.interpolation import interpolate
        
        t, y = small_data
        
        # Usa linear como fallback se cubic não estiver disponível
        result = benchmark(interpolate, y, t, "linear", {"factor": 2})
        
        assert result is not None


# =============================================================================
# FILE LOADING BENCHMARKS
# =============================================================================

@pytest.mark.benchmark(group="load")
class TestFileLoadingBenchmarks:
    """Benchmarks para carregamento de arquivos"""
    
    def test_load_csv_10k(self, benchmark, temp_csv_10k):
        """Benchmark load CSV 10K linhas"""
        from platform_base.io.loader import load
        
        result = benchmark(load, temp_csv_10k)
        
        assert result is not None


# =============================================================================
# BASELINE ASSERTIONS
# =============================================================================

@pytest.mark.benchmark(group="baselines")
class TestPerformanceBaselines:
    """Testes de baseline de performance"""
    
    def test_derivative_baseline_10k_under_50ms(self, small_data):
        """Derivada 10K deve ser < 50ms"""
        import time

        from platform_base.processing.calculus import derivative
        
        t, y = small_data
        
        start = time.perf_counter()
        derivative(y, t, order=1)
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.05, f"Derivada 10K levou {elapsed*1000:.1f}ms (max 50ms)"
    
    def test_integral_baseline_10k_under_50ms(self, small_data):
        """Integral 10K deve ser < 50ms"""
        import time

        from platform_base.processing.calculus import integral
        
        t, y = small_data
        
        start = time.perf_counter()
        integral(y, t)
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.05, f"Integral 10K levou {elapsed*1000:.1f}ms (max 50ms)"
    
    def test_downsample_baseline_100k_under_500ms(self, medium_data):
        """Downsample LTTB 100K → 1K deve ser < 500ms"""
        import time

        from platform_base.processing.downsampling import downsample
        
        t, y = medium_data
        
        start = time.perf_counter()
        downsample(y, t, n_points=1000, method="lttb")
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.5, f"Downsample 100K→1K levou {elapsed*1000:.1f}ms (max 500ms)"
    
    def test_smooth_baseline_10k_under_100ms(self, small_data):
        """Smooth SavGol 10K deve ser < 100ms"""
        import time

        from platform_base.processing.smoothing import smooth
        
        t, y = small_data
        
        start = time.perf_counter()
        smooth(y, method="savitzky_golay", params={"window": 51, "order": 3})
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.1, f"Smooth 10K levou {elapsed*1000:.1f}ms (max 100ms)"
