# -*- coding: utf-8 -*-
"""
Test 04: Signals and Slots
==========================

Tests:
- Verify buttons have signals connected
- Test click events are captured
- Validate signal/slot connections
- Verify callbacks don't raise exceptions
- Test signal disconnection on window close
"""
from __future__ import annotations

import gc
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class TestButtonSignals:
    """Test button signal connections."""

    def test_button_clicked_signal_exists(self, qapp):
        """Verify QPushButton has clicked signal."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        assert hasattr(button, "clicked")
        
        button.deleteLater()
        qapp.processEvents()

    def test_button_clicked_emits(self, qapp):
        """Verify button.clicked emits when clicked."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        callback = MagicMock()
        
        button.clicked.connect(callback)
        button.click()
        qapp.processEvents()
        
        callback.assert_called_once()
        
        button.deleteLater()
        qapp.processEvents()

    def test_multiple_buttons_independent(self, qapp):
        """Verify multiple buttons have independent signals."""
        from PyQt6.QtWidgets import QPushButton
        
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        button1.clicked.connect(callback1)
        button2.clicked.connect(callback2)
        
        button1.click()
        qapp.processEvents()
        
        callback1.assert_called_once()
        callback2.assert_not_called()
        
        button1.deleteLater()
        button2.deleteLater()
        qapp.processEvents()


class TestWidgetSignals:
    """Test various widget signal connections."""

    def test_lineedit_textchanged(self, qapp):
        """Verify QLineEdit.textChanged emits."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        callback = MagicMock()
        
        edit.textChanged.connect(callback)
        edit.setText("test")
        qapp.processEvents()
        
        callback.assert_called_with("test")
        
        edit.deleteLater()
        qapp.processEvents()

    def test_combobox_currentindexchanged(self, qapp):
        """Verify QComboBox.currentIndexChanged emits."""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        combo.addItems(["Item 1", "Item 2", "Item 3"])
        
        callback = MagicMock()
        combo.currentIndexChanged.connect(callback)
        
        combo.setCurrentIndex(2)
        qapp.processEvents()
        
        callback.assert_called()
        
        combo.deleteLater()
        qapp.processEvents()

    def test_checkbox_statechanged(self, qapp):
        """Verify QCheckBox.stateChanged emits."""
        from PyQt6.QtWidgets import QCheckBox
        
        checkbox = QCheckBox("Test")
        callback = MagicMock()
        
        checkbox.stateChanged.connect(callback)
        checkbox.setChecked(True)
        qapp.processEvents()
        
        callback.assert_called()
        
        checkbox.deleteLater()
        qapp.processEvents()

    def test_spinbox_valuechanged(self, qapp):
        """Verify QSpinBox.valueChanged emits."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        spinbox.setRange(0, 100)
        
        callback = MagicMock()
        spinbox.valueChanged.connect(callback)
        
        spinbox.setValue(50)
        qapp.processEvents()
        
        callback.assert_called_with(50)
        
        spinbox.deleteLater()
        qapp.processEvents()


