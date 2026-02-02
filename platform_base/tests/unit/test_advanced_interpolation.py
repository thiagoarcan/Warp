"""Tests for advanced interpolation methods (MLS, GPR, Lomb-Scargle)"""
import warnings
import numpy as np
import pytest

from platform_base.processing.interpolation import interpolate, SUPPORTED_METHODS


def _check_sklearn_available():
    """Check if scikit-learn is available"""
    try:
        from sklearn.gaussian_process import GaussianProcessRegressor
        return True
    except ImportError:
        return False


class TestMLSInterpolation:
    """Tests for Moving Least Squares interpolation"""
    
    def test_mls_fills_missing_values(self):
        """MLS should fill NaN values"""
        t = np.linspace(0, 10, 100)
        values = np.sin(t)
        values[20:25] = np.nan  # Create gap
        
        result = interpolate(values, t, "mls", {"degree": 2})
        
        assert np.all(np.isfinite(result.values))
        assert result.interpolation_info.is_interpolated_mask[20:25].all()
    
    def test_mls_preserves_original_values(self):
        """MLS should not modify original (non-NaN) values"""
        t = np.linspace(0, 10, 50)
        values = np.sin(t)
        values[10:15] = np.nan
        original_mask = ~np.isnan(values)
        original_values = values[original_mask].copy()
        
        result = interpolate(values, t, "mls", {"degree": 2})
        
        np.testing.assert_allclose(
            result.values[original_mask],
            original_values,
            rtol=1e-10
        )
    
    def test_mls_with_different_degrees(self):
        """MLS should work with different polynomial degrees"""
        t = np.linspace(0, 10, 100)
        values = t ** 2  # Quadratic
        values[50] = np.nan
        
        for degree in [1, 2, 3]:
            result = interpolate(values, t, "mls", {"degree": degree})
            assert np.all(np.isfinite(result.values))


class TestGPRInterpolation:
    """Tests for Gaussian Process Regression interpolation"""
    
    @pytest.mark.skipif(
        not _check_sklearn_available(),
        reason="scikit-learn not available"
    )
    def test_gpr_fills_missing_values(self):
        """GPR should fill NaN values"""
        # Filter sklearn warnings if sklearn is available
        if _check_sklearn_available():
            warnings.filterwarnings("ignore", category=Warning, module="sklearn")
        
        t = np.linspace(0, 10, 50)
        values = np.sin(t)
        values[20:25] = np.nan
        
        result = interpolate(values, t, "gpr", {
            "max_train_points": 50,
            "n_restarts": 1
        })
        
        assert np.all(np.isfinite(result.values))
        assert result.interpolation_info.is_interpolated_mask[20:25].all()
    
    @pytest.mark.skipif(
        not _check_sklearn_available(),
        reason="scikit-learn not available"
    )
    def test_gpr_provides_uncertainty(self):
        """GPR metadata should include uncertainty estimate"""
        # Filter sklearn warnings if sklearn is available
        if _check_sklearn_available():
            warnings.filterwarnings("ignore", category=Warning, module="sklearn")
        
        t = np.linspace(0, 5, 30)
        values = np.sin(t)
        values[10] = np.nan
        
        result = interpolate(values, t, "gpr", {
            "max_train_points": 30,
            "n_restarts": 1
        })
        
        assert "uncertainty_std" in result.metadata.params
    
    @pytest.mark.skipif(
        not _check_sklearn_available(),
        reason="scikit-learn not available"
    )
    def test_gpr_with_matern_kernel(self):
        """GPR should work with Matern kernel"""
        # Filter sklearn warnings if sklearn is available
        if _check_sklearn_available():
            warnings.filterwarnings("ignore", category=Warning, module="sklearn")
        
        t = np.linspace(0, 5, 30)
        values = np.sin(t)
        values[15] = np.nan
        
        result = interpolate(values, t, "gpr", {
            "kernel_type": "matern",
            "max_train_points": 30,
            "n_restarts": 1
        })
        
        assert np.all(np.isfinite(result.values))


class TestLombScargleInterpolation:
    """Tests for Lomb-Scargle spectral interpolation"""
    
    def test_lomb_scargle_fills_missing_values(self):
        """Lomb-Scargle should fill NaN values"""
        t = np.linspace(0, 10, 100)
        # Pure sine wave - ideal for spectral methods
        values = np.sin(2 * np.pi * t)
        values[40:50] = np.nan
        
        result = interpolate(values, t, "lomb_scargle_spectral", {
            "n_frequencies": 50,
            "n_components": 10
        })
        
        assert np.all(np.isfinite(result.values))
        assert result.interpolation_info.is_interpolated_mask[40:50].all()
    
    def test_lomb_scargle_with_irregular_sampling(self):
        """Lomb-Scargle should handle irregular time sampling"""
        # Irregular time points
        t = np.sort(np.random.uniform(0, 10, 100))
        values = np.sin(2 * np.pi * 0.5 * t)
        values[30:40] = np.nan
        
        result = interpolate(values, t, "lomb_scargle_spectral", {
            "n_frequencies": 50,
            "n_components": 10
        })
        
        assert np.all(np.isfinite(result.values))


class TestSupportedMethods:
    """Tests for method availability"""
    
    def test_all_methods_in_supported(self):
        """All methods should be listed in SUPPORTED_METHODS"""
        expected_methods = {
            "linear", "spline_cubic", "smoothing_spline", "resample_grid",
            "mls", "gpr", "lomb_scargle_spectral"
        }
        assert expected_methods == SUPPORTED_METHODS
    
    def test_unsupported_method_raises_error(self):
        """Unsupported method should raise InterpolationError"""
        from platform_base.utils.errors import InterpolationError
        
        t = np.linspace(0, 10, 100)
        values = np.sin(t)
        
        with pytest.raises(InterpolationError):
            interpolate(values, t, "nonexistent_method", {})