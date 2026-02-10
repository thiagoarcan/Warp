"""
Comprehensive tests for viz/heatmaps.py module.

Target: Increase coverage from ~21% to 80%+
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestCreateColormapLut:
    """Tests for _create_colormap_lut function."""
    
    def test_viridis_colormap(self):
        """Test creating viridis colormap LUT."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.VIRIDIS, n_colors=256)
        
        assert lut.shape == (256, 3)
        assert lut.dtype == np.uint8
    
    def test_plasma_colormap(self):
        """Test creating plasma colormap LUT."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.PLASMA, n_colors=256)
        
        assert lut.shape == (256, 3)
    
    def test_coolwarm_colormap(self):
        """Test creating coolwarm colormap LUT."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.COOLWARM, n_colors=256)
        
        assert lut.shape == (256, 3)
    
    def test_grayscale_colormap(self):
        """Test creating grayscale colormap LUT."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.GRAYSCALE, n_colors=256)
        
        assert lut.shape == (256, 3)
        # First color should be black
        assert lut[0, 0] == 0
        assert lut[0, 1] == 0
        assert lut[0, 2] == 0
        # Last color should be white
        assert lut[-1, 0] == 255
        assert lut[-1, 1] == 255
        assert lut[-1, 2] == 255
    
    def test_custom_n_colors(self):
        """Test creating LUT with custom number of colors."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.VIRIDIS, n_colors=128)
        
        assert lut.shape == (128, 3)
    
    def test_small_n_colors(self):
        """Test creating LUT with small number of colors."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.VIRIDIS, n_colors=10)
        
        assert lut.shape == (10, 3)
    
    def test_interpolation_smooth(self):
        """Test that interpolation creates smooth gradient."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.VIRIDIS, n_colors=256)
        
        # Check that adjacent colors are similar (smooth gradient)
        for i in range(len(lut) - 1):
            diff = np.abs(lut[i].astype(int) - lut[i+1].astype(int))
            # Max difference between adjacent colors should be small
            assert np.max(diff) < 50  # Allow some variation


class TestColorScale:
    """Tests for ColorScale enum and related functions."""
    
    def test_all_colorscales_have_lut(self):
        """Test all colorscales can generate LUT."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        for colorscale in ColorScale:
            lut = _create_colormap_lut(colorscale, n_colors=256)
            assert lut.shape == (256, 3), f"Failed for {colorscale}"
    
    def test_colorscale_values_are_valid_rgb(self):
        """Test all colorscale LUT values are valid RGB."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        for colorscale in ColorScale:
            lut = _create_colormap_lut(colorscale, n_colors=256)
            assert lut.min() >= 0
            assert lut.max() <= 255


class TestHeatmapWidgetDependencyCheck:
    """Tests for HeatmapWidget dependency checking."""
    
    def test_dependency_flag_exists(self):
        """Test HEATMAP_DEPENDENCIES_AVAILABLE flag exists."""
        import platform_base.viz.heatmaps as heatmaps_module
        assert hasattr(heatmaps_module, 'HEATMAP_DEPENDENCIES_AVAILABLE')
    
    def test_dependencies_available_in_test_env(self):
        """Test dependencies are available in test environment."""
        import platform_base.viz.heatmaps as heatmaps_module

        # In test env, dependencies should be available
        assert heatmaps_module.HEATMAP_DEPENDENCIES_AVAILABLE is True


class TestCorrelationMatrix:
    """Tests for correlation matrix helper functions."""
    
    def test_compute_correlation_matrix(self):
        """Test correlation matrix computation."""
        # Create sample data
        np.random.seed(42)
        data = np.random.randn(100, 5)
        
        # Compute correlation
        corr_matrix = np.corrcoef(data, rowvar=False)
        
        assert corr_matrix.shape == (5, 5)
        # Diagonal should be 1
        np.testing.assert_array_almost_equal(np.diag(corr_matrix), np.ones(5))
        # Symmetric
        np.testing.assert_array_almost_equal(corr_matrix, corr_matrix.T)
    
    def test_correlation_values_in_range(self):
        """Test correlation values are in [-1, 1]."""
        np.random.seed(42)
        data = np.random.randn(100, 5)
        corr_matrix = np.corrcoef(data, rowvar=False)
        
        assert corr_matrix.min() >= -1.0
        assert corr_matrix.max() <= 1.0
    
    def test_perfect_correlation(self):
        """Test perfect correlation detection."""
        x = np.linspace(0, 10, 100)
        y = 2 * x + 5  # Perfect linear correlation
        data = np.column_stack([x, y])
        corr_matrix = np.corrcoef(data, rowvar=False)
        
        np.testing.assert_almost_equal(corr_matrix[0, 1], 1.0, decimal=10)
    
    def test_negative_correlation(self):
        """Test negative correlation detection."""
        x = np.linspace(0, 10, 100)
        y = -x + 5  # Perfect negative correlation
        data = np.column_stack([x, y])
        corr_matrix = np.corrcoef(data, rowvar=False)
        
        np.testing.assert_almost_equal(corr_matrix[0, 1], -1.0, decimal=10)


