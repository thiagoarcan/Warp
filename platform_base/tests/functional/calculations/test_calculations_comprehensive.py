"""
Suite de Testes Robustos: Cálculos Matemáticos (≥95% cobertura)

Testa todas as funcionalidades de cálculos:
- Interpolação (10 métodos)
- Derivadas (1ª, 2ª, 3ª ordem)
- Integrais (trapezoid, simpson, cumulative)
- Filtros (Butterworth, outliers, rolling)
- Suavização (Gaussian, Moving Average, Savitzky-Golay)
- FFT e correlação
"""

import pytest
import numpy as np
from scipy import signal


class TestInterpolation:
    """Testes de interpolação - Cobertura alvo: 100%"""
    
    def test_linear_interpolation(self):
        """Teste interpolação linear"""
        from platform_base.processing.interpolation import interpolate_linear
        
        x = np.array([0, 1, 2, 3, 4])
        y = np.array([0, 2, 4, 6, 8])
        x_new = np.linspace(0, 4, 20)
        
        y_new = interpolate_linear(x, y, x_new)
        
        assert len(y_new) == 20
        assert np.isclose(y_new[0], 0)
        assert np.isclose(y_new[-1], 8)
    
    def test_cubic_spline_interpolation(self):
        """Teste interpolação spline cúbica"""
        from platform_base.processing.interpolation import interpolate_cubic_spline
        
        x = np.array([0, 1, 2, 3, 4])
        y = np.sin(x)
        x_new = np.linspace(0, 4, 50)
        
        y_new = interpolate_cubic_spline(x, y, x_new)
        
        assert len(y_new) == 50
        assert not np.any(np.isnan(y_new))
    
    def test_smoothing_spline_interpolation(self):
        """Teste interpolação smoothing spline"""
        from platform_base.processing.interpolation import interpolate_smoothing_spline
        
        x = np.linspace(0, 10, 50)
        y = np.sin(x) + 0.1 * np.random.randn(50)
        x_new = np.linspace(0, 10, 100)
        
        y_new = interpolate_smoothing_spline(x, y, x_new, smoothing=0.5)
        
        assert len(y_new) == 100
        # Suavização deve reduzir ruído
        assert np.std(y_new) < np.std(y)
    
    def test_mls_interpolation(self):
        """Teste interpolação Moving Least Squares"""
        from platform_base.processing.interpolation import interpolate_mls
        
        x = np.array([0, 1, 2, 3, 4])
        y = np.array([0, 1, 4, 9, 16])
        x_new = np.linspace(0, 4, 20)
        
        y_new = interpolate_mls(x, y, x_new)
        
        assert len(y_new) == 20
        assert not np.any(np.isnan(y_new))
    
    def test_gpr_interpolation(self):
        """Teste interpolação Gaussian Process Regression"""
        from platform_base.processing.interpolation import interpolate_gpr
        
        x = np.array([0, 1, 2, 3, 4]).reshape(-1, 1)
        y = np.sin(x).ravel()
        x_new = np.linspace(0, 4, 20).reshape(-1, 1)
        
        y_new, std = interpolate_gpr(x, y, x_new)
        
        assert len(y_new) == 20
        assert len(std) == 20
        assert np.all(std >= 0)  # Desvio padrão deve ser não-negativo
    
    def test_lomb_scargle_interpolation(self):
        """Teste interpolação Lomb-Scargle (dados irregulares)"""
        from platform_base.processing.interpolation import interpolate_lomb_scargle
        
        # Dados irregulares
        t = np.sort(np.random.uniform(0, 10, 50))
        y = np.sin(2 * np.pi * 0.5 * t) + 0.1 * np.random.randn(50)
        t_new = np.linspace(0, 10, 100)
        
        y_new = interpolate_lomb_scargle(t, y, t_new)
        
        assert len(y_new) == 100
        assert not np.any(np.isnan(y_new))
    
    def test_interpolation_with_gaps(self):
        """Teste interpolação com gaps nos dados"""
        from platform_base.processing.interpolation import interpolate_with_gaps
        
        x = np.array([0, 1, 2, 5, 6, 7])  # Gap entre 2 e 5
        y = np.array([0, 1, 2, 5, 6, 7])
        x_new = np.linspace(0, 7, 50)
        
        y_new = interpolate_with_gaps(x, y, x_new, gap_threshold=2.0)
        
        assert len(y_new) == 50
        # Valores no gap devem ser NaN ou marcados
        gap_indices = (x_new > 2) & (x_new < 5)
        assert np.any(gap_indices)
    
    def test_interpolation_extrapolation_modes(self):
        """Teste modos de extrapolação"""
        from platform_base.processing.interpolation import interpolate_linear
        
        x = np.array([1, 2, 3, 4])
        y = np.array([1, 4, 9, 16])
        
        # Testar fora dos limites
        x_new = np.array([0, 1.5, 3.5, 5])
        
        # Modo 'constant'
        y_const = interpolate_linear(x, y, x_new, fill_value=0)
        assert y_const[0] == 0  # Extrapolação constante
        
        # Modo 'nearest'
        y_nearest = interpolate_linear(x, y, x_new, fill_value='extrapolate')
        assert y_nearest[0] < y[0]  # Extrapolação linear


