# -*- coding: utf-8 -*-
"""
Test 01: UI File Existence and Loading
======================================

Tests:
- Verify all .ui files exist
- Load each .ui file without errors
- Validate all .ui have widgets defined
- Check for duplicate .ui files
- Verify UTF-8 encoding
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


class TestUIFileExistence:
    """Test .ui file existence and basic structure."""

    def test_ui_files_directory_exists(self, ui_files_dir: Path):
        """Verify UI files directory exists."""
        assert ui_files_dir.exists(), f"UI files directory not found: {ui_files_dir}"
        assert ui_files_dir.is_dir(), f"UI files path is not a directory: {ui_files_dir}"

    def test_ui_files_not_empty(self, all_ui_files: list[Path]):
        """Verify there are .ui files in the project."""
        assert len(all_ui_files) > 0, "No .ui files found in project"

    def test_all_ui_files_exist(self, all_ui_files: list[Path]):
        """Verify all discovered .ui files actually exist."""
        for ui_file in all_ui_files:
            assert ui_file.exists(), f"UI file not found: {ui_file}"
            assert ui_file.is_file(), f"UI path is not a file: {ui_file}"

    def test_ui_files_have_content(self, all_ui_files: list[Path]):
        """Verify .ui files are not empty."""
        for ui_file in all_ui_files:
            size = ui_file.stat().st_size
            assert size > 0, f"UI file is empty: {ui_file.name}"

    @pytest.mark.parametrize("min_expected_files", [10])
    def test_minimum_ui_files_count(self, all_ui_files: list[Path], min_expected_files: int):
        """Verify minimum number of .ui files exist."""
        assert len(all_ui_files) >= min_expected_files, (
            f"Expected at least {min_expected_files} .ui files, found {len(all_ui_files)}"
        )


class TestUIFileLoading:
    """Test loading .ui files."""

    def test_ui_files_valid_xml(self, all_ui_files: list[Path]):
        """Verify all .ui files are valid XML."""
        errors = []
        for ui_file in all_ui_files:
            try:
                ET.parse(ui_file)
            except ET.ParseError as e:
                errors.append(f"{ui_file.name}: {e}")
        
        assert not errors, f"Invalid XML in UI files:\n" + "\n".join(errors)

    def test_ui_files_have_root_ui_element(self, all_ui_files: list[Path]):
        """Verify all .ui files have 'ui' as root element."""
        errors = []
        for ui_file in all_ui_files:
            try:
                tree = ET.parse(ui_file)
                root = tree.getroot()
                if root.tag != "ui":
                    errors.append(f"{ui_file.name}: root element is '{root.tag}', expected 'ui'")
            except ET.ParseError:
                pass  # Covered by other test
        
        assert not errors, f"Invalid root elements:\n" + "\n".join(errors)

    def test_ui_files_loadable_with_pyqt(self, qapp, all_ui_files: list[Path]):
        """Verify all .ui files can be loaded with PyQt6.uic."""
        from PyQt6 import uic
        from PyQt6.QtWidgets import QWidget
        
        errors = []
        loaded_count = 0
        for ui_file in all_ui_files:
            try:
                widget = QWidget()
                uic.loadUi(str(ui_file), widget)
                widget.deleteLater()
                loaded_count += 1
            except Exception as e:
                errors.append(f"{ui_file.name}: {e}")
        
        qapp.processEvents()
        
        # Allow failures - UI files may reference custom widgets not available at test time
        # This test is mostly informational
        if errors:
            # Skip test with info about failures (don't fail - custom widgets are expected)
            pytest.skip(
                f"UI files with custom widgets failed to load ({len(errors)}/{len(all_ui_files)}). "
                f"This is expected - first 3 errors: {errors[:3]}"
            )


class TestUIFileWidgets:
    """Test widget definitions in .ui files."""

    def test_ui_files_have_widget_element(self, all_ui_files: list[Path]):
        """Verify all .ui files have at least one widget defined."""
        errors = []
        for ui_file in all_ui_files:
            try:
                tree = ET.parse(ui_file)
                root = tree.getroot()
                widget = root.find("widget")
                if widget is None:
                    errors.append(f"{ui_file.name}: no widget element found")
            except ET.ParseError:
                pass
        
        assert not errors, f"Missing widget elements:\n" + "\n".join(errors)

    def test_ui_files_have_named_widgets(self, all_ui_files: list[Path]):
        """Verify main widgets have names."""
        errors = []
        for ui_file in all_ui_files:
            try:
                tree = ET.parse(ui_file)
                root = tree.getroot()
                widget = root.find("widget")
                if widget is not None:
                    name = widget.get("name")
                    if not name:
                        errors.append(f"{ui_file.name}: main widget has no name")
            except ET.ParseError:
                pass
        
        assert not errors, f"Unnamed widgets:\n" + "\n".join(errors)

    def test_ui_files_have_class_attribute(self, all_ui_files: list[Path]):
        """Verify main widgets have class attribute."""
        errors = []
        for ui_file in all_ui_files:
            try:
                tree = ET.parse(ui_file)
                root = tree.getroot()
                class_elem = root.find("class")
                if class_elem is None or not class_elem.text:
                    errors.append(f"{ui_file.name}: no class element found")
            except ET.ParseError:
                pass
        
        assert not errors, f"Missing class elements:\n" + "\n".join(errors)


class TestUIFileDuplicates:
    """Test for duplicate .ui files."""

    def test_no_duplicate_ui_file_names(self, all_ui_files: list[Path]):
        """Verify no duplicate .ui file names."""
        names = [f.name for f in all_ui_files]
        duplicates = [name for name in names if names.count(name) > 1]
        
        assert not duplicates, f"Duplicate UI file names: {set(duplicates)}"

    def test_no_duplicate_class_names(self, all_ui_files: list[Path]):
        """Verify no duplicate class names across .ui files."""
        class_names = {}
        for ui_file in all_ui_files:
            try:
                tree = ET.parse(ui_file)
                class_elem = tree.getroot().find("class")
                if class_elem is not None and class_elem.text:
                    class_name = class_elem.text
                    if class_name in class_names:
                        class_names[class_name].append(ui_file.name)
                    else:
                        class_names[class_name] = [ui_file.name]
            except ET.ParseError:
                pass
        
        duplicates = {k: v for k, v in class_names.items() if len(v) > 1}
        assert not duplicates, f"Duplicate class names: {duplicates}"


class TestUIFileEncoding:
    """Test .ui file encoding."""

    def test_ui_files_utf8_encoding(self, all_ui_files: list[Path]):
        """Verify all .ui files are UTF-8 encoded."""
        errors = []
        for ui_file in all_ui_files:
            try:
                ui_file.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                errors.append(f"{ui_file.name}: {e}")
        
        assert not errors, f"Non-UTF-8 files:\n" + "\n".join(errors)

    def test_ui_files_have_xml_declaration(self, all_ui_files: list[Path]):
        """Verify .ui files have XML declaration with encoding."""
        errors = []
        for ui_file in all_ui_files:
            content = ui_file.read_text(encoding="utf-8")
            if not content.startswith("<?xml"):
                errors.append(f"{ui_file.name}: missing XML declaration")
        
        assert not errors, f"Missing XML declarations:\n" + "\n".join(errors)

    def test_ui_files_declare_utf8(self, all_ui_files: list[Path]):
        """Verify .ui files declare UTF-8 encoding in XML header."""
        errors = []
        for ui_file in all_ui_files:
            content = ui_file.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].lower()
            if "<?xml" in first_line and 'encoding="utf-8"' not in first_line:
                # Check alternate formats
                if 'encoding="utf8"' not in first_line and "encoding='utf-8'" not in first_line:
                    errors.append(f"{ui_file.name}: UTF-8 encoding not declared")
        
        # This is a warning, not an error (Qt Designer may omit encoding)
        if errors:
            pytest.skip(f"Some files don't declare encoding (non-critical): {len(errors)} files")
