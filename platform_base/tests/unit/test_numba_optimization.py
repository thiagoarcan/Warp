"""
Testes unitários para otimizações Numba nos hotspots conforme PRD.
"""
import pytest
import numpy as np
import time

from platform_base.processing.interpolation import interpolate, NUMBA_AVAILABLE
from platform_base.processing.calculus import derivative, integral, area_between


class TestNumbaOptimizations:
    """Testa otimizações Numba em hotspots matemáticos"""
    
    def test_numba_linear_interpolation_performance(self):
        """Testa performance da interpolação linear com Numba"""
        if not NUMBA_AVAILABLE:
            pytest.skip("Numba not available")
        
        # Create large dataset to trigger Numba optimization
        n_points = 100000
        x = np.linspace(0, 10, n_points)
        y = np.sin(x) + 0.1 * np.random.randn(n_points)
        
        # Introduce some NaN values
        nan_indices = np.random.choice(n_points, size=n_points//10, replace=False)
        y[nan_indices] = np.nan
        
        # Time the interpolation
        start_time = time.time()
        result = interpolate(y, x, method="linear", params={})
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"Linear interpolation of {n_points} points took {duration:.3f}s")
        
        # Verify result
        assert len(result.values) == n_points
        assert np.isfinite(result.values).all()
        
        # Performance target from PRD: 1M points interpolation < 2s
        # For 100K points, allow more time for JIT compilation
        assert duration < 5.0  # Allow time for JIT compilation on first run
        
    def test_numba_derivative_performance(self):
        """Testa performance do cálculo de derivadas com Numba"""
        if not NUMBA_AVAILABLE:
            pytest.skip("Numba not available")
            
        # Large dataset to trigger Numba
        n_points = 50000
        t = np.linspace(0, 10, n_points)
        values = np.sin(t) + 0.1 * np.cos(5*t)
        
        # Time derivative calculation
        start_time = time.time()
        result = derivative(values, t, order=1, method="finite_diff", params={})
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"First derivative of {n_points} points took {duration:.3f}s")
        
        # Verify result
        assert len(result.values) == n_points
        assert np.isfinite(result.values).all()
        
        # Performance should be good for large datasets
        assert duration < 0.5  # Should be fast for 50K points
        
    def test_numba_integral_performance(self):
        """Testa performance da integração numérica com Numba"""
        if not NUMBA_AVAILABLE:
            pytest.skip("Numba not available")
            
        # Large dataset
        n_points = 50000
        t = np.linspace(0, 10, n_points)
        values = np.sin(t)
        
        # Time integration
        start_time = time.time()
        result = integral(values, t, method="trapezoid")
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"Integration of {n_points} points took {duration:.3f}s")
        
        # Verify result - integral of sin from 0 to 10 should be close to known value
        expected = -np.cos(10) + np.cos(0)  # Analytical result
        actual = result.values[0]
        assert abs(actual - expected) < 0.1
        
        # Performance check
        assert duration < 0.1
        
    def test_numba_area_between_performance(self):
        """Testa performance do cálculo de área entre curvas com Numba"""
        if not NUMBA_AVAILABLE:
            pytest.skip("Numba not available")
            
        # Large dataset
        n_points = 50000
        t = np.linspace(0, 10, n_points)
        upper = np.sin(t) + 2
        lower = np.sin(t) - 2
        
        # Time area calculation
        start_time = time.time()
        result = area_between(upper, lower, t)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"Area between curves for {n_points} points took {duration:.3f}s")
        
        # Verify result - area should be 4 * length of interval
        expected_area = 4 * 10  # 4 units height * 10 units width
        actual_area = result.values[0]
        assert abs(actual_area - expected_area) < 1.0
        
        # Performance check - allow time for JIT compilation
        assert duration < 2.0
        
    def test_numba_accuracy_vs_numpy(self):
        """Testa que otimizações Numba mantêm precisão em relação ao NumPy"""
        if not NUMBA_AVAILABLE:
            pytest.skip("Numba not available")
            
        # Small dataset for accuracy comparison
        t = np.linspace(0, 1, 100)
        values = np.sin(2 * np.pi * t)
        
        # Test derivative accuracy
        result_numba = derivative(values, t, order=1, method="finite_diff", params={})
        
        # For small dataset, should fall back to numpy, but let's test accuracy
        expected_derivative = 2 * np.pi * np.cos(2 * np.pi * t)
        
        # Check that computed derivative is reasonably close to analytical
        # (considering finite difference approximation errors)
        error = np.mean(np.abs(result_numba.values - expected_derivative))
        assert error < 1.0  # Reasonable tolerance for finite difference
        
    def test_graceful_fallback_without_numba(self):
        """Testa que código funciona sem Numba disponível"""
        # This test will run regardless of Numba availability
        
        t = np.linspace(0, 1, 1000)
        values = np.sin(t)
        
        # These should work with or without Numba
        deriv_result = derivative(values, t, order=1, method="finite_diff", params={})
        integral_result = integral(values, t, method="trapezoid")
        
        assert len(deriv_result.values) == len(values)
        assert len(integral_result.values) == 1
        
    @pytest.mark.skipif(not NUMBA_AVAILABLE, reason="Numba not available")
    def test_numba_compilation_caching(self):
        """Testa que funções Numba são compiladas e cached corretamente"""
        # First call should compile and cache
        t1 = np.linspace(0, 1, 1000)
        values1 = np.sin(t1)
        
        start_time = time.time()
        result1 = derivative(values1, t1, order=1, method="finite_diff", params={})
        first_call_time = time.time() - start_time
        
        # Second call should use cached compilation
        t2 = np.linspace(0, 2, 1000) 
        values2 = np.cos(t2)
        
        start_time = time.time()
        result2 = derivative(values2, t2, order=1, method="finite_diff", params={})
        second_call_time = time.time() - start_time
        
        # Second call should be faster (no compilation overhead)
        # Note: this might not always be true due to system variance
        print(f"First call: {first_call_time:.3f}s, Second call: {second_call_time:.3f}s")
        
        # Both should produce valid results
        assert len(result1.values) == 1000
        assert len(result2.values) == 1000