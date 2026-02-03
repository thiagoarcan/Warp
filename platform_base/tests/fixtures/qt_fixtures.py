"""
Qt-specific fixtures for GUI testing.

This module provides comprehensive Qt fixtures for testing PyQt6 widgets,
signals, dialogs, and complex UI components.

Usage:
    Import these fixtures in your conftest.py or directly in test files.
    Most fixtures work with pytest-qt's qtbot fixture.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generator, TypeVar
from unittest.mock import MagicMock, patch

import pytest
from pytestqt.qtbot import QtBot

if TYPE_CHECKING:
    from PyQt6.QtCore import QObject
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


# Type variable for widget fixtures
T = TypeVar("T", bound="QWidget")


# ============================================
# QApplication Management
# ============================================


@pytest.fixture(scope="session")
def qapp_session() -> Generator["QApplication", None, None]:
    """
    Session-scoped QApplication.
    
    Creates a single QApplication instance for the entire test session.
    This is required because Qt only allows one QApplication instance.
    """
    from PyQt6.QtWidgets import QApplication

    # Check for existing app
    app = QApplication.instance()
    if app is None:
        # Create new app with basic args
        app = QApplication(sys.argv or ["test"])
    
    yield app
    
    # Note: We don't call app.quit() here because it may be needed
    # by other test modules. pytest-qt handles cleanup.


@pytest.fixture
def qapp(qapp_session: "QApplication") -> "QApplication":
    """
    Function-scoped QApplication fixture that uses the session app.
    
    This allows tests to use @pytest.fixture(autouse=True) patterns
    while ensuring there's only one QApplication.
    """
    return qapp_session


# ============================================
# QtBot Extensions
# ============================================


@pytest.fixture
def qtbot_extended(qtbot: QtBot, qapp: "QApplication") -> QtBot:
    """
    Extended QtBot with additional helper methods.
    
    Adds custom functionality to the standard qtbot fixture.
    """
    # Ensure event loop is processed
    qapp.processEvents()
    return qtbot


# ============================================
# Widget Factory Fixtures
# ============================================


@pytest.fixture
def widget_factory(qtbot: QtBot) -> callable:
    """
    Factory fixture for creating and tracking widgets.
    
    Usage:
        def test_my_widget(widget_factory):
            widget = widget_factory(MyWidget, arg1, arg2)
            # widget is automatically tracked by qtbot
    """
    created_widgets: list["QWidget"] = []
    
    def create_widget(widget_class: type[T], *args: Any, **kwargs: Any) -> T:
        widget = widget_class(*args, **kwargs)
        qtbot.addWidget(widget)
        created_widgets.append(widget)
        return widget
    
    yield create_widget
    
    # Cleanup is handled by qtbot.addWidget


@pytest.fixture
def dialog_factory(qtbot: QtBot) -> callable:
    """
    Factory fixture for creating dialog windows.
    
    Automatically handles dialog modality and cleanup.
    """
    from PyQt6.QtWidgets import QDialog
    
    def create_dialog(dialog_class: type[QDialog], *args: Any, **kwargs: Any) -> QDialog:
        dialog = dialog_class(*args, **kwargs)
        qtbot.addWidget(dialog)
        return dialog
    
    return create_dialog


# ============================================
# Signal Testing Fixtures
# ============================================


@pytest.fixture
def signal_blocker(qtbot: QtBot) -> callable:
    """
    Create a signal blocker context manager.
    
    Usage:
        with signal_blocker(widget.valueChanged):
            widget.setValue(10)  # signal is blocked
    """
    @contextmanager
    def block_signal(signal: Any) -> Generator[None, None, None]:
        with qtbot.waitSignal(signal, timeout=0, raising=False):
            yield
    
    return block_signal


@pytest.fixture
def signal_spy_factory(qtbot: QtBot) -> callable:
    """
    Factory for creating signal spies.
    
    Usage:
        spy = signal_spy_factory(my_object.my_signal)
        # do something that emits the signal
        assert spy.count() == 1
    """
    from PyQt6.QtCore import QSignalSpy
    
    def create_spy(signal: Any) -> QSignalSpy:
        return QSignalSpy(signal)
    
    return create_spy


# ============================================
# Mock Fixtures for Platform Base Components
# ============================================


@pytest.fixture
def mock_main_window(qtbot: QtBot) -> MagicMock:
    """
    Create a mock MainWindow for testing components that need it.
    
    This avoids the full initialization of MainWindow which can be slow
    and require many dependencies.
    """
    from PyQt6.QtWidgets import QMainWindow
    
    mock = MagicMock(spec=QMainWindow)
    mock.statusBar.return_value = MagicMock()
    mock.menuBar.return_value = MagicMock()
    mock.centralWidget.return_value = MagicMock()
    
    return mock


@pytest.fixture
def mock_signal_hub_qt() -> MagicMock:
    """
    Create a mock SignalHub with Qt-compatible signals.
    
    The signals are mocked but can be used with connect/emit patterns.
    """
    from PyQt6.QtCore import QObject, pyqtSignal
    
    class MockSignalHub(QObject):
        """Mock signal hub with real Qt signals for testing."""
        
        dataset_loaded = pyqtSignal(str)
        dataset_removed = pyqtSignal(str)
        series_selected = pyqtSignal(list)
        series_deselected = pyqtSignal(list)
        time_window_changed = pyqtSignal(object)
        plot_updated = pyqtSignal()
        operation_started = pyqtSignal(str)
        operation_finished = pyqtSignal(str, object)
        operation_failed = pyqtSignal(str, str)
        progress_updated = pyqtSignal(str, int)
        status_message = pyqtSignal(str)
        error_occurred = pyqtSignal(str)
    
    return MockSignalHub()


@pytest.fixture
def mock_viz_panel(qtbot: QtBot) -> MagicMock:
    """
    Create a mock visualization panel.
    """
    from PyQt6.QtWidgets import QWidget
    
    mock = MagicMock(spec=QWidget)
    mock.update.return_value = None
    mock.repaint.return_value = None
    mock.plot_series = MagicMock()
    mock.clear_plot = MagicMock()
    mock.set_time_window = MagicMock()
    
    return mock


# ============================================
# Real Widget Fixtures (with proper initialization)
# ============================================


@pytest.fixture
def real_signal_hub(qtbot: QtBot) -> Generator[Any, None, None]:
    """
    Create a real SignalHub instance for integration tests.
    """
    try:
        from platform_base.desktop.signal_hub import SignalHub
        hub = SignalHub()
        yield hub
    except ImportError:
        pytest.skip("SignalHub not available")


@pytest.fixture
def real_session_state() -> Generator[Any, None, None]:
    """
    Create a real SessionState instance for integration tests.
    """
    try:
        from platform_base.desktop.session_state import SessionState
        state = SessionState()
        yield state
    except ImportError:
        pytest.skip("SessionState not available")


# ============================================
# Context Managers for Widget Testing
# ============================================


@contextmanager
def widget_shown(widget: "QWidget", qtbot: QtBot) -> Generator["QWidget", None, None]:
    """
    Context manager that shows a widget and ensures it's hidden on exit.
    
    Usage:
        with widget_shown(my_widget, qtbot):
            # widget is visible here
            qtbot.mouseClick(my_widget.button, Qt.LeftButton)
    """
    widget.show()
    qtbot.waitExposed(widget)
    try:
        yield widget
    finally:
        widget.hide()
        widget.close()


@contextmanager
def dialog_exec_mock() -> Generator[None, None, None]:
    """
    Context manager to mock QDialog.exec() to prevent blocking.
    
    Usage:
        with dialog_exec_mock():
            dialog.exec()  # Returns immediately
    """
    with patch("PyQt6.QtWidgets.QDialog.exec", return_value=1):
        yield


# ============================================
# Event Simulation Helpers
# ============================================


@pytest.fixture
def key_event_factory(qtbot: QtBot) -> callable:
    """
    Factory for creating and sending key events.
    """
    from PyQt6.QtCore import Qt
    
    def send_key(widget: "QWidget", key: Qt.Key, modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier) -> None:
        qtbot.keyClick(widget, key, modifiers)
    
    return send_key


@pytest.fixture
def mouse_event_factory(qtbot: QtBot) -> callable:
    """
    Factory for creating and sending mouse events.
    """
    from PyQt6.QtCore import QPoint, Qt
    
    def send_click(
        widget: "QWidget",
        pos: QPoint | None = None,
        button: Qt.MouseButton = Qt.MouseButton.LeftButton
    ) -> None:
        if pos is None:
            pos = widget.rect().center()
        qtbot.mouseClick(widget, button, pos=pos)
    
    return send_click


# ============================================
# Async/Worker Testing Fixtures
# ============================================


@pytest.fixture
def qt_thread_executor(qapp: "QApplication") -> callable:
    """
    Execute a function in a Qt thread and wait for completion.
    
    Useful for testing QThread-based workers.
    """
    from PyQt6.QtCore import QThread
    
    def execute_in_thread(func: callable, *args: Any, timeout: int = 5000) -> Any:
        result = [None]
        exception = [None]
        
        class WorkerThread(QThread):
            def run(self) -> None:
                try:
                    result[0] = func(*args)
                except Exception as e:
                    exception[0] = e
        
        thread = WorkerThread()
        thread.start()
        thread.wait(timeout)
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    return execute_in_thread


# ============================================
# Cleanup Utilities
# ============================================


@pytest.fixture(autouse=True)
def cleanup_qt_objects(qapp: "QApplication") -> Generator[None, None, None]:
    """
    Automatically cleanup Qt objects after each test.
    
    This fixture runs after each test to ensure proper cleanup.
    """
    yield
    
    # Process any pending events
    qapp.processEvents()


# ============================================
# Skip Conditions
# ============================================


def requires_display() -> pytest.MarkDecorator:
    """
    Decorator to skip tests that require a display.
    
    Usage:
        @requires_display()
        def test_window_rendering():
            ...
    """
    import os
    
    skip_reason = "Test requires display"
    condition = os.environ.get("CI") and not os.environ.get("DISPLAY")
    
    return pytest.mark.skipif(condition, reason=skip_reason)


def requires_opengl() -> pytest.MarkDecorator:
    """
    Decorator to skip tests that require OpenGL.
    
    Usage:
        @requires_opengl()
        def test_3d_rendering():
            ...
    """
    try:
        from PyQt6.QtOpenGL import QOpenGLWidget
        has_opengl = True
    except ImportError:
        has_opengl = False
    
    return pytest.mark.skipif(not has_opengl, reason="OpenGL not available")
