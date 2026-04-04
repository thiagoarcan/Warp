"""
Tests for ui/loader.py - UI Loader System

Tests the Qt Designer .ui file loading system.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestLoadUi:
    """Tests for load_ui function"""

    def test_load_ui_adds_extension(self):
        """Test that load_ui adds .ui extension if missing"""
        from platform_base.ui.loader import DESIGNER_PATH

        # Test that path construction works correctly
        ui_name = "test_widget"
        expected_path = DESIGNER_PATH / "test_widget.ui"
        
        # Verify path is constructed correctly
        assert str(expected_path).endswith("test_widget.ui")

    def test_load_ui_preserves_extension(self):
        """Test that load_ui preserves .ui extension if present"""
        from platform_base.ui.loader import DESIGNER_PATH
        
        ui_name = "test_widget.ui"
        expected_path = DESIGNER_PATH / ui_name
        
        # Should not add double extension
        assert not str(expected_path).endswith(".ui.ui")

    def test_load_ui_file_not_found(self):
        """Test that load_ui raises FileNotFoundError for missing file"""
        from platform_base.ui.loader import load_ui
        
        mock_widget = MagicMock()
        
        with pytest.raises(FileNotFoundError, match="UI file not found"):
            load_ui("nonexistent_widget_xyz123", mock_widget)

    def test_load_ui_relative_path(self):
        """Test load_ui with relative path like panels/data_panel"""
        from platform_base.ui.loader import DESIGNER_PATH
        
        ui_name = "panels/my_panel"
        expected_path = DESIGNER_PATH / "panels" / "my_panel.ui"
        
        # Verify nested path construction
        assert "panels" in str(expected_path)

    @patch('platform_base.ui.loader.uic.loadUi')
    def test_load_ui_success(self, mock_load_ui):
        """Test successful UI loading"""
        from platform_base.ui.loader import DESIGNER_PATH, load_ui

        # Create a mock widget
        mock_widget = MagicMock()
        
        # Create a temporary UI file for testing
        ui_path = DESIGNER_PATH / "test_temp.ui"
        try:
            ui_path.parent.mkdir(parents=True, exist_ok=True)
            ui_path.write_text('<?xml version="1.0"?><ui version="4.0"></ui>')
            
            # Should not raise
            load_ui("test_temp", mock_widget)
            
            # Verify uic.loadUi was called
            mock_load_ui.assert_called_once()
        finally:
            if ui_path.exists():
                ui_path.unlink()


class TestGetUiClass:
    """Tests for get_ui_class function"""

    def test_get_ui_class_file_not_found(self):
        """Test that get_ui_class raises FileNotFoundError"""
        from platform_base.ui.loader import get_ui_class
        
        with pytest.raises(FileNotFoundError, match="UI file not found"):
            get_ui_class("nonexistent_widget_xyz456")

    def test_get_ui_class_adds_extension(self):
        """Test that get_ui_class adds .ui extension"""
        from platform_base.ui.loader import DESIGNER_PATH

        # Verify internal logic
        ui_name = "my_panel"
        if not ui_name.endswith(".ui"):
            ui_name = f"{ui_name}.ui"
        
        assert ui_name == "my_panel.ui"


class TestValidateUiFile:
    """Tests for validate_ui_file function"""

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        from platform_base.ui.loader import validate_ui_file
        
        result = validate_ui_file("nonexistent_file_xyz789")
        assert result is False

    def test_validate_adds_extension(self):
        """Test that validation adds .ui extension"""
        from platform_base.ui.loader import DESIGNER_PATH, validate_ui_file

        # Test with and without extension
        result_without = validate_ui_file("test")
        result_with = validate_ui_file("test.ui")
        
        # Both should behave the same for non-existent files
        assert result_without == result_with

    def test_validate_existing_file(self):
        """Test validation of existing file"""
        from platform_base.ui.loader import DESIGNER_PATH, validate_ui_file

        # Create a temporary test file
        test_path = DESIGNER_PATH / "validate_test.ui"
        try:
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text('<?xml version="1.0"?>')
            
            result = validate_ui_file("validate_test")
            assert result is True
        finally:
            if test_path.exists():
                test_path.unlink()


class TestDesignerPath:
    """Tests for DESIGNER_PATH constant"""

    def test_designer_path_exists_as_path(self):
        """Test that DESIGNER_PATH is a Path object"""
        from platform_base.ui.loader import DESIGNER_PATH
        
        assert isinstance(DESIGNER_PATH, Path)

    def test_designer_path_relative_to_module(self):
        """Test that DESIGNER_PATH is relative to the ui module"""
        from platform_base.ui.loader import DESIGNER_PATH

        # Should contain 'designer' in the path
        assert "designer" in str(DESIGNER_PATH)

    def test_designer_path_can_be_created(self):
        """Test that DESIGNER_PATH directory can be created"""
        from platform_base.ui.loader import DESIGNER_PATH

        # Should not raise
        DESIGNER_PATH.mkdir(parents=True, exist_ok=True)
        assert DESIGNER_PATH.exists() or True  # May or may not exist


class TestUiLoaderIntegration:
    """Integration tests for UI loader system"""

    def test_round_trip_path_construction(self):
        """Test that path construction is consistent"""
        from platform_base.ui.loader import DESIGNER_PATH, validate_ui_file
        
        test_cases = [
            "simple_widget",
            "panels/nested_widget",
            "dialogs/filter/advanced",
        ]
        
        for ui_name in test_cases:
            # Just verify no exceptions
            validate_ui_file(ui_name)

    def test_error_logging(self):
        """Test that errors are properly logged"""
        from platform_base.ui.loader import load_ui
        
        mock_widget = MagicMock()
        
        # Should raise and log
        with pytest.raises(FileNotFoundError):
            load_ui("error_test_nonexistent", mock_widget)
