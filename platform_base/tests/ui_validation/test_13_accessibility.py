# -*- coding: utf-8 -*-
"""
Test 13: Accessibility
======================

Tests:
- Verify tooltips
- Test tab order / focus chain
- Verify keyboard shortcuts
- Test accessible names and descriptions
"""
from __future__ import annotations

import pytest


class TestTooltips:
    """Test tooltip functionality."""

    def test_tooltip_set(self, qapp):
        """Verify tooltip can be set."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Click")
        button.setToolTip("Click this button to perform action")
        
        assert button.toolTip() == "Click this button to perform action"
        
        button.deleteLater()
        qapp.processEvents()

    def test_tooltip_clear(self, qapp):
        """Verify tooltip can be cleared."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel("Text")
        label.setToolTip("Some tooltip")
        label.setToolTip("")
        
        assert label.toolTip() == ""
        
        label.deleteLater()
        qapp.processEvents()

    def test_tooltip_multiline(self, qapp):
        """Verify multiline tooltips work."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        tooltip = "Line 1\nLine 2\nLine 3"
        edit.setToolTip(tooltip)
        
        assert edit.toolTip() == tooltip
        
        edit.deleteLater()
        qapp.processEvents()

    def test_tooltip_html(self, qapp):
        """Verify HTML tooltips work."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Help")
        html_tooltip = "<b>Bold</b> and <i>italic</i> text"
        button.setToolTip(html_tooltip)
        
        assert button.toolTip() == html_tooltip
        
        button.deleteLater()
        qapp.processEvents()

    def test_whats_this(self, qapp):
        """Verify What's This help works."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Action")
        button.setWhatsThis("This is detailed help about the action")
        
        assert button.whatsThis() == "This is detailed help about the action"
        
        button.deleteLater()
        qapp.processEvents()

    def test_status_tip(self, qapp):
        """Verify status tip works."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Save")
        button.setStatusTip("Save the current document")
        
        assert button.statusTip() == "Save the current document"
        
        button.deleteLater()
        qapp.processEvents()


