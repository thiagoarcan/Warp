"""
Qt Environment Test Module.

This module tests that the Qt environment is properly configured
and all necessary fixtures are working correctly.

Run with: pytest tests/gui/test_qt_environment.py -v
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication
    from pytestqt.qtbot import QtBot


# ============================================
# QApplication Tests
# ============================================


class TestQApplicationSetup:
    """Tests for QApplication initialization and management."""

    def test_qapp_exists(self, qapp: "QApplication") -> None:
        """Test that QApplication is properly initialized."""
        assert qapp is not None
        assert qapp.applicationName() is not None

    def test_qapp_is_singleton(self, qapp: "QApplication") -> None:
        """Test that QApplication.instance() returns the same app."""
        from PyQt6.QtWidgets import QApplication
        
        instance = QApplication.instance()
        assert instance is qapp

    def test_qapp_processes_events(self, qapp: "QApplication") -> None:
        """Test that event processing works."""
        # This should not raise
        qapp.processEvents()


# ============================================
# QtBot Tests
# ============================================


class TestQtBotFunctionality:
    """Tests for QtBot fixture functionality."""

    def test_qtbot_exists(self, qtbot: "QtBot") -> None:
        """Test that qtbot fixture is available."""
        assert qtbot is not None

    def test_qtbot_add_widget(self, qtbot: "QtBot") -> None:
        """Test that qtbot can track widgets."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        # Widget should be tracked and cleaned up automatically
        assert widget is not None

    def test_qtbot_wait_signal(self, qtbot: "QtBot") -> None:
        """Test that signal waiting works."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class Emitter(QObject):
            signal = pyqtSignal()
        
        emitter = Emitter()
        
        # Wait for signal with timeout
        with qtbot.waitSignal(emitter.signal, timeout=100):
            emitter.signal.emit()

    def test_qtbot_key_clicks(self, qtbot: "QtBot") -> None:
        """Test that key simulation works."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QLineEdit
        
        line_edit = QLineEdit()
        qtbot.addWidget(line_edit)
        
        qtbot.keyClicks(line_edit, "hello")
        assert line_edit.text() == "hello"

    def test_qtbot_mouse_click(self, qtbot: "QtBot") -> None:
        """Test that mouse simulation works."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QPushButton
        
        clicked = [False]
        
        def on_click() -> None:
            clicked[0] = True
        
        button = QPushButton("Click Me")
        button.clicked.connect(on_click)
        qtbot.addWidget(button)
        
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert clicked[0] is True


# ============================================
# Widget Tests
# ============================================


class TestBasicWidgets:
    """Tests for basic Qt widgets."""

    def test_create_widget(self, qtbot: "QtBot") -> None:
        """Test widget creation."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        assert widget is not None
        assert widget.isHidden()  # Not shown by default

    def test_widget_show_hide(self, qtbot: "QtBot") -> None:
        """Test widget visibility."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        widget.show()
        assert widget.isVisible()
        
        widget.hide()
        assert not widget.isVisible()

    def test_widget_geometry(self, qtbot: "QtBot") -> None:
        """Test widget geometry methods."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        widget.setGeometry(100, 100, 400, 300)
        
        assert widget.width() == 400
        assert widget.height() == 300


