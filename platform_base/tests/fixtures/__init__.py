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
    # Cleanup
    "cleanup_qt_objects",
    "dialog_exec_mock",
    "dialog_factory",
    # Events
    "key_event_factory",
    # Mocks
    "mock_main_window",
    "mock_signal_hub_qt",
    "mock_viz_panel",
    "mouse_event_factory",
    # QApplication
    "qapp",
    "qapp_session",
    # Threading
    "qt_thread_executor",
    "qtbot_extended",
    "real_session_state",
    # Real components
    "real_signal_hub",
    # Decorators
    "requires_display",
    "requires_opengl",
    # Signals
    "signal_blocker",
    "signal_spy_factory",
    # Factories
    "widget_factory",
    # Context managers
    "widget_shown",
]
