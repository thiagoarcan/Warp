"""
DataPanel - Painel de gerenciamento de dados conforme seção 12.4

Funcionalidades:
- Upload e carregamento de datasets
- Árvore de datasets e séries
- Preview de dados
- Configurações de carregamento
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QGroupBox, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QTabWidget, QTextEdit, QProgressBar, QComboBox, QSpinBox, QCheckBox,
    QFormLayout, QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QMutex, QMutexLocker
from PyQt6.QtGui import QFont, QIcon

from platform_base.ui.state import SessionState
from platform_base.ui.workers.file_worker import FileLoadWorker
from platform_base.io.loader import LoadConfig, get_file_info
from platform_base.core.models import Dataset, SeriesID
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class DataPanel(QWidget):
    """
    Painel de dados conforme especificação seção 12.4
    
    Features:
    - Árvore hierárquica de datasets/séries
    - Preview de dados com paginação
    - Configurações avançadas de carregamento
    - Worker threads para operações I/O
    """
    
    # Signals
    dataset_loaded = pyqtSignal(str)  # dataset_id
    series_selected = pyqtSignal(str, str)  # dataset_id, series_id
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        
        self.session_state = session_state
        self._current_dataset: Optional[Dataset] = None
        
        # Worker thread management
        self._worker_thread: Optional[QThread] = None
        self._worker: Optional[FileLoadWorker] = None
        self._worker_mutex = QMutex()
        
        self._setup_ui()
        self._setup_connections()
        
        logger.debug("data_panel_initialized")
    
    def _setup_ui(self):
        """Configura interface do painel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Dados")
        title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        # Load button
        self._load_button = QPushButton("Carregar Dataset")
        self._load_button.clicked.connect(self._open_file_dialog)
        header_layout.addWidget(self._load_button)
        
        layout.addLayout(header_layout)
        
        # Create tab widget
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)
        
        # Datasets tab
        self._create_datasets_tab()
        
        # Preview tab
        self._create_preview_tab()
        
        # Config tab
        self._create_config_tab()
        
    def _create_datasets_tab(self):
        """Cria aba de datasets"""
        datasets_widget = QWidget()
        layout = QVBoxLayout(datasets_widget)
        
        # Datasets tree
        self._datasets_tree = QTreeWidget()
        self._datasets_tree.setHeaderLabels(["Nome", "Tipo", "Pontos", "Unidade"])
        self._datasets_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._datasets_tree.itemClicked.connect(self._on_tree_item_clicked)
        
        layout.addWidget(self._datasets_tree)
        
        # Summary
        summary_group = QGroupBox("Resumo")
        summary_layout = QFormLayout(summary_group)
        
        self._summary_dataset_label = QLabel("Nenhum dataset")
        self._summary_series_label = QLabel("0")
        self._summary_points_label = QLabel("0")
        self._summary_timespan_label = QLabel("N/A")
        
        summary_layout.addRow("Dataset:", self._summary_dataset_label)
        summary_layout.addRow("Séries:", self._summary_series_label)
        summary_layout.addRow("Pontos:", self._summary_points_label)
        summary_layout.addRow("Período:", self._summary_timespan_label)
        
        layout.addWidget(summary_group)
        
        self._tabs.addTab(datasets_widget, "Datasets")
    
    def _create_preview_tab(self):
        """Cria aba de preview"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        # Preview table
        self._preview_table = QTableWidget()
        self._preview_table.setAlternatingRowColors(True)
        self._preview_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Configure table
        header = self._preview_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        
        layout.addWidget(self._preview_table)
        
        # Preview controls
        controls_layout = QHBoxLayout()
        
        self._preview_rows_combo = QComboBox()
        self._preview_rows_combo.addItems(["10", "25", "50", "100"])
        self._preview_rows_combo.setCurrentText("25")
        self._preview_rows_combo.currentTextChanged.connect(self._update_preview)
        
        controls_layout.addWidget(QLabel("Linhas:"))
        controls_layout.addWidget(self._preview_rows_combo)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        self._tabs.addTab(preview_widget, "Preview")
    
    def _create_config_tab(self):
        """Cria aba de configurações"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Load configuration
        load_group = QGroupBox("Configurações de Carregamento")
        load_layout = QFormLayout(load_group)
        
        # Timestamp column
        self._timestamp_combo = QComboBox()
        self._timestamp_combo.setEditable(True)
        self._timestamp_combo.addItem("Auto-detectar", None)
        load_layout.addRow("Coluna de timestamp:", self._timestamp_combo)
        
        # Encoding
        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(["utf-8", "latin1", "cp1252"])
        load_layout.addRow("Codificação:", self._encoding_combo)
        
        # Delimiter
        self._delimiter_combo = QComboBox()
        self._delimiter_combo.addItems([",", ";", "\\t", "|"])
        load_layout.addRow("Delimitador:", self._delimiter_combo)
        
        # Max rows
        self._max_rows_spin = QSpinBox()
        self._max_rows_spin.setRange(0, 10000000)
        self._max_rows_spin.setValue(0)
        self._max_rows_spin.setSpecialValueText("Sem limite")
        load_layout.addRow("Máximo de linhas:", self._max_rows_spin)
        
        # Max missing ratio
        self._max_missing_spin = QSpinBox()
        self._max_missing_spin.setRange(0, 100)
        self._max_missing_spin.setValue(95)
        self._max_missing_spin.setSuffix("%")
        load_layout.addRow("Máximo de dados faltantes:", self._max_missing_spin)
        
        layout.addWidget(load_group)
        
        # Validation configuration
        validation_group = QGroupBox("Validação")
        validation_layout = QFormLayout(validation_group)
        
        self._strict_validation_check = QCheckBox("Validação rigorosa")
        self._strict_validation_check.setChecked(True)
        validation_layout.addRow(self._strict_validation_check)
        
        self._auto_fix_check = QCheckBox("Correção automática")
        self._auto_fix_check.setChecked(False)
        validation_layout.addRow(self._auto_fix_check)
        
        layout.addWidget(validation_group)
        
        layout.addStretch()
        
        self._tabs.addTab(config_widget, "Configurações")
    
    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Session state connections
        self.session_state.dataset_changed.connect(self._on_dataset_changed)
        self.session_state.operation_started.connect(self._on_operation_started)
        self.session_state.operation_finished.connect(self._on_operation_finished)
    
    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Handler para mudança de dataset"""
        if dataset_id:
            try:
                self._current_dataset = self.session_state.get_dataset(dataset_id)
                self._update_datasets_tree()
                self._update_summary()
                self._update_preview()
            except Exception as e:
                logger.error("dataset_change_failed", dataset_id=dataset_id, error=str(e))
        else:
            self._current_dataset = None
            self._clear_ui()
    
    @pyqtSlot(str)
    def _on_operation_started(self, operation_name: str):
        """Handler para início de operação"""
        self._load_button.setEnabled(False)
        
    @pyqtSlot(str, bool) 
    def _on_operation_finished(self, operation_name: str, success: bool):
        """Handler para fim de operação"""
        self._load_button.setEnabled(True)
    
    def _open_file_dialog(self):
        """Abre diálogo para seleção de arquivo"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Carregar Dataset")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters([
            "Todos os formatos (*.csv *.xlsx *.parquet *.h5)",
            "CSV files (*.csv)",
            "Excel files (*.xlsx *.xls)", 
            "Parquet files (*.parquet *.pq)",
            "HDF5 files (*.h5 *.hdf5)"
        ])
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.load_dataset(file_paths[0])
    
    def load_dataset(self, file_path: str):
        """Carrega dataset usando worker thread"""
        with QMutexLocker(self._worker_mutex):
            # Stop any existing worker
            if self._worker_thread and self._worker_thread.isRunning():
                self._worker_thread.quit()
                self._worker_thread.wait()
            
            # Get load configuration
            load_config = self._get_load_config()
            
            # Create worker thread
            self._worker_thread = QThread()
            self._worker = FileLoadWorker(file_path, load_config)
            self._worker.moveToThread(self._worker_thread)
            
            # Connect worker signals
            self._worker_thread.started.connect(self._worker.load_file)
            self._worker.progress.connect(self._on_load_progress)
            self._worker.finished.connect(self._on_load_finished)
            self._worker.error.connect(self._on_load_error)
            
            # Cleanup on finish
            self._worker.finished.connect(self._worker_thread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._worker_thread.finished.connect(self._worker_thread.deleteLater)
            
            # Start loading
            self.session_state.start_operation(f"Carregando {Path(file_path).name}")
            self._worker_thread.start()
            
            logger.info("dataset_load_started", file_path=file_path)
    
    def _get_load_config(self) -> LoadConfig:
        """Constrói configuração de carregamento a partir da UI"""
        config = LoadConfig()
        
        # Timestamp column
        timestamp_text = self._timestamp_combo.currentText()
        if timestamp_text != "Auto-detectar":
            config.timestamp_column = timestamp_text
        
        # Encoding
        config.encoding = self._encoding_combo.currentText()
        
        # Delimiter 
        delimiter_text = self._delimiter_combo.currentText()
        if delimiter_text == "\\t":
            config.delimiter = "\t"
        else:
            config.delimiter = delimiter_text
        
        # Max rows
        max_rows = self._max_rows_spin.value()
        if max_rows > 0:
            config.max_rows = max_rows
        
        # Max missing ratio
        config.max_missing_ratio = self._max_missing_spin.value() / 100.0
        
        return config
    
    @pyqtSlot(int, str)
    def _on_load_progress(self, percent: int, message: str):
        """Handler para progresso de carregamento"""
        self.session_state.update_operation_progress(percent, message)
    
    @pyqtSlot(object)  # Dataset object
    def _on_load_finished(self, dataset: Dataset):
        """Handler para carregamento concluído"""
        try:
            # Add dataset to session
            dataset_id = self.session_state.add_dataset(dataset)
            
            self.session_state.finish_operation(True, "Dataset carregado com sucesso")
            self.dataset_loaded.emit(dataset_id)
            
            logger.info("dataset_loaded_successfully", dataset_id=dataset_id)
            
        except Exception as e:
            self.session_state.finish_operation(False, f"Erro ao processar dataset: {e}")
            logger.error("dataset_processing_failed", error=str(e))
    
    @pyqtSlot(str)
    def _on_load_error(self, error_message: str):
        """Handler para erro de carregamento"""
        self.session_state.finish_operation(False, f"Erro no carregamento: {error_message}")
        
        QMessageBox.critical(
            self,
            "Erro no Carregamento",
            f"Falha ao carregar arquivo:\n\n{error_message}"
        )
        
        logger.error("dataset_load_failed", error=error_message)
    
    def _update_datasets_tree(self):
        """Atualiza árvore de datasets"""
        self._datasets_tree.clear()
        
        if not self._current_dataset:
            return
        
        # Create dataset item
        dataset_item = QTreeWidgetItem(self._datasets_tree)
        dataset_item.setText(0, self._current_dataset.dataset_id)
        dataset_item.setText(1, "Dataset")
        dataset_item.setText(2, str(len(self._current_dataset.t_seconds)))
        dataset_item.setData(0, Qt.ItemDataRole.UserRole, ("dataset", self._current_dataset.dataset_id))
        
        # Add series items
        for series in self._current_dataset.series.values():
            series_item = QTreeWidgetItem(dataset_item)
            series_item.setText(0, series.name)
            series_item.setText(1, "Série")
            series_item.setText(2, str(len(series.values)))
            series_item.setText(3, str(series.unit))
            series_item.setData(0, Qt.ItemDataRole.UserRole, 
                              ("series", self._current_dataset.dataset_id, series.series_id))
        
        # Expand dataset item
        dataset_item.setExpanded(True)
        
        # Resize columns
        for i in range(4):
            self._datasets_tree.resizeColumnToContents(i)
    
    def _update_summary(self):
        """Atualiza resumo do dataset"""
        if not self._current_dataset:
            self._summary_dataset_label.setText("Nenhum dataset")
            self._summary_series_label.setText("0")
            self._summary_points_label.setText("0")
            self._summary_timespan_label.setText("N/A")
            return
        
        # Update labels
        self._summary_dataset_label.setText(self._current_dataset.dataset_id)
        self._summary_series_label.setText(str(len(self._current_dataset.series)))
        self._summary_points_label.setText(str(len(self._current_dataset.t_seconds)))
        
        # Time span
        if len(self._current_dataset.t_datetime) > 0:
            start_time = self._current_dataset.t_datetime[0]
            end_time = self._current_dataset.t_datetime[-1]
            duration = end_time - start_time
            
            # Format duration
            days = duration.astype('timedelta64[D]').astype(int)
            hours = (duration - days.astype('timedelta64[D]')).astype('timedelta64[h]').astype(int)
            
            if days > 0:
                timespan_text = f"{days}d {hours}h"
            else:
                timespan_text = f"{hours}h"
                
            self._summary_timespan_label.setText(timespan_text)
        else:
            self._summary_timespan_label.setText("N/A")
    
    def _update_preview(self):
        """Atualiza preview dos dados"""
        if not self._current_dataset:
            self._preview_table.setRowCount(0)
            self._preview_table.setColumnCount(0)
            return
        
        # Get number of rows to show
        max_rows = int(self._preview_rows_combo.currentText())
        
        # Setup table
        n_points = min(max_rows, len(self._current_dataset.t_seconds))
        n_cols = 2 + len(self._current_dataset.series)  # timestamp + datetime + series
        
        self._preview_table.setRowCount(n_points)
        self._preview_table.setColumnCount(n_cols)
        
        # Set headers
        headers = ["Timestamp (s)", "DateTime"]
        headers.extend([series.name for series in self._current_dataset.series.values()])
        self._preview_table.setHorizontalHeaderLabels(headers)
        
        # Fill data
        for row in range(n_points):
            # Timestamp
            self._preview_table.setItem(row, 0, 
                QTableWidgetItem(f"{self._current_dataset.t_seconds[row]:.3f}"))
            
            # DateTime
            dt_str = str(self._current_dataset.t_datetime[row])[:19]  # Remove microseconds
            self._preview_table.setItem(row, 1, QTableWidgetItem(dt_str))
            
            # Series values
            for col, series in enumerate(self._current_dataset.series.values(), 2):
                value = series.values[row]
                if pd.isna(value):
                    item_text = "NaN"
                else:
                    item_text = f"{value:.6g}"
                
                item = QTableWidgetItem(item_text)
                if pd.isna(value):
                    item.setForeground(Qt.GlobalColor.gray)
                
                self._preview_table.setItem(row, col, item)
        
        # Resize columns
        self._preview_table.resizeColumnsToContents()
    
    def _clear_ui(self):
        """Limpa interface"""
        self._datasets_tree.clear()
        self._preview_table.setRowCount(0)
        self._preview_table.setColumnCount(0)
        self._update_summary()
    
    @pyqtSlot(QTreeWidgetItem, int)
    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handler para clique na árvore"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if data and len(data) >= 2:
            item_type = data[0]
            
            if item_type == "series" and len(data) >= 3:
                dataset_id, series_id = data[1], data[2]
                self.series_selected.emit(dataset_id, series_id)
                logger.debug("series_selected", dataset_id=dataset_id, series_id=series_id)


# Import pandas for NaN checking
import pandas as pd