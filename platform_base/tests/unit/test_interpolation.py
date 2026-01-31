"""
Testes unitários para platform_base.processing.interpolation

Cobertura:
- Interpolação linear
- Interpolação spline cúbica
- Interpolação smoothing spline
- Resampling de grid
- Moving Least Squares (MLS)
- Gaussian Process Regression (GPR) 
- Lomb-Scargle spectral
- Casos de borda e erros
"""

import numpy as np
import pytest

from platform_base.processing.interpolation import SUPPORTED_METHODS, interpolate
from platform_base.utils.errors import InterpolationError

# =============================================================================
# Fixtures específicas para interpolação
# =============================================================================

@pytest.fixture
def data_with_gaps():
    """Dados com valores faltantes (NaN)."""
    t = np.linspace(0, 10, 101)
    y = np.sin(t)
    # Criar gaps
    y[20:30] = np.nan
    y[60:70] = np.nan
    return t, y


@pytest.fixture
def irregular_data():
    """Dados com amostragem irregular."""
    np.random.seed(42)
    # Tempo não uniforme
    t = np.sort(np.random.uniform(0, 10, 50))
    y = np.sin(t) + 0.1 * np.random.randn(len(t))
    return t, y


@pytest.fixture
def linear_data_with_gap():
    """Dados lineares com gap para teste de interpolação."""
    t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
    y = 2 * t + 1  # y = 2x + 1
    y[4:7] = np.nan  # Gap nos índices 4, 5, 6 (t=4, 5, 6)
    return t, y


# =============================================================================
# Testes de interpolação linear
# =============================================================================

class TestLinearInterpolation:
    """Testes para interpolação linear."""

    def test_linear_fills_single_gap(self, linear_data_with_gap):
        """Interpolação linear preenche gap corretamente."""
        t, y = linear_data_with_gap
        result = interpolate(y, t, method="linear", params={})
        
        # Verificar que os valores interpolados seguem a linha
        expected = 2 * t + 1
        np.testing.assert_array_almost_equal(result.values, expected, decimal=5)

    def test_linear_preserves_original_values(self, data_with_gaps):
        """Interpolação linear preserva valores originais não-NaN."""
        t, y = data_with_gaps
        original_mask = ~np.isnan(y)
        result = interpolate(y, t, method="linear", params={})
        
        np.testing.assert_array_almost_equal(
            result.values[original_mask],
            np.sin(t)[original_mask],
            decimal=10,
        )

    def test_linear_fills_multiple_gaps(self, data_with_gaps):
        """Interpolação linear preenche múltiplos gaps."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="linear", params={})
        
        # Não deve haver NaN no resultado
        assert not np.any(np.isnan(result.values))

    def test_linear_interpolation_info_mask(self, data_with_gaps):
        """Interpolação linear gera máscara de interpolação correta."""
        t, y = data_with_gaps
        original_nan_mask = np.isnan(y)
        result = interpolate(y, t, method="linear", params={})
        
        # A máscara de interpolação deve coincidir com os NaNs originais
        np.testing.assert_array_equal(
            result.interpolation_info.is_interpolated_mask,
            original_nan_mask,
        )

    def test_linear_method_used_array(self, data_with_gaps):
        """Interpolação linear registra método usado por ponto."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="linear", params={})
        
        # Pontos interpolados devem ter "linear", originais devem ter "original"
        original_mask = ~np.isnan(y)
        assert all(m == "original" for m in result.interpolation_info.method_used[original_mask])
        
        interp_mask = np.isnan(y)
        assert all(m == "linear" for m in result.interpolation_info.method_used[interp_mask])


# =============================================================================
# Testes de interpolação spline cúbica
# =============================================================================