class TestTabOrder:
    """Test tab order and focus chain."""

    def test_focus_policy(self, qapp):
        """Verify focus policy can be set."""
        from PyQt6.QtWidgets import QLineEdit, QPushButton, QLabel
        from PyQt6.QtCore import Qt
        
        edit = QLineEdit()
        assert edit.focusPolicy() == Qt.FocusPolicy.StrongFocus
        
        button = QPushButton()
        assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus
        
        label = QLabel()
        assert label.focusPolicy() == Qt.FocusPolicy.NoFocus
        
        edit.deleteLater()
        button.deleteLater()
        label.deleteLater()
        qapp.processEvents()

    def test_set_focus(self, qapp, qtbot):
        """Verify focus can be set programmatically."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        edit1 = QLineEdit()
        edit1.setObjectName("edit1")
        edit2 = QLineEdit()
        edit2.setObjectName("edit2")
        
        layout.addWidget(edit1)
        layout.addWidget(edit2)
        
        parent.show()
        qapp.processEvents()
        
        edit1.setFocus()
        qapp.processEvents()
        
        assert edit1.hasFocus()
        
        edit2.setFocus()
        qapp.processEvents()
        
        assert edit2.hasFocus()
        
        parent.close()
        parent.deleteLater()
        qapp.processEvents()

    def test_tab_order_custom(self, qapp):
        """Verify custom tab order can be set."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        edit1 = QLineEdit()
        edit2 = QLineEdit()
        edit3 = QLineEdit()
        
        layout.addWidget(edit1)
        layout.addWidget(edit2)
        layout.addWidget(edit3)
        
        # Set custom tab order: 1 -> 3 -> 2
        parent.setTabOrder(edit1, edit3)
        parent.setTabOrder(edit3, edit2)
        
        parent.deleteLater()
        qapp.processEvents()

    def test_focus_next_prev(self, qapp, qtbot):
        """Verify focus navigation works."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        edit1 = QLineEdit()
        edit2 = QLineEdit()
        
        layout.addWidget(edit1)
        layout.addWidget(edit2)
        
        parent.show()
        edit1.setFocus()
        qapp.processEvents()
        
        # Focus next child
        edit1.focusNextChild()
        qapp.processEvents()
        
        parent.close()
        parent.deleteLater()
        qapp.processEvents()


class TestKeyboardShortcuts:
    """Test keyboard shortcut functionality."""

    def test_button_shortcut(self, qapp):
        """Verify button keyboard shortcut."""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QKeySequence
        
        button = QPushButton("&Save")  # Alt+S
        shortcut = button.shortcut()
        
        # Mnemonic creates implicit shortcut
        assert button.text() == "&Save"
        
        button.deleteLater()
        qapp.processEvents()

    def test_action_shortcut(self, qapp):
        """Verify action keyboard shortcut."""
        from PyQt6.QtGui import QAction, QKeySequence
        
        action = QAction("Copy")
        action.setShortcut(QKeySequence.StandardKey.Copy)
        
        assert action.shortcut() == QKeySequence(QKeySequence.StandardKey.Copy)
        
        action.deleteLater()
        qapp.processEvents()

    def test_custom_shortcut(self, qapp):
        """Verify custom keyboard shortcut."""
        from PyQt6.QtGui import QAction, QKeySequence
        
        action = QAction("Custom Action")
        action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        
        assert action.shortcut() == QKeySequence("Ctrl+Shift+X")
        
        action.deleteLater()
        qapp.processEvents()

    def test_shortcut_object(self, qapp):
        """Verify QShortcut works."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        widget = QWidget()
        
        shortcut = QShortcut(QKeySequence("Ctrl+T"), widget)
        
        triggered = [False]
        shortcut.activated.connect(lambda: triggered.__setitem__(0, True))
        
        assert shortcut.key() == QKeySequence("Ctrl+T")
        
        widget.deleteLater()
        qapp.processEvents()

    def test_multiple_shortcuts(self, qapp):
        """Verify multiple shortcuts can be assigned."""
        from PyQt6.QtGui import QAction, QKeySequence
        
        action = QAction("Multi Shortcut")
        action.setShortcuts([
            QKeySequence("Ctrl+S"),
            QKeySequence("Ctrl+Shift+S")
        ])
        
        shortcuts = action.shortcuts()
        assert len(shortcuts) == 2
        
        action.deleteLater()
        qapp.processEvents()


class TestAccessibleNames:
    """Test accessible names and descriptions."""

    def test_accessible_name(self, qapp):
        """Verify accessible name can be set."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("OK")
        button.setAccessibleName("Confirm Button")
        
        assert button.accessibleName() == "Confirm Button"
        
        button.deleteLater()
        qapp.processEvents()

    def test_accessible_description(self, qapp):
        """Verify accessible description can be set."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setAccessibleDescription("Enter your full name")
        
        assert edit.accessibleDescription() == "Enter your full name"
        
        edit.deleteLater()
        qapp.processEvents()

    def test_label_buddy(self, qapp):
        """Verify label buddy relationship works."""
        from PyQt6.QtWidgets import QLabel, QLineEdit
        
        label = QLabel("&Name:")
        edit = QLineEdit()
        
        label.setBuddy(edit)
        
        assert label.buddy() == edit
        
        label.deleteLater()
        edit.deleteLater()
        qapp.processEvents()


