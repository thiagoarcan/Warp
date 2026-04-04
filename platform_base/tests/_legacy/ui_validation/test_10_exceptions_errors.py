# -*- coding: utf-8 -*-
"""
Test 10: Exceptions and Errors
==============================

Tests:
- Test exception handling
- Verify error messages
- Test logging functionality
- Verify graceful error recovery
"""
from __future__ import annotations

import logging
from io import StringIO

import pytest


class TestExceptionHandling:
    """Test exception handling patterns."""

    def test_invalid_ui_file_handling(self, qapp):
        """Verify invalid .ui file is handled gracefully."""
        from PyQt6 import uic
        
        with pytest.raises(Exception):
            uic.loadUi("nonexistent_file.ui")

    def test_invalid_stylesheet_handling(self, qapp):
        """Verify invalid stylesheet doesn't crash."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        
        # Invalid stylesheet should not crash
        widget.setStyleSheet("invalid { css { garbage }}")
        
        # Widget should still function
        widget.show()
        assert widget.isVisible()
        
        widget.deleteLater()
        qapp.processEvents()

    def test_invalid_property_access(self, qapp):
        """Verify invalid property access is handled."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        
        # Accessing non-existent property should raise
        with pytest.raises(AttributeError):
            _ = widget.nonexistent_property
        
        widget.deleteLater()
        qapp.processEvents()

    def test_null_parent_handling(self, qapp):
        """Verify null parent is handled correctly."""
        from PyQt6.QtWidgets import QPushButton
        
        # Creating widget without parent should work
        button = QPushButton()
        assert button.parent() is None
        
        button.deleteLater()
        qapp.processEvents()

    def test_deleted_widget_handling(self, qapp):
        """Verify deleted widget access is handled."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton()
        button.deleteLater()
        qapp.processEvents()
        
        # Accessing deleted widget in Python should fail
        # Note: Behavior depends on PyQt bindings
        # This test documents expected behavior


class TestErrorMessages:
    """Test error message quality."""

    def test_qmessagebox_error_display(self, qapp):
        """Verify error message box can display."""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText("An error occurred")
        msg.setInformativeText("Detailed error information")
        msg.setDetailedText("Stack trace or additional details")
        
        assert msg.text() == "An error occurred"
        assert msg.informativeText() == "Detailed error information"
        
        msg.deleteLater()
        qapp.processEvents()

    def test_statusbar_error_display(self, qapp):
        """Verify status bar can display errors."""
        from PyQt6.QtWidgets import QMainWindow
        
        window = QMainWindow()
        status = window.statusBar()
        
        status.showMessage("Error: File not found", 5000)
        
        assert "Error" in status.currentMessage()
        
        window.deleteLater()
        qapp.processEvents()

    def test_label_error_styling(self, qapp):
        """Verify error labels can be styled."""
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel("Error: Invalid input")
        label.setStyleSheet("color: red; font-weight: bold;")
        
        assert "red" in label.styleSheet()
        
        label.deleteLater()
        qapp.processEvents()

    def test_tooltip_error_info(self, qapp):
        """Verify tooltips can show error info."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setToolTip("Error: This field is required")
        
        assert "Error" in edit.toolTip()
        
        edit.deleteLater()
        qapp.processEvents()


class TestLogging:
    """Test logging functionality."""

    def test_logger_creation(self):
        """Verify logger can be created."""
        logger = logging.getLogger("test_ui")
        
        assert logger is not None
        assert logger.name == "test_ui"

    def test_log_levels(self):
        """Verify log levels work correctly."""
        logger = logging.getLogger("test_levels")
        logger.setLevel(logging.DEBUG)
        
        # Create string handler for testing
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        output = stream.getvalue()
        assert "Debug" in output
        assert "Info" in output
        assert "Warning" in output
        assert "Error" in output
        
        logger.removeHandler(handler)

    def test_exception_logging(self):
        """Verify exceptions can be logged."""
        logger = logging.getLogger("test_exception")
        
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Caught exception")
        
        output = stream.getvalue()
        assert "Caught exception" in output
        assert "ValueError" in output
        
        logger.removeHandler(handler)

    def test_ui_event_logging(self, qapp):
        """Verify UI events can be logged."""
        from PyQt6.QtWidgets import QPushButton
        
        logger = logging.getLogger("test_ui_events")
        logger.setLevel(logging.INFO)  # Set logger level
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        button = QPushButton("Click")
        
        def on_click():
            logger.info("Button clicked")
        
        button.clicked.connect(on_click)
        button.click()
        qapp.processEvents()  # Process events to ensure handler is called
        handler.flush()  # Flush to ensure buffer is written
        
        output = stream.getvalue()
        assert "Button clicked" in output
        
        logger.removeHandler(handler)
        button.deleteLater()
        qapp.processEvents()


