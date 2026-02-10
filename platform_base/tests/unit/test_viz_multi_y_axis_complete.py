"""
Comprehensive tests for viz/multi_y_axis.py module.

Target: Increase coverage from ~25% to 80%+
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


# Mock pyqtgraph module before importing the module under test
@pytest.fixture(autouse=True)
def mock_pyqtgraph():
    """Mock pyqtgraph to avoid Qt initialization issues."""
    mock_pg = MagicMock()
    mock_pg.AxisItem.return_value = MagicMock()
    mock_pg.ViewBox.return_value = MagicMock()
    mock_pg.PlotDataItem.return_value = MagicMock()
    mock_pg.mkPen.return_value = MagicMock()
    mock_pg.PlotItem = MagicMock
    
    # Mock AxisItem and ViewBox at module level
    with patch.dict('sys.modules', {
        'pyqtgraph': mock_pg,
    }):
        # Also patch the imports in the module
        with patch('platform_base.viz.multi_y_axis.pg', mock_pg):
            with patch('platform_base.viz.multi_y_axis.AxisItem', mock_pg.AxisItem):
                with patch('platform_base.viz.multi_y_axis.ViewBox', mock_pg.ViewBox):
                    with patch('platform_base.viz.multi_y_axis.PlotItem', MagicMock):
                        yield mock_pg


class TestAxisPosition:
    """Tests for AxisPosition enum."""
    
    def test_axis_positions_exist(self):
        """Test that all axis positions exist."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        assert hasattr(AxisPosition, 'LEFT_1')
        assert hasattr(AxisPosition, 'RIGHT_1')
        assert hasattr(AxisPosition, 'LEFT_2')
        assert hasattr(AxisPosition, 'RIGHT_2')
    
    def test_axis_positions_unique(self):
        """Test that all axis positions have unique values."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        positions = [
            AxisPosition.LEFT_1,
            AxisPosition.RIGHT_1,
            AxisPosition.LEFT_2,
            AxisPosition.RIGHT_2,
        ]
        
        assert len(set(positions)) == 4


class TestAxisConfig:
    """Tests for AxisConfig dataclass."""
    
    def test_default_values(self):
        """Test AxisConfig default values."""
        from platform_base.viz.multi_y_axis import AxisConfig, AxisPosition
        
        config = AxisConfig(position=AxisPosition.LEFT_1)
        
        assert config.label == "Value"
        assert config.color is None
        assert config.auto_range is True
        assert config.visible is True
        assert config.grid is False
        assert config.log_scale is False
        assert config.inverted is False
        assert config.min_value is None
        assert config.max_value is None
    
    def test_custom_values(self):
        """Test AxisConfig with custom values."""
        from platform_base.viz.multi_y_axis import AxisConfig, AxisPosition
        
        config = AxisConfig(
            position=AxisPosition.RIGHT_1,
            label="Temperature",
            color="#FF0000",
            auto_range=False,
            visible=True,
            grid=True,
            log_scale=True,
            inverted=True,
            min_value=0.0,
            max_value=100.0,
        )
        
        assert config.position == AxisPosition.RIGHT_1
        assert config.label == "Temperature"
        assert config.color == "#FF0000"
        assert config.auto_range is False
        assert config.grid is True
        assert config.log_scale is True
        assert config.inverted is True
        assert config.min_value == 0.0
        assert config.max_value == 100.0


class TestSeriesAxisInfo:
    """Tests for SeriesAxisInfo dataclass."""
    
    def test_creation(self):
        """Test SeriesAxisInfo creation."""
        from platform_base.viz.multi_y_axis import AxisPosition, SeriesAxisInfo
        
        mock_plot_item = MagicMock()
        mock_view_box = MagicMock()
        
        info = SeriesAxisInfo(
            series_id="test_series",
            axis_position=AxisPosition.LEFT_1,
            plot_item=mock_plot_item,
            view_box=mock_view_box,
            color="#00FF00",
        )
        
        assert info.series_id == "test_series"
        assert info.axis_position == AxisPosition.LEFT_1
        assert info.plot_item == mock_plot_item
        assert info.view_box == mock_view_box
        assert info.color == "#00FF00"
    
    def test_default_optional_values(self):
        """Test SeriesAxisInfo default optional values."""
        from platform_base.viz.multi_y_axis import AxisPosition, SeriesAxisInfo
        
        mock_plot_item = MagicMock()
        
        info = SeriesAxisInfo(
            series_id="test",
            axis_position=AxisPosition.RIGHT_1,
            plot_item=mock_plot_item,
        )
        
        assert info.view_box is None
        assert info.color is None


class TestYAxis:
    """Tests for YAxis class."""
    
    @pytest.fixture
    def mock_plot_item(self):
        """Create mock PlotItem."""
        mock = MagicMock()
        mock.vb = MagicMock()
        mock.layout = MagicMock()
        mock.scene.return_value = MagicMock()
        return mock
    
    def test_left_axis_orientation(self, mock_plot_item, mock_pyqtgraph):
        """Test left axis has correct orientation."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        assert axis.orientation == "left"
    
    def test_right_axis_orientation(self, mock_plot_item, mock_pyqtgraph):
        """Test right axis has correct orientation."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1)
        
        assert axis.orientation == "right"
    
    def test_left_2_axis_orientation(self, mock_plot_item, mock_pyqtgraph):
        """Test secondary left axis has correct orientation."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_2)
        
        assert axis.orientation == "left"
    
    def test_right_2_axis_orientation(self, mock_plot_item, mock_pyqtgraph):
        """Test secondary right axis has correct orientation."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_2)
        
        assert axis.orientation == "right"
    
    def test_primary_axis_no_viewbox(self, mock_plot_item, mock_pyqtgraph):
        """Test primary left axis doesn't create ViewBox."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        assert axis.view_box is None
    
    def test_secondary_axis_creates_viewbox(self, mock_plot_item, mock_pyqtgraph):
        """Test secondary axis creates ViewBox."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1)
        
        assert axis.view_box is not None
    
    def test_add_series_to_primary_axis(self, mock_plot_item, mock_pyqtgraph):
        """Test adding series to primary axis."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        result = axis.add_series("series1", x_data, y_data)
        
        mock_plot_item.plot.assert_called()
        assert "series1" in axis._series
    
    def test_add_series_to_secondary_axis(self, mock_plot_item, mock_pyqtgraph):
        """Test adding series to secondary axis."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1)
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        result = axis.add_series("series1", x_data, y_data)
        
        mock_pyqtgraph.PlotDataItem.assert_called()
        assert "series1" in axis._series
    
    def test_remove_series(self, mock_plot_item, mock_pyqtgraph):
        """Test removing series."""
        from platform_base.viz.multi_y_axis import AxisPosition, SeriesAxisInfo, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        # Add mock series
        mock_item = MagicMock()
        axis._series["series1"] = SeriesAxisInfo(
            series_id="series1",
            axis_position=AxisPosition.LEFT_1,
            plot_item=mock_item,
        )
        
        result = axis.remove_series("series1")
        
        assert "series1" not in axis._series
        mock_plot_item.removeItem.assert_called_with(mock_item)
    
    def test_remove_nonexistent_series(self, mock_plot_item, mock_pyqtgraph):
        """Test removing nonexistent series returns None."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        result = axis.remove_series("nonexistent")
        
        assert result is None
    
    def test_auto_range_primary_axis(self, mock_plot_item, mock_pyqtgraph):
        """Test auto range on primary axis."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        axis.auto_range()
        
        mock_plot_item.enableAutoRange.assert_called()
    
    def test_set_range(self, mock_plot_item, mock_pyqtgraph):
        """Test setting range on axis."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        axis.set_range(0.0, 100.0)
        
        mock_plot_item.setYRange.assert_called_with(0.0, 100.0)
    
    def test_set_color(self, mock_plot_item, mock_pyqtgraph):
        """Test setting axis color."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1)
        
        axis.set_color("#FF0000")
        
        assert axis.config.color == "#FF0000"
    
    def test_set_label(self, mock_plot_item, mock_pyqtgraph):
        """Test setting axis label."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        axis.set_label("Temperature (°C)")
        
        assert axis.config.label == "Temperature (°C)"
    
    def test_set_visible(self, mock_plot_item, mock_pyqtgraph):
        """Test setting axis visibility."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        axis.set_visible(False)
        
        assert axis.config.visible is False
    
    def test_series_ids_property(self, mock_plot_item, mock_pyqtgraph):
        """Test series_ids property."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        # Add mock series
        axis._series["series1"] = MagicMock()
        axis._series["series2"] = MagicMock()
        
        ids = axis.series_ids
        
        assert "series1" in ids
        assert "series2" in ids
    
    def test_series_count_property(self, mock_plot_item, mock_pyqtgraph):
        """Test series_count property."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        axis._series["series1"] = MagicMock()
        axis._series["series2"] = MagicMock()
        axis._series["series3"] = MagicMock()
        
        assert axis.series_count == 3


class TestMultiYAxisManager:
    """Tests for MultiYAxisManager class."""
    
    @pytest.fixture
    def mock_plot_item(self):
        """Create mock PlotItem."""
        mock = MagicMock()
        mock.vb = MagicMock()
        mock.layout = MagicMock()
        mock.scene.return_value = MagicMock()
        return mock
    
    @pytest.fixture
    def manager(self, mock_plot_item, mock_pyqtgraph):
        """Create MultiYAxisManager instance."""
        # Don't mock QObject.__init__ - signals need it properly initialized
        from platform_base.viz.multi_y_axis import MultiYAxisManager
        return MultiYAxisManager(mock_plot_item)
    
    def test_initialization_creates_primary_axis(self, manager):
        """Test that initialization creates primary left axis."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        assert AxisPosition.LEFT_1 in manager._axes
    
    def test_add_axis_right(self, manager, mock_pyqtgraph):
        """Test adding right axis."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        axis = manager.add_axis(AxisPosition.RIGHT_1, label="Pressure")
        
        assert AxisPosition.RIGHT_1 in manager._axes
        assert axis is not None
    
    def test_add_axis_left_2(self, manager, mock_pyqtgraph):
        """Test adding secondary left axis."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        axis = manager.add_axis(AxisPosition.LEFT_2, label="Temperature")
        
        assert AxisPosition.LEFT_2 in manager._axes
    
    def test_add_axis_duplicate_raises(self, manager, mock_pyqtgraph):
        """Test adding duplicate axis raises ValueError."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        with pytest.raises(ValueError, match="Axis already exists"):
            manager.add_axis(AxisPosition.LEFT_1, label="Duplicate")
    
    def test_remove_axis(self, manager, mock_pyqtgraph):
        """Test removing axis."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        manager.add_axis(AxisPosition.RIGHT_1, label="Temp")
        manager.remove_axis(AxisPosition.RIGHT_1)
        
        assert AxisPosition.RIGHT_1 not in manager._axes
    
    def test_remove_primary_axis_raises(self, manager):
        """Test removing primary axis raises ValueError."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        with pytest.raises(ValueError, match="Cannot remove primary"):
            manager.remove_axis(AxisPosition.LEFT_1)
    
    def test_remove_nonexistent_axis_raises(self, manager):
        """Test removing nonexistent axis raises ValueError."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        with pytest.raises(ValueError, match="No axis at"):
            manager.remove_axis(AxisPosition.RIGHT_2)
    
    def test_get_axis(self, manager, mock_pyqtgraph):
        """Test getting axis."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        axis = manager.get_axis(AxisPosition.LEFT_1)
        
        assert axis is not None
    
    def test_get_nonexistent_axis(self, manager):
        """Test getting nonexistent axis returns None."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        axis = manager.get_axis(AxisPosition.RIGHT_2)
        
        assert axis is None
    
    def test_add_series_to_primary_axis(self, manager, mock_pyqtgraph):
        """Test adding series to primary axis."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        result = manager.add_series("test", x_data, y_data, AxisPosition.LEFT_1)
        
        assert result is not None
        # Verify series is tracked in the axis
        assert manager.get_series_axis("test") == AxisPosition.LEFT_1
    
    def test_add_series_to_nonexistent_axis_raises(self, manager):
        """Test adding series to nonexistent axis raises ValueError."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        with pytest.raises(ValueError, match="does not exist"):
            manager.add_series("test", x_data, y_data, AxisPosition.RIGHT_2)
    
    def test_remove_series_from_manager(self, manager, mock_pyqtgraph):
        """Test removing series from manager."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        manager.add_series("test", x_data, y_data, AxisPosition.LEFT_1)
        result = manager.remove_series("test")
        
        assert result is True
        assert manager.get_series_axis("test") is None
    
    def test_remove_nonexistent_series(self, manager):
        """Test removing nonexistent series returns False."""
        result = manager.remove_series("nonexistent")
        
        assert result is False
    
    def test_get_series_axis(self, manager, mock_pyqtgraph):
        """Test getting axis for a series."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        manager.add_series("test", x_data, y_data, AxisPosition.LEFT_1)
        axis_pos = manager.get_series_axis("test")
        
        assert axis_pos == AxisPosition.LEFT_1
    
    def test_get_series_axis_not_found(self, manager):
        """Test getting axis for nonexistent series returns None."""
        axis_pos = manager.get_series_axis("nonexistent")
        
        assert axis_pos is None
    
    def test_auto_range_all(self, manager, mock_pyqtgraph):
        """Test auto range on all axes."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        manager.add_axis(AxisPosition.RIGHT_1, label="Temp")
        
        # Should not raise
        manager.auto_range_all()
    
    def test_sync_x_range(self, manager, mock_pyqtgraph):
        """Test X range synchronization."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        manager.add_axis(AxisPosition.RIGHT_1, label="Temp")
        
        # Should not raise
        manager.sync_x_range()
    
    def test_axis_count_property(self, manager, mock_pyqtgraph):
        """Test axis_count property."""
        from platform_base.viz.multi_y_axis import AxisPosition

        # Start with 1 (primary)
        assert manager.axis_count == 1
        
        manager.add_axis(AxisPosition.RIGHT_1)
        assert manager.axis_count == 2
        
        manager.add_axis(AxisPosition.LEFT_2)
        assert manager.axis_count == 3
    
    def test_available_positions_property(self, manager, mock_pyqtgraph):
        """Test available_positions property."""
        from platform_base.viz.multi_y_axis import AxisPosition
        
        available = manager.available_positions
        
        # LEFT_1 is taken, others available
        assert AxisPosition.LEFT_1 not in available
        assert AxisPosition.RIGHT_1 in available
        assert AxisPosition.LEFT_2 in available
        assert AxisPosition.RIGHT_2 in available


