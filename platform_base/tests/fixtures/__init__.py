"""
Test fixtures for Platform Base.

This package contains reusable fixtures for testing.
"""

from tests.fixtures.qt_fixtures import (
    cleanup_qt_objects,
    dialog_exec_mock,
    dialog_factory,
    key_event_factory,
    mock_main_window,
    mock_signal_hub_qt,
    mock_viz_panel,
    mouse_event_factory,
    qapp,
    qapp_session,
    qt_thread_executor,
    qtbot_extended,
    real_session_state,
    real_signal_hub,
    requires_display,
    requires_opengl,
    signal_blocker,
    signal_spy_factory,
    widget_factory,
    widget_shown,
)

__all__ = [
    # QApplication
    "qapp",
    "qapp_session",
    "qtbot_extended",
    # Factories
    "widget_factory",
    "dialog_factory",
    "signal_spy_factory",
    # Signals
    "signal_blocker",
    # Mocks
    "mock_main_window",
    "mock_signal_hub_qt",
    "mock_viz_panel",
    # Real components
    "real_signal_hub",
    "real_session_state",
    # Context managers
    "widget_shown",
    "dialog_exec_mock",
    # Events
    "key_event_factory",
    "mouse_event_factory",
    # Threading
    "qt_thread_executor",
    # Cleanup
    "cleanup_qt_objects",
    # Decorators
    "requires_display",
    "requires_opengl",
]
