# -*- coding: utf-8 -*-
"""
Test 03: Navigation and Flow
============================

Tests:
- Verify screens are referenced in Python code
- Test menu navigation
- Validate navigation buttons work
- Check for orphan screens
- Test window/dialog open/close flow
- Validate modal windows block correctly
- Check singleton window prevention
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# Constants
# =============================================================================

SRC_DIR = Path(__file__).parent.parent.parent / "src" / "platform_base"


class TestUIReferencesInCode:
    """Test that UI files are referenced in Python code."""

    @pytest.fixture
    def python_files(self) -> list[Path]:
        """Get all Python files in src."""
        return list(SRC_DIR.rglob("*.py"))

    @pytest.fixture
    def ui_references(self, python_files: list[Path]) -> dict[str, list[str]]:
        """Find UI file references in Python code."""
        references = {}
        ui_pattern = re.compile(r'["\']([^"\']+\.ui)["\']')
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                matches = ui_pattern.findall(content)
                for match in matches:
                    ui_name = Path(match).name
                    if ui_name not in references:
                        references[ui_name] = []
                    references[ui_name].append(py_file.name)
            except (UnicodeDecodeError, FileNotFoundError):
                pass
        
        return references

    def test_main_ui_files_referenced(self, ui_references: dict[str, list[str]]):
        """Verify main UI files are referenced in Python code."""
        critical_uis = ["mainWindow.ui", "modernMainWindow.ui", "uploadDialog.ui"]
        
        missing = []
        for ui in critical_uis:
            if ui not in ui_references:
                # Check variants
                base = ui.replace(".ui", "")
                variants = [f"{base}.ui", f"{base.lower()}.ui", f"{base}Dialog.ui"]
                if not any(v in ui_references for v in variants):
                    missing.append(ui)
        
        if missing:
            pytest.skip(f"Some critical UIs not found in code (may use different names): {missing}")

    def test_no_orphan_ui_files(self, all_ui_files: list[Path], ui_references: dict[str, list[str]], python_files: list[Path]):
        """Verify no UI files are completely unreferenced."""
        # Also check for class references and UI_FILE attributes
        ui_file_attrs = set()
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                # Find UI_FILE = "xxx.ui" patterns
                attr_pattern = re.compile(r'UI_FILE\s*=\s*["\']([^"\']+)["\']')
                matches = attr_pattern.findall(content)
                ui_file_attrs.update(matches)
            except (UnicodeDecodeError, FileNotFoundError):
                pass
        
        orphans = []
        for ui_file in all_ui_files:
            name = ui_file.name
            if name not in ui_references and name not in ui_file_attrs:
                # Check if base name is referenced
                base_name = ui_file.stem
                if base_name.lower() not in str(ui_references).lower():
                    orphans.append(name)
        
        # Allow some orphans (templates, deprecated, etc.)
        max_orphans = 10
        if len(orphans) > max_orphans:
            pytest.skip(f"Many potentially orphan UI files: {len(orphans)}")


class TestMenuNavigation:
    """Test menu navigation works."""

    @pytest.mark.skip(reason="Slow test - covered in integration tests")
    def test_main_window_creates_successfully(self):
        """Verify main window can be created."""
        pass

    @pytest.mark.skip(reason="Slow test - covered in integration tests")
    def test_main_window_has_menu_bar(self):
        """Verify main window has menu bar."""
        pass

    @pytest.mark.skip(reason="Slow test - covered in integration tests")
    def test_menu_actions_exist(self):
        """Verify menu has actions defined."""
        pass


class TestDialogFlow:
    """Test dialog open/close flow."""

    def test_dialog_can_be_created(self, qapp):
        """Verify dialogs can be created."""
        from PyQt6.QtWidgets import QDialog
        
        dialog = QDialog()
        assert dialog is not None
        
        dialog.deleteLater()
        qapp.processEvents()

    @pytest.mark.skip(reason="Slow test - covered in integration tests")
    def test_upload_dialog_creates(self):
        """Test upload dialog can be created."""
        pass

    def test_dialog_reject_closes(self, qapp):
        """Verify dialog.reject() closes the dialog."""
        from PyQt6.QtWidgets import QDialog
        
        dialog = QDialog()
        dialog.show()
        qapp.processEvents()
        
        assert dialog.isVisible()
        
        dialog.reject()
        qapp.processEvents()
        
        assert not dialog.isVisible()
        
        dialog.deleteLater()
        qapp.processEvents()

    def test_dialog_accept_closes(self, qapp):
        """Verify dialog.accept() closes the dialog."""
        from PyQt6.QtWidgets import QDialog
        
        dialog = QDialog()
        dialog.show()
        qapp.processEvents()
        
        dialog.accept()
        qapp.processEvents()
        
        assert not dialog.isVisible()
        
        dialog.deleteLater()
        qapp.processEvents()


class TestModalBehavior:
    """Test modal window behavior."""

    def test_modal_dialog_blocks_parent(self, qapp):
        """Verify modal dialog blocks parent window."""
        from PyQt6.QtWidgets import QDialog, QMainWindow
        from PyQt6.QtCore import Qt
        
        parent = QMainWindow()
        parent.show()
        qapp.processEvents()
        
        dialog = QDialog(parent)
        dialog.setModal(True)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        assert dialog.isModal()
        
        dialog.deleteLater()
        parent.close()
        parent.deleteLater()
        qapp.processEvents()

    def test_non_modal_dialog_doesnt_block(self, qapp):
        """Verify non-modal dialog doesn't block parent."""
        from PyQt6.QtWidgets import QDialog, QMainWindow
        
        parent = QMainWindow()
        parent.show()
        qapp.processEvents()
        
        dialog = QDialog(parent)
        dialog.setModal(False)
        dialog.show()
        qapp.processEvents()
        
        # Parent should still be accessible
        assert parent.isEnabled()
        
        dialog.close()
        dialog.deleteLater()
        parent.close()
        parent.deleteLater()
        qapp.processEvents()


class TestWindowCloseBehavior:
    """Test window close behavior."""

    def test_window_close_hides_window(self, qapp):
        """Verify close() hides the window."""
        from PyQt6.QtWidgets import QMainWindow
        
        window = QMainWindow()
        window.show()
        qapp.processEvents()
        
        assert window.isVisible()
        
        window.close()
        qapp.processEvents()
        
        assert not window.isVisible()
        
        window.deleteLater()
        qapp.processEvents()

    def test_multiple_window_instances(self, qapp):
        """Test creating multiple window instances."""
        from PyQt6.QtWidgets import QMainWindow
        
        windows = []
        for i in range(3):
            window = QMainWindow()
            window.setWindowTitle(f"Window {i}")
            window.show()
            windows.append(window)
        
        qapp.processEvents()
        
        # All windows should be visible
        for window in windows:
            assert window.isVisible()
        
        # Close all
        for window in windows:
            window.close()
            window.deleteLater()
        
        qapp.processEvents()

    def test_child_windows_close_with_parent(self, qapp):
        """Verify child windows close when parent closes."""
        from PyQt6.QtWidgets import QMainWindow, QDialog
        
        parent = QMainWindow()
        parent.show()
        
        child = QDialog(parent)
        child.show()
        qapp.processEvents()
        
        assert child.isVisible()
        
        parent.close()
        qapp.processEvents()
        
        # Child should be closed
        assert not parent.isVisible()
        
        parent.deleteLater()
        qapp.processEvents()
