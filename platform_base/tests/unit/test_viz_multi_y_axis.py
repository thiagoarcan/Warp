"""
Tests for multi_y_axis module - Category 2.9 Multi-Y Axis.
"""
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from platform_base.viz.multi_y_axis import AxisConfig, AxisPosition, SeriesAxisInfo


class TestAxisPosition:
    """Tests for AxisPosition enum."""
    
    def test_left_1_position(self):
        """Test LEFT_1 position exists."""
        assert AxisPosition.LEFT_1 is not None
    
    def test_right_1_position(self):
        """Test RIGHT_1 position exists."""
        assert AxisPosition.RIGHT_1 is not None
    
    def test_left_2_position(self):
        """Test LEFT_2 position exists."""
        assert AxisPosition.LEFT_2 is not None
    
    def test_right_2_position(self):
        """Test RIGHT_2 position exists."""
        assert AxisPosition.RIGHT_2 is not None
    
    def test_all_positions_unique(self):
        """Test all positions are unique."""
        positions = [
            AxisPosition.LEFT_1,
            AxisPosition.RIGHT_1,
            AxisPosition.LEFT_2,
            AxisPosition.RIGHT_2,
        ]
        assert len(set(positions)) == 4


class TestAxisConfig:
    """Tests for AxisConfig dataclass."""
    
    def test_create_basic_config(self):
        """Test creating basic AxisConfig."""
        config = AxisConfig(position=AxisPosition.LEFT_1)
        
        assert config.position == AxisPosition.LEFT_1
        assert config.label == "Value"
        assert config.auto_range is True
    
    def test_create_full_config(self):
        """Test creating AxisConfig with all options."""
        config = AxisConfig(
            position=AxisPosition.RIGHT_1,
            label="Temperature",
            color="#FF0000",
            auto_range=False,
            visible=True,
            grid=True,
            log_scale=False,
            inverted=False,
            min_value=0.0,
            max_value=100.0,
        )
        
        assert config.position == AxisPosition.RIGHT_1
        assert config.label == "Temperature"
        assert config.color == "#FF0000"
        assert config.auto_range is False
        assert config.min_value == 0.0
        assert config.max_value == 100.0
    
    def test_config_defaults(self):
        """Test AxisConfig default values."""
        config = AxisConfig(position=AxisPosition.LEFT_2)
        
        assert config.color is None
        assert config.visible is True
        assert config.grid is False
        assert config.log_scale is False
        assert config.inverted is False
        assert config.min_value is None
        assert config.max_value is None
    
    def test_config_with_inverted(self):
        """Test AxisConfig with inverted axis."""
        config = AxisConfig(
            position=AxisPosition.LEFT_1,
            inverted=True,
        )
        
        assert config.inverted is True
    
    def test_config_with_log_scale(self):
        """Test AxisConfig with log scale."""
        config = AxisConfig(
            position=AxisPosition.LEFT_1,
            log_scale=True,
        )
        
        assert config.log_scale is True


class TestSeriesAxisInfo:
    """Tests for SeriesAxisInfo dataclass."""
    
    def test_create_series_info(self):
        """Test creating SeriesAxisInfo."""
        info = SeriesAxisInfo(
            series_id="series_1",
            axis_position=AxisPosition.LEFT_1,
            plot_item=Mock(),
        )
        
        assert info.series_id == "series_1"
        assert info.axis_position == AxisPosition.LEFT_1
        assert info.view_box is None
        assert info.color is None
    
    def test_series_info_with_color(self):
        """Test SeriesAxisInfo with color."""
        info = SeriesAxisInfo(
            series_id="series_2",
            axis_position=AxisPosition.RIGHT_1,
            plot_item=Mock(),
            color="#00FF00",
        )
        
        assert info.color == "#00FF00"
    
    def test_series_info_with_viewbox(self):
        """Test SeriesAxisInfo with ViewBox."""
        mock_viewbox = Mock()
        info = SeriesAxisInfo(
            series_id="series_3",
            axis_position=AxisPosition.LEFT_2,
            plot_item=Mock(),
            view_box=mock_viewbox,
        )
        
        assert info.view_box is mock_viewbox


class TestYAxisBasics:
    """Basic tests for YAxis class without Qt."""
    
    def test_module_has_yaxis_class(self):
        """Test that module has YAxis class."""
        from platform_base.viz import multi_y_axis
        
        assert hasattr(multi_y_axis, 'YAxis')
    
    def test_module_has_manager_class(self):
        """Test that module has MultiYAxisManager class."""
        from platform_base.viz import multi_y_axis
        
        assert hasattr(multi_y_axis, 'MultiYAxisManager')


class TestMultiYAxisModule:
    """Tests for multi_y_axis module structure."""
    
    def test_module_imports(self):
        """Test that module can be imported."""
        from platform_base.viz import multi_y_axis
        assert multi_y_axis is not None
    
    def test_has_logger(self):
        """Test that module has logger."""
        from platform_base.viz import multi_y_axis
        assert hasattr(multi_y_axis, 'logger')
    
    def test_axis_positions_count(self):
        """Test correct number of axis positions."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        positions = list(AxisPosition)
        assert len(positions) == 4
    
    def test_left_positions_are_left(self):
        """Test that LEFT positions have correct names."""
        assert "LEFT" in AxisPosition.LEFT_1.name
        assert "LEFT" in AxisPosition.LEFT_2.name
    
    def test_right_positions_are_right(self):
        """Test that RIGHT positions have correct names."""
        assert "RIGHT" in AxisPosition.RIGHT_1.name
        assert "RIGHT" in AxisPosition.RIGHT_2.name
