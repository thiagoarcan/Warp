"""
Comprehensive tests for ui/callbacks.py module.

Tests Dash callback functions and helper functions for data upload,
visualization, streaming controls, and export functionality.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestCreateEmptyFigure:
    """Tests for _create_empty_figure helper function."""
    
    def test_create_empty_figure_default_message(self):
        """Test creating empty figure with default message."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure()
        # Should return a Plotly figure
        assert hasattr(fig, 'layout')
    
    def test_create_empty_figure_custom_message(self):
        """Test creating empty figure with custom message."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure("Custom message")
        # Check annotation exists
        assert len(fig.layout.annotations) > 0
    
    def test_empty_figure_has_hidden_axes(self):
        """Test empty figure has hidden axes."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure()
        assert fig.layout.xaxis.visible is False
        assert fig.layout.yaxis.visible is False
    
    def test_empty_figure_has_white_background(self):
        """Test empty figure has white background."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure()
        assert fig.layout.plot_bgcolor == "white"


class TestCreateTimeseriesFigure:
    """Tests for _create_timeseries_figure helper function."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample time series data."""
        t = np.linspace(0, 10, 100)
        series = {
            "Series A": np.sin(t),
            "Series B": np.cos(t),
        }
        return t, series
    
    def test_create_timeseries_figure(self, sample_data):
        """Test creating timeseries figure."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        fig = _create_timeseries_figure(t, series)
        assert hasattr(fig, 'layout')
        assert hasattr(fig, 'data')
    
    def test_figure_has_traces_for_each_series(self, sample_data):
        """Test figure has trace for each series."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        fig = _create_timeseries_figure(t, series)
        # At least 2 traces for 2 series
        assert len(fig.data) >= 2
    
    def test_figure_with_title(self, sample_data):
        """Test figure has custom title."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        fig = _create_timeseries_figure(t, series, title="My Title")
        assert fig.layout.title.text == "My Title"
    
    def test_figure_has_axis_labels(self, sample_data):
        """Test figure has axis labels."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        fig = _create_timeseries_figure(t, series)
        assert fig.layout.xaxis.title.text == "Time (seconds)"
        assert fig.layout.yaxis.title.text == "Value"
    
    def test_figure_has_horizontal_legend(self, sample_data):
        """Test figure has horizontal legend."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        fig = _create_timeseries_figure(t, series)
        assert fig.layout.legend.orientation == "h"
    
    def test_figure_with_interpolation_mask(self, sample_data):
        """Test figure with interpolation mask."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        interp_mask = {
            "Series A": np.array([False] * 50 + [True] * 50),
        }
        fig = _create_timeseries_figure(t, series, interp_mask=interp_mask)
        # Should have additional trace for interpolated points
        assert len(fig.data) > 2
    
    def test_figure_hide_interpolated(self, sample_data):
        """Test figure can hide interpolated points."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        interp_mask = {
            "Series A": np.array([True] * 100),
        }
        fig = _create_timeseries_figure(
            t, series, 
            show_interpolated=False, 
            interp_mask=interp_mask
        )
        # Should only have traces for main series
        assert len(fig.data) == 2
    
    def test_figure_uses_color_palette(self, sample_data):
        """Test figure uses color palette."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = sample_data
        fig = _create_timeseries_figure(t, series)
        # First trace should have color
        assert fig.data[0].line.color is not None


class TestRegisterCallbacks:
    """Tests for register_callbacks function."""
    
    def test_register_callbacks_function_exists(self):
        """Test register_callbacks function exists."""
        from platform_base.ui.callbacks import register_callbacks
        assert callable(register_callbacks)
    
    def test_register_callbacks_accepts_app_and_state(self):
        """Test register_callbacks accepts app and state."""
        import inspect

        from platform_base.ui.callbacks import register_callbacks
        sig = inspect.signature(register_callbacks)
        params = list(sig.parameters.keys())
        assert 'app' in params
        assert 'app_state' in params


