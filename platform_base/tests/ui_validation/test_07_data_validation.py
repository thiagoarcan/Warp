# -*- coding: utf-8 -*-
"""
Test 07: Data Validation
========================

Tests:
- Verify text field validators
- Test input limits (min/max)
- Validate format masks
- Verify required field validation
- Test behavior with invalid inputs
"""
from __future__ import annotations

import pytest


class TestTextFieldValidators:
    """Test text field validation."""

    def test_lineedit_accepts_text(self, qapp):
        """Verify QLineEdit accepts text."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setText("Test input")
        
        assert edit.text() == "Test input"
        
        edit.deleteLater()
        qapp.processEvents()

    def test_lineedit_max_length(self, qapp):
        """Verify QLineEdit maxLength works."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setMaxLength(10)
        
        edit.setText("This is a very long text")
        
        assert len(edit.text()) <= 10
        
        edit.deleteLater()
        qapp.processEvents()

    def test_lineedit_input_mask(self, qapp):
        """Verify QLineEdit input mask works."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setInputMask("000.000.000.000")  # IP address format
        
        assert edit.inputMask() == "000.000.000.000"
        
        edit.deleteLater()
        qapp.processEvents()

    def test_int_validator(self, qapp):
        """Verify QIntValidator works."""
        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtGui import QIntValidator
        
        edit = QLineEdit()
        validator = QIntValidator(0, 100)
        edit.setValidator(validator)
        
        assert edit.validator() is not None
        
        edit.deleteLater()
        qapp.processEvents()

    def test_double_validator(self, qapp):
        """Verify QDoubleValidator works."""
        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtGui import QDoubleValidator
        
        edit = QLineEdit()
        validator = QDoubleValidator(0.0, 100.0, 2)
        edit.setValidator(validator)
        
        assert edit.validator() is not None
        
        edit.deleteLater()
        qapp.processEvents()

    def test_regex_validator(self, qapp):
        """Verify QRegularExpressionValidator works."""
        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtCore import QRegularExpression
        from PyQt6.QtGui import QRegularExpressionValidator
        
        edit = QLineEdit()
        regex = QRegularExpression(r"[A-Za-z]+")
        validator = QRegularExpressionValidator(regex)
        edit.setValidator(validator)
        
        assert edit.validator() is not None
        
        edit.deleteLater()
        qapp.processEvents()


class TestSpinBoxLimits:
    """Test spinbox limits."""

    def test_spinbox_range(self, qapp):
        """Verify QSpinBox range works."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        spinbox.setRange(10, 100)
        
        assert spinbox.minimum() == 10
        assert spinbox.maximum() == 100
        
        spinbox.deleteLater()
        qapp.processEvents()

    def test_spinbox_clamps_value(self, qapp):
        """Verify QSpinBox clamps value to range."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        spinbox.setRange(0, 100)
        
        spinbox.setValue(150)  # Over maximum
        assert spinbox.value() == 100
        
        spinbox.setValue(-10)  # Under minimum
        assert spinbox.value() == 0
        
        spinbox.deleteLater()
        qapp.processEvents()

    def test_doublespinbox_range(self, qapp):
        """Verify QDoubleSpinBox range works."""
        from PyQt6.QtWidgets import QDoubleSpinBox
        
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0.0, 10.0)
        spinbox.setDecimals(3)
        
        assert spinbox.minimum() == 0.0
        assert spinbox.maximum() == 10.0
        assert spinbox.decimals() == 3
        
        spinbox.deleteLater()
        qapp.processEvents()

    def test_doublespinbox_step(self, qapp):
        """Verify QDoubleSpinBox step works."""
        from PyQt6.QtWidgets import QDoubleSpinBox
        
        spinbox = QDoubleSpinBox()
        spinbox.setSingleStep(0.5)
        
        assert spinbox.singleStep() == 0.5
        
        spinbox.deleteLater()
        qapp.processEvents()


class TestComboBoxValidation:
    """Test combobox validation."""

    def test_combobox_items(self, qapp):
        """Verify QComboBox items work."""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        
        assert combo.count() == 3
        assert combo.itemText(0) == "Option 1"
        
        combo.deleteLater()
        qapp.processEvents()

    def test_combobox_current_index(self, qapp):
        """Verify QComboBox current index works."""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        combo.addItems(["A", "B", "C"])
        
        combo.setCurrentIndex(1)
        assert combo.currentIndex() == 1
        assert combo.currentText() == "B"
        
        combo.deleteLater()
        qapp.processEvents()

    def test_combobox_editable(self, qapp):
        """Verify editable QComboBox works."""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(["Item 1", "Item 2"])
        
        combo.setEditText("Custom Text")
        assert combo.currentText() == "Custom Text"
        
        combo.deleteLater()
        qapp.processEvents()


class TestRequiredFieldValidation:
    """Test required field validation patterns."""

    def test_empty_field_detection(self, qapp):
        """Verify empty field can be detected."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        assert edit.text() == ""
        assert len(edit.text().strip()) == 0
        
        edit.setText("  ")  # Whitespace only
        assert len(edit.text().strip()) == 0
        
        edit.deleteLater()
        qapp.processEvents()

    def test_placeholder_text(self, qapp):
        """Verify placeholder text works."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setPlaceholderText("Enter value...")
        
        assert edit.placeholderText() == "Enter value..."
        assert edit.text() == ""  # Placeholder doesn't affect text
        
        edit.deleteLater()
        qapp.processEvents()

    def test_field_modified_status(self, qapp):
        """Verify modified status tracking."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        assert not edit.isModified()
        
        edit.setText("New value")
        edit.setModified(True)
        
        assert edit.isModified()
        
        edit.deleteLater()
        qapp.processEvents()