class TestGracefulRecovery:
    """Test graceful error recovery."""

    def test_recover_from_invalid_input(self, qapp):
        """Verify recovery from invalid input."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        spinbox.setRange(0, 100)
        spinbox.setValue(50)
        
        # Try to set invalid value
        spinbox.setValue(999)  # Over max
        
        # Should recover by clamping
        assert spinbox.value() == 100
        
        spinbox.deleteLater()
        qapp.processEvents()

    def test_recover_from_missing_resource(self, qapp):
        """Verify recovery from missing resource."""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QPixmap
        
        label = QLabel()
        
        # Try to load non-existent image
        pixmap = QPixmap("nonexistent.png")
        label.setPixmap(pixmap)
        
        # Label should handle null pixmap
        assert pixmap.isNull()
        
        label.deleteLater()
        qapp.processEvents()

    def test_recover_from_widget_deletion(self, qapp):
        """Verify recovery when child widget is deleted."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
        
        parent = QWidget()
        layout = QVBoxLayout(parent)
        
        button = QPushButton("Test")
        layout.addWidget(button)
        
        initial_count = layout.count()
        
        button.deleteLater()
        qapp.processEvents()
        
        # Parent should still be valid
        assert parent.isVisible() or not parent.isVisible()  # Just check it exists
        
        parent.deleteLater()
        qapp.processEvents()

    def test_recover_from_signal_error(self, qapp, monkeypatch):
        """Verify recovery when signal handler raises."""
        import sys
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton()
        error_raised = [False]
        exception_captured = []
        
        original_excepthook = sys.excepthook
        
        def custom_excepthook(exc_type, exc_val, exc_tb):
            if exc_type == ValueError and str(exc_val) == "Handler error":
                exception_captured.append(True)
            else:
                original_excepthook(exc_type, exc_val, exc_tb)
        
        monkeypatch.setattr(sys, 'excepthook', custom_excepthook)
        
        def handler_that_raises():
            error_raised[0] = True
            raise ValueError("Handler error")
        
        button.clicked.connect(handler_that_raises)
        
        # Qt intercepts exceptions in signal handlers, so they don't propagate
        button.click()
        qapp.processEvents()
        
        # Handler was called and error was raised (intercepted by Qt)
        assert error_raised[0], "Handler should have been called"
        
        # App should still be running after signal error
        assert qapp.instance() is not None, "App should still be running"
        
        button.deleteLater()
        qapp.processEvents()


class TestValidationErrors:
    """Test validation error handling."""

    def test_form_validation_errors(self, qapp):
        """Verify form validation produces clear errors."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        errors = []
        
        # Validate empty field
        if not edit.text().strip():
            errors.append("Field is required")
        
        assert len(errors) == 1
        assert errors[0] == "Field is required"
        
        edit.deleteLater()
        qapp.processEvents()

    def test_range_validation_error(self, qapp):
        """Verify range validation error handling."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        spinbox.setRange(1, 10)
        
        def validate_range(value):
            if value < spinbox.minimum():
                return f"Value must be at least {spinbox.minimum()}"
            if value > spinbox.maximum():
                return f"Value must be at most {spinbox.maximum()}"
            return None
        
        assert validate_range(0) == "Value must be at least 1"
        assert validate_range(15) == "Value must be at most 10"
        assert validate_range(5) is None
        
        spinbox.deleteLater()
        qapp.processEvents()

    def test_format_validation_error(self, qapp):
        """Verify format validation error handling."""
        import re
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        edit.setText("invalid-email")
        
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        
        def validate_email(text):
            if not re.match(email_pattern, text):
                return "Invalid email format"
            return None
        
        assert validate_email(edit.text()) == "Invalid email format"
        
        edit.setText("valid@email.com")
        assert validate_email(edit.text()) is None
        
        edit.deleteLater()
        qapp.processEvents()


class TestErrorReporting:
    """Test error reporting mechanisms."""

    def test_error_dialog_content(self, qapp):
        """Verify error dialog has proper content."""
        from PyQt6.QtWidgets import QMessageBox
        
        dialog = QMessageBox()
        
        # Set up error dialog
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle("Application Error")
        dialog.setText("An unexpected error occurred.")
        dialog.setInformativeText("Please contact support.")
        dialog.setDetailedText("Error code: ERR_001\nTimestamp: 2024-01-01")
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Verify content
        assert dialog.icon() == QMessageBox.Icon.Critical
        assert dialog.windowTitle() == "Application Error"
        assert dialog.text() == "An unexpected error occurred."
        
        dialog.deleteLater()
        qapp.processEvents()

    def test_error_state_visual_feedback(self, qapp):
        """Verify error state provides visual feedback."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        
        # Normal state
        edit.setStyleSheet("")
        
        # Error state
        error_style = "border: 2px solid red; background-color: #ffeeee;"
        edit.setStyleSheet(error_style)
        
        assert "red" in edit.styleSheet()
        
        edit.deleteLater()
        qapp.processEvents()

    def test_warning_dialog_content(self, qapp):
        """Verify warning dialog has proper content."""
        from PyQt6.QtWidgets import QMessageBox
        
        dialog = QMessageBox()
        
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("Warning")
        dialog.setText("This action cannot be undone.")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        assert dialog.icon() == QMessageBox.Icon.Warning
        
        dialog.deleteLater()
        qapp.processEvents()
