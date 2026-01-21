"""
VizPanel - Main visualization panel for Platform Base v2.0

Provides 2D/3D plotting capabilities with pyqtgraph and PyVista.
Replaces Dash plotly components with native PyQt6 plotting widgets.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QSplitter, QFrame, QLabel, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QToolBar
)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QActionGroup

import pyqtgraph as pg
from pyqtgraph import PlotWidget, GraphicsLayoutWidget

from platform_base.desktop.session_state import SessionState
from platform_base.desktop.signal_hub import SignalHub
from platform_base.core.models import DatasetID, SeriesID, ViewID, TimeWindow
from platform_base.utils.logging import get_logger
from platform_base.utils.i18n import tr

logger = get_logger(__name__)

# Try to import PyVista for 3D plotting
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    logger.warning("pyvista_not_available", message="3D plotting will be disabled")


class Plot2DWidget(PlotWidget):
    """Enhanced 2D plot widget with selection capabilities"""
    
    # Selection signals
    time_selection_changed = pyqtSignal(float, float)  # start_time, end_time
    point_selection_changed = pyqtSignal(object)  # selected_points
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure plot
        self.setLabel('left', 'Value')
        self.setLabel('bottom', 'Time (s)')
        self.showGrid(True, True, alpha=0.3)
        self.setBackground('w')
        
        # Enable mouse interaction
        self.setMouseEnabled(x=True, y=True)
        self.enableAutoRange()
        
        # Selection state
        self._selection_item = None
        self._is_selecting = False
        
        # Connect mouse events
        self.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        self.scene().sigMouseMoved.connect(self._on_mouse_moved)
    
    def _on_mouse_clicked(self, event):
        """Handle mouse click for selection"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Start selection mode
            pos = self.getViewBox().mapSceneToView(event.pos())
            self._start_selection(pos.x())
    
    def _on_mouse_moved(self, pos):
        """Handle mouse move during selection"""
        if self._is_selecting:
            view_pos = self.getViewBox().mapSceneToView(pos)
            self._update_selection(view_pos.x())
    
    def _start_selection(self, x_pos: float):
        """Start time selection"""
        self._is_selecting = True
        self._selection_start = x_pos
        
        # Create selection visual
        if self._selection_item:
            self.removeItem(self._selection_item)
        
        self._selection_item = pg.LinearRegionItem([x_pos, x_pos], 
                                                  brush=pg.mkBrush(0, 100, 200, 50))
        self.addItem(self._selection_item)
    
    def _update_selection(self, x_pos: float):
        """Update time selection"""
        if self._selection_item:
            start = min(self._selection_start, x_pos)
            end = max(self._selection_start, x_pos)
            self._selection_item.setRegion([start, end])
    
    def finish_selection(self):
        """Finish time selection and emit signal"""
        if self._selection_item:
            start, end = self._selection_item.getRegion()
            self.time_selection_changed.emit(start, end)
            self._is_selecting = False
    
    def clear_selection(self):
        """Clear current selection"""
        if self._selection_item:
            self.removeItem(self._selection_item)
            self._selection_item = None
        self._is_selecting = False