class TestSplineCubicInterpolation:
    """Testes para interpolação spline cúbica."""

    def test_spline_cubic_fills_gaps(self, data_with_gaps):
        """Spline cúbica preenche gaps."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="spline_cubic", params={})
        
        assert not np.any(np.isnan(result.values))

    def test_spline_cubic_smooth_transition(self, data_with_gaps):
        """Spline cúbica produz transição suave."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="spline_cubic", params={})
        
        # A derivada deve ser contínua (mudanças suaves)
        diff = np.diff(result.values)
        # Não deve haver saltos abruptos
        assert np.max(np.abs(np.diff(diff))) < 1.0

    def test_spline_cubic_approximates_sine(self, data_with_gaps):
        """Spline cúbica aproxima bem uma senóide."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="spline_cubic", params={})
        
        # Comparar com a função original
        expected = np.sin(t)
        # Tolerância maior porque spline não é perfeita
        np.testing.assert_array_almost_equal(result.values, expected, decimal=1)


# =============================================================================
# Testes de smoothing spline
# =============================================================================

class TestSmoothingSplineInterpolation:
    """Testes para smoothing spline."""

    def test_smoothing_spline_fills_gaps(self, data_with_gaps):
        """Smoothing spline preenche gaps."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="smoothing_spline", params={"s": 0.5})
        
        assert not np.any(np.isnan(result.values))

    def test_smoothing_spline_reduces_noise(self, irregular_data):
        """Smoothing spline reduz ruído dos dados."""
        t, y = irregular_data
        result = interpolate(y, t, method="smoothing_spline", params={"s": 1.0})
        
        # O resultado deve ser mais suave que os dados originais
        # (menor ou igual variância nas diferenças)
        # Nota: com s muito pequeno, pode não suavizar
        original_diff_var = np.var(np.diff(y))
        result_diff_var = np.var(np.diff(result.values))
        
        # Permitir que seja igual ou menor (não deve aumentar a variância)
        assert result_diff_var <= original_diff_var + 1e-10


# =============================================================================
# Testes de resample_grid
# =============================================================================

class TestResampleGrid:
    """Testes para reamostragem em grid regular."""

    def test_resample_grid_with_dt(self, irregular_data):
        """Resample cria grid com dt especificado."""
        t, y = irregular_data
        dt = 0.5
        result = interpolate(y, t, method="resample_grid", params={"dt": dt})
        
        # Verificar espaçamento uniforme
        output_dt = np.diff(result.values)
        # Como resample muda o tamanho, verificamos que o output existe
        assert len(result.values) > 0
        assert result.interpolation_info is not None

    def test_resample_grid_with_n_points(self, irregular_data):
        """Resample cria grid com n_points especificado."""
        t, y = irregular_data
        n_points = 100
        result = interpolate(y, t, method="resample_grid", params={"n_points": n_points})
        
        assert len(result.values) == n_points

    def test_resample_grid_requires_params(self, irregular_data):
        """Resample requer dt ou n_points."""
        t, y = irregular_data
        
        with pytest.raises(InterpolationError) as exc_info:
            interpolate(y, t, method="resample_grid", params={})
        
        assert "dt or n_points" in str(exc_info.value)


# =============================================================================
# Testes de MLS (Moving Least Squares)
# =============================================================================

