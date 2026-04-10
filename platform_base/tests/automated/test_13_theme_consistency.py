"""Consistencia visual basica entre janelas principais."""

from __future__ import annotations

from PyQt6.QtGui import QPalette

from platform_base.core.dataset_store import DatasetStore
from platform_base.core.signal_hub import SignalHub
from platform_base.core.session_state import SessionState
from platform_base.desktop.dialogs.upload_dialog import UploadDialog
from platform_base.ui.main_window_unified import MainWindow
from platform_base.ui.themes import ThemeMode, get_theme_manager


def test_main_and_upload_dialog_share_theme_window_color(qapp):
    """MainWindow e UploadDialog devem refletir a mesma base de tema."""
    store = DatasetStore()
    state = SessionState(store)
    hub = SignalHub()

    theme_manager = get_theme_manager()
    theme_manager.set_theme(ThemeMode.DARK)

    main = MainWindow(state, hub)
    dialog = UploadDialog(state, hub, main)

    qapp.processEvents()

    main_window_color = main.palette().color(QPalette.ColorRole.Window).name()
    dialog_window_color = dialog.palette().color(QPalette.ColorRole.Window).name()

    assert main_window_color == dialog_window_color