class TestInvalidInputBehavior:
    """Test behavior with invalid inputs."""

    def test_validator_rejects_invalid(self, qapp):
        """Verify validator rejects invalid input programmatically."""
        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtGui import QIntValidator, QValidator
        
        edit = QLineEdit()
        validator = QIntValidator(0, 100)
        edit.setValidator(validator)
        
        # Test validation state
        state, text, pos = validator.validate("abc", 0)
        assert state == QValidator.State.Invalid
        
        state, text, pos = validator.validate("50", 0)
        assert state == QValidator.State.Acceptable
        
        edit.deleteLater()
        qapp.processEvents()

    def test_spinbox_invalid_input_ignored(self, qapp):
        """Verify spinbox ignores invalid input."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        spinbox.setRange(0, 100)
        spinbox.setValue(50)
        
        # Try to set invalid value
        spinbox.setValue(999)
        
        # Should be clamped to max
        assert spinbox.value() == 100
        
        spinbox.deleteLater()
        qapp.processEvents()

    def test_clear_field(self, qapp):
        """Verify field can be cleared."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setText("Some text")
        
        assert edit.text() == "Some text"
        
        edit.clear()
        assert edit.text() == ""
        
        edit.deleteLater()
        qapp.processEvents()


class TestFormValidation:
    """Test form-level validation patterns."""

    def test_multiple_field_validation(self, qapp):
        """Verify multiple fields can be validated together."""
        from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout
        
        form = QWidget()
        layout = QVBoxLayout(form)
        
        name_field = QLineEdit()
        name_field.setObjectName("nameField")
        email_field = QLineEdit()
        email_field.setObjectName("emailField")
        
        layout.addWidget(name_field)
        layout.addWidget(email_field)
        
        # Simulate form validation
        def validate_form():
            errors = []
            if not name_field.text().strip():
                errors.append("Name is required")
            if "@" not in email_field.text():
                errors.append("Invalid email")
            return errors
        
        # Empty form
        errors = validate_form()
        assert len(errors) == 2
        
        # Partial fill
        name_field.setText("John")
        errors = validate_form()
        assert len(errors) == 1
        
        # Valid form
        email_field.setText("john@example.com")
        errors = validate_form()
        assert len(errors) == 0
        
        form.deleteLater()
        qapp.processEvents()

    def test_validation_styling(self, qapp):
        """Verify validation can change field styling."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        # Valid style
        edit.setStyleSheet("border: 2px solid green;")
        assert "green" in edit.styleSheet()
        
        # Invalid style
        edit.setStyleSheet("border: 2px solid red;")
        assert "red" in edit.styleSheet()
        
        edit.deleteLater()
        qapp.processEvents()
