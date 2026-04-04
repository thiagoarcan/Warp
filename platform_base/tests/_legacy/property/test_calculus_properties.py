"""
Testes baseados em propriedades - Platform Base v2.0

Usando Hypothesis para testar propriedades matemáticas e invariantes.
"""

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

# Estratégias customizadas
float_arrays = st.lists(
    st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    min_size=10,
    max_size=1000
).map(np.array)

positive_float_arrays = st.lists(
    st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False),
    min_size=10,
    max_size=1000
).map(np.array)

sorted_float_arrays = st.lists(
    st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    min_size=10,
    max_size=500,
    unique=True
).map(lambda x: np.array(sorted(x)))


class TestDerivativeProperties:
    """Testes de propriedades da derivada"""
    
    @given(st.floats(min_value=0.1, max_value=10.0), st.integers(min_value=10, max_value=500))
    @settings(max_examples=50, deadline=15000)  # 15s para compilação inicial
    def test_derivative_of_linear_is_constant(self, slope: float, n_points: int):
        """A derivada de uma função linear deve ser constante"""
        from platform_base.processing.calculus import derivative
        
        t = np.linspace(0, 10, n_points)
        y = slope * t  # y = slope * x
        
        result = derivative(y, t, order=1)
        
        # A derivada deve ser aproximadamente constante = slope
        # Ignora bordas onde erros são maiores
        middle = result.values[n_points//4:-n_points//4]
        assert np.std(middle) < 0.5  # Baixa variância
        assert abs(np.mean(middle) - slope) < 0.5  # Próximo do slope
    
    @given(st.floats(min_value=0.5, max_value=5.0), st.integers(min_value=50, max_value=500))
    @settings(max_examples=50, deadline=5000)
    def test_derivative_of_quadratic(self, a: float, n_points: int):
        """A derivada de x² deve ser aproximadamente 2x"""
        from platform_base.processing.calculus import derivative
        
        t = np.linspace(0, 5, n_points)
        y = a * t ** 2  # y = a * x^2
        
        result = derivative(y, t, order=1)
        expected = 2 * a * t  # dy/dx = 2ax
        
        # Erro relativo na região central
        middle_slice = slice(n_points//4, -n_points//4)
        error = np.abs(result.values[middle_slice] - expected[middle_slice])
        mean_error = np.mean(error)
        
        assert mean_error < 0.5 * a  # Erro proporcional a 'a'
    
    @given(st.integers(min_value=50, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_derivative_of_constant_is_zero(self, n_points: int):
        """A derivada de uma constante deve ser aproximadamente zero"""
        from platform_base.processing.calculus import derivative
        
        t = np.linspace(0, 10, n_points)
        y = np.ones(n_points) * 42.0  # constante
        
        result = derivative(y, t, order=1)
        
        # Deve ser aproximadamente zero (com ruído numérico)
        assert np.abs(np.mean(result.values)) < 1.0
        assert np.std(result.values) < 1.0


class TestIntegralProperties:
    """Testes de propriedades da integral"""
    
    @given(st.floats(min_value=0.5, max_value=10.0), st.integers(min_value=50, max_value=500))
    @settings(max_examples=50, deadline=5000)
    def test_integral_of_constant(self, c: float, n_points: int):
        """Integral de constante c de 0 a T deve ser c*T"""
        from platform_base.processing.calculus import integral
        
        T = 10.0
        t = np.linspace(0, T, n_points)
        y = np.ones(n_points) * c
        
        result = integral(y, t)
        
        # Último valor deve ser aproximadamente c * T
        expected = c * T
        assert abs(result.values[-1] - expected) < expected * 0.05
    
    @given(st.floats(min_value=0.5, max_value=5.0), st.integers(min_value=50, max_value=500))
    @settings(max_examples=50, deadline=5000)
    def test_integral_of_linear(self, slope: float, n_points: int):
        """Integral de slope*x de 0 a T deve ser slope*T²/2"""
        from platform_base.processing.calculus import integral
        
        T = 5.0
        t = np.linspace(0, T, n_points)
        y = slope * t
        
        result = integral(y, t)
        
        # Último valor deve ser aproximadamente slope * T^2 / 2
        expected = slope * T ** 2 / 2
        assert abs(result.values[-1] - expected) < expected * 0.05
    
    @given(st.integers(min_value=50, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_integral_is_monotonic_for_positive_function(self, n_points: int):
        """Integral de função positiva deve ser monotonicamente crescente"""
        from platform_base.processing.calculus import integral
        
        t = np.linspace(0, 10, n_points)
        y = np.abs(np.sin(t)) + 0.1  # Sempre positivo
        
        result = integral(y, t)
        
        # Diferenças devem ser todas >= 0 (com tolerância numérica)
        diffs = np.diff(result.values)
        assert np.all(diffs >= -1e-10)


class TestDownsamplingProperties:
    """Testes de propriedades do downsampling"""
    
    @given(
        st.integers(min_value=100, max_value=2000),
        st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=30, deadline=10000)
    def test_downsample_reduces_points(self, n_original: int, n_target: int):
        """Downsampling deve reduzir para exatamente n_target pontos"""
        from platform_base.processing.downsampling import downsample
        
        assume(n_target < n_original)  # Só testa quando há redução
        
        t = np.linspace(0, 100, n_original)
        y = np.sin(t * 0.1)
        
        result = downsample(y, t, n_points=n_target, method="lttb")
        
        assert len(result.values) == n_target
        assert len(result.t_seconds) == n_target
    
    @given(st.integers(min_value=100, max_value=1000))
    @settings(max_examples=30, deadline=10000)
    def test_downsample_preserves_range(self, n_points: int):
        """Downsampling deve preservar o range aproximado dos dados"""
        from platform_base.processing.downsampling import downsample
        
        t = np.linspace(0, 100, n_points)
        y = np.sin(t * 0.2) * 50
        
        result = downsample(y, t, n_points=50, method="lttb")
        
        # Range dos dados downsampled deve ser similar ao original
        original_range = np.ptp(y)
        downsampled_range = np.ptp(result.values)
        
        # Pelo menos 50% do range deve ser preservado
        assert downsampled_range >= original_range * 0.5
    
    @given(st.integers(min_value=50, max_value=500))
    @settings(max_examples=30, deadline=10000)
    def test_downsample_time_is_sorted(self, n_points: int):
        """Tempo após downsampling deve estar ordenado"""
        from platform_base.processing.downsampling import downsample
        
        t = np.linspace(0, 100, n_points)
        y = np.random.randn(n_points)
        
        result = downsample(y, t, n_points=20, method="lttb")
        
        # Tempo deve estar estritamente crescente
        diffs = np.diff(result.t_seconds)
        assert np.all(diffs > 0)


class TestInterpolationProperties:
    """Testes de propriedades da interpolação"""
    
    @given(st.integers(min_value=20, max_value=200))
    @settings(max_examples=30, deadline=5000)
    def test_interpolation_preserves_original_points(self, n_points: int):
        """Interpolação linear deve preservar pontos originais"""
        from platform_base.processing.interpolation import interpolate
        
        t = np.linspace(0, 10, n_points).astype(float)
        y = np.sin(t)
        
        # Interpola para os mesmos pontos
        result = interpolate(y, t, method="linear", params={})
        
        # Deve ser praticamente igual ao original
        assert np.allclose(result.values, y, atol=1e-10)
    
    @given(st.integers(min_value=20, max_value=100))
    @settings(max_examples=30, deadline=5000)
    def test_linear_interpolation_is_linear_between_points(self, n_points: int):
        """Interpolação linear entre dois pontos deve ser uma reta"""
        from platform_base.processing.interpolation import interpolate

        # Apenas 2 pontos
        t = np.array([0.0, 10.0])
        y = np.array([0.0, 100.0])
        
        result = interpolate(y, t, method="linear", params={})
        
        # Resultado deve ser linear: y = 10 * t
        # Verifica que result segue a reta
        if len(result.values) > 2:
            expected = result.values[0] + (result.values[-1] - result.values[0]) * \
                       np.linspace(0, 1, len(result.values))
            assert np.allclose(result.values, expected, atol=0.1)


class TestSmoothingProperties:
    """Testes de propriedades da suavização"""
    
    @given(st.integers(min_value=100, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_smoothing_reduces_variance(self, n_points: int):
        """Suavização deve reduzir a variância do ruído"""
        from platform_base.processing.smoothing import smooth
        
        np.random.seed(42)
        t = np.linspace(0, 10, n_points)
        signal = np.sin(t)
        noisy = signal + np.random.randn(n_points) * 0.5
        
        result = smooth(noisy, method="gaussian", params={"sigma": 5})
        
        # Variância do erro deve diminuir
        error_before = np.var(noisy - signal)
        error_after = np.var(result - signal)
        
        assert error_after < error_before
    
    @given(st.integers(min_value=100, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_smoothing_preserves_mean(self, n_points: int):
        """Suavização gaussiana deve preservar aproximadamente a média"""
        from platform_base.processing.smoothing import smooth
        
        np.random.seed(42)
        y = np.random.randn(n_points) + 100  # Média ~100
        
        result = smooth(y, method="gaussian", params={"sigma": 3})
        
        # Médias devem ser próximas
        assert abs(np.mean(result) - np.mean(y)) < 1.0
    
    @given(st.integers(min_value=100, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_smoothing_preserves_length(self, n_points: int):
        """Suavização deve preservar o número de pontos"""
        from platform_base.processing.smoothing import smooth
        
        y = np.random.randn(n_points)
        
        result = smooth(y, method="median", params={"kernel_size": 5})
        
        assert len(result) == n_points


class TestDataRoundtripProperties:
    """Testes de propriedades de roundtrip de dados"""
    
    @given(
        st.lists(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
                 min_size=20, max_size=100)
    )
    @settings(max_examples=20, deadline=10000)
    def test_csv_roundtrip(self, values: list):
        """Dados salvos e carregados devem ser iguais"""
        import os
        import tempfile

        import pandas as pd

        from platform_base.io.loader import load

        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            f.write("timestamp,value\n")
            for i, v in enumerate(values):
                ts = f"2024-01-01 00:00:{i % 60:02d}"
                f.write(f"{ts},{v}\n")
            temp_file = f.name
        
        try:
            dataset = load(temp_file)
            
            # Verifica que dados foram carregados
            assert len(dataset.series) >= 1
            
            # Pega primeira série
            series = list(dataset.series.values())[0]
            
            # Valores devem ser preservados (com tolerância para float)
            loaded_values = series.values[:len(values)]
            assert np.allclose(loaded_values, values, rtol=1e-5)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestAreaBetweenCurvesProperties:
    """Testes de propriedades da área entre curvas"""
    
    @given(st.floats(min_value=0.1, max_value=10.0), st.integers(min_value=50, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_area_is_positive_for_y1_above_y2(self, height: float, n_points: int):
        """Área deve ser positiva quando y1 > y2"""
        from platform_base.processing.calculus import area_between
        
        t = np.linspace(0, 10, n_points)
        y1 = np.ones(n_points) * (10 + height)
        y2 = np.ones(n_points) * 10
        
        result = area_between(y1, y2, t)
        
        expected_area = height * 10  # altura * largura
        assert result.values > 0
        assert abs(result.values - expected_area) < expected_area * 0.1
    
    @given(st.integers(min_value=50, max_value=500))
    @settings(max_examples=30, deadline=5000)
    def test_area_is_symmetric(self, n_points: int):
        """Área entre y1 e y2 deve ser igual a área entre y2 e y1 (em valor absoluto)"""
        from platform_base.processing.calculus import area_between
        
        t = np.linspace(0, 10, n_points)
        y1 = np.sin(t)
        y2 = np.cos(t)
        
        area1 = area_between(y1, y2, t)
        area2 = area_between(y2, y1, t)
        
        # Áreas devem ter o mesmo valor absoluto
        assert abs(abs(area1.values) - abs(area2.values)) < 0.1