class TestYAxisLayoutPositioning:
    """Tests for Y axis layout positioning."""
    
    @pytest.fixture
    def mock_plot_item(self):
        """Create mock PlotItem."""
        mock = MagicMock()
        mock.vb = MagicMock()
        mock.layout = MagicMock()
        mock.scene.return_value = MagicMock()
        return mock
    
    def test_right_1_layout_position(self, mock_plot_item, mock_pyqtgraph):
        """Test RIGHT_1 axis is added to correct layout position."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1)
        
        # Should be added to column 3
        mock_plot_item.layout.addItem.assert_called()
        call_args = mock_plot_item.layout.addItem.call_args
        assert call_args[0][1] == 2  # row
        assert call_args[0][2] == 3  # column
    
    def test_left_2_layout_position(self, mock_plot_item, mock_pyqtgraph):
        """Test LEFT_2 axis is added to correct layout position."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_2)
        
        # Should be added to column 0
        mock_plot_item.layout.addItem.assert_called()
        call_args = mock_plot_item.layout.addItem.call_args
        assert call_args[0][1] == 2  # row
        assert call_args[0][2] == 0  # column
    
    def test_right_2_layout_position(self, mock_plot_item, mock_pyqtgraph):
        """Test RIGHT_2 axis is added to correct layout position."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_2)
        
        # Should be added to column 4
        mock_plot_item.layout.addItem.assert_called()
        call_args = mock_plot_item.layout.addItem.call_args
        assert call_args[0][1] == 2  # row
        assert call_args[0][2] == 4  # column
    
    def test_left_1_no_layout_call(self, mock_plot_item, mock_pyqtgraph):
        """Test LEFT_1 (primary) doesn't add to layout."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        # Primary axis shouldn't call addItem
        mock_plot_item.layout.addItem.assert_not_called()