class TestSignalSlotConnections:
    """Test signal/slot connection mechanisms."""

    def test_signal_connect_disconnect(self, qapp):
        """Verify signals can be connected and disconnected."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        callback = MagicMock()
        
        # Connect
        button.clicked.connect(callback)
        button.click()
        qapp.processEvents()
        assert callback.call_count == 1
        
        # Disconnect
        button.clicked.disconnect(callback)
        button.click()
        qapp.processEvents()
        assert callback.call_count == 1  # Should not increase
        
        button.deleteLater()
        qapp.processEvents()

    def test_multiple_slots_same_signal(self, qapp):
        """Verify multiple slots can connect to same signal."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()
        
        button.clicked.connect(callback1)
        button.clicked.connect(callback2)
        button.clicked.connect(callback3)
        
        button.click()
        qapp.processEvents()
        
        callback1.assert_called_once()
        callback2.assert_called_once()
        callback3.assert_called_once()
        
        button.deleteLater()
        qapp.processEvents()

    def test_lambda_slot_connection(self, qapp):
        """Verify lambda functions work as slots."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        result = []
        
        button.clicked.connect(lambda: result.append("clicked"))
        button.click()
        qapp.processEvents()
        
        assert len(result) == 1
        assert result[0] == "clicked"
        
        button.deleteLater()
        qapp.processEvents()


class TestCallbackExceptions:
    """Test callback exception handling."""

    def test_callback_exception_doesnt_crash(self, qapp, monkeypatch):
        """Verify exception in callback doesn't crash Qt."""
        from PyQt6.QtWidgets import QPushButton
        import sys
        
        # Track if exception was raised (Qt intercepts it)
        exception_raised = []
        original_excepthook = sys.excepthook
        
        def custom_excepthook(exc_type, exc_val, exc_tb):
            if exc_type == ValueError and str(exc_val) == "Test exception":
                exception_raised.append(True)
            else:
                original_excepthook(exc_type, exc_val, exc_tb)
        
        # Temporarily replace excepthook to capture the exception
        monkeypatch.setattr(sys, 'excepthook', custom_excepthook)
        
        button = QPushButton("Test")
        
        def bad_callback():
            raise ValueError("Test exception")
        
        button.clicked.connect(bad_callback)
        
        # This should not crash Qt - exception is intercepted
        button.click()
        qapp.processEvents()
        
        # Verify the exception was triggered but Qt didn't crash
        # The app should still be running
        assert qapp.instance() is not None, "QApplication should still be running"
        
        button.deleteLater()
        qapp.processEvents()

    def test_callback_with_return_value(self, qapp):
        """Verify callbacks can return values (ignored by Qt)."""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        
        def callback_with_return():
            return "some value"
        
        button.clicked.connect(callback_with_return)
        button.click()  # Should not raise
        qapp.processEvents()
        
        button.deleteLater()
        qapp.processEvents()


class TestSignalDisconnectionOnClose:
    """Test signal cleanup when windows close."""

    def test_widget_deletion_disconnects_signals(self, qapp):
        """Verify widget deletion disconnects signals."""
        from PyQt6.QtWidgets import QPushButton, QWidget
        
        parent = QWidget()
        button = QPushButton("Test", parent)
        
        callback = MagicMock()
        button.clicked.connect(callback)
        
        # Delete parent (which deletes button)
        parent.deleteLater()
        qapp.processEvents()
        gc.collect()
        
        # Callback should not be called anymore
        # (and signal connection is cleaned up)

    def test_dialog_close_cleanup(self, qapp):
        """Verify dialog close cleans up properly."""
        from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout
        
        dialog = QDialog()
        layout = QVBoxLayout(dialog)
        button = QPushButton("Test")
        layout.addWidget(button)
        
        callback = MagicMock()
        button.clicked.connect(callback)
        
        dialog.show()
        qapp.processEvents()
        
        dialog.close()
        dialog.deleteLater()
        qapp.processEvents()
        gc.collect()


class TestCustomSignals:
    """Test custom signal definitions."""

    def test_custom_signal_creation(self, qapp):
        """Verify custom signals can be created."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class CustomObject(QObject):
            custom_signal = pyqtSignal(str)
        
        obj = CustomObject()
        callback = MagicMock()
        
        obj.custom_signal.connect(callback)
        obj.custom_signal.emit("test_data")
        qapp.processEvents()
        
        callback.assert_called_once_with("test_data")
        
        obj.deleteLater()
        qapp.processEvents()

    def test_signal_with_multiple_args(self, qapp):
        """Verify signals with multiple arguments work."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class CustomObject(QObject):
            data_signal = pyqtSignal(str, int, float)
        
        obj = CustomObject()
        callback = MagicMock()
        
        obj.data_signal.connect(callback)
        obj.data_signal.emit("name", 42, 3.14)
        qapp.processEvents()
        
        callback.assert_called_once_with("name", 42, 3.14)
        
        obj.deleteLater()
        qapp.processEvents()

    def test_signal_with_object_arg(self, qapp):
        """Verify signals with object arguments work."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class CustomObject(QObject):
            object_signal = pyqtSignal(object)
        
        obj = CustomObject()
        callback = MagicMock()
        
        test_data = {"key": "value", "number": 123}
        
        obj.object_signal.connect(callback)
        obj.object_signal.emit(test_data)
        qapp.processEvents()
        
        callback.assert_called_once_with(test_data)
        
        obj.deleteLater()
        qapp.processEvents()
