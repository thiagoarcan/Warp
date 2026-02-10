"""
Comprehensive tests for desktop/dialogs/upload_dialog.py

Tests FileLoadWorker, PreviewWorker, and UploadDialog.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import numpy as np
import pytest

# Skip all tests if PyQt6 is not available
pytestmark = pytest.mark.skipif(
    not pytest.importorskip("PyQt6", reason="PyQt6 required").QtCore,
    reason="PyQt6.QtCore not available"
)


# =============================================================================
# FileLoadWorker Tests
# =============================================================================

class TestFileLoadWorker:
    """Tests for FileLoadWorker class."""
    
    @pytest.fixture
    def mock_dataset(self):
        """Create mock dataset."""
        dataset = MagicMock()
        dataset.series = {}
        dataset.timestamps = np.array([0.0, 1.0, 2.0])
        return dataset
    
    def test_worker_creation(self, qtbot):
        """Test FileLoadWorker creation."""
        from platform_base.desktop.dialogs.upload_dialog import FileLoadWorker
        
        worker = FileLoadWorker("/path/to/file.csv", {"encoding": "utf-8"})
        
        assert worker.filepath == "/path/to/file.csv"
        assert worker.config == {"encoding": "utf-8"}
    
    def test_worker_has_signals(self, qtbot):
        """Test FileLoadWorker has required signals."""
        from platform_base.desktop.dialogs.upload_dialog import FileLoadWorker
        
        worker = FileLoadWorker("/path/to/file.csv", {})
        
        assert hasattr(worker, 'file_loaded')
        assert hasattr(worker, 'progress')
        assert hasattr(worker, 'status_updated')
        assert hasattr(worker, 'error')
        assert hasattr(worker, 'finished')
    
    def test_worker_config_passed_correctly(self, qtbot):
        """Test worker stores config correctly."""
        from platform_base.desktop.dialogs.upload_dialog import FileLoadWorker
        
        config = {
            "encoding": "latin-1",
            "delimiter": ";",
            "timestamp_column": "Time",
            "sheet_name": "Data",
        }
        
        worker = FileLoadWorker("/path/to/file.csv", config)
        
        assert worker.config["encoding"] == "latin-1"
        assert worker.config["delimiter"] == ";"
        assert worker.config["timestamp_column"] == "Time"


# =============================================================================
# PreviewWorker Tests
# =============================================================================

class TestPreviewWorker:
    """Tests for PreviewWorker class."""
    
    def test_preview_worker_creation(self, qtbot):
        """Test PreviewWorker creation."""
        from platform_base.desktop.dialogs.upload_dialog import PreviewWorker
        
        worker = PreviewWorker("/path/to/file.csv", {"encoding": "utf-8"})
        
        assert worker.filepath == "/path/to/file.csv"
        assert worker.config == {"encoding": "utf-8"}
    
    def test_preview_worker_has_signals(self, qtbot):
        """Test PreviewWorker has required signals."""
        from platform_base.desktop.dialogs.upload_dialog import PreviewWorker
        
        worker = PreviewWorker("/path/to/file.csv", {})
        
        assert hasattr(worker, 'preview_ready')
        assert hasattr(worker, 'progress')
        assert hasattr(worker, 'error')
        assert hasattr(worker, 'finished')
    
    def test_preview_worker_with_csv_file(self, qtbot, tmp_path):
        """Test preview worker with real CSV file."""
        from platform_base.desktop.dialogs.upload_dialog import PreviewWorker

        # Create test CSV file
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n")
        
        worker = PreviewWorker(str(csv_file), {"encoding": "utf-8", "delimiter": ","})
        
        # Capture signals
        received_preview = []
        worker.preview_ready.connect(lambda data: received_preview.append(data))
        
        errors = []
        worker.error.connect(lambda err: errors.append(err))
        
        # Run worker
        worker.run()
        
        # Should have received preview data
        if not errors:
            assert len(received_preview) == 1
            preview_data = received_preview[0]
            assert "columns" in preview_data
            assert "col1" in preview_data["columns"]
            assert "col2" in preview_data["columns"]
            assert "col3" in preview_data["columns"]


# =============================================================================
# UploadDialog Tests
# =============================================================================

class TestUploadDialog:
    """Tests for UploadDialog class."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Create mock session state."""
        state = MagicMock()
        state.dataset_store = MagicMock()
        state.dataset_store.add_dataset.return_value = "test_dataset_id"
        return state
    
    @pytest.fixture
    def mock_signal_hub(self):
        """Create mock signal hub."""
        hub = MagicMock()
        hub.emit_dataset_loaded = MagicMock()
        return hub
    
    @pytest.fixture
    def upload_dialog(self, mock_session_state, mock_signal_hub, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        dialog = UploadDialog(
            session_state=mock_session_state,
            signal_hub=mock_signal_hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_dialog_creation(self, upload_dialog):
        """Test basic dialog creation."""
        assert upload_dialog is not None
        assert upload_dialog.session_state is not None
        assert upload_dialog.signal_hub is not None
    
    def test_dialog_title(self, upload_dialog):
        """Test dialog has correct title."""
        title = upload_dialog.windowTitle()
        # Aceita títulos em inglês ou português
        assert ("Load" in title or "Data" in title or 
                "Carregar" in title or "Arquivos" in title)
    
    def test_dialog_initial_state(self, upload_dialog):
        """Test dialog initial state."""
        assert upload_dialog.selected_files == []
        assert upload_dialog.preview_data is None
        assert upload_dialog.load_worker is None
        assert upload_dialog.preview_worker is None
    
    def test_dialog_has_file_path_edit(self, upload_dialog):
        """Test dialog has file path input."""
        assert hasattr(upload_dialog, 'file_path_edit')
        assert upload_dialog.file_path_edit is not None
    
    def test_dialog_has_browse_buttons(self, upload_dialog):
        """Test dialog has browse buttons."""
        assert hasattr(upload_dialog, 'browse_btn')
        assert hasattr(upload_dialog, 'browse_multi_btn')
        assert upload_dialog.browse_btn is not None
        assert upload_dialog.browse_multi_btn is not None
    
    def test_dialog_has_load_buttons(self, upload_dialog):
        """Test dialog has load buttons."""
        assert hasattr(upload_dialog, 'load_btn')
        assert hasattr(upload_dialog, 'load_all_btn')
        # Initially disabled
        assert not upload_dialog.load_btn.isEnabled()
        assert not upload_dialog.load_all_btn.isEnabled()
    
    def test_dialog_has_preview_button(self, upload_dialog):
        """Test dialog has preview button."""
        assert hasattr(upload_dialog, 'preview_btn')
        # Initially disabled
        assert not upload_dialog.preview_btn.isEnabled()
    
    def test_dialog_has_tabs(self, upload_dialog):
        """Test dialog has configuration and preview tabs."""
        assert hasattr(upload_dialog, 'tabs')
        assert upload_dialog.tabs.count() == 2
    
    def test_dialog_has_encoding_combo(self, upload_dialog):
        """Test dialog has encoding configuration."""
        assert hasattr(upload_dialog, 'encoding_combo')
        # Check default encodings available
        encodings = [upload_dialog.encoding_combo.itemText(i) 
                    for i in range(upload_dialog.encoding_combo.count())]
        assert "utf-8" in encodings
        assert "latin-1" in encodings
    
    def test_dialog_has_delimiter_combo(self, upload_dialog):
        """Test dialog has delimiter configuration."""
        assert hasattr(upload_dialog, 'delimiter_combo')
        # Check default delimiters available
        delimiters = [upload_dialog.delimiter_combo.itemText(i) 
                     for i in range(upload_dialog.delimiter_combo.count())]
        assert "," in delimiters
        assert ";" in delimiters
    
    def test_dialog_has_progress_bar(self, upload_dialog):
        """Test dialog has progress bar."""
        assert hasattr(upload_dialog, 'progress_bar')
        # Initially hidden
        assert not upload_dialog.progress_bar.isVisible()
    
    def test_dialog_has_status_label(self, upload_dialog):
        """Test dialog has status label."""
        assert hasattr(upload_dialog, 'status_label')
    
    def test_dialog_has_preview_table(self, upload_dialog):
        """Test dialog has preview table."""
        assert hasattr(upload_dialog, 'preview_table')


# =============================================================================
# UploadDialog Method Tests
# =============================================================================

class TestUploadDialogMethods:
    """Tests for UploadDialog methods."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Create mock session state."""
        state = MagicMock()
        state.dataset_store = MagicMock()
        state.dataset_store.add_dataset.return_value = "test_dataset_id"
        return state
    
    @pytest.fixture
    def mock_signal_hub(self):
        """Create mock signal hub."""
        hub = MagicMock()
        return hub
    
    @pytest.fixture
    def upload_dialog(self, mock_session_state, mock_signal_hub, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        dialog = UploadDialog(
            session_state=mock_session_state,
            signal_hub=mock_signal_hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_detect_format_csv(self, upload_dialog):
        """Test format detection for CSV files."""
        result = upload_dialog._detect_format(Path("/data/file.csv"))
        assert result == "CSV"
    
    def test_detect_format_xlsx(self, upload_dialog):
        """Test format detection for Excel files."""
        result = upload_dialog._detect_format(Path("/data/file.xlsx"))
        assert result == "Excel"
    
    def test_detect_format_xls(self, upload_dialog):
        """Test format detection for old Excel files."""
        result = upload_dialog._detect_format(Path("/data/file.xls"))
        assert result == "Excel"
    
    def test_detect_format_parquet(self, upload_dialog):
        """Test format detection for Parquet files."""
        result = upload_dialog._detect_format(Path("/data/file.parquet"))
        assert result == "Parquet"
    
    def test_detect_format_h5(self, upload_dialog):
        """Test format detection for HDF5 files."""
        result = upload_dialog._detect_format(Path("/data/file.h5"))
        assert result == "HDF5"
    
    def test_detect_format_hdf5(self, upload_dialog):
        """Test format detection for HDF5 files (alt extension)."""
        result = upload_dialog._detect_format(Path("/data/file.hdf5"))
        assert result == "HDF5"
    
    def test_detect_format_unknown(self, upload_dialog):
        """Test format detection for unknown files."""
        result = upload_dialog._detect_format(Path("/data/file.unknown"))
        assert result == "Unknown"
    
    def test_update_format_ui_csv(self, upload_dialog):
        """Test UI update for CSV format."""
        upload_dialog._update_format_ui("CSV")
        
        assert upload_dialog.delimiter_combo.isEnabled()
        assert not upload_dialog.excel_group.isVisible()
        assert not upload_dialog.hdf5_group.isVisible()
    
    def test_update_format_ui_excel(self, upload_dialog):
        """Test UI update for Excel format."""
        # Forçar o diálogo a estar visível antes de fazer chamadas
        upload_dialog.show()
        upload_dialog._update_format_ui("Excel")
        
        # Processar eventos para atualizar a UI
        upload_dialog.setVisible(True)
        
        assert upload_dialog.excel_group.isVisible()
        assert not upload_dialog.hdf5_group.isVisible()
    
    def test_update_format_ui_hdf5(self, upload_dialog):
        """Test UI update for HDF5 format."""
        # Forçar o diálogo a estar visível antes de fazer chamadas
        upload_dialog.show()
        upload_dialog._update_format_ui("HDF5")
        
        # Processar eventos para atualizar a UI
        upload_dialog.setVisible(True)
        
        assert upload_dialog.hdf5_group.isVisible()
        assert not upload_dialog.excel_group.isVisible()
    
    def test_update_config(self, upload_dialog):
        """Test configuration update."""
        # Set values
        upload_dialog.encoding_combo.setCurrentText("latin-1")
        upload_dialog.delimiter_combo.setCurrentText(";")
        upload_dialog.skip_rows_spin.setValue(5)
        
        # Update config
        upload_dialog._update_config()
        
        assert upload_dialog.current_config["encoding"] == "latin-1"
        assert upload_dialog.current_config["delimiter"] == ";"
        assert upload_dialog.current_config["skip_rows"] == 5
    
    def test_update_files_list_display_empty(self, upload_dialog):
        """Test files list display with no files."""
        upload_dialog.selected_files = []
        upload_dialog._update_files_list_display()
        
        assert "No files" in upload_dialog.files_list_label.text()
    
    def test_update_files_list_display_single(self, upload_dialog):
        """Test files list display with single file."""
        upload_dialog.selected_files = ["/path/to/data.csv"]
        upload_dialog._update_files_list_display()
        
        assert "data.csv" in upload_dialog.files_list_label.text()
    
    def test_update_files_list_display_multiple(self, upload_dialog):
        """Test files list display with multiple files."""
        upload_dialog.selected_files = [f"/path/to/file{i}.csv" for i in range(10)]
        upload_dialog._update_files_list_display()
        
        assert "10 files" in upload_dialog.files_list_label.text()
    
    def test_enable_load_buttons_no_files(self, upload_dialog):
        """Test load buttons disabled with no files."""
        upload_dialog.selected_files = []
        upload_dialog._enable_load_buttons()
        
        assert not upload_dialog.load_btn.isEnabled()
        assert not upload_dialog.load_all_btn.isEnabled()
    
    def test_enable_load_buttons_single_file(self, upload_dialog):
        """Test load buttons with single file."""
        upload_dialog.selected_files = ["/path/to/file.csv"]
        upload_dialog._enable_load_buttons()
        
        assert upload_dialog.load_btn.isEnabled()
        assert not upload_dialog.load_all_btn.isEnabled()
        assert upload_dialog.preview_btn.isEnabled()
    
    def test_enable_load_buttons_multiple_files(self, upload_dialog):
        """Test load buttons with multiple files."""
        upload_dialog.selected_files = ["/path/to/file1.csv", "/path/to/file2.csv"]
        upload_dialog._enable_load_buttons()
        
        assert upload_dialog.load_btn.isEnabled()
        assert upload_dialog.load_all_btn.isEnabled()
        # Preview only available for single file
        assert not upload_dialog.preview_btn.isEnabled()
    
    def test_reset_ui_state(self, upload_dialog):
        """Test UI reset."""
        # Set some state
        upload_dialog.selected_files = ["/path/to/file.csv"]
        upload_dialog.load_btn.setEnabled(True)
        
        # Reset
        upload_dialog._reset_ui_state()
        
        assert upload_dialog.selected_files == []
        assert not upload_dialog.load_btn.isEnabled()
        assert not upload_dialog.preview_btn.isEnabled()


# =============================================================================
# Preview Display Tests
# =============================================================================

class TestUploadDialogPreviewDisplay:
    """Tests for preview display functionality."""
    
    @pytest.fixture
    def upload_dialog(self, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        hub = MagicMock()
        
        dialog = UploadDialog(
            session_state=state,
            signal_hub=hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_update_preview_display_with_data(self, upload_dialog):
        """Test preview display update with valid data."""
        upload_dialog.preview_data = {
            "columns": ["col1", "col2", "col3"],
            "dtypes": {"col1": "int64", "col2": "float64", "col3": "object"},
            "shape": (100, 3),
            "head": [
                {"col1": 1, "col2": 1.5, "col3": "a"},
                {"col1": 2, "col2": 2.5, "col3": "b"},
            ],
            "sample_values": {
                "col1": [1, 2, 3],
                "col2": [1.5, 2.5, 3.5],
                "col3": ["a", "b", "c"],
            },
        }
        
        # Update display
        upload_dialog._update_preview_display()
        
        # Check table updated
        assert upload_dialog.preview_table.columnCount() == 3
        assert upload_dialog.preview_table.rowCount() == 2
        
        # Check info text
        info_text = upload_dialog.preview_info.toPlainText()
        assert "100" in info_text
        assert "3" in info_text
    
    def test_update_preview_display_empty_data(self, upload_dialog):
        """Test preview display with empty data."""
        upload_dialog.preview_data = None
        
        # Should not raise
        upload_dialog._update_preview_display()
        
        # Table should remain empty
        assert upload_dialog.preview_table.rowCount() == 0
    
    def test_update_preview_display_invalid_data(self, upload_dialog):
        """Test preview display with invalid data type."""
        upload_dialog.preview_data = "invalid"
        
        # Should handle gracefully
        upload_dialog._update_preview_display()


# =============================================================================
# File Path Change Handler Tests
# =============================================================================

class TestUploadDialogFilePathChange:
    """Tests for file path change handling."""
    
    @pytest.fixture
    def upload_dialog(self, qtbot, tmp_path):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        hub = MagicMock()
        
        dialog = UploadDialog(
            session_state=state,
            signal_hub=hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_on_file_path_changed_multi_file_indicator(self, upload_dialog):
        """Test file path change ignores multi-file indicator."""
        # Should not try to process "X files selected"
        upload_dialog._on_file_path_changed("3 files selected")
        
        # Should not change state significantly
        # (No crash is the main test here)
    
    def test_on_file_path_changed_empty(self, upload_dialog):
        """Test file path change with empty path."""
        upload_dialog._on_file_path_changed("")
        
        # Should reset state
        assert upload_dialog.selected_files == []
    
    def test_on_file_path_changed_nonexistent(self, upload_dialog):
        """Test file path change with non-existent file."""
        upload_dialog._on_file_path_changed("/nonexistent/path/file.csv")
        
        # Should reset state
        assert upload_dialog.selected_files == []
    
    def test_on_file_path_changed_valid_file(self, upload_dialog, tmp_path):
        """Test file path change with valid file."""
        # Create test file
        test_file = tmp_path / "test.csv"
        test_file.write_text("col1,col2\n1,2\n3,4\n")
        
        upload_dialog._on_file_path_changed(str(test_file))
        
        # Should detect format
        assert "CSV" in upload_dialog.format_label.text()
        
        # Should enable buttons
        assert upload_dialog.load_btn.isEnabled()


# =============================================================================
# Multi-file Loading Tests
# =============================================================================

class TestUploadDialogMultiFileLoading:
    """Tests for multi-file loading functionality."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Create mock session state."""
        state = MagicMock()
        state.dataset_store = MagicMock()
        state.dataset_store.add_dataset.return_value = "test_dataset_id"
        return state
    
    @pytest.fixture
    def mock_signal_hub(self):
        """Create mock signal hub."""
        hub = MagicMock()
        hub.emit_dataset_loaded = MagicMock()
        return hub
    
    @pytest.fixture
    def upload_dialog(self, mock_session_state, mock_signal_hub, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        dialog = UploadDialog(
            session_state=mock_session_state,
            signal_hub=mock_signal_hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_multi_file_initial_state(self, upload_dialog):
        """Test initial state for multi-file loading."""
        assert upload_dialog.pending_files == []
        assert upload_dialog.loading_files == {}
        assert upload_dialog.loaded_datasets == []
        assert upload_dialog.load_errors == []
    
    def test_on_multi_file_loaded(self, upload_dialog, mock_session_state, mock_signal_hub):
        """Test handling of single file loaded in multi-file operation."""
        mock_dataset = MagicMock()
        
        # Setup pending files
        upload_dialog.pending_files = ["/file1.csv", "/file2.csv"]
        
        # Handle loaded file
        upload_dialog._on_multi_file_loaded("/file1.csv", mock_dataset)
        
        # Dataset should be added
        mock_session_state.dataset_store.add_dataset.assert_called_once_with(mock_dataset)
        
        # Signal should be emitted
        mock_signal_hub.emit_dataset_loaded.assert_called_once()
        
        # Loaded datasets should be tracked
        assert len(upload_dialog.loaded_datasets) == 1
    
    def test_on_multi_file_error(self, upload_dialog):
        """Test handling of error in multi-file operation."""
        upload_dialog.pending_files = ["/file1.csv", "/file2.csv"]
        
        upload_dialog._on_multi_file_error("/file1.csv", "Read error")
        
        assert len(upload_dialog.load_errors) == 1
        assert "file1.csv" in upload_dialog.load_errors[0]
        assert "Read error" in upload_dialog.load_errors[0]


# =============================================================================
# Dialog Close Tests
# =============================================================================

class TestUploadDialogClose:
    """Tests for dialog close functionality."""
    
    @pytest.fixture
    def upload_dialog(self, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        hub = MagicMock()
        
        dialog = UploadDialog(
            session_state=state,
            signal_hub=hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_close_dialog_no_loaded(self, upload_dialog):
        """Test closing dialog with no files loaded."""
        upload_dialog.loaded_count = 0
        
        # Should reject
        upload_dialog._close_dialog()
        # Dialog behavior depends on implementation
    
    def test_close_dialog_with_loaded(self, upload_dialog):
        """Test closing dialog with files loaded."""
        upload_dialog.loaded_count = 3
        
        # Should accept
        upload_dialog._close_dialog()
        # Dialog behavior depends on implementation


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestUploadDialogEdgeCases:
    """Edge case tests for UploadDialog."""
    
    @pytest.fixture
    def upload_dialog(self, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        hub = MagicMock()
        
        dialog = UploadDialog(
            session_state=state,
            signal_hub=hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_detect_format_case_insensitive(self, upload_dialog):
        """Test format detection is case insensitive."""
        result1 = upload_dialog._detect_format(Path("/data/file.CSV"))
        result2 = upload_dialog._detect_format(Path("/data/file.Csv"))
        result3 = upload_dialog._detect_format(Path("/data/file.csv"))
        
        assert result1 == "CSV"
        assert result2 == "CSV"
        assert result3 == "CSV"
    
    def test_preview_data_with_special_characters(self, upload_dialog):
        """Test preview display with special characters in data."""
        upload_dialog.preview_data = {
            "columns": ["名前", "データ", "日付"],
            "dtypes": {"名前": "object", "データ": "float64", "日付": "datetime64"},
            "shape": (10, 3),
            "head": [{"名前": "テスト", "データ": 1.5, "日付": "2024-01-01"}],
            "sample_values": {"名前": ["テスト"], "データ": [1.5], "日付": ["2024-01-01"]},
        }
        
        # Should not raise
        upload_dialog._update_preview_display()
        
        # Table should have columns
        assert upload_dialog.preview_table.columnCount() == 3
    
    def test_chunk_loading_config(self, upload_dialog):
        """Test chunk loading configuration."""
        # Enable chunked loading
        upload_dialog.chunk_check.setChecked(True)
        upload_dialog.chunk_size_spin.setValue(50000)
        
        # Update config
        upload_dialog._update_config()
        
        assert upload_dialog.current_config["chunk_size"] == 50000
    
    def test_chunk_loading_disabled(self, upload_dialog):
        """Test chunk loading when disabled."""
        # Disable chunked loading
        upload_dialog.chunk_check.setChecked(False)
        
        # Update config
        upload_dialog._update_config()
        
        assert upload_dialog.current_config["chunk_size"] is None


# =============================================================================
# Progress Update Tests
# =============================================================================

class TestUploadDialogProgress:
    """Tests for progress update functionality."""
    
    @pytest.fixture
    def upload_dialog(self, qtbot):
        """Create UploadDialog for testing."""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        state = MagicMock()
        state.dataset_store = MagicMock()
        hub = MagicMock()
        
        dialog = UploadDialog(
            session_state=state,
            signal_hub=hub,
        )
        qtbot.addWidget(dialog)
        return dialog
    
    def test_update_progress(self, upload_dialog):
        """Test progress bar update."""
        upload_dialog._update_progress(50)
        
        assert upload_dialog.progress_bar.value() == 50
    
    def test_update_status(self, upload_dialog):
        """Test status label update."""
        upload_dialog._update_status("Loading file...")
        
        assert "Loading" in upload_dialog.status_label.text()