class TestYAxisColorManagement:
    """Tests for Y axis color management."""
    
    @pytest.fixture
    def mock_plot_item(self):
        """Create mock PlotItem."""
        mock = MagicMock()
        mock.vb = MagicMock()
        mock.layout = MagicMock()
        mock.scene.return_value = MagicMock()
        return mock
    
    def test_axis_with_color_config(self, mock_plot_item, mock_pyqtgraph):
        """Test axis created with color config."""
        from platform_base.viz.multi_y_axis import AxisConfig, AxisPosition, YAxis
        
        config = AxisConfig(
            position=AxisPosition.RIGHT_1,
            color="#FF0000"
        )
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1, config)
        
        # Should call mkPen with color
        mock_pyqtgraph.mkPen.assert_called()
    
    def test_axis_without_color_config(self, mock_plot_item, mock_pyqtgraph):
        """Test axis created without color config."""
        from platform_base.viz.multi_y_axis import AxisConfig, AxisPosition, YAxis
        
        config = AxisConfig(
            position=AxisPosition.RIGHT_1,
            color=None
        )
        
        # Reset mock to check calls
        mock_pyqtgraph.mkPen.reset_mock()
        
        axis = YAxis(mock_plot_item, AxisPosition.RIGHT_1, config)
        
        # Should not call mkPen for color (but might call for other reasons)
        # Just verify axis was created successfully
        assert axis is not None