class Plot3DWidget(QWidget):
    """3D plotting widget using PyVista"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        if PYVISTA_AVAILABLE:
            # Create PyVista Qt interactor
            self.plotter = QtInteractor(self)
            self.plotter.background_color = 'white'
            layout.addWidget(self.plotter.interactor)
            
            # Add default lighting
            self.plotter.add_light(pv.Light())
        else:
            # Show unavailable message
            label = QLabel("3D plotting unavailable\\nInstall pyvista and vtk")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: gray; font-size: 14px;")
            layout.addWidget(label)
    
    def plot_trajectory_3d(self, x_data, y_data, z_data, time_data=None):
        """Plot 3D trajectory"""
        if not PYVISTA_AVAILABLE:
            return
        
        try:
            # Clear previous plots
            self.plotter.clear()
            
            # Create trajectory points
            import numpy as np
            points = np.column_stack([x_data, y_data, z_data])
            
            # Create trajectory line
            trajectory = pv.PolyData(points)
            
            # Add lines between consecutive points
            lines = []
            for i in range(len(points) - 1):
                lines.extend([2, i, i + 1])
            trajectory.lines = lines
            
            # Color by time if available
            if time_data is not None:
                trajectory['time'] = time_data
                self.plotter.add_mesh(trajectory, scalars='time', 
                                    line_width=3, cmap='viridis',
                                    render_lines_as_tubes=True)
            else:
                self.plotter.add_mesh(trajectory, color='blue', 
                                    line_width=3, render_lines_as_tubes=True)
            
            # Add axes
            self.plotter.add_axes()
            
            # Set camera
            self.plotter.camera_position = 'iso'
            self.plotter.reset_camera()
            
        except Exception as e:
            logger.error("3d_plot_failed", error=str(e))


class VizPanel(QWidget):
    """
    Main visualization panel widget.
    
    Features:
    - Tabbed 2D/3D plotting interface
    - Plot configuration controls
    - Multi-series plotting
    - Interactive selection
    - Export capabilities
    """
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        
        # Plot data storage
        self.active_plots: Dict[str, Dict[str, Any]] = {}
        self.plot_counter = 0
        
        self._setup_ui()
        self._connect_signals()
        
        logger.debug("viz_panel_initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Plot toolbar
        self.toolbar = self._create_plot_toolbar()
        layout.addWidget(self.toolbar)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Plot tabs (main area)
        self.plot_tabs = QTabWidget()
        self.plot_tabs.setTabsClosable(True)
        self.plot_tabs.tabCloseRequested.connect(self._close_plot_tab)
        self.plot_tabs.currentChanged.connect(self._on_tab_changed)
        splitter.addWidget(self.plot_tabs)
        
        # Plot controls (right panel)
        self.controls_widget = self._create_controls_widget()
        splitter.addWidget(self.controls_widget)
        
        # Set splitter proportions
        splitter.setSizes([800, 200])
        layout.addWidget(splitter)
        
        # Add initial welcome tab
        self._add_welcome_tab()
    
    def _create_plot_toolbar(self) -> QToolBar:
        """Create plot toolbar"""
        toolbar = QToolBar(tr("Plot Actions"))
        
        # Plot type actions
        plot_group = QActionGroup(toolbar)
        
        plot_2d_action = QAction(tr("2D Plot"), toolbar)
        plot_2d_action.setCheckable(True)
        plot_2d_action.setChecked(True)
        plot_2d_action.triggered.connect(lambda: self._create_plot("2d"))
        plot_group.addAction(plot_2d_action)
        toolbar.addAction(plot_2d_action)
        
        if PYVISTA_AVAILABLE:
            plot_3d_action = QAction(tr("3D Plot"), toolbar)
            plot_3d_action.setCheckable(True)
            plot_3d_action.triggered.connect(lambda: self._create_plot("3d"))
            plot_group.addAction(plot_3d_action)
            toolbar.addAction(plot_3d_action)
        
        toolbar.addSeparator()
        
        # Plot actions
        clear_action = QAction(tr("Clear"), toolbar)
        clear_action.triggered.connect(self._clear_current_plot)
        toolbar.addAction(clear_action)
        
        export_action = QAction(tr("Export"), toolbar)
        export_action.triggered.connect(self._export_current_plot)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Selection tools
        select_action = QAction(tr("Select"), toolbar)
        select_action.setCheckable(True)
        select_action.triggered.connect(self._toggle_selection_mode)
        toolbar.addAction(select_action)
        
        return toolbar
    
    def _create_controls_widget(self) -> QWidget:
        """Create plot controls widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Plot settings group
        settings_group = QGroupBox(tr("Plot Settings"))
        settings_layout = QVBoxLayout(settings_group)
        
        # Line width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel(tr("Line Width:")))
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setRange(1, 10)
        self.line_width_spin.setValue(2)
        self.line_width_spin.valueChanged.connect(self._update_line_width)
        width_layout.addWidget(self.line_width_spin)
        settings_layout.addLayout(width_layout)
        
        # Grid toggle
        self.grid_check = QCheckBox(tr("Show Grid"))
        self.grid_check.setChecked(True)
        self.grid_check.toggled.connect(self._toggle_grid)
        settings_layout.addWidget(self.grid_check)
        
        # Legend toggle
        self.legend_check = QCheckBox(tr("Show Legend"))
        self.legend_check.setChecked(True)
        self.legend_check.toggled.connect(self._toggle_legend)
        settings_layout.addWidget(self.legend_check)
        
        layout.addWidget(settings_group)
        
        # Series list group
        series_group = QGroupBox(tr("Active Series"))
        series_layout = QVBoxLayout(series_group)
        
        self.series_list = QWidget()
        series_list_layout = QVBoxLayout(self.series_list)
        series_layout.addWidget(self.series_list)
        
        layout.addWidget(series_group)
        
        layout.addStretch()
        return widget
    
    def _add_welcome_tab(self):
        """Add welcome tab with instructions"""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        
        welcome_text = QLabel(f"""
        <h2>{tr("Platform Base Visualization")}</h2>
        <p>{tr("Welcome to the visualization panel!")}</p>
        
        <h3>{tr("Getting Started:")}:</h3>
        <ul>
        <li>{tr("Load data using the Data panel")}</li>
        <li>{tr("Select series to plot")}</li>
        <li>{tr("Double-click series to create plots")}</li>
        <li>{tr("Use toolbar to create 2D/3D plots")}</li>
        </ul>
        
        <h3>{tr("Interaction:")}:</h3>
        <ul>
        <li>{tr("Ctrl+Click to start time selection")}</li>
        <li>{tr("Mouse wheel to zoom")}</li>
        <li>{tr("Drag to pan")}</li>
        <li>{tr("Right-click for context menu")}</li>
        </ul>
        """)
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        self.plot_tabs.addTab(welcome_widget, tr("Welcome"))
    
    def _connect_signals(self):
        """Connect signals"""
        # Listen to selection changes
        self.session_state.selection_changed.connect(self._on_selection_changed)
        
        # Listen to plot requests
        self.signal_hub.plot_created.connect(self._on_plot_requested)
        self.signal_hub.series_selected.connect(self._on_series_selected)
    
    @pyqtSlot()
    def _create_plot(self, plot_type: str):
        """Create new plot tab"""
        self.plot_counter += 1
        plot_id = f"plot_{self.plot_counter}"
        
        if plot_type == "2d":
            plot_widget = Plot2DWidget()
            plot_widget.time_selection_changed.connect(self._on_time_selection)
            tab_name = f"2D Plot {self.plot_counter}"
        elif plot_type == "3d" and PYVISTA_AVAILABLE:
            plot_widget = Plot3DWidget()
            tab_name = f"3D Plot {self.plot_counter}"
        else:
            logger.warning("unsupported_plot_type", plot_type=plot_type)
            return
        
        # Add to tabs
        tab_index = self.plot_tabs.addTab(plot_widget, tab_name)
        self.plot_tabs.setCurrentIndex(tab_index)
        
        # Store plot info
        self.active_plots[plot_id] = {
            "widget": plot_widget,
            "type": plot_type,
            "tab_index": tab_index,
            "series": {}
        }
        
        # Auto-plot selected series
        self._plot_selected_series(plot_id)
        
        logger.debug("plot_created", plot_id=plot_id, plot_type=plot_type)
    
    @pyqtSlot(int)
    def _close_plot_tab(self, index: int):
        """Close plot tab"""
        # Find plot_id for this tab
        plot_id = None
        for pid, pinfo in self.active_plots.items():
            if pinfo["tab_index"] == index:
                plot_id = pid
                break
        
        if plot_id:
            del self.active_plots[plot_id]
            self.plot_tabs.removeTab(index)
            
            # Update tab indices
            for pinfo in self.active_plots.values():
                if pinfo["tab_index"] > index:
                    pinfo["tab_index"] -= 1
            
            logger.debug("plot_closed", plot_id=plot_id)
    
    @pyqtSlot(int)
    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        if index >= 0:
            widget = self.plot_tabs.widget(index)
            logger.debug("tab_changed", index=index, 
                        widget_type=type(widget).__name__)
    
    @pyqtSlot()
    def _clear_current_plot(self):
        """Clear current plot"""
        current_index = self.plot_tabs.currentIndex()
        if current_index < 0:
            return
        
        # Find current plot
        for plot_id, pinfo in self.active_plots.items():
            if pinfo["tab_index"] == current_index:
                widget = pinfo["widget"]
                if hasattr(widget, 'clear'):
                    widget.clear()
                elif hasattr(widget, 'plotter'):
                    widget.plotter.clear()
                pinfo["series"].clear()
                logger.debug("plot_cleared", plot_id=plot_id)
                break
    
    @pyqtSlot()
    def _export_current_plot(self):
        """Export current plot"""
        logger.info("plot_export_requested")
        # Export functionality to be implemented
    
    @pyqtSlot()
    def _toggle_selection_mode(self):
        """Toggle selection mode"""
        logger.debug("selection_mode_toggled")
        # Selection mode logic to be implemented
    
    @pyqtSlot(float, float)
    def _on_time_selection(self, start_time: float, end_time: float):
        """Handle time selection from plot"""
        time_window = TimeWindow(start=start_time, end=end_time)
        self.session_state.set_time_window(time_window)
        self.signal_hub.emit_time_selection(start_time, end_time)
        logger.debug("time_selection_from_plot", start=start_time, end=end_time)
    
    @pyqtSlot(str)
    def _on_plot_requested(self, view_id: str):
        """Handle plot request from signal hub"""
        self._create_plot("2d")
    
    @pyqtSlot(str, str)
    def _on_series_selected(self, dataset_id: str, series_id: str):
        """Handle series selection"""
        # Add series to current plot if available
        current_index = self.plot_tabs.currentIndex()
        if current_index < 0:
            return
        
        for plot_id, pinfo in self.active_plots.items():
            if pinfo["tab_index"] == current_index:
                self._add_series_to_plot(plot_id, dataset_id, series_id)
                break
    
    @pyqtSlot(object)
    def _on_selection_changed(self, selection_state):
        """Handle selection state changes"""
        # Update all plots to reflect selection
        if selection_state.time_window:
            self._update_time_selection_visual(selection_state.time_window)
    
    def _plot_selected_series(self, plot_id: str):
        """Plot currently selected series"""
        selection = self.session_state.selection
        
        if not selection.dataset_id or not selection.series_ids:
            return
        
        for series_id in selection.series_ids:
            self._add_series_to_plot(plot_id, selection.dataset_id, series_id)
    
    def _add_series_to_plot(self, plot_id: str, dataset_id: str, series_id: str):
        """Add series to specific plot"""
        if plot_id not in self.active_plots:
            return
        
        try:
            # Get data
            dataset = self.session_state.dataset_store.get_dataset(dataset_id)
            series = dataset.series[series_id]
            
            plot_info = self.active_plots[plot_id]
            widget = plot_info["widget"]
            
            if plot_info["type"] == "2d" and isinstance(widget, Plot2DWidget):
                # Plot 2D
                curve = widget.plot(dataset.t_seconds, series.values,
                                  pen=pg.mkPen(width=self.line_width_spin.value()),
                                  name=series.name)
                
                plot_info["series"][series_id] = {
                    "curve": curve,
                    "dataset_id": dataset_id,
                    "name": series.name
                }
                
            elif plot_info["type"] == "3d" and isinstance(widget, Plot3DWidget):
                # For 3D, need at least 3 series (x, y, z)
                if len(plot_info["series"]) >= 2:
                    # Get first three series for 3D plot
                    series_list = list(plot_info["series"].values())
                    x_data = series_list[0]["data"]
                    y_data = series_list[1]["data"]
                    z_data = series.values
                    
                    widget.plot_trajectory_3d(x_data, y_data, z_data, dataset.t_seconds)
                
                plot_info["series"][series_id] = {
                    "data": series.values,
                    "dataset_id": dataset_id,
                    "name": series.name
                }
            
            logger.debug("series_added_to_plot", plot_id=plot_id, 
                        dataset_id=dataset_id, series_id=series_id)
            
        except Exception as e:
            logger.error("failed_to_add_series_to_plot", 
                        plot_id=plot_id, dataset_id=dataset_id, 
                        series_id=series_id, error=str(e))
    
    def _update_time_selection_visual(self, time_window: TimeWindow):
        """Update time selection visual on all 2D plots"""
        for plot_info in self.active_plots.values():
            if plot_info["type"] == "2d":
                widget = plot_info["widget"]
                # Update selection visual
                if hasattr(widget, '_selection_item') and widget._selection_item:
                    widget._selection_item.setRegion([time_window.start, time_window.end])
    
    # Control event handlers
    @pyqtSlot(int)
    def _update_line_width(self, width: int):
        """Update line width for all plots"""
        for plot_info in self.active_plots.values():
            if plot_info["type"] == "2d":
                for series_info in plot_info["series"].values():
                    if "curve" in series_info:
                        series_info["curve"].setPen(pg.mkPen(width=width))
    
    @pyqtSlot(bool)
    def _toggle_grid(self, enabled: bool):
        """Toggle grid for all 2D plots"""
        for plot_info in self.active_plots.values():
            if plot_info["type"] == "2d":
                widget = plot_info["widget"]
                widget.showGrid(enabled, enabled, alpha=0.3)
    
    @pyqtSlot(bool)
    def _toggle_legend(self, enabled: bool):
        """Toggle legend for all plots"""
        for plot_info in self.active_plots.values():
            if plot_info["type"] == "2d":
                widget = plot_info["widget"]
                if enabled:
                    widget.addLegend()
                else:
                    if hasattr(widget, 'legend'):
                        widget.legend.clear()