"""
Testes unitários para algoritmo LTTB (Largest Triangle Three Buckets) conforme PRD.
"""
import pytest
import numpy as np

from platform_base.viz.base import _downsample_lttb, _detect_features


class TestLTTBDownsampling:
    """Testa algoritmo LTTB para downsampling inteligente"""
    
    def test_lttb_basic_downsampling(self):
        """Testa downsampling básico com LTTB"""
        # Create test data
        x = np.linspace(0, 10, 1000)
        y = np.sin(x) + 0.1 * np.random.randn(len(x))
        
        # Downsample to 100 points
        x_down, y_down = _downsample_lttb(x, y, max_points=100)
        
        # Verify output size
        assert len(x_down) == 100
        assert len(y_down) == 100
        
        # Verify endpoints are preserved
        assert x_down[0] == x[0]
        assert x_down[-1] == x[-1]
        assert y_down[0] == y[0]
        assert y_down[-1] == y[-1]
        
    def test_lttb_no_downsampling_needed(self):
        """Testa caso onde não é necessário downsampling"""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([1, 4, 2, 5, 3])
        
        x_down, y_down = _downsample_lttb(x, y, max_points=10)
        
        # Should return original data
        np.testing.assert_array_equal(x_down, x)
        np.testing.assert_array_equal(y_down, y)
        
    def test_lttb_extreme_downsampling(self):
        """Testa downsampling extremo para poucos pontos"""
        x = np.linspace(0, 10, 1000)
        y = np.sin(x)
        
        # Downsample to only 3 points
        x_down, y_down = _downsample_lttb(x, y, max_points=3)
        
        assert len(x_down) == 3
        assert len(y_down) == 3
        
        # Should include first and last points
        assert x_down[0] == x[0]
        assert x_down[-1] == x[-1]
        
    def test_feature_detection(self):
        """Testa detecção de features (peaks, valleys, edges)"""
        # Create signal with known features
        x = np.linspace(0, 4*np.pi, 100)
        y = np.sin(x)  # Has clear peaks and valleys
        
        peaks, valleys, edges = _detect_features(x, y)
        
        # Should detect some peaks and valleys in sine wave
        assert len(peaks) > 0
        assert len(valleys) > 0
        
        # Peaks should be at positive values
        assert all(y[peaks] > 0)
        # Valleys should be at negative values  
        assert all(y[valleys] < 0)
        
    def test_feature_preservation(self):
        """Testa preservação de features durante downsampling"""
        # Create signal with distinct peak
        x = np.linspace(0, 10, 1000)
        y = np.exp(-(x - 5)**2)  # Gaussian peak at x=5
        
        # Find the peak
        peak_idx = np.argmax(y)
        peak_value = y[peak_idx]
        
        # Downsample with feature preservation
        x_down, y_down = _downsample_lttb(x, y, max_points=50, preserve_features=["peaks"])
        
        # Peak value should be preserved (approximately)
        max_down_value = np.max(y_down)
        assert abs(max_down_value - peak_value) < 0.1
        
    def test_lttb_preserves_trend(self):
        """Testa se LTTB preserva tendências gerais dos dados"""
        # Create trending data
        x = np.linspace(0, 10, 1000)
        y = x + 0.1 * np.sin(10*x)  # Linear trend with small oscillations
        
        x_down, y_down = _downsample_lttb(x, y, max_points=100)
        
        # Check that overall trend is preserved
        # Linear regression should have similar slope
        orig_slope = np.polyfit(x, y, 1)[0]
        down_slope = np.polyfit(x_down, y_down, 1)[0]
        
        assert abs(orig_slope - down_slope) < 0.1
        
    def test_lttb_with_noise(self):
        """Testa LTTB com dados ruidosos"""
        # Create noisy signal
        x = np.linspace(0, 10, 1000)
        y_clean = np.sin(x)
        y_noisy = y_clean + 0.3 * np.random.randn(len(x))
        
        x_down, y_down = _downsample_lttb(x, y_noisy, max_points=100)
        
        # Should still capture general sine wave structure
        # (This is a qualitative test - we check basic properties)
        assert len(x_down) == 100
        assert np.min(y_down) < 0  # Should have negative values
        assert np.max(y_down) > 0  # Should have positive values
        
    def test_lttb_monotonic_data(self):
        """Testa LTTB com dados monotônicos"""
        x = np.linspace(0, 10, 1000)
        y = x**2  # Monotonic increasing
        
        x_down, y_down = _downsample_lttb(x, y, max_points=50)
        
        # Should maintain monotonic property
        assert all(np.diff(y_down) >= 0)  # Non-decreasing
        
    def test_lttb_constant_data(self):
        """Testa LTTB com dados constantes"""
        x = np.linspace(0, 10, 1000)
        y = np.ones_like(x) * 5  # Constant value
        
        x_down, y_down = _downsample_lttb(x, y, max_points=50)
        
        # Should return equally spaced points with same value
        assert len(x_down) == 50
        np.testing.assert_allclose(y_down, 5, rtol=1e-10)


class TestFeatureDetection:
    """Testes específicos para detecção de features"""
    
    def test_peak_detection_sine_wave(self):
        """Testa detecção de picos em onda senoidal"""
        x = np.linspace(0, 4*np.pi, 200)
        y = np.sin(x)
        
        peaks, valleys, edges = _detect_features(x, y)
        
        # Sine wave should have ~2 peaks and ~2 valleys in 2 cycles
        assert 1 <= len(peaks) <= 3
        assert 1 <= len(valleys) <= 3
        
    def test_no_features_in_flat_data(self):
        """Testa que dados planos não geram features"""
        x = np.linspace(0, 10, 100)
        y = np.ones_like(x)  # Flat line
        
        peaks, valleys, edges = _detect_features(x, y)
        
        assert len(peaks) == 0
        assert len(valleys) == 0
        
    def test_edge_detection_step_function(self):
        """Testa detecção de bordas em função degrau"""
        x = np.linspace(0, 10, 100)
        y = np.where(x > 5, 1, 0)  # Step function
        
        peaks, valleys, edges = _detect_features(x, y)
        
        # Should detect edge at transition
        assert len(edges) > 0
        
        # Edge should be near x=5
        edge_x_positions = x[edges]
        assert any(abs(pos - 5) < 0.5 for pos in edge_x_positions)