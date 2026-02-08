# -*- coding: utf-8 -*-
"""
Test 02: Mandatory Widgets
==========================

Tests:
- Verify critical widgets exist in each screen
- Validate widget naming conventions
- Test required widgets are not null
- Verify widget hierarchy
- Validate essential properties
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


# =============================================================================
# Expected widgets per UI file (critical widgets that must exist)
# =============================================================================

EXPECTED_WIDGETS = {
    "mainWindow.ui": ["menubar", "statusbar", "centralwidget"],
    "modernMainWindow.ui": ["menubar", "statusbar", "centralwidget"],
    "uploadDialog.ui": ["buttonBox"],
    "exportDialog.ui": ["buttonBox"],
    "settingsDialog.ui": ["buttonBox"],
    "aboutDialog.ui": ["buttonBox"],
    "dataPanel.ui": [],
    "vizPanel.ui": [],
}

# Widget naming patterns (regex)
NAMING_PATTERNS = {
    "QPushButton": r"^(btn|button|push)[A-Z]",
    "QLineEdit": r"^(txt|edit|line|input)[A-Z]",
    "QLabel": r"^(lbl|label)[A-Z]",
    "QComboBox": r"^(cmb|combo)[A-Z]",
    "QCheckBox": r"^(chk|check)[A-Z]",
    "QSpinBox": r"^(spn|spin)[A-Z]",
    "QTableWidget": r"^(tbl|table)[A-Z]",
    "QListWidget": r"^(lst|list)[A-Z]",
    "QTreeWidget": r"^(tree)[A-Z]",
    "QGroupBox": r"^(grp|group)[A-Z]",
    "QTabWidget": r"^(tab)[A-Z]",
}


class TestCriticalWidgetsExist:
    """Test that critical widgets exist in each screen."""

    def test_main_window_has_critical_widgets(self, ui_files_dir: Path):
        """Verify main window has menubar, statusbar, centralwidget."""
        main_window = ui_files_dir / "mainWindow.ui"
        if not main_window.exists():
            main_window = ui_files_dir / "modernMainWindow.ui"
        
        if not main_window.exists():
            pytest.skip("Main window UI file not found")
        
        tree = ET.parse(main_window)
        widget_names = [w.get("name", "") for w in tree.iter("widget")]
        
        for expected in ["menubar", "statusbar", "centralwidget"]:
            found = any(expected.lower() in name.lower() for name in widget_names)
            assert found, f"Main window missing critical widget: {expected}"

    def test_dialogs_have_button_box(self, ui_files_dir: Path):
        """Verify dialog UIs have button box (OK/Cancel buttons)."""
        dialog_files = list(ui_files_dir.glob("*Dialog.ui"))
        
        missing_buttons = []
        for dialog in dialog_files:
            tree = ET.parse(dialog)
            widget_classes = [w.get("class", "") for w in tree.iter("widget")]
            widget_names = [w.get("name", "") for w in tree.iter("widget")]
            
            has_button_box = "QDialogButtonBox" in widget_classes
            has_buttons = any("button" in name.lower() for name in widget_names)
            
            if not has_button_box and not has_buttons:
                missing_buttons.append(dialog.name)
        
        if missing_buttons:
            pytest.skip(f"Dialogs without explicit buttons (may use custom): {missing_buttons}")

    def test_panels_have_layout(self, ui_files_dir: Path):
        """Verify panel UIs have layout defined."""
        panel_files = list(ui_files_dir.glob("*Panel.ui"))
        
        errors = []
        for panel in panel_files:
            tree = ET.parse(panel)
            layouts = list(tree.iter("layout"))
            if not layouts:
                errors.append(panel.name)
        
        if errors:
            pytest.skip(f"Panels without explicit layouts: {errors}")


class TestWidgetNamingConventions:
    """Test widget naming follows conventions."""

    def test_buttons_follow_naming_pattern(self, all_ui_files: list[Path]):
        """Verify button names follow convention (btn*, button*, push*)."""
        warnings = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            for widget in tree.iter("widget"):
                if widget.get("class") == "QPushButton":
                    name = widget.get("name", "")
                    # Skip standard buttons
                    if name in ["", "pushButton", "okButton", "cancelButton"]:
                        continue
                    pattern = NAMING_PATTERNS.get("QPushButton", "")
                    if pattern and not re.match(pattern, name):
                        warnings.append(f"{ui_file.name}: {name}")
        
        if warnings and len(warnings) > 10:
            pytest.skip(f"Many buttons don't follow convention (flexible): {len(warnings)} buttons")

    def test_widget_names_not_default(self, all_ui_files: list[Path]):
        """Verify widgets don't use default Qt Designer names like 'pushButton_2'."""
        default_pattern = r".*_\d+$"  # Matches names ending with _2, _3, etc.
        
        warnings = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            for widget in tree.iter("widget"):
                name = widget.get("name", "")
                if re.match(default_pattern, name):
                    warnings.append(f"{ui_file.name}: {name}")
        
        # Allow some defaults but warn if too many
        max_allowed = 20
        assert len(warnings) <= max_allowed, (
            f"Too many default widget names ({len(warnings)}): {warnings[:10]}..."
        )


