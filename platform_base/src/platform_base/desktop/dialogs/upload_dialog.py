"""
UploadDialog - File upload dialog for Platform Base v2.0

Provides interface for loading data files with format detection and configuration.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QFormLayout, QComboBox, QLineEdit,
    QSpinBox, QCheckBox, QFileDialog, QTextEdit,
    QProgressBar, QLabel, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from platform_base.desktop.session_state import SessionState
from platform_base.desktop.signal_hub import SignalHub
from platform_base.desktop.workers.base_worker import BaseWorker
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class FileLoadWorker(BaseWorker):
    """Worker thread for loading files"""
    
    file_loaded = pyqtSignal(str, object)  # filepath, dataset
    preview_ready = pyqtSignal(object)  # preview_data
    
    def __init__(self, filepath: str, config: Dict[str, Any]):
        super().__init__()
        self.filepath = filepath
        self.config = config
    
    def run(self):
        """Load file in background thread"""
        try:
            self.progress.emit(0)
            self.status_updated.emit("Loading file...")
            
            # Import loader (avoid import at module level)
            from platform_base.io.loader import load
            from platform_base.io.loader import LoadConfig
            
            # Create load config
            load_config = LoadConfig(
                timestamp_column=self.config.get("timestamp_column"),
                delimiter=self.config.get("delimiter", ","),
                encoding=self.config.get("encoding", "utf-8"),
                sheet_name=self.config.get("sheet_name"),
                hdf5_key=self.config.get("hdf5_key"),
                chunk_size=self.config.get("chunk_size")
            )
            
            self.progress.emit(25)
            self.status_updated.emit("Parsing data...")
            
            # Load dataset
            dataset = load(self.filepath, load_config)
            
            self.progress.emit(75)
            self.status_updated.emit("Validating data...")
            
            # Emit success
            self.progress.emit(100)
            self.status_updated.emit("File loaded successfully")
            self.file_loaded.emit(self.filepath, dataset)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))


class PreviewWorker(BaseWorker):
    """Worker for generating file preview"""
    
    preview_ready = pyqtSignal(object)  # preview_data
    
    def __init__(self, filepath: str, config: Dict[str, Any]):
        super().__init__()
        self.filepath = filepath
        self.config = config
    
    def run(self):
        """Generate preview in background thread"""
        try:
            self.progress.emit(0)
            self.status_updated.emit("Generating preview...")
            
            import pandas as pd
            
            # Read first few rows based on file type
            filepath = Path(self.filepath)
            
            if filepath.suffix.lower() == '.csv':
                df = pd.read_csv(
                    filepath,
                    nrows=100,
                    delimiter=self.config.get("delimiter", ","),
                    encoding=self.config.get("encoding", "utf-8")
                )
            elif filepath.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(
                    filepath,
                    nrows=100,
                    sheet_name=self.config.get("sheet_name", 0)
                )
            else:
                # For other formats, use basic read
                df = pd.DataFrame({"Preview": ["Preview not available for this format"]})
            
            self.progress.emit(50)
            
            # Generate preview data
            preview_data = {
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "shape": df.shape,
                "head": df.head(10).to_dict('records'),
                "sample_values": {col: list(df[col].dropna().head(5)) for col in df.columns}
            }
            
            self.progress.emit(100)
            self.status_updated.emit("Preview generated")
            self.preview_ready.emit(preview_data)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Preview error: {str(e)}")


class UploadDialog(QDialog):
    """
    File upload dialog.
    
    Features:
    - File selection with format detection
    - Load configuration options
    - Data preview
    - Progress indication
    - Error handling
    """
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        
        self.selected_files: List[str] = []
        self.current_config: Dict[str, Any] = {}
        self.preview_data: Optional[Dict[str, Any]] = None
        
        # Worker threads
        self.load_worker: Optional[FileLoadWorker] = None
        self.preview_worker: Optional[PreviewWorker] = None
        
        self._setup_ui()
        self._connect_signals()
        
        logger.debug("upload_dialog_initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Load Data Files")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # File selection section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # File path and browse button
        path_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select file to load...")
        self.file_path_edit.textChanged.connect(self._on_file_path_changed)
        path_layout.addWidget(self.file_path_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)
        path_layout.addWidget(self.browse_btn)
        
        file_layout.addLayout(path_layout)
        
        # Format detection
        self.format_label = QLabel("Format: Not detected")
        file_layout.addWidget(self.format_label)
        
        layout.addWidget(file_group)
        
        # Configuration and preview tabs
        self.tabs = QTabWidget()
        
        # Configuration tab
        self.config_tab = self._create_config_tab()
        self.tabs.addTab(self.config_tab, "Configuration")
        
        # Preview tab
        self.preview_tab = self._create_preview_tab()
        self.tabs.addTab(self.preview_tab, "Preview")
        
        layout.addWidget(self.tabs)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Select a file to begin")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Generate Preview")
        self.preview_btn.clicked.connect(self._generate_preview)
        self.preview_btn.setEnabled(False)
        buttons_layout.addWidget(self.preview_btn)
        
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.load_btn = QPushButton("Load Data")
        self.load_btn.clicked.connect(self._load_file)
        self.load_btn.setEnabled(False)
        self.load_btn.setDefault(True)
        buttons_layout.addWidget(self.load_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_config_tab(self) -> QWidget:
        """Create configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # General configuration
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        # Encoding
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "latin-1", "cp1252", "ascii"])
        self.encoding_combo.currentTextChanged.connect(self._update_config)
        general_layout.addRow("Encoding:", self.encoding_combo)
        
        # Delimiter (for CSV)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([",", ";", "\\t", "|"])
        self.delimiter_combo.setEditable(True)
        self.delimiter_combo.currentTextChanged.connect(self._update_config)
        general_layout.addRow("Delimiter:", self.delimiter_combo)
        
        layout.addWidget(general_group)
        
        # Schema configuration
        schema_group = QGroupBox("Schema Detection")
        schema_layout = QFormLayout(schema_group)
        
        # Timestamp column
        self.timestamp_combo = QComboBox()
        self.timestamp_combo.addItem("Auto-detect", None)
        self.timestamp_combo.currentTextChanged.connect(self._update_config)
        schema_layout.addRow("Timestamp Column:", self.timestamp_combo)
        
        # Skip rows
        self.skip_rows_spin = QSpinBox()
        self.skip_rows_spin.setRange(0, 100)
        self.skip_rows_spin.valueChanged.connect(self._update_config)
        schema_layout.addRow("Skip Rows:", self.skip_rows_spin)
        
        layout.addWidget(schema_group)
        
        # Excel-specific configuration
        self.excel_group = QGroupBox("Excel Settings")
        excel_layout = QFormLayout(self.excel_group)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentTextChanged.connect(self._update_config)
        excel_layout.addRow("Sheet:", self.sheet_combo)
        
        layout.addWidget(self.excel_group)
        
        # HDF5-specific configuration
        self.hdf5_group = QGroupBox("HDF5 Settings")
        hdf5_layout = QFormLayout(self.hdf5_group)
        
        self.hdf5_key_edit = QLineEdit()
        self.hdf5_key_edit.textChanged.connect(self._update_config)
        hdf5_layout.addRow("Key:", self.hdf5_key_edit)
        
        layout.addWidget(self.hdf5_group)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        self.chunk_check = QCheckBox("Use chunked loading")
        self.chunk_check.toggled.connect(self._update_config)
        advanced_layout.addRow("Performance:", self.chunk_check)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1000, 1000000)
        self.chunk_size_spin.setValue(10000)
        self.chunk_size_spin.setEnabled(False)
        self.chunk_size_spin.valueChanged.connect(self._update_config)
        advanced_layout.addRow("Chunk Size:", self.chunk_size_spin)
        
        self.chunk_check.toggled.connect(self.chunk_size_spin.setEnabled)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        
        # Initially hide format-specific groups
        self.excel_group.setVisible(False)
        self.hdf5_group.setVisible(False)
        
        return widget
    
    def _create_preview_tab(self) -> QWidget:
        """Create preview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preview controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Data Preview:"))
        controls_layout.addStretch()
        
        self.refresh_preview_btn = QPushButton("Refresh")
        self.refresh_preview_btn.clicked.connect(self._generate_preview)
        self.refresh_preview_btn.setEnabled(False)
        controls_layout.addWidget(self.refresh_preview_btn)
        
        layout.addLayout(controls_layout)
        
        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.preview_table)
        
        # Preview info
        self.preview_info = QTextEdit()
        self.preview_info.setMaximumHeight(100)
        self.preview_info.setReadOnly(True)
        font = QFont("Consolas", 9)
        self.preview_info.setFont(font)
        layout.addWidget(self.preview_info)
        
        return widget
    
    def _connect_signals(self):
        """Connect signals"""
        pass
    
    @pyqtSlot()
    def _browse_file(self):
        """Open file browser"""
        file_filters = [
            "All Supported (*.csv *.xlsx *.xls *.parquet *.h5 *.hdf5)",
            "CSV Files (*.csv)",
            "Excel Files (*.xlsx *.xls)", 
            "Parquet Files (*.parquet)",
            "HDF5 Files (*.h5 *.hdf5)",
            "All Files (*)"
        ]
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "", ";;".join(file_filters)
        )
        
        if filepath:
            self.file_path_edit.setText(filepath)
    
    @pyqtSlot(str)
    def _on_file_path_changed(self, filepath: str):
        """Handle file path change"""
        if not filepath or not Path(filepath).exists():
            self._reset_ui_state()
            return
        
        # Detect format
        file_path = Path(filepath)
        format_detected = self._detect_format(file_path)
        self.format_label.setText(f"Format: {format_detected}")
        
        # Update UI based on format
        self._update_format_ui(format_detected)
        
        # Update column options for timestamp detection
        self._update_column_options(filepath)
        
        # Enable buttons
        self.preview_btn.setEnabled(True)
        self.refresh_preview_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        
        self.status_label.setText("File selected. Configure options or generate preview.")
    
    def _detect_format(self, file_path: Path) -> str:
        """Detect file format"""
        suffix = file_path.suffix.lower()
        format_map = {
            '.csv': 'CSV',
            '.xlsx': 'Excel',
            '.xls': 'Excel',
            '.parquet': 'Parquet',
            '.h5': 'HDF5',
            '.hdf5': 'HDF5'
        }
        return format_map.get(suffix, 'Unknown')
    
    def _update_format_ui(self, format_type: str):
        """Update UI based on detected format"""
        # Show/hide format-specific options
        self.excel_group.setVisible(format_type == 'Excel')
        self.hdf5_group.setVisible(format_type == 'HDF5')
        
        # Update delimiter visibility
        self.delimiter_combo.setEnabled(format_type == 'CSV')
        
        # Update configuration
        self._update_config()
    
    def _update_column_options(self, filepath: str):
        """Update column options from file"""
        try:
            # Quick column detection
            file_path = Path(filepath)
            
            if file_path.suffix.lower() == '.csv':
                import pandas as pd
                df_sample = pd.read_csv(filepath, nrows=1)
                columns = list(df_sample.columns)
                
                # Update timestamp column options
                self.timestamp_combo.clear()
                self.timestamp_combo.addItem("Auto-detect", None)
                for col in columns:
                    self.timestamp_combo.addItem(col, col)
                    
        except Exception as e:
            logger.warning("column_detection_failed", error=str(e))
    
    def _update_config(self):
        """Update current configuration"""
        self.current_config = {
            "encoding": self.encoding_combo.currentText(),
            "delimiter": self.delimiter_combo.currentText(),
            "timestamp_column": self.timestamp_combo.currentData(),
            "skip_rows": self.skip_rows_spin.value(),
            "sheet_name": self.sheet_combo.currentText() if self.sheet_combo.count() > 0 else None,
            "hdf5_key": self.hdf5_key_edit.text() if self.hdf5_key_edit.text() else None,
            "chunk_size": self.chunk_size_spin.value() if self.chunk_check.isChecked() else None
        }
        
        logger.debug("upload_config_updated", config=self.current_config)
    
    @pyqtSlot()
    def _generate_preview(self):
        """Generate file preview"""
        filepath = self.file_path_edit.text()
        if not filepath:
            return
        
        # Start preview worker
        self.preview_worker = PreviewWorker(filepath, self.current_config)
        self.preview_worker.preview_ready.connect(self._on_preview_ready)
        self.preview_worker.error.connect(self._on_preview_error)
        self.preview_worker.progress.connect(self._update_progress)
        self.preview_worker.status_updated.connect(self._update_status)
        self.preview_worker.finished.connect(self._on_preview_finished)
        
        self.preview_worker.start()
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.preview_btn.setEnabled(False)
        self.refresh_preview_btn.setEnabled(False)
    
    @pyqtSlot(object)
    def _on_preview_ready(self, preview_data: Dict[str, Any]):
        """Handle preview data ready"""
        self.preview_data = preview_data
        self._update_preview_display()
        
        # Switch to preview tab
        self.tabs.setCurrentIndex(1)
    
    @pyqtSlot(str)
    def _on_preview_error(self, error_message: str):
        """Handle preview error"""
        QMessageBox.warning(self, "Preview Error", f"Failed to generate preview:\\n{error_message}")
        logger.error("preview_generation_failed", error=error_message)
    
    @pyqtSlot()
    def _on_preview_finished(self):
        """Handle preview worker finished"""
        self.progress_bar.setVisible(False)
        self.preview_btn.setEnabled(True)
        self.refresh_preview_btn.setEnabled(True)
        
        if self.preview_worker:
            self.preview_worker.deleteLater()
            self.preview_worker = None
    
    def _update_preview_display(self):
        """Update preview table and info"""
        if not self.preview_data:
            return
        
        try:
            # Ensure preview_data is a dict and has expected structure
            if not isinstance(self.preview_data, dict):
                logger.error("preview_data_invalid_type", 
                           type=type(self.preview_data).__name__)
                return
            
            # Update preview table
            head_data = self.preview_data.get("head", [])
            columns = self.preview_data.get("columns", [])
        
        if head_data and columns:
            self.preview_table.setRowCount(len(head_data))
            self.preview_table.setColumnCount(len(columns))
            self.preview_table.setHorizontalHeaderLabels(columns)
            
            for row, record in enumerate(head_data):
                for col, column_name in enumerate(columns):
                    value = record.get(column_name, "")
                    item = QTableWidgetItem(str(value))
                    self.preview_table.setItem(row, col, item)
            
            # Auto-resize columns
            self.preview_table.resizeColumnsToContents()
            header = self.preview_table.horizontalHeader()
            header.setStretchLastSection(True)
        
        # Update info text
        shape = self.preview_data.get("shape", (0, 0))
        dtypes = self.preview_data.get("dtypes", {})
        
        info_lines = [
            f"Shape: {shape[0]} rows × {shape[1]} columns",
            "",
            "Column Types:"
        ]
        
            for col, dtype in dtypes.items():
                info_lines.append(f"  {col}: {dtype}")
            
            self.preview_info.setPlainText("\\n".join(info_lines))
            
        except Exception as e:
            logger.error("preview_display_error", error=str(e))
            self.preview_info.setPlainText(f"Error displaying preview: {str(e)}")
            # Clear preview table on error
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
    
    @pyqtSlot()
    def _load_file(self):
        """Load the selected file"""
        filepath = self.file_path_edit.text()
        if not filepath:
            return
        
        # Start load worker
        self.load_worker = FileLoadWorker(filepath, self.current_config)
        self.load_worker.file_loaded.connect(self._on_file_loaded)
        self.load_worker.error.connect(self._on_load_error)
        self.load_worker.progress.connect(self._update_progress)
        self.load_worker.status_updated.connect(self._update_status)
        self.load_worker.finished.connect(self._on_load_finished)
        
        self.load_worker.start()
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.load_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
    
    @pyqtSlot(str, object)
    def _on_file_loaded(self, filepath: str, dataset):
        """Handle file loaded successfully"""
        # Add dataset to store
        dataset_id = self.session_state.dataset_store.add_dataset(dataset)
        
        # Emit signal
        self.signal_hub.emit_dataset_loaded(dataset_id)
        
        # Close dialog
        self.accept()
        
        logger.info("file_loaded_successfully", filepath=filepath, dataset_id=dataset_id)
    
    @pyqtSlot(str)
    def _on_load_error(self, error_message: str):
        """Handle load error"""
        QMessageBox.critical(self, "Load Error", f"Failed to load file:\\n{error_message}")
        logger.error("file_load_failed", error=error_message)
    
    @pyqtSlot()
    def _on_load_finished(self):
        """Handle load worker finished"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        
        if self.load_worker:
            self.load_worker.deleteLater()
            self.load_worker = None
    
    @pyqtSlot(int)
    def _update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def _update_status(self, message: str):
        """Update status label"""
        self.status_label.setText(message)
    
    def _reset_ui_state(self):
        """Reset UI to initial state"""
        self.format_label.setText("Format: Not detected")
        self.preview_btn.setEnabled(False)
        self.refresh_preview_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.status_label.setText("Select a file to begin")
        
        # Clear preview
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.preview_info.clear()
    
    def closeEvent(self, event):
        """Handle dialog close"""
        # Stop any running workers
        if self.load_worker and self.load_worker.isRunning():
            self.load_worker.terminate()
            self.load_worker.wait()
        
        if self.preview_worker and self.preview_worker.isRunning():
            self.preview_worker.terminate()
            self.preview_worker.wait()
        
        event.accept()