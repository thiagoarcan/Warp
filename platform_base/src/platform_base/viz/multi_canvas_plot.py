"""
Multi-Canvas Plot Widget - Supports up to 4 independent plots per tab
Original implementation for Platform Base v2.0
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSpinBox, QSplitter, QFrame
)

from platform_base.viz.hue_coordinator import get_hue_coordinator
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class IndependentPlotCanvas(pg.PlotWidget):
    """Single independent plot canvas with enhanced features"""
    
    series_clicked = pyqtSignal(str)  # series_id
    context_menu_requested = pyqtSignal(object, str)  # event, series_id
    
    def __init__(self, canvas_id: int, parent=None):
        super().__init__(parent)
        
        self.canvas_id = canvas_id
        self.hue_coordinator = get_hue_coordinator()
        
        # Series registry for this canvas
        self._series_registry: Dict[str, Dict[str, Any]] = {}
        self._visible_series: set = set()
        # Bidirectional mapping for faster legend lookup
        self._name_to_series_id: Dict[str, str] = {}
        
        # Plot configuration
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('bottom', 'Tempo')
        self.setLabel('left', 'Valor')
        
        # Interactive legend
        self.legend_item = self.addLegend(offset=(10, 10))
        self.legend_item.setMovable(True)
        
        # Axes management
        self._extra_y_axes: List[pg.AxisItem] = []
        self._axis_viewboxes: List[pg.ViewBox] = []
        
        # Setup interactions
        self._setup_mouse_interactions()
        
    def _setup_mouse_interactions(self):
        """Configure mouse event handlers"""
        self.scene().sigMouseClicked.connect(self._handle_mouse_click)
        self.scene().sigMouseMoved.connect(self._handle_mouse_hover)
        
        # Make legend interactive
        self.legend_item.sigItemClicked.connect(self._on_legend_item_clicked)
        
    def _handle_mouse_click(self, event):
        """Handle mouse clicks on plot"""
        if event.button() == Qt.MouseButton.RightButton:
            # Determine which series was clicked
            clicked_series = self._find_series_at_position(event.scenePos())
            if clicked_series:
                self.context_menu_requested.emit(event, clicked_series)
                
    def _handle_mouse_hover(self, pos):
        """Display tooltip showing values at cursor position"""
        view_coords = self.plotItem.vb.mapSceneToView(pos)
        x_coord = view_coords.x()
        
        # Find values for all visible series at this x coordinate
        tooltip_lines = [f"Tempo: {x_coord:.2f}"]
        
        for series_id in self._visible_series:
            series_info = self._series_registry.get(series_id)
            if series_info:
                x_data = series_info['x_data']
                y_data = series_info['y_data']
                
                # Find nearest point
                idx = np.argmin(np.abs(x_data - x_coord))
                if idx < len(y_data):
                    y_val = y_data[idx]
                    name = series_info['name']
                    tooltip_lines.append(f"{name}: {y_val:.4f}")
        
        tooltip_text = "\n".join(tooltip_lines)
        self.setToolTip(tooltip_text)
        
    def _on_legend_item_clicked(self, legend_item, label_item):
        """Adapter for PyQtGraph legend click signal - converts to series_id"""
        # PyQtGraph emits (legend_item, label_item), need to find series_id
        # Use bidirectional mapping for O(1) lookup
        label_text = label_item.text()  # Call the method to get text
        series_id = self._name_to_series_id.get(label_text)
        
        if series_id:
            self._handle_legend_click(series_id)
        else:
            logger.warning(f"Legend click for unknown series: {label_text}")
    
    def _handle_legend_click(self, series_id):
        """Toggle series visibility on legend click"""
        if series_id in self._visible_series:
            self.hide_series(series_id)
        else:
            self.show_series(series_id)
            
    def _find_series_at_position(self, scene_pos) -> Optional[str]:
        """Find which series is near the clicked position"""
        view_pos = self.plotItem.vb.mapSceneToView(scene_pos)
        x_click = view_pos.x()
        y_click = view_pos.y()
        
        # Calculate dynamic threshold based on current axis ranges
        x_range = self.plotItem.vb.viewRange()[0]
        y_range = self.plotItem.vb.viewRange()[1]
        x_span = abs(x_range[1] - x_range[0])
        y_span = abs(y_range[1] - y_range[0])
        
        # Use 2% of the diagonal as threshold
        threshold = 0.02 * np.sqrt(x_span**2 + y_span**2)
        
        min_distance = float('inf')
        closest_series = None
        
        for series_id in self._visible_series:
            series_info = self._series_registry.get(series_id)
            if series_info and series_info['curve_item'].isVisible():
                x_data = series_info['x_data']
                y_data = series_info['y_data']
                
                # Find nearest point
                idx = np.argmin(np.abs(x_data - x_click))
                if idx < len(y_data):
                    distance = np.sqrt((x_data[idx] - x_click)**2 + (y_data[idx] - y_click)**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_series = series_id
        
        return closest_series if min_distance < threshold else None
        
    def add_series_to_canvas(self, series_id: str, x_data: np.ndarray, y_data: np.ndarray,
                            series_name: str = None, axis_index: int = 0):
        """
        Add a data series to this canvas
        
        Args:
            series_id: Unique identifier
            x_data: Time/X axis data
            y_data: Value/Y axis data
            series_name: Display name
            axis_index: Which Y axis to use (0 = primary)
        """
        display_name = series_name or series_id
        
        # Get consistent color from coordinator
        hue = self.hue_coordinator.assign_hue_to_series(series_id)
        pen = pg.mkPen(color=hue, width=2)
        
        # Create curve
        curve = pg.PlotCurveItem(x_data, y_data, pen=pen, name=display_name)
        
        # Add to appropriate viewbox
        if axis_index == 0:
            self.addItem(curve)
        else:
            if axis_index - 1 < len(self._axis_viewboxes):
                vb = self._axis_viewboxes[axis_index - 1]
                vb.addItem(curve)
        
        # Register series
        self._series_registry[series_id] = {
            'curve_item': curve,
            'x_data': x_data,
            'y_data': y_data,
            'name': display_name,
            'hue': hue,
            'axis_index': axis_index,
            'visible': True
        }
        
        # Maintain bidirectional mapping
        self._name_to_series_id[display_name] = series_id
        
        self._visible_series.add(series_id)
        
        logger.debug(f"Series added to canvas {self.canvas_id}: {series_id}")
        
    def remove_series_from_canvas(self, series_id: str):
        """Remove series from canvas"""
        if series_id in self._series_registry:
            series_info = self._series_registry[series_id]
            curve = series_info['curve_item']
            display_name = series_info['name']
            
            # Remove from plot
            if series_info['axis_index'] == 0:
                self.removeItem(curve)
            else:
                vb_idx = series_info['axis_index'] - 1
                if vb_idx < len(self._axis_viewboxes):
                    self._axis_viewboxes[vb_idx].removeItem(curve)
            
            # Release color
            self.hue_coordinator.release_series_hue(series_id)
            
            # Remove from bidirectional mapping
            self._name_to_series_id.pop(display_name, None)
            
            # Unregister
            del self._series_registry[series_id]
            self._visible_series.discard(series_id)
            
    def hide_series(self, series_id: str):
        """Hide a series without removing it"""
        if series_id in self._series_registry:
            self._series_registry[series_id]['curve_item'].setVisible(False)
            self._series_registry[series_id]['visible'] = False
            self._visible_series.discard(series_id)
            self._adjust_axes()
            
    def show_series(self, series_id: str):
        """Show a hidden series"""
        if series_id in self._series_registry:
            self._series_registry[series_id]['curve_item'].setVisible(True)
            self._series_registry[series_id]['visible'] = True
            self._visible_series.add(series_id)
            self._adjust_axes()
            
    def _adjust_axes(self):
        """Auto-adjust axes based on visible data"""
        if not self._visible_series:
            return
            
        # Collect visible data ranges
        all_x = []
        all_y = []
        
        for series_id in self._visible_series:
            series_info = self._series_registry[series_id]
            all_x.extend(series_info['x_data'])
            all_y.extend(series_info['y_data'])
        
        if all_x and all_y:
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            
            # Add 5% padding
            x_padding = (x_max - x_min) * 0.05
            y_padding = (y_max - y_min) * 0.05
            
            self.setXRange(x_min - x_padding, x_max + x_padding)
            self.setYRange(y_min - y_padding, y_max + y_padding)
            
    def create_secondary_y_axis(self, label: str = "Y2") -> int:
        """Create additional Y axis on right side"""
        # Create axis
        axis = pg.AxisItem('right')
        axis.setLabel(label)
        
        # Create viewbox
        vb = pg.ViewBox()
        vb.setXLink(self.plotItem.vb)
        
        # Add to scene
        self.scene().addItem(vb)
        
        # Position viewbox to match main plot
        vb.setGeometry(self.plotItem.vb.sceneBoundingRect())
        
        # Link viewbox size to main plot
        self.plotItem.vb.sigResized.connect(lambda: self._update_viewbox_geometry(vb))
        
        # Store references
        self._extra_y_axes.append(axis)
        self._axis_viewboxes.append(vb)
        
        return len(self._axis_viewboxes)  # Return axis index
        
    def _update_viewbox_geometry(self, vb: pg.ViewBox):
        """Update secondary viewbox geometry to match primary"""
        vb.setGeometry(self.plotItem.vb.sceneBoundingRect())
        
    def set_datetime_x_axis(self, enable: bool = True):
        """Enable datetime formatting for X axis"""
        if enable:
            axis = pg.DateAxisItem(orientation='bottom')
            self.plotItem.setAxisItems({'bottom': axis})
        else:
            axis = pg.AxisItem(orientation='bottom')
            self.plotItem.setAxisItems({'bottom': axis})


class MultiCanvasPlotWidget(QWidget):
    """Widget supporting up to 4 independent plot canvases in grid layout"""
    
    canvas_added = pyqtSignal(int)  # canvas_id
    canvas_removed = pyqtSignal(int)  # canvas_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.active_canvases: Dict[int, IndependentPlotCanvas] = {}
        self.next_canvas_id = 0
        
        self._setup_ui()
        
        # Start with one canvas
        self.add_canvas()
        
    def _setup_ui(self):
        """Setup widget layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Control toolbar
        toolbar = QHBoxLayout()
        
        self.add_canvas_btn = QPushButton("+ Adicionar Gráfico")
        self.add_canvas_btn.clicked.connect(self.add_canvas)
        toolbar.addWidget(self.add_canvas_btn)
        
        self.remove_canvas_btn = QPushButton("- Remover Gráfico")
        self.remove_canvas_btn.clicked.connect(self.remove_last_canvas)
        toolbar.addWidget(self.remove_canvas_btn)
        
        toolbar.addWidget(QLabel("Gráficos:"))
        self.canvas_count_label = QLabel("0")
        toolbar.addWidget(self.canvas_count_label)
        
        toolbar.addStretch()
        
        main_layout.addLayout(toolbar)
        
        # Grid container for canvases
        self.canvas_grid = QGridLayout()
        self.canvas_grid.setSpacing(5)
        main_layout.addLayout(self.canvas_grid)
        
        self.setLayout(main_layout)
        
    def add_canvas(self) -> int:
        """Add new plot canvas to grid"""
        if len(self.active_canvases) >= 4:
            logger.warning("Maximum 4 canvases reached")
            return -1
            
        canvas_id = self.next_canvas_id
        self.next_canvas_id += 1
        
        canvas = IndependentPlotCanvas(canvas_id, self)
        self.active_canvases[canvas_id] = canvas
        
        # Update grid layout
        self._update_grid_layout()
        
        # Update UI
        self.canvas_count_label.setText(str(len(self.active_canvases)))
        self.remove_canvas_btn.setEnabled(len(self.active_canvases) > 1)
        self.add_canvas_btn.setEnabled(len(self.active_canvases) < 4)
        
        self.canvas_added.emit(canvas_id)
        
        logger.debug(f"Canvas added: {canvas_id}")
        return canvas_id
        
    def remove_canvas(self, canvas_id: int):
        """Remove specific canvas"""
        if canvas_id in self.active_canvases:
            canvas = self.active_canvases[canvas_id]
            
            # Remove from grid
            self.canvas_grid.removeWidget(canvas)
            canvas.deleteLater()
            
            del self.active_canvases[canvas_id]
            
            # Update grid
            self._update_grid_layout()
            
            # Update UI
            self.canvas_count_label.setText(str(len(self.active_canvases)))
            self.remove_canvas_btn.setEnabled(len(self.active_canvases) > 1)
            self.add_canvas_btn.setEnabled(len(self.active_canvases) < 4)
            
            self.canvas_removed.emit(canvas_id)
            
    def remove_last_canvas(self):
        """Remove most recently added canvas"""
        if self.active_canvases:
            last_id = max(self.active_canvases.keys())
            self.remove_canvas(last_id)
            
    def _update_grid_layout(self):
        """Reorganize canvases in grid based on count"""
        # Clear grid
        for i in reversed(range(self.canvas_grid.count())):
            self.canvas_grid.itemAt(i).widget().setParent(None)
        
        # Determine grid arrangement
        num_canvases = len(self.active_canvases)
        
        if num_canvases == 1:
            rows, cols = 1, 1
        elif num_canvases == 2:
            rows, cols = 1, 2
        elif num_canvases == 3:
            rows, cols = 2, 2  # 3 canvases in 2x2 grid
        else:  # 4 canvases
            rows, cols = 2, 2
            
        # Add canvases to grid
        canvas_ids = sorted(self.active_canvases.keys())
        for idx, canvas_id in enumerate(canvas_ids):
            row = idx // cols
            col = idx % cols
            self.canvas_grid.addWidget(self.active_canvases[canvas_id], row, col)
            
    def get_canvas(self, canvas_id: int) -> Optional[IndependentPlotCanvas]:
        """Retrieve specific canvas"""
        return self.active_canvases.get(canvas_id)
        
    def get_all_canvases(self) -> List[IndependentPlotCanvas]:
        """Get list of all active canvases"""
        return list(self.active_canvases.values())
