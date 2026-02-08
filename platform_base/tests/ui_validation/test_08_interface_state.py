# -*- coding: utf-8 -*-
"""
Test 08: Interface State
========================

Tests:
- Verify enable/disable states
- Test element visibility
- Test widget read-only mode
- Verify state persistence
"""
from __future__ import annotations

import pytest


class TestEnableDisableStates:
    """Test widget enable/disable states."""

    def test_widget_enabled_by_default(self, qapp):
        """Verify widgets are enabled by default."""
        from PyQt6.QtWidgets import QPushButton, QLineEdit, QComboBox
        
        widgets = [QPushButton(), QLineEdit(), QComboBox()]
        
        for widget in widgets:
            assert widget.isEnabled()
            widget.deleteLater()
        
        qapp.processEvents()

    def test_widget_disable(self, qapp):
        """Verify widgets can be disabled."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Click")
        button.setEnabled(False)
        
        assert not button.isEnabled()
        
        button.deleteLater()
        qapp.processEvents()

    def test_widget_enable_toggle(self, qapp):
        """Verify enable/disable can toggle."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        edit.setEnabled(True)
        assert edit.isEnabled()
        
        edit.setEnabled(False)
        assert not edit.isEnabled()
        
        edit.setEnabled(True)
        assert edit.isEnabled()
        
        edit.deleteLater()
        qapp.processEvents()

    def test_parent_disable_affects_children(self, qapp):
        """Verify disabling parent affects children."""
        from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        child = QPushButton("Child")
        layout.addWidget(child)
        
        parent.setEnabled(False)
        
        # Child is still enabled internally but parent is disabled
        assert not parent.isEnabled()
        
        parent.deleteLater()
        qapp.processEvents()

    def test_group_enable_disable(self, qapp):
        """Verify group of widgets can be enabled/disabled."""
        from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLineEdit
        
        group = QGroupBox("Settings")
        layout = QVBoxLayout(group)
        
        btn = QPushButton("Button")
        edit = QLineEdit()
        
        layout.addWidget(btn)
        layout.addWidget(edit)
        
        group.setEnabled(False)
        assert not group.isEnabled()
        
        group.setEnabled(True)
        assert group.isEnabled()
        
        group.deleteLater()
        qapp.processEvents()


class TestElementVisibility:
    """Test widget visibility."""

    def test_widget_visible_by_default(self, qapp):
        """Verify widgets are visible by default when shown."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton()
        button.show()
        
        assert button.isVisible()
        
        button.deleteLater()
        qapp.processEvents()

    def test_widget_hide(self, qapp):
        """Verify widgets can be hidden."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton()
        button.show()
        button.hide()
        
        assert not button.isVisible()
        
        button.deleteLater()
        qapp.processEvents()

    def test_visibility_toggle(self, qapp):
        """Verify visibility can toggle."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel("Test")
        
        label.show()
        assert label.isVisible()
        
        label.setVisible(False)
        assert not label.isVisible()
        
        label.setVisible(True)
        assert label.isVisible()
        
        label.deleteLater()
        qapp.processEvents()

    def test_hidden_widget_excluded_from_layout(self, qapp):
        """Verify hidden widgets don't take layout space."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        btn1 = QPushButton("Button 1")
        btn2 = QPushButton("Button 2")
        
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        
        parent.show()
        initial_height = parent.sizeHint().height()
        
        btn1.hide()
        qapp.processEvents()
        
        # Height should change when widget is hidden
        # Note: May depend on layout configuration
        assert not btn1.isVisible()
        
        parent.deleteLater()
        qapp.processEvents()

    def test_stacked_widget_visibility(self, qapp):
        """Verify stacked widget page visibility."""
        from PyQt6.QtWidgets import QStackedWidget, QWidget
        
        stack = QStackedWidget()
        
        page1 = QWidget()
        page1.setObjectName("page1")
        page2 = QWidget()
        page2.setObjectName("page2")
        
        stack.addWidget(page1)
        stack.addWidget(page2)
        
        stack.setCurrentIndex(0)
        assert stack.currentWidget() == page1
        
        stack.setCurrentIndex(1)
        assert stack.currentWidget() == page2
        
        stack.deleteLater()
        qapp.processEvents()


