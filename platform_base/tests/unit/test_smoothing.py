"""
Testes unitários para platform_base.processing.smoothing

Cobertura:
- Savitzky-Golay filter
- Gaussian smoothing
- Median filter
- Lowpass filter (Butterworth)
- Casos de borda e erros
"""

import numpy as np
import pytest

from platform_base.processing.smoothing import smooth

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def noisy_sine():
    """Sinal senoidal com ruído."""
    np.random.seed(42)
    t = np.linspace(0, 10, 1001)
    y = np.sin(t) + 0.3 * np.random.randn(len(t))
    return t, y


@pytest.fixture
def step_signal():
    """Sinal com degraus (step function)."""
    n = 100
    y = np.zeros(n)
    y[25:75] = 1.0
    return y


@pytest.fixture
def impulse_signal():
    """Sinal com picos/outliers."""
    np.random.seed(42)
    n = 100
    y = np.random.randn(n) * 0.1
    # Adicionar alguns outliers
    y[30] = 5.0
    y[60] = -4.0
    y[80] = 3.0
    return y


# =============================================================================
# Testes Savitzky-Golay
# =============================================================================

class TestSavitzkyGolaySmoothing:
    """Testes para Savitzky-Golay filter."""

    def test_savgol_preserves_length(self, noisy_sine):
        """Savitzky-Golay preserva comprimento do array."""
        _, y = noisy_sine
        result = smooth(y, "savitzky_golay", {"window_length": 11, "polyorder": 3})
        assert len(result) == len(y)

    def test_savgol_reduces_noise(self, noisy_sine):
        """Savitzky-Golay reduz variância do ruído."""
        _, y = noisy_sine
        result = smooth(y, "savitzky_golay", {"window_length": 21, "polyorder": 3})
        
        # Variância do resultado deve ser menor que do original
        assert np.var(result) < np.var(y)

    def test_savgol_preserves_shape(self, noisy_sine):
        """Savitzky-Golay preserva forma geral do sinal."""
        t, y = noisy_sine
        result = smooth(y, "savitzky_golay", {"window_length": 11, "polyorder": 3})
        
        # Correlação com seno puro deve aumentar
        pure_sine = np.sin(t)
        original_corr = np.corrcoef(y, pure_sine)[0, 1]
        result_corr = np.corrcoef(result, pure_sine)[0, 1]
        
        assert result_corr > original_corr

    def test_savgol_with_different_window_sizes(self, noisy_sine):
        """Savitzky-Golay funciona com diferentes tamanhos de janela."""
        _, y = noisy_sine
        
        for window_length in [5, 11, 21, 31]:
            result = smooth(y, "savitzky_golay", {
                "window_length": window_length, 
                "polyorder": 2
            })
            assert len(result) == len(y)

    def test_savgol_with_different_orders(self, noisy_sine):
        """Savitzky-Golay funciona com diferentes ordens de polinômio."""
        _, y = noisy_sine
        
        for polyorder in [1, 2, 3, 4]:
            result = smooth(y, "savitzky_golay", {
                "window_length": 11, 
                "polyorder": polyorder
            })
            assert len(result) == len(y)

    def test_savgol_default_params(self, noisy_sine):
        """Savitzky-Golay usa parâmetros padrão quando não especificados."""
        _, y = noisy_sine
        result = smooth(y, "savitzky_golay", {})
        assert len(result) == len(y)


# =============================================================================
# Testes Gaussian Smoothing
# =============================================================================

class TestGaussianSmoothing:
    """Testes para smoothing gaussiano."""

    def test_gaussian_preserves_length(self, noisy_sine):
        """Gaussian preserva comprimento do array."""
        _, y = noisy_sine
        result = smooth(y, "gaussian", {"sigma": 2.0})
        assert len(result) == len(y)

    def test_gaussian_reduces_noise(self, noisy_sine):
        """Gaussian reduz variância do ruído."""
        _, y = noisy_sine
        result = smooth(y, "gaussian", {"sigma": 3.0})
        
        # Diferenças entre pontos consecutivos devem ser menores
        original_diff_var = np.var(np.diff(y))
        result_diff_var = np.var(np.diff(result))
        
        assert result_diff_var < original_diff_var

    def test_gaussian_higher_sigma_more_smooth(self, noisy_sine):
        """Maior sigma produz mais suavização."""
        _, y = noisy_sine
        
        result_1 = smooth(y, "gaussian", {"sigma": 1.0})
        result_5 = smooth(y, "gaussian", {"sigma": 5.0})
        
        # Com sigma maior, a variância das diferenças é menor
        diff_var_1 = np.var(np.diff(result_1))
        diff_var_5 = np.var(np.diff(result_5))
        
        assert diff_var_5 < diff_var_1

    def test_gaussian_default_sigma(self, noisy_sine):
        """Gaussian usa sigma padrão quando não especificado."""
        _, y = noisy_sine
        result = smooth(y, "gaussian", {})
        assert len(result) == len(y)


# =============================================================================
# Testes Median Filter
# =============================================================================