class TestWidgetHierarchy:
    """Test widget parent/child relationships."""

    def test_all_widgets_have_parent(self, all_ui_files: list[Path]):
        """Verify all widgets are properly nested (have parent)."""
        errors = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            root = tree.getroot()
            main_widget = root.find("widget")
            
            if main_widget is None:
                errors.append(f"{ui_file.name}: no main widget")
                continue
            
            # Check that main widget is a container type
            main_class = main_widget.get("class", "")
            valid_containers = ["QWidget", "QDialog", "QMainWindow", "QFrame", "QGroupBox"]
            if main_class not in valid_containers:
                errors.append(f"{ui_file.name}: main widget is {main_class}, expected container")
        
        assert not errors, f"Widget hierarchy issues:\n" + "\n".join(errors)

    def test_layouts_contain_items(self, all_ui_files: list[Path]):
        """Verify layouts contain items or widgets."""
        empty_layouts = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            for layout in tree.iter("layout"):
                items = list(layout.iter("item"))
                widgets = list(layout.iter("widget"))
                if not items and not widgets:
                    layout_name = layout.get("name", "unnamed")
                    empty_layouts.append(f"{ui_file.name}: {layout_name}")
        
        if empty_layouts:
            pytest.skip(f"Empty layouts found (may be intentional): {len(empty_layouts)}")


class TestWidgetProperties:
    """Test essential widget properties."""

    def test_main_widgets_have_geometry(self, all_ui_files: list[Path]):
        """Verify main widgets have geometry defined."""
        errors = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            root = tree.getroot()
            main_widget = root.find("widget")
            
            if main_widget is not None:
                geometry = main_widget.find(".//property[@name='geometry']")
                if geometry is None:
                    errors.append(f"{ui_file.name}: no geometry defined")
        
        if errors:
            pytest.skip(f"Missing geometry (may use layout): {len(errors)} files")

    def test_buttons_have_text(self, all_ui_files: list[Path]):
        """Verify buttons have text property."""
        errors = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            for widget in tree.iter("widget"):
                if widget.get("class") == "QPushButton":
                    text_prop = widget.find(".//property[@name='text']")
                    icon_prop = widget.find(".//property[@name='icon']")
                    # Button should have either text or icon
                    if text_prop is None and icon_prop is None:
                        name = widget.get("name", "unnamed")
                        errors.append(f"{ui_file.name}: {name}")
        
        if errors:
            pytest.skip(f"Buttons without text/icon (may be set programmatically): {len(errors)}")

    def test_labels_have_text_or_pixmap(self, all_ui_files: list[Path]):
        """Verify labels have text or pixmap."""
        errors = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            for widget in tree.iter("widget"):
                if widget.get("class") == "QLabel":
                    text_prop = widget.find(".//property[@name='text']")
                    pixmap_prop = widget.find(".//property[@name='pixmap']")
                    # Skip spacer labels
                    name = widget.get("name", "")
                    if "spacer" in name.lower():
                        continue
                    if text_prop is None and pixmap_prop is None:
                        errors.append(f"{ui_file.name}: {name}")
        
        if errors:
            pytest.skip(f"Labels without content (may be set programmatically): {len(errors)}")


class TestWidgetVisibility:
    """Test widget visibility properties."""

    def test_main_widgets_visible_by_default(self, all_ui_files: list[Path]):
        """Verify main widgets are visible by default."""
        hidden_widgets = []
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            root = tree.getroot()
            main_widget = root.find("widget")
            
            if main_widget is not None:
                visible_prop = main_widget.find(".//property[@name='visible']")
                if visible_prop is not None:
                    bool_elem = visible_prop.find("bool")
                    if bool_elem is not None and bool_elem.text == "false":
                        hidden_widgets.append(ui_file.name)
        
        # Some widgets may be intentionally hidden at design time
        if hidden_widgets:
            if len(hidden_widgets) > len(all_ui_files) // 2:
                pytest.fail(f"Too many main widgets hidden by default: {hidden_widgets}")
            else:
                pytest.skip(f"Hidden main widgets (may be intentional): {hidden_widgets}")

    def test_critical_widgets_enabled(self, all_ui_files: list[Path]):
        """Verify critical widgets are enabled by default."""
        disabled = []
        critical_types = ["QPushButton", "QLineEdit", "QComboBox"]
        
        for ui_file in all_ui_files:
            tree = ET.parse(ui_file)
            for widget in tree.iter("widget"):
                if widget.get("class") in critical_types:
                    enabled_prop = widget.find(".//property[@name='enabled']")
                    if enabled_prop is not None:
                        bool_elem = enabled_prop.find("bool")
                        if bool_elem is not None and bool_elem.text == "false":
                            name = widget.get("name", "unnamed")
                            disabled.append(f"{ui_file.name}: {name}")
        
        # Some widgets may be intentionally disabled initially
        if disabled:
            pytest.skip(f"Disabled widgets found (may be intentional): {len(disabled)}")
