"""
Plot Context Menu System - Platform Base v2.0

Provides rich context menus for plot interactions with:
- Mathematical analysis tools
- Data manipulation options
- Export and visualization controls
- Selection and annotation features
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.core.models import DatasetID, SeriesID
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class MathAnalysisDialog(QDialog, UiLoaderMixin):
    """
    Dialog for mathematical analysis operations
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "mathAnalysisDialog.ui"

    operation_requested = pyqtSignal(str, dict)  # operation_name, parameters

    def __init__(self, operation: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.operation = operation
        self.setWindowTitle(f"{tr('Mathematical Analysis')} - {operation.title()}")
        self.setModal(True)
        self.resize(350, 200)

        # Carrega do arquivo .ui ou lança erro
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Widgets comuns
        apply_btn = self.findChild(QPushButton, "applyBtn")
        cancel_btn = self.findChild(QPushButton, "cancelBtn")
        
        # Busca widgets específicos por operação
        self.derivative_order = self.findChild(QSpinBox, "derivativeOrder")
        self.derivative_method = self.findChild(QComboBox, "derivativeMethod")
        self.enable_smoothing = self.findChild(QCheckBox, "enableSmoothing")
        self.smoothing_window = self.findChild(QSpinBox, "smoothingWindow")
        self.integral_method = self.findChild(QComboBox, "integralMethod")
        self.smooth_method = self.findChild(QComboBox, "smoothMethod")
        self.window_size = self.findChild(QSpinBox, "windowSize")
        self.polyorder = self.findChild(QSpinBox, "polyorder")
        
        # Conecta sinais
        if apply_btn:
            apply_btn.clicked.connect(self._apply_operation)
            apply_btn.setDefault(True)
        if cancel_btn:
            cancel_btn.clicked.connect(self.reject)
        if self.enable_smoothing and self.smoothing_window:
            self.enable_smoothing.toggled.connect(self.smoothing_window.setEnabled)

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
                    "params": {"window_length": self.smoothing_window.value()},
                }

        elif self.operation == "integral":
            params = {
                "method": self.integral_method.currentText(),
            }

        elif self.operation == "smooth":
            params = {
                "method": self.smooth_method.currentText(),
                "window_size": self.window_size.value(),
                "polyorder": self.polyorder.value(),
            }

        elif self.operation == "interpolate":
            params = {
                "method": self.interp_method.currentText(),
            }

        elif self.operation == "resample":
            params = {
                "method": self.resample_method.currentText(),
                "n_points": self.target_points.value(),
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
                 plot_position: QPointF | None = None,
                 dataset_id: DatasetID | None = None,
                 series_id: SeriesID | None = None,
                 parent: QWidget | None = None):
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
        math_menu = self.addMenu(tr("📊 Mathematical Analysis"))
        self._setup_math_menu(math_menu)

        # Data Processing submenu
        processing_menu = self.addMenu(tr("🔧 Data Processing"))
        self._setup_processing_menu(processing_menu)

        self.addSeparator()

        # Visualization controls
        viz_menu = self.addMenu(tr("👁️ Visualization"))
        self._setup_visualization_menu(viz_menu)

        self.addSeparator()

        # Selection tools
        self._setup_selection_menu()

        self.addSeparator()

        # Export options
        export_menu = self.addMenu(tr("💾 Export"))
        self._setup_export_menu(export_menu)

        self.addSeparator()

        # Series management (if series context available)
        if self.dataset_id and self.series_id:
            self._setup_series_menu()

    def _setup_math_menu(self, menu: QMenu):
        """Setup mathematical analysis menu"""
        # Derivatives
        derivative_action = menu.addAction(tr("📈 Calculate Derivative..."))
        derivative_action.triggered.connect(
            lambda: self._show_analysis_dialog("derivative"))

        # Integrals
        integral_action = menu.addAction(tr("📉 Calculate Integral..."))
        integral_action.triggered.connect(
            lambda: self._show_analysis_dialog("integral"))

        menu.addSeparator()

        # Statistical analysis
        stats_action = menu.addAction(tr("📊 Show Statistics"))
        stats_action.triggered.connect(self._show_statistics)

        # FFT Analysis
        fft_action = menu.addAction(tr("🌊 FFT Analysis"))
        fft_action.triggered.connect(self._show_fft_analysis)

        # Correlation analysis (if multiple series)
        if self._has_multiple_series():
            correlation_action = menu.addAction(tr("🔗 Correlation Analysis"))
            correlation_action.triggered.connect(self._show_correlation_analysis)

    def _setup_processing_menu(self, menu: QMenu):
        """Setup data processing menu"""
        # Smoothing
        smooth_action = menu.addAction(tr("🌊 Smooth Data..."))
        smooth_action.triggered.connect(
            lambda: self._show_analysis_dialog("smooth"))

        # Interpolation
        interp_action = menu.addAction(tr("🎯 Interpolate Missing Data..."))
        interp_action.triggered.connect(
            lambda: self._show_analysis_dialog("interpolate"))

        # Resampling/Downsampling
        resample_action = menu.addAction(tr("📏 Resample Data..."))
        resample_action.triggered.connect(
            lambda: self._show_analysis_dialog("resample"))

        menu.addSeparator()

        # Filtering
        filter_menu = menu.addMenu(tr("🔍 Filters"))

        lowpass_action = filter_menu.addAction(tr("Low-pass Filter"))
        lowpass_action.triggered.connect(
            lambda: self._apply_filter("lowpass"))

        highpass_action = filter_menu.addAction(tr("High-pass Filter"))
        highpass_action.triggered.connect(
            lambda: self._apply_filter("highpass"))

        bandpass_action = filter_menu.addAction(tr("Band-pass Filter"))
        bandpass_action.triggered.connect(
            lambda: self._apply_filter("bandpass"))

        # Outlier detection
        outlier_action = menu.addAction(tr("🎯 Detect Outliers"))
        outlier_action.triggered.connect(self._detect_outliers)

    def _setup_visualization_menu(self, menu: QMenu):
        """Setup visualization menu"""
        # Zoom controls
        zoom_selection_action = menu.addAction(tr("🔍 Zoom to Selection"))
        zoom_selection_action.triggered.connect(self.zoom_to_selection_requested.emit)
        zoom_selection_action.setShortcut(QKeySequence("Ctrl+Z"))

        reset_zoom_action = menu.addAction(tr("🔄 Reset Zoom"))
        reset_zoom_action.triggered.connect(self.reset_zoom_requested.emit)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+R"))

        menu.addSeparator()

        # Grid and styling
        grid_action = menu.addAction(tr("⊞ Toggle Grid"))
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self._toggle_grid)

        legend_action = menu.addAction(tr("📝 Toggle Legend"))
        legend_action.setCheckable(True)
        legend_action.setChecked(True)
        legend_action.triggered.connect(self._toggle_legend)

        # Annotations
        if self.plot_position:
            menu.addSeparator()
            annotate_action = menu.addAction(tr("📝 Add Annotation..."))
            annotate_action.triggered.connect(self._add_annotation)

    def _setup_selection_menu(self):
        """Setup selection tools menu"""
        # Clear selection
        clear_selection_action = self.addAction(tr("🗑️ Clear Selection"))
        clear_selection_action.triggered.connect(self._clear_selection)
        clear_selection_action.setShortcut(QKeySequence("Escape"))

        # Select all
        select_all_action = self.addAction(tr("☑️ Select All"))
        select_all_action.triggered.connect(self._select_all)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))

        # Invert selection
        invert_selection_action = self.addAction(tr("🔄 Invert Selection"))
        invert_selection_action.triggered.connect(self._invert_selection)
        invert_selection_action.setShortcut(QKeySequence("Ctrl+I"))

    def _setup_export_menu(self, menu: QMenu):
        """Setup export menu"""
        # Plot export
        plot_export_menu = menu.addMenu(tr("🖼️ Export Plot"))

        for fmt in ["PNG", "SVG", "PDF", "JPEG"]:
            action = plot_export_menu.addAction(fmt)
            action.triggered.connect(
                lambda checked, f=fmt: self.export_plot_requested.emit(f.lower()))

        # Data export
        data_action = menu.addAction(tr("📊 Export Data..."))
        data_action.triggered.connect(self.export_data_requested.emit)

        # Copy to clipboard
        copy_action = menu.addAction(tr("📋 Copy to Clipboard"))
        copy_action.triggered.connect(self._copy_to_clipboard)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))

    def _setup_series_menu(self):
        """Setup series management menu"""
        # Duplicate series
        duplicate_action = self.addAction(tr("📄 Duplicate Series"))
        duplicate_action.triggered.connect(self._duplicate_series)

        # Hide/show series
        hide_action = self.addAction(tr("👁️ Hide Series"))
        hide_action.triggered.connect(self._hide_series)

        # Remove series
        remove_action = self.addAction(tr("🗑️ Remove Series"))
        remove_action.triggered.connect(self._remove_series)

        self.addSeparator()

        # Series properties
        properties_action = self.addAction(tr("⚙️ Series Properties..."))
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
                "Count": len(values),
                "Mean": np.mean(values),
                "Std Dev": np.std(values),
                "Min": np.min(values),
                "Max": np.max(values),
                "Median": np.median(values),
                "Q25": np.percentile(values, 25),
                "Q75": np.percentile(values, 75),
                "Skewness": self._calculate_skewness(values),
                "Kurtosis": self._calculate_kurtosis(values),
            }

            # Show in message box
            stats_text = "\n".join([f"{k}: {v:.6g}" for k, v in stats.items()])
            QMessageBox.information(self.parent(),
                                  f"Statistics - {series.name}",
                                  stats_text)

        except Exception as e:
            logger.exception("statistics_calculation_failed", error=str(e))
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
        """Show FFT analysis of selected series"""
        if not self.dataset_id or not self.series_id:
            QMessageBox.warning(self.parent(), "Warning",
                              "Please select a series first.")
            return

        try:
            import numpy as np

            # Get series data
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)
            series = dataset.series[self.series_id]
            values = series.values
            timestamps = dataset.timestamps

            # Remove NaN values
            valid_mask = ~np.isnan(values)
            clean_values = values[valid_mask]
            clean_times = timestamps[valid_mask] if len(timestamps) == len(values) else None

            if len(clean_values) < 4:
                QMessageBox.warning(self.parent(), "FFT Analysis",
                                  "Insufficient data points for FFT (minimum 4).")
                return

            # Calculate sampling frequency
            if clean_times is not None and len(clean_times) > 1:
                dt = np.mean(np.diff(clean_times))
                sample_freq = 1.0 / dt if dt > 0 else 1.0
            else:
                sample_freq = 1.0

            # Compute FFT
            n = len(clean_values)
            fft_vals = np.fft.rfft(clean_values - np.mean(clean_values))
            fft_freq = np.fft.rfftfreq(n, d=1.0/sample_freq)
            fft_magnitude = np.abs(fft_vals) * 2.0 / n

            # Find dominant frequencies
            sorted_indices = np.argsort(fft_magnitude[1:])[::-1] + 1  # Exclude DC
            top_freqs = fft_freq[sorted_indices[:5]]
            top_mags = fft_magnitude[sorted_indices[:5]]

            # Build results message
            msg = f"""<h3>FFT Analysis: {series.name}</h3>
<table>
<tr><td><b>Sample Frequency:</b></td><td>{sample_freq:.4g} Hz</td></tr>
<tr><td><b>Points Analyzed:</b></td><td>{n:,}</td></tr>
<tr><td><b>Frequency Resolution:</b></td><td>{sample_freq/n:.4g} Hz</td></tr>
</table>
<h4>Dominant Frequencies</h4>
<table>
<tr><th>Rank</th><th>Frequency (Hz)</th><th>Magnitude</th></tr>"""

            for i, (freq, mag) in enumerate(zip(top_freqs, top_mags), 1):
                if mag > 1e-10:  # Only show significant peaks
                    msg += f"<tr><td>{i}</td><td>{freq:.4g}</td><td>{mag:.4g}</td></tr>"

            msg += "</table>"

            # Show dialog with option to plot
            dialog = QMessageBox(self.parent())
            dialog.setWindowTitle("FFT Analysis")
            dialog.setTextFormat(Qt.TextFormat.RichText)
            dialog.setText(msg)
            dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Save)
            dialog.button(QMessageBox.StandardButton.Save).setText("Plot Spectrum")

            result = dialog.exec()

            if result == QMessageBox.StandardButton.Save:
                # Emit signal to create spectrum plot
                self.math_operation_requested.emit(
                    "fft_spectrum",
                    {"frequencies": fft_freq.tolist(), "magnitudes": fft_magnitude.tolist()},
                    self.dataset_id,
                    self.series_id,
                )

            logger.info("fft_analysis_completed", series=series.name, sample_freq=sample_freq)

        except Exception as e:
            logger.exception("fft_analysis_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", f"FFT analysis failed: {e}")

    def _show_correlation_analysis(self):
        """Show correlation analysis between series"""
        if not self.dataset_id:
            QMessageBox.warning(self.parent(), "Warning",
                              "Please select a dataset first.")
            return

        try:
            import numpy as np

            # Get all series in dataset
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)

            if len(dataset.series) < 2:
                QMessageBox.warning(self.parent(), "Correlation Analysis",
                                  "At least 2 series required for correlation analysis.")
                return

            series_names = list(dataset.series.keys())
            series_values = [dataset.series[name].values for name in series_names]

            # Calculate correlation matrix
            n_series = len(series_names)
            corr_matrix = np.zeros((n_series, n_series))

            for i in range(n_series):
                for j in range(n_series):
                    # Handle different lengths and NaN values
                    min_len = min(len(series_values[i]), len(series_values[j]))
                    vals_i = series_values[i][:min_len]
                    vals_j = series_values[j][:min_len]

                    # Remove NaN pairs
                    valid_mask = ~(np.isnan(vals_i) | np.isnan(vals_j))
                    if np.sum(valid_mask) > 1:
                        corr_matrix[i, j] = np.corrcoef(
                            vals_i[valid_mask],
                            vals_j[valid_mask]
                        )[0, 1]
                    else:
                        corr_matrix[i, j] = np.nan

            # Build correlation table
            msg = f"<h3>Correlation Matrix</h3><p>Dataset: {self.dataset_id}</p>"
            msg += "<table border='1' cellpadding='4'><tr><th></th>"

            # Header row
            for name in series_names:
                short_name = name[:10] + "..." if len(name) > 10 else name
                msg += f"<th>{short_name}</th>"
            msg += "</tr>"

            # Data rows
            for i, name_i in enumerate(series_names):
                short_name = name_i[:10] + "..." if len(name_i) > 10 else name_i
                msg += f"<tr><td><b>{short_name}</b></td>"
                for j in range(n_series):
                    val = corr_matrix[i, j]
                    if np.isnan(val):
                        cell = "N/A"
                        color = "#888888"
                    else:
                        cell = f"{val:.3f}"
                        # Color code: green for positive, red for negative
                        if val > 0.7:
                            color = "#228B22"
                        elif val < -0.7:
                            color = "#DC143C"
                        elif val > 0.3:
                            color = "#90EE90"
                        elif val < -0.3:
                            color = "#FFA07A"
                        else:
                            color = "#FFFFFF"
                    msg += f"<td style='background-color:{color}'>{cell}</td>"
                msg += "</tr>"
            msg += "</table>"

            # Show results
            dialog = QMessageBox(self.parent())
            dialog.setWindowTitle("Correlation Analysis")
            dialog.setTextFormat(Qt.TextFormat.RichText)
            dialog.setText(msg)
            dialog.exec()

            logger.info("correlation_analysis_completed", n_series=n_series)

        except Exception as e:
            logger.exception("correlation_analysis_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", f"Correlation analysis failed: {e}")

    def _has_multiple_series(self) -> bool:
        """Check if multiple series are available"""
        try:
            if not self.dataset_id:
                return False
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)
            return len(dataset.series) > 1
        except Exception:
            return False

    def _apply_filter(self, filter_type: str):
        """Apply filter to data"""
        if not self.dataset_id or not self.series_id:
            QMessageBox.warning(self.parent(), "Warning",
                              "Please select a series first.")
            return

        try:
            from platform_base.streaming.filters import ButterworthFilter, FilterType

            # Get cutoff frequency from user
            cutoff, ok = QInputDialog.getDouble(
                self.parent(),
                f"{filter_type.title()} Filter",
                "Cutoff frequency (Hz):",
                value=10.0,
                min=0.1,
                max=1000.0,
                decimals=2,
            )

            if not ok:
                return

            # Map filter type
            filter_map = {
                "lowpass": FilterType.LOWPASS,
                "highpass": FilterType.HIGHPASS,
                "bandpass": FilterType.BANDPASS,
            }

            if filter_type not in filter_map:
                QMessageBox.warning(self.parent(), "Error", f"Unknown filter type: {filter_type}")
                return

            # Emit signal to apply filter
            self.math_operation_requested.emit(
                "filter",
                {"filter_type": filter_type, "cutoff": cutoff},
                self.dataset_id,
                self.series_id,
            )

            logger.info("filter_requested", filter_type=filter_type, cutoff=cutoff)

        except Exception as e:
            logger.exception("filter_apply_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", f"Failed to apply filter: {e}")

    def _detect_outliers(self):
        """Detect outliers in data"""
        if not self.dataset_id or not self.series_id:
            QMessageBox.warning(self.parent(), "Warning",
                              "Please select a series first.")
            return

        try:
            # Get threshold from user
            threshold, ok = QInputDialog.getDouble(
                self.parent(),
                "Outlier Detection",
                "Z-score threshold:",
                value=3.0,
                min=1.0,
                max=10.0,
                decimals=1,
            )

            if not ok:
                return

            # Get series data
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)
            series = dataset.series[self.series_id]
            values = series.values

            import numpy as np

            # Calculate z-scores
            mean = np.nanmean(values)
            std = np.nanstd(values)

            if std == 0:
                QMessageBox.information(self.parent(), "Outlier Detection",
                                      "No outliers detected (constant data).")
                return

            z_scores = np.abs((values - mean) / std)
            outlier_mask = z_scores > threshold
            outlier_count = np.sum(outlier_mask)
            outlier_indices = np.where(outlier_mask)[0]

            # Show results
            if outlier_count == 0:
                QMessageBox.information(self.parent(), "Outlier Detection",
                                      f"No outliers detected with threshold {threshold}.")
            else:
                msg = f"Found {outlier_count} outliers with threshold {threshold}.\n\n"
                msg += f"Outlier indices (first 10): {outlier_indices[:10].tolist()}"
                if outlier_count > 10:
                    msg += f"\n... and {outlier_count - 10} more"

                reply = QMessageBox.question(
                    self.parent(),
                    "Outlier Detection",
                    msg + "\n\nRemove outliers (set to NaN)?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.math_operation_requested.emit(
                        "remove_outliers",
                        {"threshold": threshold, "method": "zscore"},
                        self.dataset_id,
                        self.series_id,
                    )

            logger.info("outlier_detection_completed", count=outlier_count)

        except Exception as e:
            logger.exception("outlier_detection_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", f"Outlier detection failed: {e}")

    def _toggle_grid(self):
        """Toggle plot grid"""
        parent_widget = self.parent()
        if hasattr(parent_widget, "showGrid"):
            # Get current grid state and toggle
            current_state = getattr(parent_widget, "_grid_visible", True)
            new_state = not current_state
            parent_widget.showGrid(new_state, new_state, alpha=0.3)
            parent_widget._grid_visible = new_state
            logger.debug("grid_toggled", visible=new_state)

    def _toggle_legend(self):
        """Toggle plot legend"""
        parent_widget = self.parent()
        if hasattr(parent_widget, "legend") and parent_widget.legend is not None:
            legend = parent_widget.legend
            if legend.isVisible():
                legend.hide()
            else:
                legend.show()
            logger.debug("legend_toggled", visible=legend.isVisible())
        elif hasattr(parent_widget, "addLegend"):
            parent_widget.addLegend()
            logger.debug("legend_added")

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
        # Clear selection in session state
        self.session_state.clear_selection()

        # Clear visual selection on plot
        parent_widget = self.parent()
        if hasattr(parent_widget, "clear_selection"):
            parent_widget.clear_selection()
        elif hasattr(parent_widget, "_selection_item") and parent_widget._selection_item:
            parent_widget.removeItem(parent_widget._selection_item)
            parent_widget._selection_item = None

        logger.debug("selection_cleared")

    def _select_all(self):
        """Select all data points"""
        parent_widget = self.parent()

        if hasattr(parent_widget, "_series_data") and parent_widget._series_data:
            # Get all series data
            for series_id, series_data in parent_widget._series_data.items():
                if "x_data" in series_data and "y_data" in series_data:
                    x_data = series_data["x_data"]
                    # Create selection for entire range
                    if len(x_data) > 0:
                        x_min, x_max = x_data[0], x_data[-1]
                        if hasattr(parent_widget, "_start_selection"):
                            parent_widget._start_selection(x_min)
                            parent_widget._update_selection(x_max)
                            parent_widget.finish_selection()
                        break

        logger.debug("select_all_requested")

    def _invert_selection(self):
        """Invert current selection"""
        # Get current time window selection
        time_window = self.session_state.selection.time_window

        if time_window is None:
            # No selection to invert
            QMessageBox.information(self.parent(), "Invert Selection",
                                  "No selection to invert. Select a region first.")
            return

        parent_widget = self.parent()
        if hasattr(parent_widget, "_series_data") and parent_widget._series_data:
            # Get full data range
            for series_data in parent_widget._series_data.values():
                if "x_data" in series_data:
                    x_data = series_data["x_data"]
                    if len(x_data) > 0:
                        full_start, full_end = x_data[0], x_data[-1]

                        # Create inverted selection (before and after current)
                        # For simplicity, select the larger unselected region
                        before_size = time_window.start - full_start
                        after_size = full_end - time_window.end

                        if before_size > after_size:
                            new_start, new_end = full_start, time_window.start
                        else:
                            new_start, new_end = time_window.end, full_end

                        # Update selection
                        from platform_base.core.models import TimeWindow as TW
                        self.session_state.set_time_window(TW(start=new_start, end=new_end))
                        break

        logger.debug("selection_inverted")

    def _copy_to_clipboard(self):
        """Copy plot or data to clipboard"""
        from PyQt6.QtGui import QGuiApplication, QImage
        from PyQt6.QtWidgets import QApplication

        parent_widget = self.parent()

        try:
            # Try to get plot as image
            if hasattr(parent_widget, "grab"):
                # Capture widget as image
                pixmap = parent_widget.grab()
                QApplication.clipboard().setPixmap(pixmap)
                QMessageBox.information(self.parent(), "Copy to Clipboard",
                                      "Plot image copied to clipboard!")
                logger.info("plot_copied_to_clipboard")
            elif hasattr(parent_widget, "_series_data"):
                # Copy data as text
                import numpy as np

                text_lines = ["Time,Value,Series"]
                for series_id, series_data in parent_widget._series_data.items():
                    if "x_data" in series_data and "y_data" in series_data:
                        x_data = series_data["x_data"]
                        y_data = series_data["y_data"]
                        name = series_data.get("name", series_id)
                        for x, y in zip(x_data[:100], y_data[:100]):  # Limit to first 100 points
                            text_lines.append(f"{x},{y},{name}")

                QApplication.clipboard().setText("\n".join(text_lines))
                QMessageBox.information(self.parent(), "Copy to Clipboard",
                                      f"Data copied to clipboard ({len(text_lines)-1} rows)!")
                logger.info("data_copied_to_clipboard")
            else:
                QMessageBox.warning(self.parent(), "Copy to Clipboard",
                                  "Unable to copy - no data available.")

        except Exception as e:
            logger.exception("copy_to_clipboard_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", f"Copy failed: {e}")

    def _duplicate_series(self):
        """Duplicate current series"""
        if self.dataset_id and self.series_id:
            self.duplicate_series_requested.emit(self.dataset_id, self.series_id)

    def _hide_series(self):
        """Hide current series"""
        if not self.series_id:
            return

        parent_widget = self.parent()
        if hasattr(parent_widget, "_series_data") and self.series_id in parent_widget._series_data:
            series_data = parent_widget._series_data[self.series_id]
            if "plot_item" in series_data:
                plot_item = series_data["plot_item"]
                # Toggle visibility
                current_visible = plot_item.isVisible()
                plot_item.setVisible(not current_visible)
                logger.debug("series_visibility_toggled", series_id=self.series_id, visible=not current_visible)

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
        if not self.dataset_id or not self.series_id:
            QMessageBox.warning(self.parent(), "Warning",
                              "Please select a series first.")
            return

        try:
            dataset = self.session_state.dataset_store.get_dataset(self.dataset_id)
            series = dataset.series[self.series_id]

            import numpy as np

            # Build properties text
            props = f"""<h3>Series Properties</h3>
<table>
<tr><td><b>Name:</b></td><td>{series.name}</td></tr>
<tr><td><b>ID:</b></td><td>{self.series_id}</td></tr>
<tr><td><b>Unit:</b></td><td>{series.unit or 'N/A'}</td></tr>
<tr><td><b>Points:</b></td><td>{len(series.values):,}</td></tr>
<tr><td><b>Min:</b></td><td>{np.nanmin(series.values):.6g}</td></tr>
<tr><td><b>Max:</b></td><td>{np.nanmax(series.values):.6g}</td></tr>
<tr><td><b>Mean:</b></td><td>{np.nanmean(series.values):.6g}</td></tr>
<tr><td><b>Std:</b></td><td>{np.nanstd(series.values):.6g}</td></tr>
<tr><td><b>NaN count:</b></td><td>{np.isnan(series.values).sum():,}</td></tr>
</table>"""

            if series.lineage:
                props += f"""<h4>Lineage</h4>
<table>
<tr><td><b>Operation:</b></td><td>{series.lineage.operation}</td></tr>
<tr><td><b>Origin:</b></td><td>{', '.join(series.lineage.origin_series)}</td></tr>
<tr><td><b>Created:</b></td><td>{series.lineage.timestamp}</td></tr>
</table>"""

            msg = QMessageBox(self.parent())
            msg.setWindowTitle("Series Properties")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText(props)
            msg.exec()

            logger.debug("series_properties_shown", series_id=self.series_id)

        except Exception as e:
            logger.exception("series_properties_failed", error=str(e))
            QMessageBox.warning(self.parent(), "Error", f"Failed to get properties: {e}")


def create_plot_context_menu(session_state: SessionState, signal_hub: SignalHub,
                           plot_position: QPointF | None = None,
                           dataset_id: DatasetID | None = None,
                           series_id: SeriesID | None = None,
                           parent: QWidget | None = None) -> PlotContextMenu:
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
        parent=parent,
    )
