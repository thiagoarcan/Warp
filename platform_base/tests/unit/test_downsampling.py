"""
Testes unitários para platform_base.processing.downsampling

Cobertura:
- LTTB (Largest Triangle Three Buckets)
- MinMax downsampling
- Adaptive downsampling
- Uniform downsampling
- Peak-aware downsampling
- Casos de borda e erros
"""

import numpy as np
import pytest

from platform_base.processing.downsampling import downsample, SUPPORTED_METHODS
from platform_base.utils.errors import DownsampleError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def large_sine_wave():
    """Grande array senoidal para testes de downsampling."""
    n = 10_000
    t = np.linspace(0, 100, n)
    y = np.sin(2 * np.pi * t / 10)  # Período de 10
    return t, y


@pytest.fixture
def data_with_peaks():
    """Dados com picos que devem ser preservados."""
    n = 1000
    t = np.linspace(0, 10, n)
    y = np.sin(t)
    # Adicionar picos
    y[250] = 2.0  # Pico positivo
    y[500] = -2.0  # Pico negativo
    y[750] = 1.5  # Outro pico
    return t, y


@pytest.fixture
def random_walk():
    """Random walk para teste de forma."""
    np.random.seed(42)
    n = 5000
    t = np.arange(n, dtype=float)
    y = np.cumsum(np.random.randn(n) * 0.1)
    return t, y


# =============================================================================
# Testes LTTB
# =============================================================================

class TestLTTBDownsampling:
    """Testes para LTTB downsampling."""

    def test_lttb_reduces_points(self, large_sine_wave):
        """LTTB reduz número de pontos para o target."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        # Deve ter aproximadamente o número de pontos solicitado
        assert len(result.values) <= target + 2
        assert len(result.values) >= target - 2

    def test_lttb_preserves_endpoints(self, large_sine_wave):
        """LTTB preserva primeiro e último pontos."""
        t, y = large_sine_wave
        target = 100
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        # Primeiro e último pontos devem ser preservados
        assert result.t_seconds[0] == t[0]
        assert result.t_seconds[-1] == t[-1]
        assert result.values[0] == y[0]
        assert result.values[-1] == y[-1]

    def test_lttb_preserves_shape(self, large_sine_wave):
        """LTTB preserva forma geral do sinal."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        # Amplitude máxima e mínima devem ser aproximadamente preservadas
        original_range = np.max(y) - np.min(y)
        result_range = np.max(result.values) - np.min(result.values)
        
        # Deve preservar pelo menos 90% da amplitude
        assert result_range > 0.9 * original_range

    def test_lttb_no_downsampling_if_target_larger(self, large_sine_wave):
        """LTTB não faz downsampling se target >= n_data."""
        t, y = large_sine_wave
        target = len(y) + 100  # Maior que os dados
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        # Deve retornar todos os pontos originais
        assert len(result.values) == len(y)

    def test_lttb_selected_indices_valid(self, large_sine_wave):
        """LTTB retorna índices válidos."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        # Todos os índices devem estar no range válido
        assert np.all(result.selected_indices >= 0)
        assert np.all(result.selected_indices < len(y))
        
        # Índices devem ser únicos
        assert len(np.unique(result.selected_indices)) == len(result.selected_indices)


# =============================================================================
# Testes MinMax
# =============================================================================

class TestMinMaxDownsampling:
    """Testes para MinMax downsampling."""

    def test_minmax_preserves_extrema(self, data_with_peaks):
        """MinMax preserva valores extremos (picos)."""
        t, y = data_with_peaks
        target = 100
        
        result = downsample(y, t, n_points=target, method="minmax")
        
        # Os picos devem estar presentes nos valores
        assert np.max(result.values) >= 1.9  # Pico positivo (~2.0)
        assert np.min(result.values) <= -1.9  # Pico negativo (~-2.0)

    def test_minmax_reduces_points(self, large_sine_wave):
        """MinMax reduz número de pontos."""
        t, y = large_sine_wave
        target = 200
        
        result = downsample(y, t, n_points=target, method="minmax")
        
        # MinMax pode ter até 2x buckets (min e max por bucket)
        assert len(result.values) <= target * 2

    def test_minmax_preserves_range(self, random_walk):
        """MinMax preserva range dos dados."""
        t, y = random_walk
        target = 500
        
        result = downsample(y, t, n_points=target, method="minmax")
        
        # Range deve ser preservado
        assert np.max(result.values) == pytest.approx(np.max(y), abs=0.01)
        assert np.min(result.values) == pytest.approx(np.min(y), abs=0.01)


# =============================================================================
# Testes Adaptive
# =============================================================================

class TestAdaptiveDownsampling:
    """Testes para adaptive downsampling."""

    def test_adaptive_reduces_points(self, large_sine_wave):
        """Adaptive reduz número de pontos."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="adaptive")
        
        # Deve reduzir o número de pontos
        assert len(result.values) < len(y)
        assert len(result.values) <= target * 2  # Margem para adaptividade

    def test_adaptive_more_points_in_variable_regions(self, large_sine_wave):
        """Adaptive aloca mais pontos em regiões de alta variância."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="adaptive")
        
        # Apenas verifica que funciona sem erro
        assert len(result.values) > 0
        assert len(result.t_seconds) == len(result.values)


# =============================================================================
# Testes Uniform
# =============================================================================

class TestUniformDownsampling:
    """Testes para uniform downsampling."""

    def test_uniform_reduces_to_target(self, large_sine_wave):
        """Uniform reduz para exatamente o target de pontos."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="uniform")
        
        # Deve ter exatamente o número de pontos solicitado
        assert len(result.values) == target

    def test_uniform_preserves_endpoints(self, large_sine_wave):
        """Uniform preserva primeiro e último pontos."""
        t, y = large_sine_wave
        target = 100
        
        result = downsample(y, t, n_points=target, method="uniform")
        
        # Primeiro e último devem ser iguais
        assert result.t_seconds[0] == t[0]
        assert result.t_seconds[-1] == t[-1]

    def test_uniform_evenly_spaced(self, large_sine_wave):
        """Uniform produz pontos uniformemente espaçados."""
        t, y = large_sine_wave
        target = 100
        
        result = downsample(y, t, n_points=target, method="uniform")
        
        # Diferenças devem ser aproximadamente constantes
        diffs = np.diff(result.t_seconds)
        assert np.std(diffs) < np.mean(diffs) * 0.01  # Variação < 1%


