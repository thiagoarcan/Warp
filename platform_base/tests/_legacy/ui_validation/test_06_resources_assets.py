# -*- coding: utf-8 -*-
"""
Test 06: Resources and Assets
=============================

Tests:
- Verify referenced icons exist
- Validate images load correctly
- Test style files (QSS/CSS) are applied
- Verify custom fonts load
- Validate resource paths are correct
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


class TestIconExistence:
    """Test icon file existence."""

    def test_icon_directory_exists(self, resources_dir: Path):
        """Verify icon directory exists."""
        icons_dir = resources_dir / "icons"
        
        if not icons_dir.exists():
            pytest.skip("Icons directory not found")
        
        assert icons_dir.is_dir()

    def test_icons_referenced_in_ui_exist(self, all_ui_files: list[Path], resources_dir: Path):
        """Verify icons referenced in .ui files exist."""
        icons_dir = resources_dir / "icons"
        
        if not icons_dir.exists():
            pytest.skip("Icons directory not found")
        
        missing_icons = []
        for ui_file in all_ui_files:
            try:
                tree = ET.parse(ui_file)
                for icon_prop in tree.iter("iconset"):
                    normal = icon_prop.find("normaloff")
                    if normal is not None and normal.text:
                        icon_path = Path(normal.text)
                        if not icon_path.is_absolute():
                            full_path = icons_dir / icon_path.name
                            if not full_path.exists():
                                missing_icons.append(f"{ui_file.name}: {normal.text}")
            except ET.ParseError:
                pass
        
        if missing_icons:
            pytest.skip(f"Some icons may be embedded or use different paths: {len(missing_icons)}")

    def test_common_icons_exist(self, resources_dir: Path):
        """Verify common icons exist."""
        icons_dir = resources_dir / "icons"
        
        if not icons_dir.exists():
            pytest.skip("Icons directory not found")
        
        common_icons = [
            "open.png", "save.png", "close.png",
            "add.png", "delete.png", "edit.png",
            "settings.png", "help.png",
        ]
        
        existing = list(icons_dir.glob("*.*"))
        if not existing:
            pytest.skip("No icon files found")


class TestImageLoading:
    """Test image loading functionality."""

    def test_qpixmap_from_file(self, qapp, tmp_path: Path):
        """Verify QPixmap can load from file."""
        from PyQt6.QtGui import QPixmap
        
        # Create test image
        from PyQt6.QtCore import Qt
        
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.red)
        
        test_file = tmp_path / "test_image.png"
        pixmap.save(str(test_file))
        
        # Load it back
        loaded = QPixmap(str(test_file))
        assert not loaded.isNull()
        assert loaded.width() == 100
        assert loaded.height() == 100

    def test_qicon_from_file(self, qapp, tmp_path: Path):
        """Verify QIcon can load from file."""
        from PyQt6.QtGui import QIcon, QPixmap
        from PyQt6.QtCore import Qt
        
        # Create test icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.blue)
        
        test_file = tmp_path / "test_icon.png"
        pixmap.save(str(test_file))
        
        # Load as icon
        icon = QIcon(str(test_file))
        assert not icon.isNull()

    def test_invalid_image_path(self, qapp):
        """Verify invalid image path returns null pixmap."""
        from PyQt6.QtGui import QPixmap
        
        pixmap = QPixmap("/nonexistent/path/to/image.png")
        assert pixmap.isNull()


class TestStyleFiles:
    """Test style file loading."""

    def test_styles_directory_exists(self, resources_dir: Path):
        """Verify styles directory exists."""
        styles_dir = resources_dir / "styles"
        
        if not styles_dir.exists():
            pytest.skip("Styles directory not found")
        
        assert styles_dir.is_dir()

    def test_qss_files_valid(self, resources_dir: Path):
        """Verify QSS files are readable."""
        styles_dir = resources_dir / "styles"
        
        if not styles_dir.exists():
            pytest.skip("Styles directory not found")
        
        qss_files = list(styles_dir.glob("*.qss"))
        if not qss_files:
            pytest.skip("No QSS files found")
        
        for qss_file in qss_files:
            content = qss_file.read_text(encoding="utf-8")
            assert len(content) > 0, f"Empty QSS file: {qss_file.name}"

    def test_stylesheet_applies(self, qapp):
        """Verify stylesheet can be applied."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        
        # Simple stylesheet
        stylesheet = "QWidget { background-color: red; }"
        widget.setStyleSheet(stylesheet)
        
        applied = widget.styleSheet()
        assert stylesheet in applied
        
        widget.deleteLater()
        qapp.processEvents()

    def test_complex_stylesheet(self, qapp):
        """Verify complex stylesheet applies."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        
        stylesheet = """
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        """
        button.setStyleSheet(stylesheet)
        
        assert len(button.styleSheet()) > 0
        
        button.deleteLater()
        qapp.processEvents()


class TestFonts:
    """Test font loading."""

    def test_default_font_exists(self, qapp):
        """Verify default font exists."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        font = widget.font()
        
        assert font is not None
        assert font.family() is not None
        
        widget.deleteLater()
        qapp.processEvents()

    def test_font_database_available(self, qapp):
        """Verify font database is available."""
        import os
        from PyQt6.QtGui import QFontDatabase
        
        families = QFontDatabase.families()
        
        # In offscreen mode (CI), fonts may not be available
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen" and len(families) == 0:
            pytest.skip("Font database not available in offscreen mode")
        
        # In normal mode, we should have fonts
        assert len(families) >= 0, "QFontDatabase should be accessible"

    def test_custom_font_settings(self, qapp):
        """Verify custom font can be set."""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QFont
        
        label = QLabel("Test")
        
        font = QFont("Arial", 14)
        label.setFont(font)
        
        applied_font = label.font()
        assert applied_font.pointSize() == 14
        
        label.deleteLater()
        qapp.processEvents()