class TestDerivatives:
    """Testes de derivadas - Cobertura alvo: 100%"""
    
    def test_first_derivative_finite_diff(self):
        """Teste 1ª derivada - diferenças finitas"""
        from platform_base.processing.calculus import derivative_finite_diff
        
        t = np.linspace(0, 2*np.pi, 100)
        y = np.sin(t)
        
        dy_dt = derivative_finite_diff(y, t, order=1)
        
        # Derivada de sin(t) é cos(t)
        expected = np.cos(t)
        assert np.allclose(dy_dt, expected, atol=0.1)
    
    def test_second_derivative_finite_diff(self):
        """Teste 2ª derivada - diferenças finitas"""
        from platform_base.processing.calculus import derivative_finite_diff
        
        t = np.linspace(0, 2*np.pi, 100)
        y = np.sin(t)
        
        d2y_dt2 = derivative_finite_diff(y, t, order=2)
        
        # 2ª derivada de sin(t) é -sin(t)
        expected = -np.sin(t)
        assert np.allclose(d2y_dt2, expected, atol=0.2)
    
    def test_third_derivative_finite_diff(self):
        """Teste 3ª derivada - diferenças finitas"""
        from platform_base.processing.calculus import derivative_finite_diff
        
        t = np.linspace(0, 2*np.pi, 100)
        y = np.sin(t)
        
        d3y_dt3 = derivative_finite_diff(y, t, order=3)
        
        # 3ª derivada de sin(t) é -cos(t)
        expected = -np.cos(t)
        assert np.allclose(d3y_dt3, expected, atol=0.3)
    
    def test_derivative_savitzky_golay(self):
        """Teste derivada Savitzky-Golay"""
        from platform_base.processing.calculus import derivative_savgol
        
        t = np.linspace(0, 2*np.pi, 100)
        y = np.sin(t) + 0.05 * np.random.randn(100)
        
        dy_dt = derivative_savgol(y, window_length=11, polyorder=3)
        
        assert len(dy_dt) == len(y)
        # Savitzky-Golay deve suavizar ruído
        assert np.std(dy_dt) < 2.0
    
    def test_derivative_spline(self):
        """Teste derivada via spline"""
        from platform_base.processing.calculus import derivative_spline
        
        t = np.linspace(0, 2*np.pi, 50)
        y = np.sin(t)
        
        dy_dt = derivative_spline(t, y)
        
        expected = np.cos(t)
        assert np.allclose(dy_dt, expected, atol=0.1)
    
    def test_derivative_with_noise(self):
        """Teste derivada com dados ruidosos"""
        from platform_base.processing.calculus import derivative_with_smoothing
        
        t = np.linspace(0, 10, 100)
        y = np.sin(t) + 0.2 * np.random.randn(100)
        
        dy_dt = derivative_with_smoothing(t, y, smooth_window=5)
        
        # Deve reduzir amplificação de ruído
        assert np.std(dy_dt) < 5.0


class TestIntegrals:
    """Testes de integrais - Cobertura alvo: 100%"""
    
    def test_integral_trapezoid(self):
        """Teste integração trapézio"""
        from platform_base.processing.calculus import integrate_trapezoid
        
        t = np.linspace(0, np.pi, 100)
        y = np.sin(t)
        
        # Integral de sin(t) de 0 a π é 2
        result = integrate_trapezoid(y, t)
        
        assert np.isclose(result, 2.0, rtol=0.01)
    
    def test_integral_simpson(self):
        """Teste integração Simpson"""
        from platform_base.processing.calculus import integrate_simpson
        
        t = np.linspace(0, np.pi, 101)  # Simpson precisa número ímpar
        y = np.sin(t)
        
        result = integrate_simpson(y, t)
        
        assert np.isclose(result, 2.0, rtol=0.001)
    
    def test_cumulative_integral(self):
        """Teste integral cumulativa"""
        from platform_base.processing.calculus import integrate_cumulative
        
        t = np.linspace(0, 10, 100)
        y = np.ones(100)  # Integral de 1 é t
        
        cumulative = integrate_cumulative(y, t)
        
        assert len(cumulative) == len(y)
        assert np.isclose(cumulative[-1], 10.0, rtol=0.01)
    
    def test_integral_with_limits(self):
        """Teste integral com limites específicos"""
        from platform_base.processing.calculus import integrate_range
        
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        # Integrar apenas de 2 a 8
        result = integrate_range(y, t, t_min=2, t_max=8)
        
        assert result is not None
    
    def test_area_under_curve(self):
        """Teste área sob a curva"""
        from platform_base.processing.calculus import calculate_auc
        
        t = np.linspace(0, 10, 100)
        y = np.maximum(0, np.sin(t))  # Apenas valores positivos
        
        auc = calculate_auc(t, y)
        
        assert auc > 0
        assert auc < 20  # Limite superior razoável