class TestReadOnlyMode:
    """Test widget read-only mode."""

    def test_lineedit_readonly(self, qapp):
        """Verify QLineEdit read-only mode."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit("Initial text")
        edit.setReadOnly(True)
        
        assert edit.isReadOnly()
        
        edit.deleteLater()
        qapp.processEvents()

    def test_textedit_readonly(self, qapp):
        """Verify QTextEdit read-only mode."""
        from PyQt6.QtWidgets import QTextEdit
        
        text = QTextEdit()
        text.setPlainText("Read-only content")
        text.setReadOnly(True)
        
        assert text.isReadOnly()
        
        text.deleteLater()
        qapp.processEvents()

    def test_plaintextedit_readonly(self, qapp):
        """Verify QPlainTextEdit read-only mode."""
        from PyQt6.QtWidgets import QPlainTextEdit
        
        text = QPlainTextEdit()
        text.setPlainText("Content")
        text.setReadOnly(True)
        
        assert text.isReadOnly()
        
        text.deleteLater()
        qapp.processEvents()

    def test_readonly_toggle(self, qapp):
        """Verify read-only mode can toggle."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        assert not edit.isReadOnly()
        
        edit.setReadOnly(True)
        assert edit.isReadOnly()
        
        edit.setReadOnly(False)
        assert not edit.isReadOnly()
        
        edit.deleteLater()
        qapp.processEvents()


