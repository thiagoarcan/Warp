"""
Tests for figures_2d module - Category 2D Visualization.
"""
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest


class TestHexToQColor:
    """Tests for _hex_to_qcolor function."""
    
    def test_hex_with_hash(self, qapp):
        """Test converting hex color with hash."""
        from platform_base.viz.figures_2d import _hex_to_qcolor
        color = _hex_to_qcolor("#FF0000")
        assert color.red() == 255
        assert color.green() == 0
        assert color.blue() == 0
    
    def test_hex_without_hash(self, qapp):
        """Test converting hex color without hash."""
        from platform_base.viz.figures_2d import _hex_to_qcolor
        color = _hex_to_qcolor("00FF00")
        assert color.red() == 0
        assert color.green() == 255
        assert color.blue() == 0


class TestPrepareDataForPlotting:
    """Tests for _prepare_data_for_plotting function."""
    
    @pytest.fixture
    def prepare_data(self):
        """Get function."""
        from platform_base.viz.figures_2d import _prepare_data_for_plotting
        return _prepare_data_for_plotting
    
    def test_small_data_unchanged(self, prepare_data):
        """Test that small data passes through unchanged."""
        t = np.arange(100)
        values = np.sin(t)
        
        t_out, values_out = prepare_data(t, values, max_points=1000)
        
        assert len(t_out) == 100
        np.testing.assert_array_equal(t_out, t)
    
    def test_large_data_downsampled(self, prepare_data):
        """Test that large data is downsampled."""
        t = np.arange(200000)
        values = np.sin(t * 0.01)
        
        t_out, values_out = prepare_data(t, values, max_points=10000)
        
        assert len(t_out) <= 10000
        assert len(values_out) <= 10000
    
    def test_preserves_data_range(self, prepare_data):
        """Test that downsampling preserves data range."""
        t = np.arange(200000)
        values = np.sin(t * 0.01)
        
        t_out, values_out = prepare_data(t, values, max_points=10000)
        
        # Range should be approximately preserved
        assert t_out[0] == t[0]
        assert t_out[-1] == t[-1] or abs(t_out[-1] - t[-1]) < 10


class TestPlot2DWidgetBasics:
    """Basic tests for Plot2DWidget that don't require Qt."""
    
    def test_pyqtgraph_availability_check(self):
        """Test that module checks for pyqtgraph availability."""
        from platform_base.viz import figures_2d

        # Module should have PYQTGRAPH_AVAILABLE constant
        assert hasattr(figures_2d, 'PYQTGRAPH_AVAILABLE')
    
    def test_module_has_plot_widget_class(self):
        """Test that module defines Plot2DWidget class."""
        from platform_base.viz import figures_2d
        
        assert hasattr(figures_2d, 'Plot2DWidget')


class TestFigures2DFunctions:
    """Tests for standalone functions in figures_2d module."""
    
    def test_module_imports(self):
        """Test that module can be imported."""
        from platform_base.viz import figures_2d
        assert figures_2d is not None
    
    def test_has_hex_to_qcolor(self):
        """Test that module has _hex_to_qcolor function."""
        from platform_base.viz import figures_2d
        assert hasattr(figures_2d, '_hex_to_qcolor')
    
    def test_has_prepare_data_function(self):
        """Test that module has _prepare_data_for_plotting function."""
        from platform_base.viz import figures_2d
        assert hasattr(figures_2d, '_prepare_data_for_plotting')
    
    def test_has_logger(self):
        """Test that module has logger."""
        from platform_base.viz import figures_2d
        assert hasattr(figures_2d, 'logger')