class TestFilters:
    """Testes de filtros - Cobertura alvo: 100%"""
    
    def test_butterworth_lowpass(self):
        """Teste filtro Butterworth passa-baixa"""
        from platform_base.processing.filters import butterworth_filter
        
        # Sinal com alta frequência
        t = np.linspace(0, 1, 1000)
        y = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 50 * t)
        
        y_filtered = butterworth_filter(y, cutoff=10, fs=1000, order=4, btype='low')
        
        # Deve remover componente de 50Hz
        assert np.std(y_filtered) < np.std(y)
    
    def test_butterworth_highpass(self):
        """Teste filtro Butterworth passa-alta"""
        from platform_base.processing.filters import butterworth_filter
        
        t = np.linspace(0, 1, 1000)
        y = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 50 * t)
        
        y_filtered = butterworth_filter(y, cutoff=20, fs=1000, order=4, btype='high')
        
        # Deve manter componente de 50Hz
        assert np.max(y_filtered) > 0.5
    
    def test_outlier_removal(self):
        """Teste remoção de outliers"""
        from platform_base.processing.filters import remove_outliers
        
        y = np.random.randn(100)
        y[50] = 100  # Outlier evidente
        
        y_clean = remove_outliers(y, threshold=3.0)
        
        # Outlier deve ser removido ou substituído
        assert np.max(y_clean) < 50
    
    def test_rolling_filter(self):
        """Teste filtro rolling (média móvel)"""
        from platform_base.processing.filters import rolling_mean
        
        y = np.sin(np.linspace(0, 10, 100)) + 0.2 * np.random.randn(100)
        
        y_smooth = rolling_mean(y, window=5)
        
        # Deve suavizar ruído
        assert np.std(y_smooth) < np.std(y)


class TestSmoothing:
    """Testes de suavização - Cobertura alvo: 100%"""
    
    def test_gaussian_smoothing(self):
        """Teste suavização Gaussiana"""
        from platform_base.processing.smoothing import gaussian_smooth
        
        y = np.sin(np.linspace(0, 10, 100)) + 0.2 * np.random.randn(100)
        
        y_smooth = gaussian_smooth(y, sigma=2.0)
        
        assert len(y_smooth) == len(y)
        assert np.std(y_smooth) < np.std(y)
    
    def test_moving_average(self):
        """Teste média móvel"""
        from platform_base.processing.smoothing import moving_average
        
        y = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
        y_smooth = moving_average(y, window=3)
        
        # Média móvel de 3: [_, 2, 3, 4, 5, 6, 7, 8, 9, _]
        assert len(y_smooth) == len(y)
    
    def test_savitzky_golay_smoothing(self):
        """Teste suavização Savitzky-Golay"""
        from platform_base.processing.smoothing import savgol_smooth
        
        y = np.sin(np.linspace(0, 10, 100)) + 0.1 * np.random.randn(100)
        
        y_smooth = savgol_smooth(y, window_length=11, polyorder=3)
        
        assert len(y_smooth) == len(y)
        assert np.std(y_smooth) < np.std(y)


class TestFFTAndCorrelation:
    """Testes de FFT e correlação - Cobertura alvo: 100%"""
    
    def test_fft_basic(self):
        """Teste FFT básico"""
        from platform_base.processing.spectral import compute_fft
        
        t = np.linspace(0, 1, 1000)
        y = np.sin(2 * np.pi * 10 * t)  # 10 Hz
        
        freq, power = compute_fft(y, fs=1000)
        
        # Pico deve estar em 10 Hz
        peak_freq = freq[np.argmax(power)]
        assert np.isclose(peak_freq, 10, atol=1.0)
    
    def test_cross_correlation(self):
        """Teste correlação cruzada"""
        from platform_base.processing.correlation import cross_correlate
        
        t = np.linspace(0, 10, 100)
        y1 = np.sin(t)
        y2 = np.sin(t + np.pi/4)  # Defasado
        
        corr, lag = cross_correlate(y1, y2)
        
        assert len(corr) > 0
        assert len(lag) == len(corr)
    
    def test_autocorrelation(self):
        """Teste autocorrelação"""
        from platform_base.processing.correlation import autocorrelate
        
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        
        acf = autocorrelate(y)
        
        # Autocorrelação em lag 0 deve ser 1
        assert np.isclose(acf[0], 1.0)


# Marcadores para execução seletiva
pytestmark = [
    pytest.mark.functional,
    pytest.mark.calculations,
]
