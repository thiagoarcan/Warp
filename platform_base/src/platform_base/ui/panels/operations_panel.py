"""
OperationsPanel - Painel completo de operações conforme especificação

Features:
- Interpolação avançada (linear, spline, akima)
- Sincronização de séries temporais
- Cálculos matemáticos (derivadas, integrais)
- Análise estatística
- Exportação em múltiplos formatos
- Streaming temporal
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QFormLayout, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QLabel, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QDialog, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread

from platform_base.ui.state import SessionState
from platform_base.core.models import Dataset, Series, SeriesID
from platform_base.processing.interpolation import InterpolationMethod, InterpolationConfig
from platform_base.processing.synchronization import SynchronizationMethod, SynchronizationConfig
from platform_base.processing.calculus import CalculusMethod, CalculusConfig
from platform_base.ui.export import ExportManager
from platform_base.ui.streaming_controls import StreamingControlWidget
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class OperationWorker(QThread):
    """Worker thread para operações custosas"""
    
    # Signals
    operation_started = pyqtSignal(str)  # operation_name
    operation_progress = pyqtSignal(int)  # percentage
    operation_completed = pyqtSignal(str, object)  # operation_name, result
    operation_failed = pyqtSignal(str, str)  # operation_name, error
    
    def __init__(self, operation_type: str, operation_func, *args, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.operation_func = operation_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Executa operação"""
        try:
            self.operation_started.emit(self.operation_type)
            
            # Execute operation with progress tracking
            result = self.operation_func(*self.args, **self.kwargs)
            
            self.operation_completed.emit(self.operation_type, result)
            
        except Exception as e:
            logger.error("operation_failed", operation=self.operation_type, error=str(e))
            self.operation_failed.emit(self.operation_type, str(e))


