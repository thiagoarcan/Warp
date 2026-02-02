"""
ConfigPanel - Configuration and operations panel for Platform Base v2.0

Provides interface for data processing operations and parameter configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class InterpolationConfigWidget(QWidget):
    """Interpolation configuration widget"""

    parameters_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Method selection
        method_layout = QFormLayout()

        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "linear", "spline_cubic", "smoothing_spline",
            "resample_grid", "mls", "gpr", "lomb_scargle",
        ])
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        method_layout.addRow("Method:", self.method_combo)

        layout.addLayout(method_layout)

        # Parameters widget (changes based on method)
        self.params_widget = QWidget()
        self.params_layout = QFormLayout(self.params_widget)
        layout.addWidget(self.params_widget)

        # Initialize with linear parameters
        self._setup_linear_params()

    def _on_method_changed(self, method: str):
        """Handle method change"""
        # Clear existing parameters
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Setup parameters for selected method
        if method == "linear":
            self._setup_linear_params()
        elif method == "spline_cubic":
            self._setup_spline_params()
        elif method == "gpr":
            self._setup_gpr_params()
        # Add more methods as needed

        self._emit_parameters()

    def _setup_linear_params(self):
        """Setup linear interpolation parameters"""
        self.fill_value_check = QCheckBox("Use fill value")
        self.params_layout.addRow("Fill Strategy:", self.fill_value_check)

        self.fill_value_spin = QDoubleSpinBox()
        self.fill_value_spin.setRange(-1e10, 1e10)
        self.fill_value_spin.setValue(0.0)
        self.fill_value_spin.setEnabled(False)
        self.params_layout.addRow("Fill Value:", self.fill_value_spin)

        self.fill_value_check.toggled.connect(self.fill_value_spin.setEnabled)
        self.fill_value_check.toggled.connect(self._emit_parameters)
        self.fill_value_spin.valueChanged.connect(self._emit_parameters)

    def _setup_spline_params(self):
        """Setup spline interpolation parameters"""
        self.smoothing_spin = QDoubleSpinBox()
        self.smoothing_spin.setRange(0.0, 1000.0)
        self.smoothing_spin.setValue(0.0)
        self.smoothing_spin.valueChanged.connect(self._emit_parameters)
        self.params_layout.addRow("Smoothing Factor:", self.smoothing_spin)

        self.order_spin = QSpinBox()
        self.order_spin.setRange(1, 5)
        self.order_spin.setValue(3)
        self.order_spin.valueChanged.connect(self._emit_parameters)
        self.params_layout.addRow("Spline Order:", self.order_spin)

    def _setup_gpr_params(self):
        """Setup GPR parameters"""
        self.kernel_combo = QComboBox()
        self.kernel_combo.addItems(["rbf", "matern", "linear"])
        self.kernel_combo.currentTextChanged.connect(self._emit_parameters)
        self.params_layout.addRow("Kernel:", self.kernel_combo)

        self.length_scale_spin = QDoubleSpinBox()
        self.length_scale_spin.setRange(0.1, 100.0)
        self.length_scale_spin.setValue(1.0)
        self.length_scale_spin.valueChanged.connect(self._emit_parameters)
        self.params_layout.addRow("Length Scale:", self.length_scale_spin)

    def _emit_parameters(self):
        """Emit current parameters"""
        params = self.get_parameters()
        self.parameters_changed.emit(params)

    def get_parameters(self) -> dict[str, Any]:
        """Get current parameters"""
        method = self.method_combo.currentText()
        params = {"method": method}

        if method == "linear":
            if hasattr(self, "fill_value_check") and self.fill_value_check.isChecked():
                params["fill_value"] = self.fill_value_spin.value()
        elif method == "spline_cubic":
            if hasattr(self, "smoothing_spin"):
                params["smoothing_factor"] = self.smoothing_spin.value()
                params["spline_order"] = self.order_spin.value()
        elif method == "gpr" and hasattr(self, "kernel_combo"):
            params["kernel"] = self.kernel_combo.currentText()
            params["length_scale"] = self.length_scale_spin.value()

        return params


class CalculusConfigWidget(QWidget):
    """Calculus operations configuration widget"""

    parameters_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Operation selection
        operation_layout = QFormLayout()

        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "derivative_1st", "derivative_2nd", "derivative_3rd",
            "integral", "area_under_curve",
        ])
        self.operation_combo.currentTextChanged.connect(self._on_operation_changed)
        operation_layout.addRow("Operation:", self.operation_combo)

        layout.addLayout(operation_layout)

        # Parameters
        params_layout = QFormLayout()

        # Smoothing before derivative
        self.smooth_check = QCheckBox("Apply smoothing")
        self.smooth_check.toggled.connect(self._emit_parameters)
        params_layout.addRow("Pre-processing:", self.smooth_check)

        self.smooth_window = QSpinBox()
        self.smooth_window.setRange(3, 51)
        self.smooth_window.setValue(5)
        self.smooth_window.setSingleStep(2)  # Odd numbers only
        self.smooth_window.setEnabled(False)
        self.smooth_window.valueChanged.connect(self._emit_parameters)
        params_layout.addRow("Smooth Window:", self.smooth_window)

        self.smooth_check.toggled.connect(self.smooth_window.setEnabled)

        # Method for derivatives
        self.derivative_method = QComboBox()
        self.derivative_method.addItems(["gradient", "savgol", "finite_diff"])
        self.derivative_method.currentTextChanged.connect(self._emit_parameters)
        params_layout.addRow("Derivative Method:", self.derivative_method)

        layout.addLayout(params_layout)

    def _on_operation_changed(self, operation: str):
        """Handle operation change"""
        # Enable/disable derivative-specific options
        is_derivative = "derivative" in operation
        self.derivative_method.setEnabled(is_derivative)
        self._emit_parameters()

    def _emit_parameters(self):
        """Emit current parameters"""
        params = self.get_parameters()
        self.parameters_changed.emit(params)

    def get_parameters(self) -> dict[str, Any]:
        """Get current parameters"""
        return {
            "operation": self.operation_combo.currentText(),
            "apply_smoothing": self.smooth_check.isChecked(),
            "smooth_window": self.smooth_window.value() if self.smooth_check.isChecked() else None,
            "derivative_method": self.derivative_method.currentText() if self.derivative_method.isEnabled() else None,
        }


class ConfigPanel(QWidget):
    """
    Configuration and operations panel.

    Features:
    - Operation configuration tabs
    - Parameter adjustment widgets
    - Execute operation buttons
    - Operation history
    """

    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub

        self.current_params: dict[str, dict[str, Any]] = {}

        self._setup_ui()
        self._connect_signals()

        logger.debug("config_panel_initialized")

    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Configuration tabs
        self.config_tabs = QTabWidget()

        # Interpolation tab
        self.interp_widget = InterpolationConfigWidget()
        self.interp_widget.parameters_changed.connect(
            lambda params: self._update_params("interpolation", params))
        self.config_tabs.addTab(self.interp_widget, "Interpolation")

        # Calculus tab
        self.calculus_widget = CalculusConfigWidget()
        self.calculus_widget.parameters_changed.connect(
            lambda params: self._update_params("calculus", params))
        self.config_tabs.addTab(self.calculus_widget, "Calculus")

        # Synchronization tab
        self.sync_widget = self._create_sync_widget()
        self.config_tabs.addTab(self.sync_widget, "Synchronization")

        layout.addWidget(self.config_tabs)

        # Execute buttons
        buttons_layout = QHBoxLayout()

        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self._execute_operation)
        self.execute_btn.setEnabled(False)
        buttons_layout.addWidget(self.execute_btn)

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._preview_operation)
        self.preview_btn.setEnabled(False)
        buttons_layout.addWidget(self.preview_btn)

        layout.addLayout(buttons_layout)

        # Operation history
        history_group = QGroupBox("Operation History")
        history_layout = QVBoxLayout(history_group)

        self.history_list = QTextEdit()
        self.history_list.setMaximumHeight(100)
        self.history_list.setReadOnly(True)
        history_layout.addWidget(self.history_list)

        layout.addWidget(history_group)

        # Status
        self.status_label = QLabel("Select data to enable operations")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

    def _create_sync_widget(self) -> QWidget:
        """Create synchronization configuration widget"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Sync method
        self.sync_method_combo = QComboBox()
        self.sync_method_combo.addItems([
            "common_grid_interpolate", "kalman_align", "dtw_align",
        ])
        self.sync_method_combo.currentTextChanged.connect(
            lambda: self._update_params("synchronization", self._get_sync_params()))
        layout.addRow("Method:", self.sync_method_combo)

        # Target frequency
        self.target_freq_spin = QDoubleSpinBox()
        self.target_freq_spin.setRange(0.001, 1000.0)
        self.target_freq_spin.setValue(1.0)
        self.target_freq_spin.setSuffix(" Hz")
        self.target_freq_spin.valueChanged.connect(
            lambda: self._update_params("synchronization", self._get_sync_params()))
        layout.addRow("Target Frequency:", self.target_freq_spin)

        # Interpolation method for resampling
        self.resample_method_combo = QComboBox()
        self.resample_method_combo.addItems(["linear", "cubic", "nearest"])
        self.resample_method_combo.currentTextChanged.connect(
            lambda: self._update_params("synchronization", self._get_sync_params()))
        layout.addRow("Resample Method:", self.resample_method_combo)

        return widget

    def _get_sync_params(self) -> dict[str, Any]:
        """Get synchronization parameters"""
        return {
            "method": self.sync_method_combo.currentText(),
            "target_frequency": self.target_freq_spin.value(),
            "resample_method": self.resample_method_combo.currentText(),
        }

    def _connect_signals(self):
        """Connect signals"""
        # Listen to selection changes
        self.session_state.selection_changed.connect(self._on_selection_changed)

        # Listen to processing state changes
        self.session_state.processing_state_changed.connect(self._on_processing_changed)

        # Listen to operation completion
        self.signal_hub.operation_completed.connect(self._on_operation_completed)
        self.signal_hub.operation_failed.connect(self._on_operation_failed)

    @pyqtSlot(str, dict)
    def _update_params(self, operation_type: str, params: dict[str, Any]):
        """Update parameters for operation type"""
        self.current_params[operation_type] = params
        logger.debug("params_updated", operation_type=operation_type, params=params)

    @pyqtSlot()
    def _execute_operation(self):
        """Execute the configured operation"""
        current_tab = self.config_tabs.currentIndex()
        tab_names = ["interpolation", "calculus", "synchronization"]
        operation_type = tab_names[current_tab]

        if operation_type not in self.current_params:
            self.status_label.setText("No parameters configured")
            return

        # Check if data is selected
        selection = self.session_state.selection
        if not selection.dataset_id or not selection.series_ids:
            self.status_label.setText("No data selected")
            return

        # Generate operation ID
        import time
        operation_id = f"{operation_type}_{int(time.time())}"

        # Start operation
        self.session_state.start_operation(
            operation_id, operation_type, self.current_params[operation_type],
        )

        # Emit signal to start processing
        self.signal_hub.emit_operation_started(operation_type, operation_id)

        self.status_label.setText(f"Executing {operation_type}...")
        self.execute_btn.setEnabled(False)

        logger.info("operation_started_from_config",
                   operation_type=operation_type, operation_id=operation_id)

    @pyqtSlot()
    def _preview_operation(self):
        """Preview the operation result"""
        operation_type = self.operation_combo.currentText()
        if not operation_type:
            self.status_label.setText("No operation selected")
            return

        selection = self.session_state.selection
        if not selection.dataset_id:
            self.status_label.setText("No dataset selected")
            return

        try:
            # Preparar preview
            params = self.current_params.get(operation_type, {})
            dataset = self.session_state.dataset_store.get_dataset(selection.dataset_id)
            series_names = [s.name for s in dataset.series if s.id in selection.series_ids]

            # Construir preview text
            preview_text = f"Operation: {operation_type}\n"
            preview_text += f"Series: {', '.join(series_names)}\n"
            preview_text += "Parameters:\n"
            for key, value in params.items():
                preview_text += f"  {key}: {value}\n"

            self.status_label.setText("Ready to execute")
            logger.info(f"operation_preview: {operation_type}")

        except Exception as e:
            logger.exception(f"Preview failed: {e}")
            self.status_label.setText(f"Preview failed: {str(e)}")

    @pyqtSlot(object)
    def _on_selection_changed(self, selection_state):
        """Handle selection changes"""
        has_selection = bool(selection_state.dataset_id and
                            len(selection_state.series_ids) > 0)

        self.execute_btn.setEnabled(has_selection)
        self.preview_btn.setEnabled(has_selection)

        if has_selection:
            n_series = len(selection_state.series_ids)
            self.status_label.setText(f"{n_series} series selected")
        else:
            self.status_label.setText("Select data to enable operations")

    @pyqtSlot(object)
    def _on_processing_changed(self, processing_state):
        """Handle processing state changes"""
        n_active = len(processing_state.active_operations)

        if n_active > 0:
            self.status_label.setText(f"{n_active} operations running...")
            self.execute_btn.setEnabled(False)
        else:
            # Re-enable based on selection
            selection = self.session_state.selection
            has_selection = (selection.dataset_id and
                           len(selection.series_ids) > 0)
            self.execute_btn.setEnabled(has_selection)

    @pyqtSlot(str, object)
    def _on_operation_completed(self, operation_id: str, result):
        """Handle operation completion"""
        self.status_label.setText("Operation completed successfully")
        self.execute_btn.setEnabled(True)

        # Add to history
        timestamp = str(result.get("timestamp", "Unknown")).split(".")[0] if isinstance(result, dict) else "Unknown"
        self.history_list.append(f"✓ {operation_id} completed at {timestamp}")

        logger.info("operation_completed_in_config", operation_id=operation_id)

    @pyqtSlot(str, str)
    def _on_operation_failed(self, operation_id: str, error_message: str):
        """Handle operation failure"""
        self.status_label.setText(f"Operation failed: {error_message}")
        self.execute_btn.setEnabled(True)

        # Add to history
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history_list.append(f"✗ {operation_id} failed at {timestamp}: {error_message}")

        logger.error("operation_failed_in_config",
                    operation_id=operation_id, error=error_message)