class TestMultiYAxisSignals:
    """Tests for MultiYAxisManager signals."""
    
    @pytest.fixture
    def mock_plot_item(self):
        """Create mock PlotItem."""
        mock = MagicMock()
        mock.vb = MagicMock()
        mock.layout = MagicMock()
        mock.scene.return_value = MagicMock()
        return mock
    
    def test_manager_has_signals(self, mock_plot_item, mock_pyqtgraph):
        """Test MultiYAxisManager has required signals."""
        from platform_base.viz.multi_y_axis import MultiYAxisManager
        
        manager = MultiYAxisManager(mock_plot_item)
        
        # Check signal attributes exist
        assert hasattr(manager, 'axis_added')
        assert hasattr(manager, 'axis_removed')
        assert hasattr(manager, 'series_moved')


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.fixture
    def mock_plot_item(self):
        """Create mock PlotItem."""
        mock = MagicMock()
        mock.vb = MagicMock()
        mock.layout = MagicMock()
        mock.scene.return_value = MagicMock()
        return mock
    
    def test_empty_data_series(self, mock_plot_item, mock_pyqtgraph):
        """Test adding series with empty data."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        x_data = np.array([], dtype=float)
        y_data = np.array([], dtype=float)
        
        # Should not raise
        result = axis.add_series("empty_series", x_data, y_data)
        assert "empty_series" in axis._series
    
    def test_large_data_series(self, mock_plot_item, mock_pyqtgraph):
        """Test adding series with large data."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        x_data = np.arange(100000, dtype=float)
        y_data = np.sin(x_data)
        
        # Should not raise
        result = axis.add_series("large_series", x_data, y_data)
        assert "large_series" in axis._series
    
    def test_nan_data_series(self, mock_plot_item, mock_pyqtgraph):
        """Test adding series with NaN values."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        x_data = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        y_data = np.array([1.0, np.nan, 3.0, 4.0, 5.0])
        
        # Should not raise
        result = axis.add_series("nan_series", x_data, y_data)
        assert "nan_series" in axis._series
    
    def test_duplicate_series_id(self, mock_plot_item, mock_pyqtgraph):
        """Test adding series with duplicate ID."""
        from platform_base.viz.multi_y_axis import AxisPosition, YAxis
        
        axis = YAxis(mock_plot_item, AxisPosition.LEFT_1)
        
        x_data = np.arange(100, dtype=float)
        y_data = np.sin(x_data)
        
        axis.add_series("series1", x_data, y_data)
        
        # Adding again should overwrite
        axis.add_series("series1", x_data * 2, y_data * 2)
        
        assert "series1" in axis._series