class TestComplexWidgets:
    """Tests for complex Qt widgets."""

    def test_qlineedit(self, qtbot: "QtBot") -> None:
        """Test QLineEdit functionality."""
        from PyQt6.QtWidgets import QLineEdit
        
        edit = QLineEdit()
        qtbot.addWidget(edit)
        
        edit.setText("test value")
        assert edit.text() == "test value"
        
        edit.clear()
        assert edit.text() == ""

    def test_qcombobox(self, qtbot: "QtBot") -> None:
        """Test QComboBox functionality."""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        qtbot.addWidget(combo)
        
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        assert combo.count() == 3
        
        combo.setCurrentIndex(1)
        assert combo.currentText() == "Option 2"

    def test_qcheckbox(self, qtbot: "QtBot") -> None:
        """Test QCheckBox functionality."""
        from PyQt6.QtWidgets import QCheckBox
        
        checkbox = QCheckBox("Enable feature")
        qtbot.addWidget(checkbox)
        
        assert not checkbox.isChecked()
        
        checkbox.setChecked(True)
        assert checkbox.isChecked()

    def test_qspinbox(self, qtbot: "QtBot") -> None:
        """Test QSpinBox functionality."""
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        qtbot.addWidget(spinbox)
        
        spinbox.setRange(0, 100)
        spinbox.setValue(50)
        
        assert spinbox.value() == 50

    def test_qslider(self, qtbot: "QtBot") -> None:
        """Test QSlider functionality."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QSlider
        
        slider = QSlider(Qt.Orientation.Horizontal)
        qtbot.addWidget(slider)
        
        slider.setRange(0, 100)
        slider.setValue(75)
        
        assert slider.value() == 75


# ============================================
# Signal Tests
# ============================================


class TestSignals:
    """Tests for Qt signal/slot mechanism."""

    def test_signal_emit(self, qtbot: "QtBot") -> None:
        """Test basic signal emission."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class Sender(QObject):
            value_changed = pyqtSignal(int)
        
        sender = Sender()
        received = []
        
        sender.value_changed.connect(lambda v: received.append(v))
        sender.value_changed.emit(42)
        
        assert received == [42]

    def test_signal_with_multiple_args(self, qtbot: "QtBot") -> None:
        """Test signal with multiple arguments."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class Sender(QObject):
            data_changed = pyqtSignal(str, int, float)
        
        sender = Sender()
        received = []
        
        sender.data_changed.connect(lambda s, i, f: received.append((s, i, f)))
        sender.data_changed.emit("test", 10, 3.14)
        
        assert received == [("test", 10, 3.14)]

    def test_signal_disconnect(self, qtbot: "QtBot") -> None:
        """Test signal disconnection."""
        from PyQt6.QtCore import QObject, pyqtSignal
        
        class Sender(QObject):
            triggered = pyqtSignal()
        
        sender = Sender()
        count = [0]
        
        def handler() -> None:
            count[0] += 1
        
        sender.triggered.connect(handler)
        sender.triggered.emit()
        assert count[0] == 1
        
        sender.triggered.disconnect(handler)
        sender.triggered.emit()
        assert count[0] == 1  # Still 1, handler was disconnected

    def test_blocker_signal(self, qtbot: "QtBot") -> None:
        """Test signal blocking."""
        from PyQt6.QtCore import QObject
        from PyQt6.QtWidgets import QSpinBox
        
        spinbox = QSpinBox()
        qtbot.addWidget(spinbox)
        
        count = [0]
        
        def on_change(val: int) -> None:
            count[0] += 1
        
        spinbox.valueChanged.connect(on_change)
        
        # Normal emit
        spinbox.setValue(10)
        assert count[0] == 1
        
        # Blocked emit
        spinbox.blockSignals(True)
        spinbox.setValue(20)
        spinbox.blockSignals(False)
        assert count[0] == 1  # Still 1, signal was blocked


# ============================================
# Layout Tests
# ============================================


class TestLayouts:
    """Tests for Qt layouts."""

    def test_vbox_layout(self, qtbot: "QtBot") -> None:
        """Test QVBoxLayout."""
        from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        layout = QVBoxLayout(widget)
        
        label1 = QLabel("Label 1")
        label2 = QLabel("Label 2")
        
        layout.addWidget(label1)
        layout.addWidget(label2)
        
        assert layout.count() == 2

    def test_hbox_layout(self, qtbot: "QtBot") -> None:
        """Test QHBoxLayout."""
        from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        layout = QHBoxLayout(widget)
        
        btn1 = QPushButton("Button 1")
        btn2 = QPushButton("Button 2")
        
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        
        assert layout.count() == 2

    def test_grid_layout(self, qtbot: "QtBot") -> None:
        """Test QGridLayout."""
        from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget
        
        widget = QWidget()
        qtbot.addWidget(widget)
        
        layout = QGridLayout(widget)
        
        for i in range(3):
            for j in range(3):
                layout.addWidget(QLabel(f"({i},{j})"), i, j)
        
        assert layout.count() == 9


# ============================================
# Dialog Tests
# ============================================


class TestDialogs:
    """Tests for Qt dialogs."""

    def test_message_box_creation(self, qtbot: "QtBot") -> None:
        """Test QMessageBox creation (not exec)."""
        from PyQt6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox()
        qtbot.addWidget(msg_box)
        
        msg_box.setText("Test message")
        msg_box.setWindowTitle("Test Title")
        
        assert msg_box.text() == "Test message"

    def test_input_dialog_creation(self, qtbot: "QtBot") -> None:
        """Test QInputDialog creation (not exec)."""
        from PyQt6.QtWidgets import QInputDialog
        
        dialog = QInputDialog()
        qtbot.addWidget(dialog)
        
        dialog.setLabelText("Enter value:")
        dialog.setTextValue("default")
        
        assert dialog.textValue() == "default"

    def test_file_dialog_creation(self, qtbot: "QtBot") -> None:
        """Test QFileDialog creation (not exec)."""
        from PyQt6.QtWidgets import QFileDialog
        
        dialog = QFileDialog()
        qtbot.addWidget(dialog)
        
        dialog.setWindowTitle("Select File")
        dialog.setNameFilter("CSV files (*.csv)")
        
        assert "CSV" in dialog.nameFilters()[0]


# ============================================
# Timer Tests
# ============================================


class TestTimers:
    """Tests for Qt timers."""

    def test_single_shot_timer(self, qtbot: "QtBot", qapp: "QApplication") -> None:
        """Test QTimer.singleShot."""
        from PyQt6.QtCore import QTimer
        
        called = [False]
        
        def on_timeout() -> None:
            called[0] = True
        
        QTimer.singleShot(10, on_timeout)
        
        # Wait a bit for timer to fire
        qtbot.wait(50)
        
        assert called[0] is True

    def test_repeating_timer(self, qtbot: "QtBot", qapp: "QApplication") -> None:
        """Test repeating QTimer."""
        from PyQt6.QtCore import QTimer
        
        count = [0]
        
        timer = QTimer()
        timer.setInterval(10)
        timer.timeout.connect(lambda: count.__setitem__(0, count[0] + 1))
        timer.start()
        
        # Wait for a few ticks
        qtbot.wait(100)
        timer.stop()
        
        assert count[0] >= 5


# ============================================
# Platform Base Component Tests
# ============================================


class TestPlatformBaseComponents:
    """Tests for Platform Base specific components."""

    def test_signal_hub_import(self) -> None:
        """Test that SignalHub can be imported."""
        try:
            from platform_base.desktop.signal_hub import SignalHub
            assert SignalHub is not None
        except ImportError as e:
            pytest.skip(f"SignalHub not available: {e}")

    def test_session_state_import(self) -> None:
        """Test that SessionState can be imported."""
        try:
            from platform_base.desktop.session_state import SessionState
            assert SessionState is not None
        except ImportError as e:
            pytest.skip(f"SessionState not available: {e}")

    def test_signal_hub_creation(self, qtbot: "QtBot") -> None:
        """Test SignalHub instantiation."""
        try:
            from platform_base.desktop.signal_hub import SignalHub
            hub = SignalHub()
            assert hub is not None
        except ImportError as e:
            pytest.skip(f"SignalHub not available: {e}")

    def test_signal_hub_signals(self, qtbot: "QtBot") -> None:
        """Test SignalHub signals can be connected."""
        try:
            from platform_base.desktop.signal_hub import SignalHub
            
            hub = SignalHub()
            received = []
            
            # Try to connect to a signal
            if hasattr(hub, "dataset_loaded"):
                hub.dataset_loaded.connect(lambda x: received.append(x))
            elif hasattr(hub, "status_message"):
                hub.status_message.connect(lambda x: received.append(x))
            else:
                pytest.skip("No suitable signal found on SignalHub")
                
        except ImportError as e:
            pytest.skip(f"SignalHub not available: {e}")


# ============================================
# Environment Check Summary
# ============================================


class TestEnvironmentSummary:
    """Summary tests for environment validation."""

    def test_pyqt6_version(self) -> None:
        """Test PyQt6 version."""
        from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
        
        print(f"\nPyQt6 Version: {PYQT_VERSION_STR}")
        print(f"Qt Version: {QT_VERSION_STR}")
        
        assert PYQT_VERSION_STR >= "6.5.0"

    def test_pytest_qt_available(self) -> None:
        """Test pytest-qt is available."""
        import pytestqt
        
        print(f"\npytest-qt Version: {pytestqt.__version__}")
        assert pytestqt.__version__ >= "4.0.0"

    def test_all_required_imports(self) -> None:
        """Test all required Qt imports work."""
        from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
        from PyQt6.QtWidgets import (
            QApplication,
            QCheckBox,
            QComboBox,
            QDialog,
            QDockWidget,
            QFileDialog,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QListWidget,
            QMainWindow,
            QMenuBar,
            QMessageBox,
            QPushButton,
            QScrollArea,
            QSlider,
            QSpinBox,
            QSplitter,
            QStatusBar,
            QTableWidget,
            QTabWidget,
            QToolBar,
            QTreeWidget,
            QVBoxLayout,
            QWidget,
        )

        # All imports successful
        assert True

    def test_pyqtgraph_available(self) -> None:
        """Test pyqtgraph is available."""
        try:
            import pyqtgraph as pg
            print(f"\npyqtgraph Version: {pg.__version__}")
            assert pg.__version__ >= "0.13.0"
        except ImportError:
            pytest.skip("pyqtgraph not available")

    def test_pyvista_available(self) -> None:
        """Test pyvista is available."""
        try:
            import pyvista as pv
            print(f"\npyvista Version: {pv.__version__}")
            assert pv.__version__ >= "0.42.0"
        except ImportError:
            pytest.skip("pyvista not available")