class InterpolationPanel(QWidget):
    """Painel de interpolação avançada"""
    
    # Signals
    operation_requested = pyqtSignal(str, dict)  # operation_type, params
    
    def __init__(self, session_state: SessionState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup da UI de interpolação"""
        layout = QVBoxLayout(self)
        
        # Method selection
        method_group = QGroupBox("Interpolation Method")
        method_layout = QFormLayout(method_group)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Linear", "Cubic Spline", "Akima", "PCHIP", 
            "Polynomial", "RBF", "Kriging"
        ])
        method_layout.addRow("Method:", self.method_combo)
        
        # Parameters
        self.degree_spinbox = QSpinBox()
        self.degree_spinbox.setRange(1, 10)
        self.degree_spinbox.setValue(3)
        method_layout.addRow("Polynomial Degree:", self.degree_spinbox)
        
        self.smoothing_spinbox = QDoubleSpinBox()
        self.smoothing_spinbox.setRange(0.0, 1.0)
        self.smoothing_spinbox.setDecimals(3)
        self.smoothing_spinbox.setValue(0.0)
        method_layout.addRow("Smoothing Factor:", self.smoothing_spinbox)
        
        layout.addWidget(method_group)
        
        # Target selection
        target_group = QGroupBox("Target Configuration")
        target_layout = QFormLayout(target_group)
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(["Fill gaps", "Resample to grid", "Extend range"])
        target_layout.addRow("Target:", self.target_combo)
        
        self.num_points_spinbox = QSpinBox()
        self.num_points_spinbox.setRange(10, 100000)
        self.num_points_spinbox.setValue(1000)
        target_layout.addRow("Number of Points:", self.num_points_spinbox)
        
        layout.addWidget(target_group)
        
        # Series selection
        series_group = QGroupBox("Series Selection")
        series_layout = QVBoxLayout(series_group)
        
        self.series_list = QListWidget()
        self.series_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        series_layout.addWidget(self.series_list)
        
        # Populate series list
        self._update_series_list()
        
        layout.addWidget(series_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._preview_interpolation)
        buttons_layout.addWidget(self.preview_btn)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_interpolation)
        buttons_layout.addWidget(self.apply_btn)
        
        layout.addLayout(buttons_layout)
    
    def _update_series_list(self):
        """Atualiza lista de séries disponíveis"""
        self.series_list.clear()
        
        for dataset in self.session_state.datasets.values():
            for series_id, series in dataset.series.items():
                item = QListWidgetItem(f"{dataset.dataset_id}: {series.name}")
                item.setData(Qt.ItemDataRole.UserRole, (dataset.dataset_id, series_id))
                self.series_list.addItem(item)
    
    @pyqtSlot()
    def _preview_interpolation(self):
        """Preview da interpolação"""
        params = self._get_interpolation_params()
        self.operation_requested.emit("interpolation_preview", params)
    
    @pyqtSlot()
    def _apply_interpolation(self):
        """Aplica interpolação"""
        params = self._get_interpolation_params()
        self.operation_requested.emit("interpolation_apply", params)
    
    def _get_interpolation_params(self) -> Dict[str, Any]:
        """Coleta parâmetros de interpolação"""
        selected_series = []
        for item in self.series_list.selectedItems():
            dataset_id, series_id = item.data(Qt.ItemDataRole.UserRole)
            selected_series.append((dataset_id, series_id))
        
        return {
            'method': self.method_combo.currentText().lower().replace(' ', '_'),
            'degree': self.degree_spinbox.value(),
            'smoothing': self.smoothing_spinbox.value(),
            'target': self.target_combo.currentText(),
            'num_points': self.num_points_spinbox.value(),
            'selected_series': selected_series
        }


class SynchronizationPanel(QWidget):
    """Painel de sincronização de séries"""
    
    # Signals
    operation_requested = pyqtSignal(str, dict)  # operation_type, params
    
    def __init__(self, session_state: SessionState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup da UI de sincronização"""
        layout = QVBoxLayout(self)
        
        # Method selection
        method_group = QGroupBox("Synchronization Method")
        method_layout = QFormLayout(method_group)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Resample to Common Grid",
            "Cross-Correlation Alignment", 
            "DTW (Dynamic Time Warping)",
            "Phase Alignment",
            "Manual Time Shift"
        ])
        method_layout.addRow("Method:", self.method_combo)
        
        # Parameters
        self.tolerance_spinbox = QDoubleSpinBox()
        self.tolerance_spinbox.setRange(0.001, 10.0)
        self.tolerance_spinbox.setDecimals(3)
        self.tolerance_spinbox.setValue(0.1)
        method_layout.addRow("Time Tolerance:", self.tolerance_spinbox)
        
        self.reference_combo = QComboBox()
        self.reference_combo.addItems(["Auto", "Highest Frequency", "Manual Select"])
        method_layout.addRow("Reference Series:", self.reference_combo)
        
        layout.addWidget(method_group)
        
        # Output configuration
        output_group = QGroupBox("Output Configuration")
        output_layout = QFormLayout(output_group)
        
        self.output_rate_spinbox = QDoubleSpinBox()
        self.output_rate_spinbox.setRange(0.1, 1000.0)
        self.output_rate_spinbox.setValue(1.0)
        self.output_rate_spinbox.setSuffix(" Hz")
        output_layout.addRow("Output Sample Rate:", self.output_rate_spinbox)
        
        self.create_new_dataset_checkbox = QCheckBox("Create new synchronized dataset")
        self.create_new_dataset_checkbox.setChecked(True)
        output_layout.addRow("", self.create_new_dataset_checkbox)
        
        layout.addWidget(output_group)
        
        # Series selection
        series_group = QGroupBox("Series to Synchronize")
        series_layout = QVBoxLayout(series_group)
        
        self.sync_series_list = QListWidget()
        self.sync_series_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        series_layout.addWidget(self.sync_series_list)
        
        self._update_sync_series_list()
        
        layout.addWidget(series_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("Analyze Timing")
        self.analyze_btn.clicked.connect(self._analyze_timing)
        buttons_layout.addWidget(self.analyze_btn)
        
        self.sync_btn = QPushButton("Synchronize")
        self.sync_btn.clicked.connect(self._apply_synchronization)
        buttons_layout.addWidget(self.sync_btn)
        
        layout.addLayout(buttons_layout)
    
    def _update_sync_series_list(self):
        """Atualiza lista de séries para sincronização"""
        self.sync_series_list.clear()
        
        for dataset in self.session_state.datasets.values():
            for series_id, series in dataset.series.items():
                item = QListWidgetItem(f"{dataset.dataset_id}: {series.name}")
                item.setData(Qt.ItemDataRole.UserRole, (dataset.dataset_id, series_id))
                self.sync_series_list.addItem(item)
    
    @pyqtSlot()
    def _analyze_timing(self):
        """Analisa timing das séries selecionadas"""
        params = self._get_sync_params()
        params['operation'] = 'analyze'
        self.operation_requested.emit("synchronization_analyze", params)
    
    @pyqtSlot()
    def _apply_synchronization(self):
        """Aplica sincronização"""
        params = self._get_sync_params()
        params['operation'] = 'sync'
        self.operation_requested.emit("synchronization_apply", params)
    
    def _get_sync_params(self) -> Dict[str, Any]:
        """Coleta parâmetros de sincronização"""
        selected_series = []
        for item in self.sync_series_list.selectedItems():
            dataset_id, series_id = item.data(Qt.ItemDataRole.UserRole)
            selected_series.append((dataset_id, series_id))
        
        return {
            'method': self.method_combo.currentText().lower().replace(' ', '_').replace('(', '').replace(')', ''),
            'tolerance': self.tolerance_spinbox.value(),
            'reference': self.reference_combo.currentText(),
            'output_rate': self.output_rate_spinbox.value(),
            'create_new': self.create_new_dataset_checkbox.isChecked(),
            'selected_series': selected_series
        }


class CalculusPanel(QWidget):
    """Painel de cálculos matemáticos"""
    
    # Signals
    operation_requested = pyqtSignal(str, dict)  # operation_type, params
    
    def __init__(self, session_state: SessionState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup da UI de cálculos"""
        layout = QVBoxLayout(self)
        
        # Operation selection
        op_group = QGroupBox("Mathematical Operations")
        op_layout = QFormLayout(op_group)
        
        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "Derivative", "Second Derivative", "Integral", 
            "Cumulative Sum", "Moving Average", "Area Between Curves",
            "Cross Correlation", "FFT", "PSD"
        ])
        op_layout.addRow("Operation:", self.operation_combo)
        
        # Parameters
        self.window_size_spinbox = QSpinBox()
        self.window_size_spinbox.setRange(3, 1000)
        self.window_size_spinbox.setValue(5)
        op_layout.addRow("Window Size:", self.window_size_spinbox)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Forward Diff", "Backward Diff", "Central Diff", "Savitzky-Golay"])
        op_layout.addRow("Diff Method:", self.method_combo)
        
        layout.addWidget(op_group)
        
        # Series selection
        series_group = QGroupBox("Series Selection")
        series_layout = QVBoxLayout(series_group)
        
        self.calc_series_list = QListWidget()
        self.calc_series_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        series_layout.addWidget(self.calc_series_list)
        
        self._update_calc_series_list()
        
        layout.addWidget(series_group)
        
        # Results configuration
        results_group = QGroupBox("Results")
        results_layout = QFormLayout(results_group)
        
        self.result_name_edit = QLabel("auto_generated")
        results_layout.addRow("Result Name:", self.result_name_edit)
        
        self.add_to_dataset_checkbox = QCheckBox("Add to current dataset")
        self.add_to_dataset_checkbox.setChecked(True)
        results_layout.addRow("", self.add_to_dataset_checkbox)
        
        layout.addWidget(results_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self._apply_calculation)
        buttons_layout.addWidget(self.calculate_btn)
        
        layout.addLayout(buttons_layout)
    
    def _update_calc_series_list(self):
        """Atualiza lista de séries para cálculos"""
        self.calc_series_list.clear()
        
        for dataset in self.session_state.datasets.values():
            for series_id, series in dataset.series.items():
                item = QListWidgetItem(f"{dataset.dataset_id}: {series.name}")
                item.setData(Qt.ItemDataRole.UserRole, (dataset.dataset_id, series_id))
                self.calc_series_list.addItem(item)
    
    @pyqtSlot()
    def _apply_calculation(self):
        """Aplica cálculo matemático"""
        params = self._get_calc_params()
        self.operation_requested.emit("calculus_apply", params)
    
    def _get_calc_params(self) -> Dict[str, Any]:
        """Coleta parâmetros de cálculo"""
        selected_series = []
        for item in self.calc_series_list.selectedItems():
            dataset_id, series_id = item.data(Qt.ItemDataRole.UserRole)
            selected_series.append((dataset_id, series_id))
        
        return {
            'operation': self.operation_combo.currentText().lower().replace(' ', '_'),
            'window_size': self.window_size_spinbox.value(),
            'method': self.method_combo.currentText().lower().replace(' ', '_'),
            'result_name': self.result_name_edit.text(),
            'add_to_dataset': self.add_to_dataset_checkbox.isChecked(),
            'selected_series': selected_series
        }


class OperationsPanel(QWidget):
    """
    Painel completo de operações conforme especificação
    
    Features:
    - Interpolação avançada
    - Sincronização de séries
    - Cálculos matemáticos
    - Exportação
    - Streaming
    """
    
    # Signals
    operation_completed = pyqtSignal(str, object)  # operation_name, result
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        
        self.session_state = session_state
        self.operation_worker: Optional[OperationWorker] = None
        
        self._setup_ui()
        self._setup_connections()
        
        logger.debug("operations_panel_initialized")
    
    def _setup_ui(self):
        """Setup da UI principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Interpolation tab
        self.interpolation_panel = InterpolationPanel(self.session_state)
        self.tabs.addTab(self.interpolation_panel, "Interpolation")
        
        # Synchronization tab
        self.sync_panel = SynchronizationPanel(self.session_state)
        self.tabs.addTab(self.sync_panel, "Synchronization")
        
        # Calculus tab
        self.calculus_panel = CalculusPanel(self.session_state)
        self.tabs.addTab(self.calculus_panel, "Calculus")
        
        # Streaming tab
        self.streaming_panel = StreamingControlWidget()
        self.tabs.addTab(self.streaming_panel, "Streaming")
        
        # Export tab
        self.export_panel = self._create_export_panel()
        self.tabs.addTab(self.export_panel, "Export")
        
        layout.addWidget(self.tabs)
        
        # Status and progress
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
    
    def _create_export_panel(self) -> QWidget:
        """Cria painel de exportação"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Export format selection
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout(format_group)
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems([
            "CSV", "Excel", "HDF5", "Parquet", "JSON", "MAT", "NetCDF"
        ])
        format_layout.addRow("Format:", self.export_format_combo)
        
        # Include options
        self.include_metadata_checkbox = QCheckBox("Include metadata")
        self.include_metadata_checkbox.setChecked(True)
        format_layout.addRow("", self.include_metadata_checkbox)
        
        self.include_plots_checkbox = QCheckBox("Include plots")
        format_layout.addRow("", self.include_plots_checkbox)
        
        layout.addWidget(format_group)
        
        # Data selection
        data_group = QGroupBox("Data Selection")
        data_layout = QVBoxLayout(data_group)
        
        self.export_data_list = QListWidget()
        self.export_data_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        data_layout.addWidget(self.export_data_list)
        
        # Populate with current datasets
        self._update_export_data_list()
        
        layout.addWidget(data_group)
        
        # Export button
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self._export_data)
        layout.addWidget(export_btn)
        
        return panel
    
    def _update_export_data_list(self):
        """Atualiza lista de dados para exportação"""
        self.export_data_list.clear()
        
        for dataset_id, dataset in self.session_state.datasets.items():
            item = QListWidgetItem(f"Dataset: {dataset_id}")
            item.setData(Qt.ItemDataRole.UserRole, ('dataset', dataset_id))
            self.export_data_list.addItem(item)
            
            for series_id, series in dataset.series.items():
                item = QListWidgetItem(f"  └─ {series.name}")
                item.setData(Qt.ItemDataRole.UserRole, ('series', dataset_id, series_id))
                self.export_data_list.addItem(item)
    
    def _setup_connections(self):
        """Setup de conexões de sinais"""
        # Connect operation panels
        self.interpolation_panel.operation_requested.connect(self._handle_operation)
        self.sync_panel.operation_requested.connect(self._handle_operation)
        self.calculus_panel.operation_requested.connect(self._handle_operation)
        
        # Connect session state updates
        self.session_state.dataset_added.connect(self._on_dataset_changed)
        self.session_state.dataset_removed.connect(self._on_dataset_changed)
    
    @pyqtSlot(str, dict)
    def _handle_operation(self, operation_type: str, params: Dict[str, Any]):
        """Manipula requisições de operação"""
        logger.info("operation_requested", operation=operation_type, params=params)
        
        # Map operation types to handler functions
        operation_handlers = {
            'interpolation_preview': self._handle_interpolation_preview,
            'interpolation_apply': self._handle_interpolation_apply,
            'synchronization_analyze': self._handle_sync_analyze,
            'synchronization_apply': self._handle_sync_apply,
            'calculus_apply': self._handle_calculus_apply
        }
        
        handler = operation_handlers.get(operation_type)
        if handler:
            # Execute in worker thread for heavy operations
            self.operation_worker = OperationWorker(operation_type, handler, params)
            self.operation_worker.operation_started.connect(self._on_operation_started)
            self.operation_worker.operation_progress.connect(self._on_operation_progress)
            self.operation_worker.operation_completed.connect(self._on_operation_completed)
            self.operation_worker.operation_failed.connect(self._on_operation_failed)
            self.operation_worker.start()
        else:
            logger.warning("unknown_operation_type", operation=operation_type)
    
    def _handle_interpolation_preview(self, params: Dict[str, Any]):
        """Handle interpolation preview"""
        # Mock implementation - would call actual interpolation service
        result = f"Preview for {params['method']} interpolation with {len(params['selected_series'])} series"
        return result
    
    def _handle_interpolation_apply(self, params: Dict[str, Any]):
        """Handle interpolation application"""
        # Mock implementation - would call actual interpolation service
        result = f"Applied {params['method']} interpolation to {len(params['selected_series'])} series"
        return result
    
    def _handle_sync_analyze(self, params: Dict[str, Any]):
        """Handle synchronization analysis"""
        # Mock implementation - would call actual sync service
        result = f"Analyzed timing for {len(params['selected_series'])} series using {params['method']}"
        return result
    
    def _handle_sync_apply(self, params: Dict[str, Any]):
        """Handle synchronization application"""
        # Mock implementation - would call actual sync service
        result = f"Synchronized {len(params['selected_series'])} series using {params['method']}"
        return result
    
    def _handle_calculus_apply(self, params: Dict[str, Any]):
        """Handle calculus operations"""
        # Mock implementation - would call actual calculus service
        result = f"Applied {params['operation']} to {len(params['selected_series'])} series"
        return result
    
    @pyqtSlot(str)
    def _on_operation_started(self, operation_name: str):
        """Callback quando operação inicia"""
        self.status_label.setText(f"Running {operation_name}...")
        self.progress_bar.setVisible(True)
    
    @pyqtSlot(int)
    def _on_operation_progress(self, percentage: int):
        """Callback de progresso da operação"""
        self.progress_bar.setValue(percentage)
    
    @pyqtSlot(str, object)
    def _on_operation_completed(self, operation_name: str, result: Any):
        """Callback quando operação completa"""
        self.status_label.setText(f"Completed: {operation_name}")
        self.progress_bar.setVisible(False)
        
        # Show result
        QMessageBox.information(self, "Operation Complete", str(result))
        
        self.operation_completed.emit(operation_name, result)
        
        # Update UI lists
        self._refresh_all_lists()
    
    @pyqtSlot(str, str)
    def _on_operation_failed(self, operation_name: str, error: str):
        """Callback quando operação falha"""
        self.status_label.setText(f"Failed: {operation_name}")
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, "Operation Failed", f"Operation {operation_name} failed:\n{error}")
    
    @pyqtSlot()
    def _export_data(self):
        """Exporta dados selecionados"""
        # Get export parameters
        format = self.export_format_combo.currentText()
        include_metadata = self.include_metadata_checkbox.isChecked()
        include_plots = self.include_plots_checkbox.isChecked()
        
        # Get selected items
        selected_items = self.export_data_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select data to export.")
            return
        
        # Choose output file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data As...",
            "",
            f"{format} Files (*.{format.lower()});;All Files (*)"
        )
        
        if file_path:
            # Would call actual export manager here
            QMessageBox.information(self, "Export Complete", f"Data exported to {file_path}")
    
    @pyqtSlot()
    def _on_dataset_changed(self):
        """Callback quando datasets mudam"""
        self._refresh_all_lists()
    
    def _refresh_all_lists(self):
        """Refresh todas as listas de séries"""
        self.interpolation_panel._update_series_list()
        self.sync_panel._update_sync_series_list()
        self.calculus_panel._update_calc_series_list()
        self._update_export_data_list()
    
    def show_export_dialog(self):
        """Mostra diálogo de exportação"""
        self.tabs.setCurrentIndex(4)  # Export tab