class TestMedianFilter:
    """Testes para median filter."""

    def test_median_preserves_length(self, impulse_signal):
        """Median filter preserva comprimento do array."""
        result = smooth(impulse_signal, "median", {"kernel_size": 5})
        assert len(result) == len(impulse_signal)

    def test_median_removes_outliers(self, impulse_signal):
        """Median filter remove outliers/picos."""
        result = smooth(impulse_signal, "median", {"kernel_size": 5})
        
        # O valor máximo absoluto deve ser menor após filtrar
        assert np.max(np.abs(result)) < np.max(np.abs(impulse_signal))

    def test_median_preserves_step(self, step_signal):
        """Median filter preserva edges de step function."""
        result = smooth(step_signal, "median", {"kernel_size": 3})
        
        # Após o transiente, deve manter ~1.0 no meio
        assert np.mean(result[30:70]) > 0.9

    def test_median_with_different_kernel_sizes(self, impulse_signal):
        """Median filter funciona com diferentes tamanhos de kernel."""
        for kernel_size in [3, 5, 7, 9]:
            result = smooth(impulse_signal, "median", {"kernel_size": kernel_size})
            assert len(result) == len(impulse_signal)

    def test_median_default_kernel_size(self, impulse_signal):
        """Median filter usa kernel_size padrão quando não especificado."""
        result = smooth(impulse_signal, "median", {})
        assert len(result) == len(impulse_signal)


# =============================================================================
# Testes Lowpass Filter (Butterworth)
# =============================================================================

class TestLowpassFilter:
    """Testes para lowpass filter."""

    def test_lowpass_preserves_length(self, noisy_sine):
        """Lowpass filter preserva comprimento do array."""
        _, y = noisy_sine
        result = smooth(y, "lowpass", {"cutoff": 0.1, "order": 3})
        assert len(result) == len(y)

    def test_lowpass_removes_high_frequency(self):
        """Lowpass filter remove alta frequência."""
        np.random.seed(42)
        t = np.linspace(0, 1, 1001)
        
        # Sinal composto: baixa freq + alta freq
        low_freq = np.sin(2 * np.pi * 2 * t)  # 2 Hz
        high_freq = 0.5 * np.sin(2 * np.pi * 50 * t)  # 50 Hz
        signal = low_freq + high_freq
        
        # Cutoff em 0.1 (freq normalizada) deve remover 50 Hz
        result = smooth(signal, "lowpass", {"cutoff": 0.1, "order": 3})
        
        # O resultado deve estar mais próximo da componente de baixa frequência
        correlation_original = np.corrcoef(signal, low_freq)[0, 1]
        correlation_filtered = np.corrcoef(result, low_freq)[0, 1]
        
        assert correlation_filtered > correlation_original

    def test_lowpass_with_different_orders(self, noisy_sine):
        """Lowpass filter funciona com diferentes ordens."""
        _, y = noisy_sine
        
        for order in [1, 2, 3, 4, 5]:
            result = smooth(y, "lowpass", {"cutoff": 0.1, "order": order})
            assert len(result) == len(y)

    def test_lowpass_default_params(self, noisy_sine):
        """Lowpass filter usa parâmetros padrão quando não especificados."""
        _, y = noisy_sine
        result = smooth(y, "lowpass", {})
        assert len(result) == len(y)


# =============================================================================
# Testes de casos de borda
# =============================================================================

class TestSmoothingEdgeCases:
    """Testes para casos de borda."""

    def test_invalid_method_raises(self):
        """Método inválido levanta ValueError."""
        values = np.random.randn(100)
        
        with pytest.raises(ValueError) as exc_info:
            smooth(values, "invalid_method", {})
        
        assert "Unknown smoothing method" in str(exc_info.value)

    def test_small_array_savgol(self):
        """Savitzky-Golay funciona com array pequeno (se window_length adequado)."""
        values = np.array([1, 2, 3, 4, 5])
        result = smooth(values, "savitzky_golay", {"window_length": 3, "polyorder": 1})
        assert len(result) == 5

    def test_small_array_gaussian(self):
        """Gaussian funciona com array pequeno."""
        values = np.array([1, 2, 3, 4, 5])
        result = smooth(values, "gaussian", {"sigma": 1.0})
        assert len(result) == 5

    def test_constant_array(self):
        """Smoothing de array constante retorna constante."""
        values = np.ones(100) * 5.0
        
        for method, params in [
            ("gaussian", {"sigma": 2.0}),
            ("savitzky_golay", {"window_length": 7, "polyorder": 2}),
            ("median", {"kernel_size": 5}),
        ]:
            result = smooth(values, method, params)
            np.testing.assert_array_almost_equal(result, values, decimal=5)


# =============================================================================
# Smoke tests
# =============================================================================

@pytest.mark.smoke
class TestSmoothingSmoke:
    """Smoke tests para smoothing."""

    def test_all_methods_work(self):
        """Todos os métodos funcionam com dados básicos."""
        values = np.random.randn(100)
        
        methods_params = [
            ("savitzky_golay", {"window_length": 7, "polyorder": 2}),
            ("gaussian", {"sigma": 1.0}),
            ("median", {"kernel_size": 5}),
            ("lowpass", {"cutoff": 0.1, "order": 3}),
        ]
        
        for method, params in methods_params:
            result = smooth(values, method, params)
            assert len(result) == len(values)
            assert np.all(np.isfinite(result))

    def test_basic_noise_reduction(self):
        """Smoothing básico reduz variação."""
        np.random.seed(42)
        values = np.random.randn(100)
        result = smooth(values, "gaussian", {"sigma": 3.0})
        
        assert np.var(result) < np.var(values)


# =============================================================================
# Legacy test (mantido para compatibilidade)
# =============================================================================

def test_smooth_returns_same_length():
    values = np.random.randn(100)
    result = smooth(values, "gaussian", {"sigma": 1.0})
    assert len(result) == len(values)

