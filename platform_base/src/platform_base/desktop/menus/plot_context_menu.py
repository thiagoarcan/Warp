"""
Plot Context Menu System - Platform Base v2.0

Provides rich context menus for plot interactions with:
- Mathematical analysis tools
- Data manipulation options  
- Export and visualization controls
- Selection and annotation features
"""

from __future__ import annotations

from typing import Optional, Dict, Any, Callable, List
from PyQt6.QtWidgets import (
    QMenu, QWidget, QInputDialog, QMessageBox,
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QSpinBox, QCheckBox, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QActionGroup, QIcon, QKeySequence, QAction

from platform_base.desktop.signal_hub import SignalHub
from platform_base.desktop.session_state import SessionState
from platform_base.core.models import DatasetID, SeriesID
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class MathAnalysisDialog(QDialog):
    """Dialog for mathematical analysis operations"""
    
    operation_requested = pyqtSignal(str, dict)  # operation_name, parameters
    
    def __init__(self, operation: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.operation = operation
        self.setWindowTitle(f"Mathematical Analysis - {operation.title()}")
        self.setModal(True)
        self.resize(350, 200)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup dialog UI based on operation"""
        layout = QVBoxLayout(self)
        
        if self.operation == "derivative":
            self._setup_derivative_ui(layout)
        elif self.operation == "integral":
            self._setup_integral_ui(layout)
        elif self.operation == "smooth":
            self._setup_smoothing_ui(layout)
        elif self.operation == "interpolate":
            self._setup_interpolation_ui(layout)
        elif self.operation == "resample":
            self._setup_resample_ui(layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_operation)
        apply_btn.setDefault(True)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_derivative_ui(self, layout: QVBoxLayout):
        """Setup derivative calculation UI"""
        params_group = QGroupBox("Derivative Parameters")
        params_layout = QFormLayout(params_group)
        
        self.derivative_order = QSpinBox()
        self.derivative_order.setRange(1, 3)
        self.derivative_order.setValue(1)
        params_layout.addRow("Order:", self.derivative_order)
        
        self.derivative_method = QComboBox()
        self.derivative_method.addItems([
            "finite_diff", "savitzky_golay", "spline_derivative"
        ])
        params_layout.addRow("Method:", self.derivative_method)
        
        # Smoothing options
        self.enable_smoothing = QCheckBox("Apply smoothing")
        params_layout.addRow("", self.enable_smoothing)
        
        self.smoothing_window = QSpinBox()
        self.smoothing_window.setRange(3, 51)
        self.smoothing_window.setValue(7)
        self.smoothing_window.setSingleStep(2)  # Keep odd numbers
        self.smoothing_window.setEnabled(False)
        params_layout.addRow("Window size:", self.smoothing_window)
        
        self.enable_smoothing.toggled.connect(self.smoothing_window.setEnabled)
        
        layout.addWidget(params_group)
    
    def _setup_integral_ui(self, layout: QVBoxLayout):
        """Setup integral calculation UI"""
        params_group = QGroupBox("Integration Parameters")
        params_layout = QFormLayout(params_group)
        
        self.integral_method = QComboBox()
        self.integral_method.addItems(["trapezoid", "simpson", "cumulative"])
        params_layout.addRow("Method:", self.integral_method)
        
        layout.addWidget(params_group)
    
    def _setup_smoothing_ui(self, layout: QVBoxLayout):
        """Setup smoothing UI"""
        params_group = QGroupBox("Smoothing Parameters")
        params_layout = QFormLayout(params_group)
        
        self.smooth_method = QComboBox()
        self.smooth_method.addItems([
            "moving_average", "savitzky_golay", "gaussian", 
            "lowpass_filter", "median_filter"
        ])
        params_layout.addRow("Method:", self.smooth_method)
        
        self.window_size = QSpinBox()
        self.window_size.setRange(3, 101)
        self.window_size.setValue(11)
        params_layout.addRow("Window Size:", self.window_size)
        
        self.polyorder = QSpinBox()
        self.polyorder.setRange(1, 10)
        self.polyorder.setValue(3)
        params_layout.addRow("Polynomial Order:", self.polyorder)
        
        layout.addWidget(params_group)
    
    def _setup_interpolation_ui(self, layout: QVBoxLayout):
        """Setup interpolation UI"""
        params_group = QGroupBox("Interpolation Parameters")
        params_layout = QFormLayout(params_group)
        
        self.interp_method = QComboBox()
        self.interp_method.addItems([
            "linear", "spline_cubic", "smoothing_spline", 
            "mls", "gpr", "lomb_scargle_spectral"
        ])
        params_layout.addRow("Method:", self.interp_method)
        
        layout.addWidget(params_group)
    
    def _setup_resample_ui(self, layout: QVBoxLayout):
        """Setup resampling UI"""
        params_group = QGroupBox("Resampling Parameters")
        params_layout = QFormLayout(params_group)
        
        self.resample_method = QComboBox()
        self.resample_method.addItems(["lttb", "minmax", "adaptive", "uniform"])
        params_layout.addRow("Method:", self.resample_method)
        
        self.target_points = QSpinBox()
        self.target_points.setRange(10, 100000)
        self.target_points.setValue(1000)
        params_layout.addRow("Target Points:", self.target_points)
        
        layout.addWidget(params_group)
    
    def _apply_operation(self):
        """Apply the selected operation"""
        params = {}
        
        if self.operation == "derivative":
            params = {
                "order": self.derivative_order.value(),
                "method": self.derivative_method.currentText(),
            }
            if self.enable_smoothing.isChecked():
                params["smoothing"] = {
                    "method": "savitzky_golay",
                    "params": {"window_length": self.smoothing_window.value()}
                }
        
        elif self.operation == "integral":
            params = {
                "method": self.integral_method.currentText()
            }
        
        elif self.operation == "smooth":
            params = {
                "method": self.smooth_method.currentText(),
                "window_size": self.window_size.value(),
                "polyorder": self.polyorder.value()
            }
        
        elif self.operation == "interpolate":
            params = {
                "method": self.interp_method.currentText()
            }
        
        elif self.operation == "resample":
            params = {
                "method": self.resample_method.currentText(),
                "n_points": self.target_points.value()
            }
        
        self.operation_requested.emit(self.operation, params)
        self.accept()


class PlotContextMenu(QMenu):
    """
    Context menu for plot widgets providing analysis and manipulation tools.
    
    Features:
    - Mathematical analysis (derivatives, integrals)
    - Data manipulation (smoothing, interpolation, resampling)
    - Visualization controls (zoom, export, annotations)
    - Selection tools
    - Series management
    """
    
    # Signals for operations
    math_operation_requested = pyqtSignal(str, dict, str, str)  # operation, params, dataset_id, series_id
    zoom_to_selection_requested = pyqtSignal()
    reset_zoom_requested = pyqtSignal()
    export_plot_requested = pyqtSignal(str)  # format
    export_data_requested = pyqtSignal()
    create_annotation_requested = pyqtSignal(float, float, str)  # x, y, text
    duplicate_series_requested = pyqtSignal(str, str)  # dataset_id, series_id
    remove_series_requested = pyqtSignal(str, str)  # dataset_id, series_id
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 plot_position: Optional[QPointF] = None,
                 dataset_id: Optional[DatasetID] = None,
                 series_id: Optional[SeriesID] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        self.plot_position = plot_position
        self.dataset_id = dataset_id
        self.series_id = series_id
        
        self._setup_menu()
        
        logger.debug("plot_context_menu_created",
                    dataset_id=dataset_id, series_id=series_id)
    
    def _setup_menu(self):
        """Setup context menu structure"""
        # Mathematical Analysis submenu
        math_menu = self.addMenu("📊 Mathematical Analysis")
        self._setup_math_menu(math_menu)
        
        # Data Processing submenu
        processing_menu = self.addMenu("🔧 Data Processing")
        self._setup_processing_menu(processing_menu)
        
        self.addSeparator()
        
        # Visualization controls
        viz_menu = self.addMenu("👁️ Visualization")
        self._setup_visualization_menu(viz_menu)
        
        self.addSeparator()
        
        # Selection tools
        self._setup_selection_menu()
        
        self.addSeparator()
        
        # Export options
        export_menu = self.addMenu("💾 Export")
        self._setup_export_menu(export_menu)
        
        self.addSeparator()
        
        # Series management (if series context available)
        if self.dataset_id and self.series_id:
            self._setup_series_menu()
    
    def _setup_math_menu(self, menu: QMenu):
        """Setup mathematical analysis menu"""
        # Derivatives
        derivative_action = menu.addAction("📈 Calculate Derivative...")
        derivative_action.triggered.connect(
            lambda: self._show_analysis_dialog("derivative"))
        
        # Integrals
        integral_action = menu.addAction("📉 Calculate Integral...")
        integral_action.triggered.connect(
            lambda: self._show_analysis_dialog("integral"))
        
        menu.addSeparator()
        
        # Statistical analysis
        stats_action = menu.addAction("📊 Show Statistics")
        stats_action.triggered.connect(self._show_statistics)
        
        # FFT Analysis
        fft_action = menu.addAction("🌊 FFT Analysis")
        fft_action.triggered.connect(self._show_fft_analysis)
        
        # Correlation analysis (if multiple series)
        if self._has_multiple_series():
            correlation_action = menu.addAction("🔗 Correlation Analysis")
            correlation_action.triggered.connect(self._show_correlation_analysis)
    
    def _setup_processing_menu(self, menu: QMenu):
        """Setup data processing menu"""
        # Smoothing
        smooth_action = menu.addAction("🌊 Smooth Data...")
        smooth_action.triggered.connect(
            lambda: self._show_analysis_dialog("smooth"))
        
        # Interpolation
        interp_action = menu.addAction("🎯 Interpolate Missing Data...")
        interp_action.triggered.connect(
            lambda: self._show_analysis_dialog("interpolate"))
        
        # Resampling/Downsampling
        resample_action = menu.addAction("📏 Resample Data...")
        resample_action.triggered.connect(
            lambda: self._show_analysis_dialog("resample"))
        
        menu.addSeparator()
        
        # Filtering
        filter_menu = menu.addMenu("🔍 Filters")
        
        lowpass_action = filter_menu.addAction("Low-pass Filter")
        lowpass_action.triggered.connect(
            lambda: self._apply_filter("lowpass"))
        
        highpass_action = filter_menu.addAction("High-pass Filter")
        highpass_action.triggered.connect(
            lambda: self._apply_filter("highpass"))
        
        bandpass_action = filter_menu.addAction("Band-pass Filter")
        bandpass_action.triggered.connect(
            lambda: self._apply_filter("bandpass"))
        
        # Outlier detection
        outlier_action = menu.addAction("🎯 Detect Outliers")
        outlier_action.triggered.connect(self._detect_outliers)
    
    def _setup_visualization_menu(self, menu: QMenu):
        """Setup visualization menu"""
        # Zoom controls
        zoom_selection_action = menu.addAction("🔍 Zoom to Selection")
        zoom_selection_action.triggered.connect(self.zoom_to_selection_requested.emit)
        zoom_selection_action.setShortcut(QKeySequence("Ctrl+Z"))
        
        reset_zoom_action = menu.addAction("🔄 Reset Zoom")
        reset_zoom_action.triggered.connect(self.reset_zoom_requested.emit)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+R"))
        
        menu.addSeparator()
        
        # Grid and styling
        grid_action = menu.addAction("⊞ Toggle Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self._toggle_grid)
        
        legend_action = menu.addAction("📝 Toggle Legend")
        legend_action.setCheckable(True)
        legend_action.setChecked(True)
        legend_action.triggered.connect(self._toggle_legend)
        
        # Annotations
        if self.plot_position:
            menu.addSeparator()
            annotate_action = menu.addAction("📝 Add Annotation...")
            annotate_action.triggered.connect(self._add_annotation)
    
    def _setup_selection_menu(self):
        """Setup selection tools menu"""
        # Clear selection
        clear_selection_action = self.addAction("🗑️ Clear Selection")
        clear_selection_action.triggered.connect(self._clear_selection)
        clear_selection_action.setShortcut(QKeySequence("Escape"))
        
        # Select all
        select_all_action = self.addAction("☑️ Select All")
        select_all_action.triggered.connect(self._select_all)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        
        # Invert selection
        invert_selection_action = self.addAction("🔄 Invert Selection")
        invert_selection_action.triggered.connect(self._invert_selection)
        invert_selection_action.setShortcut(QKeySequence("Ctrl+I"))
    
    def _setup_export_menu(self, menu: QMenu):
        """Setup export menu"""
        # Plot export
        plot_export_menu = menu.addMenu("🖼️ Export Plot")
        
        for fmt in ["PNG", "SVG", "PDF", "JPEG"]:
            action = plot_export_menu.addAction(fmt)
            action.triggered.connect(
                lambda checked, f=fmt: self.export_plot_requested.emit(f.lower()))
        
        # Data export
        data_action = menu.addAction("📊 Export Data...")
        data_action.triggered.connect(self.export_data_requested.emit)
        
        # Copy to clipboard
        copy_action = menu.addAction("📋 Copy to Clipboard")
        copy_action.triggered.connect(self._copy_to_clipboard)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
    
    def _setup_series_menu(self):
        """Setup series management menu"""
        # Duplicate series
        duplicate_action = self.addAction("📄 Duplicate Series")
        duplicate_action.triggered.connect(self._duplicate_series)
        
        # Hide/show series
        hide_action = self.addAction("👁️ Hide Series")
        hide_action.triggered.connect(self._hide_series)
        
        # Remove series
        remove_action = self.addAction("🗑️ Remove Series")
        remove_action.triggered.connect(self._remove_series)
        
        self.addSeparator()
        
        # Series properties
        properties_action = self.addAction("⚙️ Series Properties...")
        properties_action.triggered.connect(self._show_series_properties)
    
    def _show_analysis_dialog(self, operation: str):
        """Show mathematical analysis dialog"""
        dialog = MathAnalysisDialog(operation, self.parent())
        dialog.operation_requested.connect(
            lambda op, params: self.math_operation_requested.emit(
                op, params, self.dataset_id, self.series_id))
        dialog.exec()
    
    def _show_statistics(self):
        """Show statistical analysis"""
        if not self.dataset_id or not self.series_id:
            return
        
        try:
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)
            series = dataset.series[self.series_id]
            values = series.values
            
            # Calculate statistics
            import numpy as np
            stats = {
                'Count': len(values),
                'Mean': np.mean(values),
                'Std Dev': np.std(values),
                'Min': np.min(values),
                'Max': np.max(values),
                'Median': np.median(values),
                'Q25': np.percentile(values, 25),
                'Q75': np.percentile(values, 75),
                'Skewness': self._calculate_skewness(values),
                'Kurtosis': self._calculate_kurtosis(values)
            }
            
            # Show in message box
            stats_text = "\n".join([f"{k}: {v:.6g}" for k, v in stats.items()])
            QMessageBox.information(self.parent(), 
                                  f"Statistics - {series.name}", 
                                  stats_text)
            
        except Exception as e:
            logger.error("statistics_calculation_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", 
                              f"Failed to calculate statistics: {e}")
    
    def _calculate_skewness(self, values):
        """Calculate skewness"""
        import numpy as np
        n = len(values)
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return 0
        
        return (np.sum(((values - mean) / std) ** 3)) / n
    
    def _calculate_kurtosis(self, values):
        """Calculate kurtosis"""
        import numpy as np
        n = len(values)
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return 0
        
        return (np.sum(((values - mean) / std) ** 4)) / n - 3  # Excess kurtosis
    
    def _show_fft_analysis(self):
        """Show FFT analysis"""
        # Placeholder for FFT analysis
        QMessageBox.information(self.parent(), "FFT Analysis", 
                              "FFT analysis feature coming soon!")
    
    def _show_correlation_analysis(self):
        """Show correlation analysis"""
        # Placeholder for correlation analysis
        QMessageBox.information(self.parent(), "Correlation Analysis", 
                              "Correlation analysis feature coming soon!")
    
    def _has_multiple_series(self) -> bool:
        """Check if multiple series are available"""
        try:
            if not self.dataset_id:
                return False
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)
            return len(dataset.series) > 1
        except:
            return False
    
    def _apply_filter(self, filter_type: str):
        """Apply filter to data"""
        # Placeholder for filter implementation
        QMessageBox.information(self.parent(), f"{filter_type.title()} Filter", 
                              f"{filter_type.title()} filter feature coming soon!")
    
    def _detect_outliers(self):
        """Detect outliers in data"""
        # Placeholder for outlier detection
        QMessageBox.information(self.parent(), "Outlier Detection", 
                              "Outlier detection feature coming soon!")
    
    def _toggle_grid(self):
        """Toggle plot grid"""
        # Signal to be handled by plot widget
        pass
    
    def _toggle_legend(self):
        """Toggle plot legend"""
        # Signal to be handled by plot widget
        pass
    
    def _add_annotation(self):
        """Add annotation at plot position"""
        if not self.plot_position:
            return
        
        text, ok = QInputDialog.getText(self.parent(), 
                                       "Add Annotation", 
                                       "Annotation text:")
        if ok and text:
            self.create_annotation_requested.emit(
                self.plot_position.x(), 
                self.plot_position.y(), 
                text)
    
    def _clear_selection(self):
        """Clear current selection"""
        # Signal to be handled by selection system
        pass
    
    def _select_all(self):
        """Select all data points"""
        # Signal to be handled by selection system
        pass
    
    def _invert_selection(self):
        """Invert current selection"""
        # Signal to be handled by selection system
        pass
    
    def _copy_to_clipboard(self):
        """Copy plot or data to clipboard"""
        # Placeholder for clipboard functionality
        QMessageBox.information(self.parent(), "Copy to Clipboard", 
                              "Copy to clipboard feature coming soon!")
    
    def _duplicate_series(self):
        """Duplicate current series"""
        if self.dataset_id and self.series_id:
            self.duplicate_series_requested.emit(self.dataset_id, self.series_id)
    
    def _hide_series(self):
        """Hide current series"""
        # Signal to be handled by plot widget
        pass
    
    def _remove_series(self):
        """Remove current series"""
        if self.dataset_id and self.series_id:
            reply = QMessageBox.question(self.parent(), 
                                       "Remove Series",
                                       f"Remove series '{self.series_id}'?",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.remove_series_requested.emit(self.dataset_id, self.series_id)
    
    def _show_series_properties(self):
        """Show series properties dialog"""
        # Placeholder for series properties
        QMessageBox.information(self.parent(), "Series Properties", 
                              "Series properties dialog coming soon!")


def create_plot_context_menu(session_state: SessionState, signal_hub: SignalHub,
                           plot_position: Optional[QPointF] = None,
                           dataset_id: Optional[DatasetID] = None, 
                           series_id: Optional[SeriesID] = None,
                           parent: Optional[QWidget] = None) -> PlotContextMenu:
    """
    Factory function to create plot context menu.
    
    Args:
        session_state: Current session state
        signal_hub: Signal communication hub
        plot_position: Position in plot coordinates
        dataset_id: Dataset ID for series-specific actions
        series_id: Series ID for series-specific actions
        parent: Parent widget
        
    Returns:
        Configured PlotContextMenu instance
    """
    return PlotContextMenu(
        session_state=session_state,
        signal_hub=signal_hub,
        plot_position=plot_position,
        dataset_id=dataset_id,
        series_id=series_id,
        parent=parent
    )