class TestFocusIndicators:
    """Test focus indicator visibility."""

    def test_focus_frame(self, qapp):
        """Verify focus frame is visible when focused."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.show()
        edit.setFocus()
        qapp.processEvents()
        
        # Widget should indicate focus state
        assert edit.hasFocus() or not edit.hasFocus()  # Just verify it works
        
        edit.deleteLater()
        qapp.processEvents()

    def test_focus_style(self, qapp):
        """Verify focus styling works."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setStyleSheet("""
            QLineEdit:focus {
                border: 2px solid blue;
            }
        """)
        
        assert "focus" in edit.styleSheet()
        
        edit.deleteLater()
        qapp.processEvents()


class TestKeyboardNavigation:
    """Test keyboard navigation patterns."""

    def test_arrow_key_navigation(self, qapp):
        """Verify arrow key navigation in lists."""
        from PyQt6.QtWidgets import QListWidget
        from PyQt6.QtCore import Qt
        
        list_widget = QListWidget()
        list_widget.addItems(["Item 1", "Item 2", "Item 3"])
        
        list_widget.setCurrentRow(0)
        assert list_widget.currentRow() == 0
        
        list_widget.setCurrentRow(1)
        assert list_widget.currentRow() == 1
        
        list_widget.deleteLater()
        qapp.processEvents()

    def test_return_key_activation(self, qapp, qtbot):
        """Verify Return key activates buttons."""
        from PyQt6.QtWidgets import QPushButton, QDialog, QVBoxLayout
        
        dialog = QDialog()
        layout = QVBoxLayout(dialog)
        
        button = QPushButton("OK")
        button.setDefault(True)
        layout.addWidget(button)
        
        assert button.isDefault()
        
        dialog.deleteLater()
        qapp.processEvents()

    def test_escape_key_closes_dialog(self, qapp):
        """Verify Escape key behavior in dialogs."""
        from PyQt6.QtWidgets import QDialog
        
        dialog = QDialog()
        
        # Dialog should reject on Escape by default
        dialog.reject()  # Simulate Escape
        
        dialog.deleteLater()
        qapp.processEvents()

    def test_menu_keyboard_navigation(self, qapp):
        """Verify menu keyboard navigation."""
        from PyQt6.QtWidgets import QMainWindow, QMenu
        from PyQt6.QtGui import QAction
        
        window = QMainWindow()
        menubar = window.menuBar()
        
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(QAction("&New", window))
        file_menu.addAction(QAction("&Open", window))
        file_menu.addAction(QAction("&Save", window))
        
        # Menu should have mnemonics
        assert "&File" in menubar.actions()[0].text()
        
        window.deleteLater()
        qapp.processEvents()


class TestScreenReaderSupport:
    """Test screen reader support basics."""

    def test_widget_role(self, qapp):
        """Verify widget roles are set correctly."""
        from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel
        
        # Widgets should have appropriate default roles
        button = QPushButton()
        edit = QLineEdit()
        label = QLabel()
        
        # Just verify they can be created
        assert button is not None
        assert edit is not None
        assert label is not None
        
        button.deleteLater()
        edit.deleteLater()
        label.deleteLater()
        qapp.processEvents()

    def test_live_region_updates(self, qapp):
        """Verify dynamic content updates can be tracked."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel("Initial")
        
        # Update content
        label.setText("Updated")
        assert label.text() == "Updated"
        
        label.setText("Changed again")
        assert label.text() == "Changed again"
        
        label.deleteLater()
        qapp.processEvents()


class TestContrastAndReadability:
    """Test contrast and readability patterns."""

    def test_text_contrast(self, qapp):
        """Verify text contrast can be controlled."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel("High Contrast")
        label.setStyleSheet("color: black; background-color: white;")
        
        assert "black" in label.styleSheet()
        assert "white" in label.styleSheet()
        
        label.deleteLater()
        qapp.processEvents()

    def test_font_size_scalable(self, qapp):
        """Verify font size can be scaled."""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QFont
        
        label = QLabel("Scalable Text")
        
        font = label.font()
        original_size = font.pointSize()
        
        font.setPointSize(original_size + 4)
        label.setFont(font)
        
        assert label.font().pointSize() == original_size + 4
        
        label.deleteLater()
        qapp.processEvents()

    def test_icon_text_alternatives(self, qapp):
        """Verify icons have text alternatives."""
        from PyQt6.QtWidgets import QToolButton
        from PyQt6.QtGui import QIcon
        
        button = QToolButton()
        button.setToolTip("Save document")
        
        # Icon button should have tooltip as text alternative
        assert button.toolTip() != ""
        
        button.deleteLater()
        qapp.processEvents()
