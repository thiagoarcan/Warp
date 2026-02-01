"""
Multi-Y Axis System for Platform Base

Supports up to 4 Y axes with proper synchronization and visual management.

Features:
- Up to 4 independent Y axes (2 left, 2 right)
- Automatic axis color matching with series
- Auto-range per axis
- Drag-drop series between axes
- Visual indicators

Category 2.9 - Multi-Y Axis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from pyqtgraph import AxisItem, PlotItem, ViewBox

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


class AxisPosition(Enum):
    """Position of Y axis."""
    LEFT_1 = auto()    # Primary left (default)
    RIGHT_1 = auto()   # Primary right
    LEFT_2 = auto()    # Secondary left (outer)
    RIGHT_2 = auto()   # Secondary right (outer)


@dataclass
class AxisConfig:
    """Configuration for a Y axis."""
    position: AxisPosition
    label: str = "Value"
    color: str | None = None
    auto_range: bool = True
    visible: bool = True
    grid: bool = False
    log_scale: bool = False
    inverted: bool = False
    min_value: float | None = None
    max_value: float | None = None


@dataclass
class SeriesAxisInfo:
    """Tracks which axis a series is on."""
    series_id: str
    axis_position: AxisPosition
    plot_item: Any  # PlotDataItem
    view_box: ViewBox | None = None
    color: str | None = None


class YAxis:
    """
    Represents a single Y axis with its associated ViewBox.
    
    Manages its own range, scale, and appearance independently
    while sharing X axis with the main plot.
    """
    
    def __init__(
        self,
        plot_item: PlotItem,
        position: AxisPosition,
        config: AxisConfig | None = None,
    ):
        """
        Initialize Y axis.
        
        Args:
            plot_item: Main PlotItem to attach to
            position: Position of this axis
            config: Axis configuration
        """
        self.plot_item = plot_item
        self.position = position
        self.config = config or AxisConfig(position=position)
        
        # Determine orientation
        if position in (AxisPosition.LEFT_1, AxisPosition.LEFT_2):
            self.orientation = "left"
        else:
            self.orientation = "right"
        
        # Create axis item
        self.axis_item = AxisItem(self.orientation)
        self.axis_item.setLabel(self.config.label)
        
        if self.config.color:
            self.axis_item.setPen(pg.mkPen(color=self.config.color))
            self.axis_item.setTextPen(pg.mkPen(color=self.config.color))
        
        # Create ViewBox for this axis (except primary left)
        self.view_box: ViewBox | None = None
        if position != AxisPosition.LEFT_1:
            self.view_box = ViewBox()
            self.view_box.setXLink(plot_item.vb)  # Link X axis
        
        # Series on this axis
        self._series: dict[str, SeriesAxisInfo] = {}
        
        # Add to layout
        self._add_to_layout()
        
        logger.debug("y_axis_created", position=position.name, label=self.config.label)
    
    def _add_to_layout(self):
        """Add axis to plot layout."""
        layout = self.plot_item.layout
        
        # Determine row and column based on position
        # Layout: col 0-1 = left axes, col 2 = plot, col 3-4 = right axes
        row = 2  # Main row
        
        if self.position == AxisPosition.LEFT_1:
            # Primary left - this is the default axis
            pass  # Already handled by PlotItem
        elif self.position == AxisPosition.RIGHT_1:
            layout.addItem(self.axis_item, row, 3)
        elif self.position == AxisPosition.LEFT_2:
            layout.addItem(self.axis_item, row, 0)
        elif self.position == AxisPosition.RIGHT_2:
            layout.addItem(self.axis_item, row, 4)
        
        # Add ViewBox to scene if not primary
        if self.view_box is not None:
            self.plot_item.scene().addItem(self.view_box)
    
    def add_series(self, series_id: str, x_data, y_data, **kwargs) -> Any:
        """
        Add series to this axis.
        
        Args:
            series_id: Unique series identifier
            x_data: X data
            y_data: Y data
            **kwargs: Plot options (pen, color, etc.)
            
        Returns:
            PlotDataItem
        """
        if self.position == AxisPosition.LEFT_1:
            # Plot directly on main PlotItem
            item = self.plot_item.plot(x_data, y_data, **kwargs)
            view_box = self.plot_item.vb
        else:
            # Plot on our ViewBox
            item = pg.PlotDataItem(x_data, y_data, **kwargs)
            self.view_box.addItem(item)
            view_box = self.view_box
        
        # Track series
        color = kwargs.get('pen', {}).opts.get('color') if hasattr(kwargs.get('pen', {}), 'opts') else None
        self._series[series_id] = SeriesAxisInfo(
            series_id=series_id,
            axis_position=self.position,
            plot_item=item,
            view_box=view_box,
            color=color,
        )
        
        # Update range
        if self.config.auto_range:
            self.auto_range()
        
        return item
    
    def remove_series(self, series_id: str) -> Any | None:
        """
        Remove series from this axis.
        
        Args:
            series_id: Series to remove
            
        Returns:
            Removed plot item or None
        """
        if series_id not in self._series:
            return None
        
        info = self._series.pop(series_id)
        
        if self.position == AxisPosition.LEFT_1:
            self.plot_item.removeItem(info.plot_item)
        elif self.view_box is not None:
            self.view_box.removeItem(info.plot_item)
        
        return info.plot_item
    
    def auto_range(self):
        """Auto-range this axis based on data."""
        if self.position == AxisPosition.LEFT_1:
            self.plot_item.enableAutoRange(axis=ViewBox.YAxis)
        elif self.view_box is not None:
            self.view_box.enableAutoRange(axis=ViewBox.YAxis)
    
    def set_range(self, min_val: float, max_val: float):
        """Set explicit range for this axis."""
        if self.position == AxisPosition.LEFT_1:
            self.plot_item.setYRange(min_val, max_val)
        elif self.view_box is not None:
            self.view_box.setYRange(min_val, max_val)
    
    def set_color(self, color: str):
        """Set axis color."""
        self.config.color = color
        pen = pg.mkPen(color=color)
        self.axis_item.setPen(pen)
        self.axis_item.setTextPen(pen)
    
    def set_label(self, label: str):
        """Set axis label."""
        self.config.label = label
        self.axis_item.setLabel(label)
    
    def set_visible(self, visible: bool):
        """Set axis visibility."""
        self.config.visible = visible
        self.axis_item.setVisible(visible)
    
    @property
    def series_ids(self) -> list[str]:
        """Get IDs of series on this axis."""
        return list(self._series.keys())
    
    @property
    def series_count(self) -> int:
        """Number of series on this axis."""
        return len(self._series)


class MultiYAxisManager(QObject):
    """
    Manages multiple Y axes for a plot.
    
    Supports up to 4 Y axes (2 left, 2 right) with automatic
    synchronization and series management.
    """
    
    # Signals
    axis_added = pyqtSignal(str)  # axis_position
    axis_removed = pyqtSignal(str)  # axis_position
    series_moved = pyqtSignal(str, str, str)  # series_id, from_axis, to_axis
    
    def __init__(self, plot_item: PlotItem, parent: QObject | None = None):
        """
        Initialize multi-axis manager.
        
        Args:
            plot_item: PlotItem to manage axes for
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.plot_item = plot_item
        self._axes: dict[AxisPosition, YAxis] = {}
        
        # Primary left axis is always present
        self._axes[AxisPosition.LEFT_1] = YAxis(
            plot_item,
            AxisPosition.LEFT_1,
            AxisConfig(position=AxisPosition.LEFT_1, label="Y"),
        )
        
        logger.debug("multi_y_axis_manager_created")
    
    def add_axis(
        self,
        position: AxisPosition,
        label: str = "Value",
        color: str | None = None,
    ) -> YAxis:
        """
        Add a Y axis at the specified position.
        
        Args:
            position: Where to place the axis
            label: Axis label
            color: Axis color
            
        Returns:
            Created YAxis
            
        Raises:
            ValueError: If axis already exists at position
        """
        if position in self._axes:
            raise ValueError(f"Axis already exists at {position.name}")
        
        config = AxisConfig(position=position, label=label, color=color)
        axis = YAxis(self.plot_item, position, config)
        self._axes[position] = axis
        
        self.axis_added.emit(position.name)
        logger.info("y_axis_added", position=position.name, label=label)
        
        return axis
    
    def remove_axis(self, position: AxisPosition):
        """
        Remove Y axis at position.
        
        Args:
            position: Axis position to remove
            
        Raises:
            ValueError: If trying to remove primary axis or axis doesn't exist
        """
        if position == AxisPosition.LEFT_1:
            raise ValueError("Cannot remove primary Y axis")
        
        if position not in self._axes:
            raise ValueError(f"No axis at {position.name}")
        
        axis = self._axes.pop(position)
        
        # Remove axis from layout
        self.plot_item.layout.removeItem(axis.axis_item)
        
        # Remove ViewBox from scene
        if axis.view_box is not None:
            self.plot_item.scene().removeItem(axis.view_box)
        
        self.axis_removed.emit(position.name)
        logger.info("y_axis_removed", position=position.name)
    
    def get_axis(self, position: AxisPosition) -> YAxis | None:
        """Get axis at position."""
        return self._axes.get(position)
    
    def move_series(
        self,
        series_id: str,
        from_position: AxisPosition,
        to_position: AxisPosition,
    ):
        """
        Move series from one axis to another.
        
        Args:
            series_id: Series to move
            from_position: Current axis
            to_position: Target axis
        """
        from_axis = self._axes.get(from_position)
        to_axis = self._axes.get(to_position)
        
        if from_axis is None:
            raise ValueError(f"Source axis {from_position.name} does not exist")
        if to_axis is None:
            raise ValueError(f"Target axis {to_position.name} does not exist")
        
        # Get series info before removal
        info = from_axis._series.get(series_id)
        if info is None:
            raise ValueError(f"Series {series_id} not on axis {from_position.name}")
        
        # Get data from plot item
        if hasattr(info.plot_item, 'getData'):
            x_data, y_data = info.plot_item.getData()
        else:
            raise ValueError("Cannot get data from plot item")
        
        # Remove from source
        from_axis.remove_series(series_id)
        
        # Add to target
        pen = pg.mkPen(color=info.color) if info.color else None
        to_axis.add_series(series_id, x_data, y_data, pen=pen)
        
        self.series_moved.emit(series_id, from_position.name, to_position.name)
        logger.info("series_moved", 
                   series_id=series_id,
                   from_axis=from_position.name,
                   to_axis=to_position.name)
    
    def add_series(
        self,
        series_id: str,
        x_data,
        y_data,
        axis_position: AxisPosition = AxisPosition.LEFT_1,
        **kwargs,
    ) -> Any:
        """
        Add series to specified axis.
        
        Args:
            series_id: Unique series identifier
            x_data: X data
            y_data: Y data
            axis_position: Which axis to add to
            **kwargs: Plot options
            
        Returns:
            PlotDataItem
        """
        axis = self._axes.get(axis_position)
        if axis is None:
            raise ValueError(f"Axis {axis_position.name} does not exist")
        
        return axis.add_series(series_id, x_data, y_data, **kwargs)
    
    def remove_series(self, series_id: str) -> bool:
        """
        Remove series from any axis.
        
        Args:
            series_id: Series to remove
            
        Returns:
            True if found and removed
        """
        for axis in self._axes.values():
            if series_id in axis._series:
                axis.remove_series(series_id)
                return True
        return False
    
    def get_series_axis(self, series_id: str) -> AxisPosition | None:
        """Get which axis a series is on."""
        for position, axis in self._axes.items():
            if series_id in axis._series:
                return position
        return None
    
    def auto_range_all(self):
        """Auto-range all axes."""
        for axis in self._axes.values():
            axis.auto_range()
    
    def sync_x_range(self):
        """Ensure all ViewBoxes are synced to main X axis."""
        for axis in self._axes.values():
            if axis.view_box is not None:
                axis.view_box.setXLink(self.plot_item.vb)
    
    def update_geometry(self):
        """Update ViewBox geometries to match main plot."""
        for axis in self._axes.values():
            if axis.view_box is not None:
                axis.view_box.setGeometry(self.plot_item.vb.sceneBoundingRect())
    
    @property
    def axis_count(self) -> int:
        """Number of active axes."""
        return len(self._axes)
    
    @property
    def available_positions(self) -> list[AxisPosition]:
        """Positions where axes can be added."""
        all_positions = set(AxisPosition)
        used_positions = set(self._axes.keys())
        return list(all_positions - used_positions)


def create_multi_axis_plot(title: str = "") -> tuple[PlotItem, MultiYAxisManager]:
    """
    Create a plot with multi-axis support.
    
    Args:
        title: Plot title
        
    Returns:
        Tuple of (PlotItem, MultiYAxisManager)
    """
    plot_widget = pg.PlotWidget(title=title)
    plot_item = plot_widget.plotItem
    
    manager = MultiYAxisManager(plot_item)
    
    return plot_item, manager


__all__ = [
    "AxisConfig",
    "AxisPosition",
    "MultiYAxisManager",
    "SeriesAxisInfo",
    "YAxis",
    "create_multi_axis_plot",
]
