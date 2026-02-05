"""
UploadDialog - File upload dialog for Platform Base v2.0

Provides interface for loading data files with format detection and configuration.

Interface carregada de: desktop/ui_files/uploadDialog.ui
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.workers.base_worker import BaseWorker
from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class FileLoadWorker(BaseWorker):
    """Worker thread for loading files"""

    file_loaded = pyqtSignal(str, object)  # filepath, dataset
    preview_ready = pyqtSignal(object)  # preview_data

    def __init__(self, filepath: str, config: dict[str, Any]):
        super().__init__()
        self.filepath = filepath
        self.config = config

    def run(self):
        """Load file in background thread"""
        try:
            self.progress.emit(0)
            self.status_updated.emit("Loading file...")

            # Import loader (avoid import at module level)
            from platform_base.io.loader import LoadConfig, load

            # Create load config
            load_config = LoadConfig(
                timestamp_column=self.config.get("timestamp_column"),
                delimiter=self.config.get("delimiter", ","),
                encoding=self.config.get("encoding", "utf-8"),
                sheet_name=self.config.get("sheet_name", 0),  # Default to first sheet
                hdf5_key=self.config.get("hdf5_key") or "/data",
                chunk_size=self.config.get("chunk_size"),
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

    def __init__(self, filepath: str, config: dict[str, Any]):
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
            logger.debug("preview_worker_start", filepath=str(filepath), config=self.config)

            # Ensure file exists
            if not filepath.exists():
                raise FileNotFoundError(f"File not found: {filepath}")

            df = None
            if filepath.suffix.lower() == ".csv":
                df = pd.read_csv(
                    filepath,
                    nrows=100,
                    delimiter=self.config.get("delimiter", ","),
                    encoding=self.config.get("encoding", "utf-8"),
                )
            elif filepath.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(
                    filepath,
                    nrows=100,
                    sheet_name=self.config.get("sheet_name", 0),
                )
            else:
                # For other formats, use basic read
                df = pd.DataFrame({"Preview": ["Preview not available for this format"]})

            # Validate DataFrame
            if df is None:
                raise ValueError("Failed to read data from file")

            if isinstance(df, pd.DataFrame) and df.empty:
                raise ValueError("DataFrame is empty")
            if not isinstance(df, pd.DataFrame):
                raise ValueError(f"Expected DataFrame, got {type(df)}")

            logger.debug("preview_dataframe_loaded", shape=df.shape, columns=list(df.columns))

            self.progress.emit(50)

            # Generate preview data - ensure all data is JSON serializable
            try:
                preview_data = {
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "shape": df.shape,
                    "head": df.head(10).to_dict("records"),
                    "sample_values": {col: list(df[col].dropna().head(5)) for col in df.columns},
                }

                # Validate preview_data structure
                required_keys = ["columns", "dtypes", "shape", "head", "sample_values"]
                for key in required_keys:
                    if key not in preview_data:
                        raise ValueError(f"Missing required key in preview_data: {key}")

                logger.debug("preview_data_generated", keys=list(preview_data.keys()))

            except Exception as e:
                logger.exception("preview_data_generation_failed", error=str(e))
                raise ValueError(f"Failed to generate preview data: {e!s}")

            self.progress.emit(100)
            self.status_updated.emit("Preview generated")
            self.preview_ready.emit(preview_data)
            self.finished.emit()

        except Exception as e:
            self.error.emit(f"Preview error: {e!s}")


class UploadDialog(QDialog, UiLoaderMixin):
    """
    File upload dialog.

    Features:
    - File selection with format detection
    - Load configuration options
    - Data preview
    - Progress indication
    - Error handling
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/uploadDialog.ui"

    def __init__(self, session_state: SessionState, signal_hub: SignalHub,
                 parent: QWidget | None = None):
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub

        self.selected_files: list[str] = []
        self.current_config: dict[str, Any] = {}
        self.preview_data: dict[str, Any] | None = None

        # Worker threads
        self.load_worker: FileLoadWorker | None = None
        self.preview_worker: PreviewWorker | None = None

        # Multi-file loading state
        self.pending_files: list[str] = []
        self.loading_files: dict[str, FileLoadWorker] = {}
        self.loaded_datasets: list[str] = []  # Track loaded dataset IDs
        self.load_errors: list[str] = []

        # Tenta carregar do arquivo .ui, senão usa fallback
        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()

        self._connect_signals()

        logger.debug("upload_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Encontra widgets do arquivo .ui
        self.file_path_edit = self.findChild(QLineEdit, "filePathEdit")
        self.browse_btn = self.findChild(QPushButton, "browseBtn")
        self.browse_multi_btn = self.findChild(QPushButton, "browseMultiBtn")
        self.files_list_label = self.findChild(QLabel, "filesListLabel")
        self.format_label = self.findChild(QLabel, "formatLabel")
        
        self.tabs = self.findChild(QTabWidget, "tabs")
        
        # Configuration widgets
        self.encoding_combo = self.findChild(QComboBox, "encodingCombo")
        self.delimiter_combo = self.findChild(QComboBox, "delimiterCombo")
        self.timestamp_combo = self.findChild(QComboBox, "timestampCombo")
        self.sheet_combo = self.findChild(QComboBox, "sheetCombo")
        self.hdf5_key_combo = self.findChild(QComboBox, "hdf5KeyCombo")
        
        # Excel and HDF5 groups
        self.excel_group = self.findChild(QGroupBox, "excelGroup")
        self.hdf5_group = self.findChild(QGroupBox, "hdf5Group")
        
        # Preview widgets
        self.preview_table = self.findChild(QTableWidget, "previewTable")
        self.preview_info_label = self.findChild(QLabel, "previewInfoLabel")
        
        # Progress widgets
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        self.status_label = self.findChild(QLabel, "statusLabel")
        self.loaded_files_label = self.findChild(QLabel, "loadedFilesLabel")
        
        # Buttons
        self.preview_btn = self.findChild(QPushButton, "previewBtn")
        self.cancel_btn = self.findChild(QPushButton, "cancelBtn")
        self.load_all_btn = self.findChild(QPushButton, "loadAllBtn")
        self.load_btn = self.findChild(QPushButton, "loadBtn")
        
        # Inicializa o contador de arquivos carregados
        self.loaded_count = 0
        
        # Oculta grupos específicos de formato inicialmente
        if self.excel_group:
            self.excel_group.setVisible(False)
        if self.hdf5_group:
            self.hdf5_group.setVisible(False)
        
        logger.debug("upload_dialog_ui_loaded_from_file")

    def _setup_ui_fallback(self):
        """Setup user interface"""
        self.setWindowTitle(tr("Load Data Files"))
        self.setModal(True)
        self.resize(900, 700)

        layout = QVBoxLayout(self)

        # File selection section
        file_group = QGroupBox(tr("File Selection"))
        file_layout = QVBoxLayout(file_group)

        # File path and browse buttons
        path_layout = QHBoxLayout()

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText(tr("Select file(s) to load..."))
        self.file_path_edit.textChanged.connect(self._on_file_path_changed)
        path_layout.addWidget(self.file_path_edit)

        self.browse_btn = QPushButton(tr("Browse..."))
        self.browse_btn.clicked.connect(self._browse_file)
        self.browse_btn.setToolTip(tr("Select a single file"))
        path_layout.addWidget(self.browse_btn)

        self.browse_multi_btn = QPushButton(tr("Select Multiple..."))
        self.browse_multi_btn.clicked.connect(self._browse_multiple_files)
        self.browse_multi_btn.setToolTip(tr("Select multiple files at once"))
        path_layout.addWidget(self.browse_multi_btn)

        file_layout.addLayout(path_layout)

        # Selected files list
        self.files_list_label = QLabel(tr("No files selected"))
        self.files_list_label.setWordWrap(True)
        file_layout.addWidget(self.files_list_label)

        # Format detection
        self.format_label = QLabel(tr("Format: Not detected"))
        file_layout.addWidget(self.format_label)

        layout.addWidget(file_group)

        # Configuration and preview tabs
        self.tabs = QTabWidget()

        # Configuration tab
        self.config_tab = self._create_config_tab()
        self.tabs.addTab(self.config_tab, tr("Configuration"))

        # Preview tab
        self.preview_tab = self._create_preview_tab()
        self.tabs.addTab(self.preview_tab, tr("Preview"))

        layout.addWidget(self.tabs)

        # Progress section
        progress_group = QGroupBox(tr("Progress"))
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel(tr("Select a file to begin"))
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # Loaded files list (for multiple files)
        self.loaded_files_label = QLabel("")
        self.loaded_files_label.setStyleSheet("color: green; font-weight: bold;")
        self.loaded_files_label.setWordWrap(True)
        layout.addWidget(self.loaded_files_label)
        self.loaded_count = 0

        # Buttons
        buttons_layout = QHBoxLayout()

        self.preview_btn = QPushButton(tr("Generate Preview"))
        self.preview_btn.clicked.connect(self._generate_preview)
        self.preview_btn.setEnabled(False)
        buttons_layout.addWidget(self.preview_btn)

        buttons_layout.addStretch()

        self.cancel_btn = QPushButton(tr("Close"))
        self.cancel_btn.clicked.connect(self._close_dialog)
        buttons_layout.addWidget(self.cancel_btn)

        self.load_all_btn = QPushButton(tr("Load All Selected"))
        self.load_all_btn.clicked.connect(self._load_all_files)
        self.load_all_btn.setEnabled(False)
        self.load_all_btn.setToolTip(tr("Load all selected files simultaneously"))
        self.load_all_btn.setStyleSheet("font-weight: bold;")
        buttons_layout.addWidget(self.load_all_btn)

        self.load_btn = QPushButton(tr("Load && Close"))
        self.load_btn.clicked.connect(self._load_file)
        self.load_btn.setEnabled(False)
        self.load_btn.setToolTip(tr("Load single file and close dialog"))
        buttons_layout.addWidget(self.load_btn)

        layout.addLayout(buttons_layout)

    def _create_config_tab(self) -> QWidget:
        """Create configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # General configuration
        general_group = QGroupBox(tr("General Settings"))
        general_layout = QFormLayout(general_group)

        # Encoding
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "latin-1", "cp1252", "ascii"])
        self.encoding_combo.currentTextChanged.connect(self._update_config)
        general_layout.addRow(tr("Encoding:"), self.encoding_combo)

        # Delimiter (for CSV)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([",", ";", "\\t", "|"])
        self.delimiter_combo.setEditable(True)
        self.delimiter_combo.currentTextChanged.connect(self._update_config)
        general_layout.addRow(tr("Delimiter:"), self.delimiter_combo)

        layout.addWidget(general_group)

        # Schema configuration
        schema_group = QGroupBox(tr("Schema Detection"))
        schema_layout = QFormLayout(schema_group)

        # Timestamp column
        self.timestamp_combo = QComboBox()
        self.timestamp_combo.addItem(tr("Auto-detect"), None)
        self.timestamp_combo.currentTextChanged.connect(self._update_config)
        schema_layout.addRow(tr("Timestamp Column:"), self.timestamp_combo)

        # Skip rows
        self.skip_rows_spin = QSpinBox()
        self.skip_rows_spin.setRange(0, 100)
        self.skip_rows_spin.valueChanged.connect(self._update_config)
        schema_layout.addRow(tr("Skip Rows:"), self.skip_rows_spin)

        layout.addWidget(schema_group)

        # Excel-specific configuration
        self.excel_group = QGroupBox(tr("Excel Settings"))
        excel_layout = QFormLayout(self.excel_group)

        self.sheet_combo = QComboBox()
        self.sheet_combo.currentTextChanged.connect(self._update_config)
        excel_layout.addRow(tr("Sheet:"), self.sheet_combo)

        layout.addWidget(self.excel_group)

        # HDF5-specific configuration
        self.hdf5_group = QGroupBox(tr("HDF5 Settings"))
        hdf5_layout = QFormLayout(self.hdf5_group)

        self.hdf5_key_edit = QLineEdit()
        self.hdf5_key_edit.textChanged.connect(self._update_config)
        hdf5_layout.addRow(tr("Key:"), self.hdf5_key_edit)

        layout.addWidget(self.hdf5_group)

        # Advanced options
        advanced_group = QGroupBox(tr("Advanced Options"))
        advanced_layout = QFormLayout(advanced_group)

        self.chunk_check = QCheckBox(tr("Use chunked loading"))
        self.chunk_check.toggled.connect(self._update_config)
        advanced_layout.addRow(tr("Performance:"), self.chunk_check)

        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1000, 1000000)
        self.chunk_size_spin.setValue(10000)
        self.chunk_size_spin.setEnabled(False)
        self.chunk_size_spin.valueChanged.connect(self._update_config)
        advanced_layout.addRow(tr("Chunk Size:"), self.chunk_size_spin)

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
        controls_layout.addWidget(QLabel(tr("Data Preview:")))
        controls_layout.addStretch()

        self.refresh_preview_btn = QPushButton(tr("Refresh"))
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
        # Conecta sinais dos widgets
        if self.file_path_edit:
            self.file_path_edit.textChanged.connect(self._on_file_path_changed)
        if self.browse_btn:
            self.browse_btn.clicked.connect(self._browse_file)
        if self.browse_multi_btn:
            self.browse_multi_btn.clicked.connect(self._browse_multiple_files)
        if self.preview_btn:
            self.preview_btn.clicked.connect(self._generate_preview)
        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self._close_dialog)
        if self.load_all_btn:
            self.load_all_btn.clicked.connect(self._load_all_files)
        if self.load_btn:
            self.load_btn.clicked.connect(self._load_file)

    @pyqtSlot()
    def _browse_file(self):
        """Open file browser for single file"""
        file_filters = [
            "All Supported (*.csv *.xlsx *.xls *.parquet *.h5 *.hdf5)",
            "CSV Files (*.csv)",
            "Excel Files (*.xlsx *.xls)",
            "Parquet Files (*.parquet)",
            "HDF5 Files (*.h5 *.hdf5)",
            "All Files (*)",
        ]

        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("Select Data File"), "", ";;".join(file_filters),
        )

        if filepath:
            self.selected_files = [filepath]
            self.file_path_edit.setText(filepath)
            self._update_files_list_display()

    @pyqtSlot()
    def _browse_multiple_files(self):
        """Open file browser for multiple files"""
        file_filters = [
            "All Supported (*.csv *.xlsx *.xls *.parquet *.h5 *.hdf5)",
            "CSV Files (*.csv)",
            "Excel Files (*.xlsx *.xls)",
            "Parquet Files (*.parquet)",
            "HDF5 Files (*.h5 *.hdf5)",
            "All Files (*)",
        ]

        # Use non-native dialog to ensure multi-selection works on Windows
        dialog = QFileDialog(self, tr("Select Data Files"))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Allow multiple file selection
        dialog.setNameFilters(file_filters)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)  # Use Qt dialog

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            filepaths = dialog.selectedFiles()
            if filepaths:
                self.selected_files = filepaths
                if len(filepaths) == 1:
                    self.file_path_edit.setText(filepaths[0])
                else:
                    self.file_path_edit.setText(f"{len(filepaths)} files selected")
                self._update_files_list_display()
                self._enable_load_buttons()

    def _update_files_list_display(self):
        """Update the display showing selected files"""
        if not self.selected_files:
            self.files_list_label.setText(tr("No files selected"))
            return

        if len(self.selected_files) == 1:
            self.files_list_label.setText(f"📄 {Path(self.selected_files[0]).name}")
        else:
            file_names = [Path(f).name for f in self.selected_files]
            display_text = f"📄 {len(file_names)} files: " + ", ".join(file_names[:5])
            if len(file_names) > 5:
                display_text += f" ... (+{len(file_names) - 5} more)"
            self.files_list_label.setText(display_text)

    def _enable_load_buttons(self):
        """Enable load buttons based on selected files"""
        has_files = len(self.selected_files) > 0
        has_multiple = len(self.selected_files) > 1

        self.load_btn.setEnabled(has_files)
        self.load_all_btn.setEnabled(has_multiple)
        self.preview_btn.setEnabled(has_files and len(self.selected_files) == 1)

        if has_multiple:
            self.status_label.setText(
                tr("{count} files selected. Click 'Load All Selected' to load them.").format(
                    count=len(self.selected_files),
                ),
            )
        elif has_files:
            self.status_label.setText(tr("File selected. Configure options or generate preview."))
    @pyqtSlot(str)
    def _on_file_path_changed(self, filepath: str):
        """Handle file path change"""
        # Check for multi-file indicator
        if filepath and "files selected" in filepath:
            # Multiple files selected, don't try to parse as path
            return

        if not filepath or not Path(filepath).exists():
            self._reset_ui_state()
            return

        # Update selected_files if single file
        if len(self.selected_files) != 1 or self.selected_files[0] != filepath:
            self.selected_files = [filepath]
            self._update_files_list_display()

        # Detect format
        file_path = Path(filepath)
        format_detected = self._detect_format(file_path)
        self.format_label.setText(f"{tr('Format')}: {format_detected}")

        # Update UI based on format
        self._update_format_ui(format_detected)

        # Update column options for timestamp detection
        self._update_column_options(filepath)

        # Enable buttons
        self._enable_load_buttons()
        self.refresh_preview_btn.setEnabled(True)

        self.status_label.setText(tr("File selected. Configure options or generate preview."))

    def _detect_format(self, file_path: Path) -> str:
        """Detect file format"""
        suffix = file_path.suffix.lower()
        format_map = {
            ".csv": "CSV",
            ".xlsx": "Excel",
            ".xls": "Excel",
            ".parquet": "Parquet",
            ".h5": "HDF5",
            ".hdf5": "HDF5",
        }
        return format_map.get(suffix, "Unknown")

    def _update_format_ui(self, format_type: str):
        """Update UI based on detected format"""
        # Show/hide format-specific options
        self.excel_group.setVisible(format_type == "Excel")
        self.hdf5_group.setVisible(format_type == "HDF5")

        # Update delimiter visibility
        self.delimiter_combo.setEnabled(format_type == "CSV")

        # Update configuration
        self._update_config()

    def _update_column_options(self, filepath: str):
        """Update column options from file"""
        try:
            # Quick column detection
            file_path = Path(filepath)

            if file_path.suffix.lower() == ".csv":
                import pandas as pd
                df_sample = pd.read_csv(filepath, nrows=1)
                columns = list(df_sample.columns)

                # Update timestamp column options
                self.timestamp_combo.clear()
                self.timestamp_combo.addItem(tr("Auto-detect"), None)
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
            "sheet_name": self.sheet_combo.currentText() if self.sheet_combo.count() > 0 else 0,
            "hdf5_key": self.hdf5_key_edit.text() if self.hdf5_key_edit.text() else None,
            "chunk_size": self.chunk_size_spin.value() if self.chunk_check.isChecked() else None,
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
    def _on_preview_ready(self, preview_data: dict[str, Any]):
        """Handle preview data ready"""
        try:
            logger.debug("preview_ready_received", type=type(preview_data).__name__)

            # Validate received data
            if not isinstance(preview_data, dict):
                logger.error("preview_ready_invalid_type", type=type(preview_data).__name__)
                self._on_preview_error(f"Invalid preview data type: {type(preview_data).__name__}")
                return

            # Store preview data
            self.preview_data = preview_data

            # Update display
            self._update_preview_display()

            # Switch to preview tab
            self.tabs.setCurrentIndex(1)

        except Exception as e:
            logger.exception("preview_ready_handler_failed", error=str(e))
            self._on_preview_error(f"Failed to process preview: {e!s}")

    @pyqtSlot(str)
    def _on_preview_error(self, error_message: str):
        """Handle preview error"""
        QMessageBox.warning(self, tr("Preview Error"), f"{tr('Failed to generate preview')}:\\n{error_message}")
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
                           type=type(self.preview_data).__name__,
                           preview_data=str(self.preview_data)[:200])
                return

            logger.debug("preview_display_start", keys=list(self.preview_data.keys()))

            # Update preview table
            head_data = self.preview_data.get("head", [])
            columns = self.preview_data.get("columns", [])

            logger.debug("preview_display_data",
                        head_data_len=len(head_data) if head_data else 0,
                        columns_len=len(columns) if columns else 0)

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
                "Column Types:",
            ]

            for col, dtype in dtypes.items():
                info_lines.append(f"  {col}: {dtype}")

            self.preview_info.setPlainText("\\n".join(info_lines))

        except Exception as e:
            logger.exception("preview_display_error", error=str(e))
            self.preview_info.setPlainText(f"Error displaying preview: {e!s}")
            # Clear preview table on error
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)

    @pyqtSlot()
    def _load_file(self):
        """Load the selected file and close dialog"""
        self._close_after_load = True
        self._start_file_load()

    @pyqtSlot()
    def _load_file_and_continue(self):
        """Load the selected file and keep dialog open for more files"""
        self._close_after_load = False
        self._start_file_load()

    def _start_file_load(self):
        """Start the file loading process for single file"""
        filepath = self.file_path_edit.text()
        if not filepath or not Path(filepath).exists():
            # Check if we have selected_files instead
            if self.selected_files and len(self.selected_files) == 1:
                filepath = self.selected_files[0]
            else:
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
        self.load_all_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)

    @pyqtSlot()
    def _load_all_files(self):
        """Load all selected files simultaneously"""
        if not self.selected_files:
            return

        # Reset state
        self.pending_files = list(self.selected_files)
        self.loading_files = {}
        self.loaded_datasets = []
        self.load_errors = []

        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.pending_files))
        self.progress_bar.setValue(0)
        self.load_btn.setEnabled(False)
        self.load_all_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.browse_multi_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)

        self.status_label.setText(
            tr("Loading {count} files...").format(count=len(self.pending_files)),
        )

        logger.info("multi_file_load_started", file_count=len(self.pending_files))

        # Start loading all files in parallel
        for filepath in self.pending_files:
            worker = FileLoadWorker(filepath, self.current_config)
            worker.file_loaded.connect(self._on_multi_file_loaded)
            worker.error.connect(lambda err, fp=filepath: self._on_multi_file_error(fp, err))
            worker.finished.connect(lambda fp=filepath: self._on_multi_file_finished(fp))

            self.loading_files[filepath] = worker
            worker.start()

    @pyqtSlot(str, object)
    def _on_multi_file_loaded(self, filepath: str, dataset):
        """Handle single file loaded in multi-file operation"""
        # Add dataset to store
        dataset_id = self.session_state.dataset_store.add_dataset(dataset)
        self.loaded_datasets.append(dataset_id)

        # Emit signal
        self.signal_hub.emit_dataset_loaded(dataset_id)

        # Update loaded count
        self.loaded_count += 1

        # Update progress
        completed = len(self.loaded_datasets) + len(self.load_errors)
        self.progress_bar.setValue(completed)

        self.loaded_files_label.setText(
            tr("✓ {count}/{total} files loaded").format(
                count=len(self.loaded_datasets),
                total=len(self.pending_files),
            ),
        )

        logger.info("multi_file_loaded",
                   filepath=filepath,
                   dataset_id=dataset_id,
                   progress=f"{completed}/{len(self.pending_files)}")

    def _on_multi_file_error(self, filepath: str, error_message: str):
        """Handle error loading single file in multi-file operation"""
        self.load_errors.append(f"{Path(filepath).name}: {error_message}")
        logger.error("multi_file_load_error", filepath=filepath, error=error_message)

        # Update progress
        completed = len(self.loaded_datasets) + len(self.load_errors)
        self.progress_bar.setValue(completed)

    def _on_multi_file_finished(self, filepath: str):
        """Handle worker finished for single file in multi-file operation"""
        # Remove from loading dict
        if filepath in self.loading_files:
            worker = self.loading_files.pop(filepath)
            # Ensure thread is properly stopped before cleanup
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)
            worker.deleteLater()

        # Check if all files are done
        if not self.loading_files:
            self._on_all_files_loaded()

    def _on_all_files_loaded(self):
        """Handle completion of all file loading"""
        self.progress_bar.setVisible(False)
        self.browse_btn.setEnabled(True)
        self.browse_multi_btn.setEnabled(True)

        len(self.pending_files)
        success = len(self.loaded_datasets)
        errors = len(self.load_errors)

        # Show summary
        if errors == 0:
            self.status_label.setText(
                tr("✓ All {count} files loaded successfully!").format(count=success),
            )
            self.loaded_files_label.setStyleSheet("color: green; font-weight: bold;")
            self.loaded_files_label.setText(
                tr("✓ {count} datasets ready").format(count=success),
            )
            logger.info("multi_file_load_complete", success=success, errors=0)

            # Auto-close after success
            QMessageBox.information(
                self,
                tr("Load Complete"),
                tr("{count} files loaded successfully!").format(count=success),
            )
            self.accept()
        else:
            # Some errors occurred
            self.loaded_files_label.setStyleSheet("color: orange; font-weight: bold;")
            self.loaded_files_label.setText(
                tr("⚠ {success} loaded, {errors} failed").format(success=success, errors=errors),
            )
            self.status_label.setText(tr("Loading completed with some errors"))

            # Show error details
            error_details = "\n".join(self.load_errors[:10])
            if len(self.load_errors) > 10:
                error_details += f"\n... and {len(self.load_errors) - 10} more errors"

            QMessageBox.warning(
                self,
                tr("Load Completed with Errors"),
                tr("{success} files loaded, {errors} failed:\n\n{details}").format(
                    success=success, errors=errors, details=error_details,
                ),
            )

            logger.warning("multi_file_load_complete_with_errors",
                          success=success, errors=errors)

            if success > 0:
                self.accept()
            else:
                # Re-enable buttons if nothing was loaded
                self._enable_load_buttons()

    @pyqtSlot(str, object)
    def _on_file_loaded(self, filepath: str, dataset):
        """Handle file loaded successfully"""
        # Add dataset to store
        dataset_id = self.session_state.dataset_store.add_dataset(dataset)

        # Emit signal
        self.signal_hub.emit_dataset_loaded(dataset_id)

        # Update loaded count
        self.loaded_count += 1
        self.loaded_files_label.setText(
            tr("✓ {count} file(s) loaded successfully").format(count=self.loaded_count),
        )

        logger.info("file_loaded_successfully", filepath=filepath, dataset_id=dataset_id)

        # Close dialog or prepare for next file
        if getattr(self, "_close_after_load", True):
            self.accept()
        else:
            # Reset for next file
            self.file_path_edit.clear()
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.preview_info.clear()
            self.status_label.setText(tr("Select another file to load"))
            self._browse_file()  # Open file browser for next file

    @pyqtSlot()
    def _close_dialog(self):
        """Close the dialog"""
        if self.loaded_count > 0:
            self.accept()
        else:
            self.reject()

    @pyqtSlot(str)
    def _on_load_error(self, error_message: str):
        """Handle load error"""
        QMessageBox.critical(self, tr("Load Error"), f"{tr('Failed to load file')}:\\n{error_message}")
        logger.error("file_load_failed", error=error_message)

    @pyqtSlot()
    def _on_load_finished(self):
        """Handle load worker finished"""
        self.progress_bar.setVisible(False)
        self._enable_load_buttons()

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
        self.selected_files = []
        self.format_label.setText(tr("Format: Not detected"))
        self.files_list_label.setText(tr("No files selected"))
        self.preview_btn.setEnabled(False)
        self.refresh_preview_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.load_all_btn.setEnabled(False)
        self.status_label.setText(tr("Select a file to begin"))

        # Clear preview
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.preview_info.clear()

    def closeEvent(self, event):
        """Handle dialog close"""
        # Stop any running single workers
        if self.load_worker and self.load_worker.isRunning():
            self.load_worker.terminate()
            self.load_worker.wait()

        if self.preview_worker and self.preview_worker.isRunning():
            self.preview_worker.terminate()
            self.preview_worker.wait()

        # Stop any running multi-file workers
        for _filepath, worker in list(self.loading_files.items()):
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        self.loading_files.clear()

        event.accept()