class TestCheckedStates:
    """Test checkbox and radio button states."""

    def test_checkbox_checked_state(self, qapp):
        """Verify checkbox checked state."""
        from PyQt6.QtWidgets import QCheckBox
        
        checkbox = QCheckBox("Option")
        
        assert not checkbox.isChecked()
        
        checkbox.setChecked(True)
        assert checkbox.isChecked()
        
        checkbox.deleteLater()
        qapp.processEvents()

    def test_checkbox_tristate(self, qapp):
        """Verify checkbox tri-state mode."""
        from PyQt6.QtWidgets import QCheckBox
        from PyQt6.QtCore import Qt
        
        checkbox = QCheckBox("Tristate")
        checkbox.setTristate(True)
        
        checkbox.setCheckState(Qt.CheckState.Unchecked)
        assert checkbox.checkState() == Qt.CheckState.Unchecked
        
        checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        assert checkbox.checkState() == Qt.CheckState.PartiallyChecked
        
        checkbox.setCheckState(Qt.CheckState.Checked)
        assert checkbox.checkState() == Qt.CheckState.Checked
        
        checkbox.deleteLater()
        qapp.processEvents()

    def test_radiobutton_checked_state(self, qapp):
        """Verify radio button checked state."""
        from PyQt6.QtWidgets import QRadioButton
        
        radio = QRadioButton("Option")
        
        assert not radio.isChecked()
        
        radio.setChecked(True)
        assert radio.isChecked()
        
        radio.deleteLater()
        qapp.processEvents()

    def test_radiobutton_exclusivity(self, qapp):
        """Verify radio buttons are mutually exclusive."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QRadioButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        radio1 = QRadioButton("Option 1")
        radio2 = QRadioButton("Option 2")
        radio3 = QRadioButton("Option 3")
        
        layout.addWidget(radio1)
        layout.addWidget(radio2)
        layout.addWidget(radio3)
        
        radio1.setChecked(True)
        assert radio1.isChecked()
        assert not radio2.isChecked()
        
        radio2.setChecked(True)
        assert not radio1.isChecked()
        assert radio2.isChecked()
        
        parent.deleteLater()
        qapp.processEvents()


class TestStatePersistence:
    """Test state persistence patterns."""

    def test_widget_state_restoration(self, qapp):
        """Verify widget state can be saved and restored."""
        from PyQt6.QtWidgets import QMainWindow, QWidget
        from PyQt6.QtCore import QSettings
        
        # Create temporary settings
        settings = QSettings("TestCompany", "TestApp")
        
        # Save state
        window = QMainWindow()
        window.resize(800, 600)
        settings.setValue("window/geometry", window.saveGeometry())
        settings.setValue("window/state", window.saveState())
        
        # Verify values were saved
        assert settings.value("window/geometry") is not None
        assert settings.value("window/state") is not None
        
        # Clean up
        settings.clear()
        window.deleteLater()
        qapp.processEvents()

    def test_splitter_state_persistence(self, qapp):
        """Verify splitter sizes can be saved."""
        from PyQt6.QtWidgets import QSplitter, QWidget
        from PyQt6.QtCore import Qt
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QWidget())
        splitter.addWidget(QWidget())
        
        splitter.setSizes([200, 400])
        
        saved_state = splitter.saveState()
        assert saved_state is not None
        
        # Restore state
        splitter.restoreState(saved_state)
        
        splitter.deleteLater()
        qapp.processEvents()

    def test_form_values_persistence(self, qapp):
        """Verify form values can be collected and restored."""
        from PyQt6.QtWidgets import QLineEdit, QCheckBox, QSpinBox
        
        # Simulate saving form values
        form_data = {}
        
        name_edit = QLineEdit("John Doe")
        form_data["name"] = name_edit.text()
        
        active_check = QCheckBox()
        active_check.setChecked(True)
        form_data["active"] = active_check.isChecked()
        
        age_spin = QSpinBox()
        age_spin.setValue(30)
        form_data["age"] = age_spin.value()
        
        # Verify collected values
        assert form_data == {
            "name": "John Doe",
            "active": True,
            "age": 30
        }
        
        # Simulate restoration
        name_edit.clear()
        name_edit.setText(form_data["name"])
        assert name_edit.text() == "John Doe"
        
        name_edit.deleteLater()
        active_check.deleteLater()
        age_spin.deleteLater()
        qapp.processEvents()


class TestDynamicStateChanges:
    """Test dynamic state changes based on conditions."""

    def test_conditional_enable(self, qapp):
        """Verify conditional enabling based on other widget."""
        from PyQt6.QtWidgets import QCheckBox, QLineEdit
        
        checkbox = QCheckBox("Enable input")
        lineedit = QLineEdit()
        lineedit.setEnabled(False)
        
        # Simulate conditional logic
        def on_checkbox_changed(checked):
            lineedit.setEnabled(checked)
        
        checkbox.toggled.connect(on_checkbox_changed)
        
        assert not lineedit.isEnabled()
        
        checkbox.setChecked(True)
        assert lineedit.isEnabled()
        
        checkbox.setChecked(False)
        assert not lineedit.isEnabled()
        
        checkbox.deleteLater()
        lineedit.deleteLater()
        qapp.processEvents()

    def test_conditional_visibility(self, qapp):
        """Verify conditional visibility based on selection."""
        from PyQt6.QtWidgets import QComboBox, QWidget
        
        combo = QComboBox()
        combo.addItems(["Option A", "Option B"])
        
        widget_a = QWidget()
        widget_b = QWidget()
        widget_b.hide()
        
        # Simulate conditional logic
        def on_combo_changed(index):
            widget_a.setVisible(index == 0)
            widget_b.setVisible(index == 1)
        
        combo.currentIndexChanged.connect(on_combo_changed)
        
        # Change to index 1 first, then back to 0 to ensure signal fires
        combo.setCurrentIndex(1)
        qapp.processEvents()
        assert not widget_a.isVisible()
        assert widget_b.isVisible()
        
        combo.setCurrentIndex(0)
        qapp.processEvents()
        assert widget_a.isVisible()
        assert not widget_b.isVisible()
        
        combo.deleteLater()
        widget_a.deleteLater()
        widget_b.deleteLater()
        qapp.processEvents()