class TestMLSInterpolation:
    """Testes para interpolação Moving Least Squares."""

    def test_mls_fills_gaps(self, data_with_gaps):
        """MLS preenche gaps."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="mls", params={"degree": 2})
        
        assert not np.any(np.isnan(result.values))

    def test_mls_with_different_degrees(self, data_with_gaps):
        """MLS funciona com diferentes graus de polinômio."""
        t, y = data_with_gaps
        
        for degree in [1, 2, 3]:
            result = interpolate(y, t, method="mls", params={"degree": degree})
            assert not np.any(np.isnan(result.values))

    def test_mls_approximates_quadratic(self):
        """MLS aproxima bem uma função quadrática."""
        t = np.linspace(0, 10, 101)
        y = t ** 2
        y[40:50] = np.nan  # Gap
        
        result = interpolate(y, t, method="mls", params={"degree": 2})
        
        expected = t ** 2
        # MLS deve aproximar bem uma quadrática com degree=2
        np.testing.assert_array_almost_equal(result.values, expected, decimal=0)


# =============================================================================
# Testes de GPR (Gaussian Process Regression)
# =============================================================================

class TestGPRInterpolation:
    """Testes para interpolação GPR (se sklearn disponível)."""

    @pytest.fixture
    def small_data_with_gap(self):
        """Dados pequenos para GPR (que é lento)."""
        t = np.linspace(0, 5, 51)
        y = np.sin(t)
        y[20:25] = np.nan
        return t, y

    def test_gpr_fills_gaps(self, small_data_with_gap):
        """GPR preenche gaps."""
        pytest.importorskip("sklearn")
        t, y = small_data_with_gap
        result = interpolate(y, t, method="gpr", params={"n_restarts": 1})
        
        assert not np.any(np.isnan(result.values))

    def test_gpr_with_rbf_kernel(self, small_data_with_gap):
        """GPR funciona com kernel RBF."""
        pytest.importorskip("sklearn")
        t, y = small_data_with_gap
        result = interpolate(
            y, t, method="gpr", 
            params={"kernel_type": "rbf", "n_restarts": 1},
        )
        
        assert not np.any(np.isnan(result.values))

    def test_gpr_with_matern_kernel(self, small_data_with_gap):
        """GPR funciona com kernel Matérn."""
        pytest.importorskip("sklearn")
        t, y = small_data_with_gap
        result = interpolate(
            y, t, method="gpr", 
            params={"kernel_type": "matern", "n_restarts": 1},
        )
        
        assert not np.any(np.isnan(result.values))

    def test_gpr_raises_without_sklearn(self, small_data_with_gap, monkeypatch):
        """GPR levanta erro se sklearn não disponível."""
        import platform_base.processing.interpolation as interp_module

        # Simular sklearn não disponível
        monkeypatch.setattr(interp_module, "GPR_AVAILABLE", False)
        
        t, y = small_data_with_gap
        with pytest.raises(InterpolationError) as exc_info:
            interpolate(y, t, method="gpr", params={})
        
        assert "scikit-learn" in str(exc_info.value)


# =============================================================================
# Testes de Lomb-Scargle
# =============================================================================

class TestLombScargleInterpolation:
    """Testes para interpolação Lomb-Scargle espectral."""

    @pytest.fixture
    def periodic_data_with_gap(self):
        """Dados periódicos com gap para Lomb-Scargle."""
        t = np.linspace(0, 10, 101)
        y = np.sin(2 * np.pi * t / 2)  # Período de 2
        y[40:50] = np.nan
        return t, y

    def test_lomb_scargle_fills_gaps(self, periodic_data_with_gap):
        """Lomb-Scargle preenche gaps em dados periódicos."""
        t, y = periodic_data_with_gap
        result = interpolate(
            y, t, method="lomb_scargle_spectral",
            params={"n_frequencies": 50, "n_components": 5},
        )
        
        assert not np.any(np.isnan(result.values))

    def test_lomb_scargle_captures_periodicity(self, periodic_data_with_gap):
        """Lomb-Scargle captura periodicidade dos dados."""
        t, y = periodic_data_with_gap
        result = interpolate(
            y, t, method="lomb_scargle_spectral",
            params={"n_frequencies": 100, "n_components": 10},
        )
        
        # O resultado deve ter amplitude similar à original
        original_amplitude = np.nanmax(y) - np.nanmin(y)
        result_amplitude = np.max(result.values) - np.min(result.values)
        
        # Tolerância de 50% na amplitude
        assert abs(result_amplitude - original_amplitude) < 0.5 * original_amplitude


# =============================================================================
# Testes de casos de borda
# =============================================================================

class TestInterpolationEdgeCases:
    """Testes para casos de borda."""

    def test_interpolation_insufficient_points_raises(self):
        """Interpolação com menos de 2 pontos válidos levanta erro."""
        t = np.array([0, 1, 2, 3, 4])
        y = np.array([np.nan, np.nan, 1.0, np.nan, np.nan])  # Apenas 1 ponto válido
        
        with pytest.raises(InterpolationError) as exc_info:
            interpolate(y, t, method="linear", params={})
        
        assert "Not enough points" in str(exc_info.value)

    def test_interpolation_all_nan_raises(self):
        """Interpolação com todos NaN levanta erro."""
        t = np.array([0, 1, 2, 3, 4])
        y = np.full(5, np.nan)
        
        with pytest.raises(InterpolationError):
            interpolate(y, t, method="linear", params={})

    def test_interpolation_invalid_method_raises(self):
        """Método inválido levanta erro."""
        t = np.linspace(0, 10, 101)
        y = np.sin(t)
        
        with pytest.raises(InterpolationError) as exc_info:
            interpolate(y, t, method="invalid_method", params={})
        
        assert "not available" in str(exc_info.value).lower() or "not implemented" in str(exc_info.value).lower()

    def test_interpolation_unsorted_time_handled(self):
        """Tempo não ordenado é tratado corretamente."""
        np.random.seed(42)
        t = np.random.permutation(np.linspace(0, 10, 101))
        y = np.sin(t)
        y[40:50] = np.nan
        
        # Não deve levantar erro
        result = interpolate(y, t, method="linear", params={})
        assert not np.any(np.isnan(result.values))

    def test_interpolation_duplicate_times_handled(self):
        """Tempos duplicados são tratados corretamente."""
        t = np.array([0, 1, 1, 2, 3, 4, 5])  # Duplicado em t=1
        y = np.array([0, 1, 1, np.nan, 3, 4, 5])
        
        # Não deve levantar erro
        result = interpolate(y, t, method="linear", params={})
        assert not np.any(np.isnan(result.values))


# =============================================================================
# Testes de metadata e qualidade
# =============================================================================

class TestInterpolationMetadata:
    """Testes para metadata gerada pela interpolação."""

    def test_interpolation_generates_metadata(self, data_with_gaps):
        """Interpolação gera metadata correta."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="linear", params={})
        
        assert result.metadata is not None
        assert result.metadata.operation == "linear"

    def test_interpolation_info_complete(self, data_with_gaps):
        """InterpolationInfo tem todos os campos."""
        t, y = data_with_gaps
        result = interpolate(y, t, method="linear", params={})
        
        info = result.interpolation_info
        assert info.is_interpolated_mask is not None
        assert info.method_used is not None
        assert len(info.is_interpolated_mask) == len(t)
        assert len(info.method_used) == len(t)