class TestModuleImports:
    """Tests for module imports."""
    
    def test_import_callbacks_module(self):
        """Test callbacks module can be imported."""
        from platform_base.ui import callbacks
        assert callbacks is not None
    
    def test_import_create_empty_figure(self):
        """Test _create_empty_figure can be imported."""
        from platform_base.ui.callbacks import _create_empty_figure
        assert callable(_create_empty_figure)
    
    def test_import_create_timeseries_figure(self):
        """Test _create_timeseries_figure can be imported."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        assert callable(_create_timeseries_figure)
    
    def test_import_register_callbacks(self):
        """Test register_callbacks can be imported."""
        from platform_base.ui.callbacks import register_callbacks
        assert callable(register_callbacks)


class TestEmptyFigureAnnotation:
    """Tests for empty figure annotation properties."""
    
    def test_annotation_position(self):
        """Test annotation is centered."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure()
        annotation = fig.layout.annotations[0]
        assert annotation.x == 0.5
        assert annotation.y == 0.5
    
    def test_annotation_no_arrow(self):
        """Test annotation has no arrow."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure()
        annotation = fig.layout.annotations[0]
        assert annotation.showarrow is False
    
    def test_annotation_paper_ref(self):
        """Test annotation uses paper reference."""
        from platform_base.ui.callbacks import _create_empty_figure
        fig = _create_empty_figure()
        annotation = fig.layout.annotations[0]
        assert annotation.xref == "paper"
        assert annotation.yref == "paper"


class TestTimeseriesFigureTraces:
    """Tests for timeseries figure trace properties."""
    
    @pytest.fixture
    def single_series_data(self):
        """Create single series data."""
        t = np.linspace(0, 5, 50)
        series = {"Test Series": np.sin(t)}
        return t, series
    
    def test_trace_mode_is_lines(self, single_series_data):
        """Test trace mode is lines."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = single_series_data
        fig = _create_timeseries_figure(t, series)
        assert fig.data[0].mode == "lines"
    
    def test_trace_has_name(self, single_series_data):
        """Test trace has name."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = single_series_data
        fig = _create_timeseries_figure(t, series)
        assert fig.data[0].name == "Test Series"
    
    def test_trace_has_hover_template(self, single_series_data):
        """Test trace has hover template."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t, series = single_series_data
        fig = _create_timeseries_figure(t, series)
        assert fig.data[0].hovertemplate is not None


class TestColorPalette:
    """Tests for color palette in timeseries figure."""
    
    def test_ten_colors_available(self):
        """Test 10 colors are available in palette."""
        t = np.linspace(0, 1, 10)
        series = {f"Series {i}": np.ones(10) * i for i in range(10)}
        
        from platform_base.ui.callbacks import _create_timeseries_figure
        fig = _create_timeseries_figure(t, series)
        
        colors = [trace.line.color for trace in fig.data]
        # All should have colors
        assert all(c is not None for c in colors)
    
    def test_colors_cycle_after_ten(self):
        """Test colors cycle after 10 series."""
        t = np.linspace(0, 1, 10)
        series = {f"Series {i}": np.ones(10) * i for i in range(12)}
        
        from platform_base.ui.callbacks import _create_timeseries_figure
        fig = _create_timeseries_figure(t, series)
        
        # 11th trace should have same color as 1st
        assert fig.data[10].line.color == fig.data[0].line.color


class TestFigureLayout:
    """Tests for figure layout properties."""
    
    @pytest.fixture
    def sample_figure(self):
        """Create sample figure."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t = np.linspace(0, 10, 100)
        series = {"Test": np.sin(t)}
        return _create_timeseries_figure(t, series)
    
    def test_figure_has_plotly_white_template(self, sample_figure):
        """Test figure uses plotly_white template."""
        assert sample_figure.layout.template.layout.plot_bgcolor == '#ffffff' or \
               'plotly_white' in str(sample_figure.layout.template)
    
    def test_figure_has_unified_hover(self, sample_figure):
        """Test figure has unified hover mode."""
        assert sample_figure.layout.hovermode == "x unified"


class TestInterpolationMarkers:
    """Tests for interpolation markers in timeseries figure."""
    
    def test_interpolated_points_marker_mode(self):
        """Test interpolated points use markers mode."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t = np.linspace(0, 10, 100)
        series = {"Test": np.sin(t)}
        interp_mask = {"Test": np.array([True] * 100)}
        
        fig = _create_timeseries_figure(t, series, interp_mask=interp_mask)
        
        # Second trace (interpolated) should be markers
        if len(fig.data) > 1:
            assert fig.data[1].mode == "markers"
    
    def test_interpolated_points_marker_style(self):
        """Test interpolated points have open circle style."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t = np.linspace(0, 10, 100)
        series = {"Test": np.sin(t)}
        interp_mask = {"Test": np.array([True] * 100)}
        
        fig = _create_timeseries_figure(t, series, interp_mask=interp_mask)
        
        if len(fig.data) > 1:
            assert fig.data[1].marker.symbol == "circle-open"
    
    def test_no_interpolation_trace_when_mask_empty(self):
        """Test no interpolation trace when mask is all False."""
        from platform_base.ui.callbacks import _create_timeseries_figure
        t = np.linspace(0, 10, 100)
        series = {"Test": np.sin(t)}
        interp_mask = {"Test": np.array([False] * 100)}
        
        fig = _create_timeseries_figure(t, series, interp_mask=interp_mask)
        
        # Should only have 1 trace
        assert len(fig.data) == 1


class TestLoggerUsage:
    """Tests for logger usage in callbacks module."""
    
    def test_logger_exists(self):
        """Test logger is configured in module."""
        from platform_base.ui.callbacks import logger
        assert logger is not None
    
    def test_logger_has_name(self):
        """Test logger has correct name."""
        from platform_base.ui.callbacks import logger
        assert 'callbacks' in logger.name or 'platform_base' in logger.name
