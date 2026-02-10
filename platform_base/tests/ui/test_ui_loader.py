"""
Test UI Loader functionality

Basic tests to ensure UI files can be loaded and validated.
These tests focus on file validation without requiring Qt GUI.
"""

import pytest
from pathlib import Path
import xml.etree.ElementTree as ET


class TestUIFiles:
    """Test UI files exist and are valid XML"""
    
    def test_designer_path_exists(self):
        """Test that designer path exists"""
        # Import here to avoid Qt initialization
        from platform_base.ui.loader import DESIGNER_PATH
        assert DESIGNER_PATH.exists(), f"Designer path not found: {DESIGNER_PATH}"
        assert DESIGNER_PATH.is_dir(), f"Designer path is not a directory: {DESIGNER_PATH}"
    
    def test_main_window_ui_exists(self):
        """Test that main_window.ui exists"""
        from platform_base.ui.loader import DESIGNER_PATH
        ui_file = DESIGNER_PATH / "main_window.ui"
        assert ui_file.exists(), f"main_window.ui not found at {ui_file}"
    
    def test_data_panel_ui_exists(self):
        """Test that data_panel.ui exists"""
        from platform_base.ui.loader import DESIGNER_PATH
        ui_file = DESIGNER_PATH / "panels" / "data_panel.ui"
        assert ui_file.exists(), f"data_panel.ui not found at {ui_file}"
    
    def test_main_window_ui_valid_xml(self):
        """Test that main_window.ui is valid XML"""
        from platform_base.ui.loader import DESIGNER_PATH
        ui_file = DESIGNER_PATH / "main_window.ui"
        tree = ET.parse(str(ui_file))
        root = tree.getroot()
        assert root.tag == "ui", "Root tag should be 'ui'"
        assert root.get("version") == "4.0", "UI version should be 4.0"
    
    def test_data_panel_ui_valid_xml(self):
        """Test that data_panel.ui is valid XML"""
        from platform_base.ui.loader import DESIGNER_PATH
        ui_file = DESIGNER_PATH / "panels" / "data_panel.ui"
        tree = ET.parse(str(ui_file))
        root = tree.getroot()
        assert root.tag == "ui", "Root tag should be 'ui'"
        assert root.get("version") == "4.0", "UI version should be 4.0"
    
    def test_validate_ui_file_existing(self):
        """Test validate_ui_file with existing file"""
        from platform_base.ui.loader import validate_ui_file
        assert validate_ui_file("main_window"), "main_window.ui should be valid"
        assert validate_ui_file("panels/data_panel"), "data_panel.ui should be valid"
    
    def test_validate_ui_file_nonexisting(self):
        """Test validate_ui_file with non-existing file"""
        from platform_base.ui.loader import validate_ui_file
        assert not validate_ui_file("nonexistent"), "nonexistent.ui should not be valid"
    
    def test_validate_ui_file_with_extension(self):
        """Test validate_ui_file with .ui extension"""
        from platform_base.ui.loader import validate_ui_file
        assert validate_ui_file("main_window.ui"), "main_window.ui should be valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