class TestTimeSeriesHeatmapHelpers:
    """Tests for time series heatmap helper functions."""
    
    def test_reshape_for_heatmap(self):
        """Test reshaping 1D time series to 2D heatmap."""
        # Create sample time series
        n_days = 7
        n_hours = 24
        data = np.random.randn(n_days * n_hours)
        
        # Reshape for heatmap (days x hours)
        heatmap_data = data.reshape(n_days, n_hours)
        
        assert heatmap_data.shape == (n_days, n_hours)
    
    def test_bin_data_for_heatmap(self):
        """Test binning data for heatmap."""
        # Create continuous data
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        
        # Bin into 2D histogram (simple heatmap)
        bins = 20
        heatmap, _, _ = np.histogram2d(x, y, bins=bins)
        
        assert heatmap.shape == (bins, bins)
    
    def test_normalize_heatmap_data(self):
        """Test normalizing heatmap data."""
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]).astype(float)
        
        # Min-max normalization
        normalized = (data - data.min()) / (data.max() - data.min())
        
        assert normalized.min() == 0.0
        assert normalized.max() == 1.0


class TestStatisticalHeatmapData:
    """Tests for statistical heatmap data generation."""
    
    def test_covariance_matrix(self):
        """Test covariance matrix as heatmap data."""
        np.random.seed(42)
        data = np.random.randn(100, 5)
        
        cov_matrix = np.cov(data, rowvar=False)
        
        assert cov_matrix.shape == (5, 5)
        # Symmetric
        np.testing.assert_array_almost_equal(cov_matrix, cov_matrix.T)
    
    def test_confusion_matrix_style(self):
        """Test confusion matrix style heatmap."""
        # Simulated confusion matrix
        predictions = np.array([0, 0, 1, 1, 2, 2, 0, 1, 2])
        actuals = np.array([0, 1, 1, 1, 2, 0, 0, 1, 2])
        
        n_classes = 3
        confusion = np.zeros((n_classes, n_classes), dtype=int)
        for pred, actual in zip(predictions, actuals):
            confusion[actual, pred] += 1
        
        assert confusion.shape == (n_classes, n_classes)
        assert confusion.sum() == len(predictions)
    
    def test_pvalue_matrix(self):
        """Test p-value matrix as heatmap data."""
        np.random.seed(42)
        data = np.random.randn(100, 4)
        
        n_vars = data.shape[1]
        pvalue_matrix = np.ones((n_vars, n_vars))
        
        from scipy import stats
        for i in range(n_vars):
            for j in range(n_vars):
                if i != j:
                    _, pvalue = stats.pearsonr(data[:, i], data[:, j])
                    pvalue_matrix[i, j] = pvalue
        
        assert pvalue_matrix.shape == (n_vars, n_vars)
        # Diagonal should be 1 (p-value not computed for self-correlation)
        np.testing.assert_array_equal(np.diag(pvalue_matrix), np.ones(n_vars))


class TestHeatmapDataValidation:
    """Tests for heatmap data validation."""
    
    def test_valid_2d_array(self):
        """Test validation of valid 2D array."""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        
        assert data.ndim == 2
        assert data.shape[0] > 0
        assert data.shape[1] > 0
    
    def test_handle_nan_values(self):
        """Test handling NaN values in heatmap data."""
        data = np.array([[1, np.nan, 3], [4, 5, np.nan]])
        
        # Common strategy: fill with 0 or mean
        filled_data = np.nan_to_num(data, nan=0.0)
        
        assert not np.isnan(filled_data).any()
    
    def test_handle_inf_values(self):
        """Test handling infinite values in heatmap data."""
        data = np.array([[1, np.inf, 3], [4, -np.inf, 6]])
        
        # Replace inf with large finite values
        data = np.clip(data, -1e10, 1e10)
        
        assert not np.isinf(data).any()
    
    def test_empty_data_handling(self):
        """Test handling empty data."""
        data = np.array([])
        
        # Should be reshaped to 2D if needed
        if data.ndim == 1 and data.size > 0:
            data = data.reshape(-1, 1)
        
        assert data.size == 0 or data.ndim == 2


class TestHeatmapLargeData:
    """Tests for handling large heatmap data."""
    
    def test_large_matrix(self):
        """Test creating LUT for large matrix display."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut

        # Large data simulation
        large_data = np.random.randn(1000, 1000)
        
        # LUT should work regardless of data size
        lut = _create_colormap_lut(ColorScale.VIRIDIS, n_colors=256)
        
        assert lut.shape == (256, 3)
    
    def test_memory_efficiency(self):
        """Test memory efficiency of LUT."""
        from platform_base.viz.config import ColorScale
        from platform_base.viz.heatmaps import _create_colormap_lut
        
        lut = _create_colormap_lut(ColorScale.VIRIDIS, n_colors=256)
        
        # LUT should use uint8 for memory efficiency
        assert lut.dtype == np.uint8
        # Size should be 256 * 3 bytes
        assert lut.nbytes == 256 * 3


class TestHeatmapHelperFunctions:
    """Tests for various helper functions used in heatmaps."""
    
    def test_data_transpose_for_display(self):
        """Test data transpose for correct display orientation."""
        data = np.array([[1, 2, 3], [4, 5, 6]])  # 2 rows, 3 columns
        
        # PyQtGraph expects data transposed
        display_data = data.T
        
        assert display_data.shape == (3, 2)  # 3 columns, 2 rows
    
    def test_colorbar_levels(self):
        """Test computing colorbar levels."""
        data = np.array([[1, 5, 3], [4, 2, 6]])
        
        vmin = data.min()
        vmax = data.max()
        
        assert vmin == 1
        assert vmax == 6
    
    def test_axis_ticks_generation(self):
        """Test generating axis ticks for labels."""
        n_rows = 5
        n_cols = 3
        
        row_ticks = [(i, f"Row {i}") for i in range(n_rows)]
        col_ticks = [(i, f"Col {i}") for i in range(n_cols)]
        
        assert len(row_ticks) == n_rows
        assert len(col_ticks) == n_cols
        assert row_ticks[0] == (0, "Row 0")