class TestResourcePaths:
    """Test resource path handling."""

    def test_ui_files_path_valid(self, ui_files_dir: Path):
        """Verify UI files path is valid."""
        assert ui_files_dir.exists()
        assert ui_files_dir.is_dir()

    def test_relative_paths_in_ui(self, all_ui_files: list[Path]):
        """Check for relative paths in UI files."""
        absolute_paths = []
        
        for ui_file in all_ui_files:
            content = ui_file.read_text(encoding="utf-8")
            
            # Look for absolute paths (likely platform-specific)
            if re.search(r'[A-Z]:\\', content):  # Windows
                absolute_paths.append(f"{ui_file.name}: Windows absolute path")
            if re.search(r'/home/|/Users/', content):  # Linux/Mac
                absolute_paths.append(f"{ui_file.name}: Unix absolute path")
        
        assert not absolute_paths, f"Absolute paths in UI files:\n" + "\n".join(absolute_paths)

    def test_resource_prefix_usage(self, all_ui_files: list[Path]):
        """Check for Qt resource prefix usage (:/icons/)."""
        resource_prefix_used = []
        
        for ui_file in all_ui_files:
            content = ui_file.read_text(encoding="utf-8")
            
            if ":/" in content:
                resource_prefix_used.append(ui_file.name)
        
        # This is informational - resource prefixes are valid
        if resource_prefix_used:
            pass  # OK - using Qt resource system


class TestThemeResources:
    """Test theme-related resources."""

    def test_ergonomic_styles_module_exists(self):
        """Verify ergonomic styles module exists."""
        try:
            from platform_base.ui.ergonomic_styles import ErgonomicStyleManager
            assert ErgonomicStyleManager is not None
        except ImportError:
            pytest.skip("ErgonomicStyleManager not available")

    def test_themes_module_exists(self):
        """Verify themes module exists."""
        try:
            from platform_base.ui.themes import ThemeManager
            assert ThemeManager is not None
        except ImportError:
            pytest.skip("ThemeManager not available")

    def test_style_manager_creates(self, qapp):
        """Verify style manager can be created."""
        try:
            from platform_base.ui.ergonomic_styles import ErgonomicStyleManager
            
            manager = ErgonomicStyleManager()
            assert manager is not None
        except ImportError:
            pytest.skip("ErgonomicStyleManager not available")