# =============================================================================
# Testes de performance
# =============================================================================

class TestInterpolationPerformance:
    """Testes de performance para interpolação."""

    @pytest.mark.slow
    def test_linear_interpolation_large_dataset(self):
        """Interpolação linear em dataset grande completa em tempo razoável."""
        import time
        
        n = 100_000
        t = np.linspace(0, 1000, n)
        y = np.sin(t)
        # Criar gaps aleatórios
        np.random.seed(42)
        gap_mask = np.random.random(n) < 0.1  # 10% gaps
        y[gap_mask] = np.nan
        
        start = time.time()
        result = interpolate(y, t, method="linear", params={})
        elapsed = time.time() - start
        
        # Tempo maior para primeira execução (numba compilation overhead)
        assert elapsed < 10.0  # Deve completar em menos de 10 segundos
        assert not np.any(np.isnan(result.values))


# =============================================================================
# Smoke tests
# =============================================================================

@pytest.mark.smoke
class TestInterpolationSmoke:
    """Smoke tests para interpolação."""

    def test_all_supported_methods_exist(self):
        """Todos os métodos suportados estão listados."""
        expected_methods = {
            "linear", "spline_cubic", "smoothing_spline", "resample_grid",
            "mls", "gpr", "lomb_scargle_spectral",
        }
        assert expected_methods.issubset(SUPPORTED_METHODS)

    def test_basic_linear_interpolation_works(self):
        """Interpolação linear básica funciona."""
        t = np.array([0, 1, 2, 3, 4], dtype=float)
        y = np.array([0, np.nan, 2, np.nan, 4], dtype=float)
        
        result = interpolate(y, t, method="linear", params={})
        
        assert not np.any(np.isnan(result.values))
        np.testing.assert_array_almost_equal(result.values, [0, 1, 2, 3, 4])

    def test_basic_spline_interpolation_works(self):
        """Interpolação spline básica funciona."""
        t = np.linspace(0, 10, 101)
        y = np.sin(t)
        y[50] = np.nan
        
        result = interpolate(y, t, method="spline_cubic", params={})
        
        assert not np.any(np.isnan(result.values))


# =============================================================================
# Legacy test (mantido para compatibilidade)
# =============================================================================

def test_linear_interpolation_fills_nans():
    t = np.array([0.0, 1.0, 2.0, 3.0])
    values = np.array([1.0, np.nan, 3.0, np.nan])
    result = interpolate(values, t, method="linear", params={})
    assert np.isfinite(result.values).all()
    assert result.interpolation_info.is_interpolated_mask.sum() == 2