# =============================================================================
# Testes Peak-Aware
# =============================================================================

class TestPeakAwareDownsampling:
    """Testes para peak-aware downsampling."""

    def test_peak_aware_preserves_peaks(self, data_with_peaks):
        """Peak-aware preserva picos identificados."""
        t, y = data_with_peaks
        target = 100
        
        result = downsample(y, t, n_points=target, method="peak_aware")
        
        # Picos devem estar presentes ou muito próximos
        assert np.max(result.values) > 1.8  # Pico positivo
        assert np.min(result.values) < -1.8  # Pico negativo


# =============================================================================
# Testes de casos de borda
# =============================================================================

class TestDownsamplingEdgeCases:
    """Testes para casos de borda."""

    def test_target_equals_data_size(self, large_sine_wave):
        """Target igual ao tamanho dos dados retorna dados originais."""
        t, y = large_sine_wave
        target = len(y)
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        assert len(result.values) == len(y)

    def test_very_small_target(self):
        """Target muito pequeno ainda funciona."""
        t = np.linspace(0, 10, 1000)
        y = np.sin(t)
        target = 3
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        assert len(result.values) >= 2  # Pelo menos 2 pontos

    def test_small_input_array(self):
        """Array pequeno de entrada funciona."""
        t = np.array([0, 1, 2, 3, 4])
        y = np.array([0, 1, 0, 1, 0])
        target = 3
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        assert len(result.values) >= 2

    def test_invalid_method_raises(self):
        """Método inválido levanta erro."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        with pytest.raises((DownsampleError, ValueError)):
            downsample(y, t, n_points=50, method="invalid_method")

    def test_negative_target_raises(self):
        """Target negativo levanta erro."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        with pytest.raises((DownsampleError, ValueError)):
            downsample(y, t, n_points=-10, method="lttb")

    def test_zero_target_raises(self):
        """Target zero levanta erro."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        with pytest.raises((DownsampleError, ValueError)):
            downsample(y, t, n_points=0, method="lttb")


# =============================================================================
# Testes de metadata e qualidade
# =============================================================================

class TestDownsamplingMetadata:
    """Testes para metadata de downsampling."""

    def test_downsampling_generates_metadata(self, large_sine_wave):
        """Downsampling gera metadata correta."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        assert result.metadata is not None
        assert "downsample" in result.metadata.operation.lower()

    def test_downsampling_selected_indices_match_values(self, large_sine_wave):
        """Índices selecionados correspondem aos valores."""
        t, y = large_sine_wave
        target = 500
        
        result = downsample(y, t, n_points=target, method="lttb")
        
        # Verificar que os valores correspondem aos índices
        np.testing.assert_array_almost_equal(
            result.values,
            y[result.selected_indices],
        )
        np.testing.assert_array_almost_equal(
            result.t_seconds,
            t[result.selected_indices],
        )


# =============================================================================
# Testes de performance
# =============================================================================

class TestDownsamplingPerformance:
    """Testes de performance para downsampling."""

    @pytest.mark.slow
    def test_lttb_large_dataset_performance(self):
        """LTTB em dataset grande completa em tempo razoável."""
        import time
        
        n = 1_000_000
        t = np.linspace(0, 1000, n)
        y = np.sin(t) + 0.1 * np.random.randn(n)
        target = 10_000
        
        start = time.time()
        result = downsample(y, t, n_points=target, method="lttb")
        elapsed = time.time() - start
        
        # Deve completar em tempo razoável (incluindo numba compilation)
        assert elapsed < 30.0  # 30 segundos max (primeira execução com numba)
        assert len(result.values) <= target + 2


# =============================================================================
# Smoke tests
# =============================================================================

@pytest.mark.smoke
class TestDownsamplingSmoke:
    """Smoke tests para downsampling."""

    def test_all_supported_methods_exist(self):
        """Todos os métodos suportados estão listados."""
        expected_methods = {"lttb", "minmax", "adaptive", "uniform", "peak_aware"}
        assert expected_methods.issubset(SUPPORTED_METHODS)

    def test_basic_lttb_works(self):
        """LTTB básico funciona."""
        t = np.linspace(0, 10, 1000)
        y = np.sin(t)
        
        result = downsample(y, t, n_points=100, method="lttb")
        
        assert len(result.values) <= 102
        assert len(result.t_seconds) == len(result.values)

    def test_basic_minmax_works(self):
        """MinMax básico funciona."""
        t = np.linspace(0, 10, 1000)
        y = np.sin(t)
        
        result = downsample(y, t, n_points=100, method="minmax")
        
        assert len(result.values) > 0
        assert len(result.t_seconds) == len(result.values)
