"""
Desktop UI Module - Platform Base v2.0

PyQt6 Desktop interface implementation.
"""

from .app import create_application, main
from .main_window import MainWindow
from .session_state import SessionState
from .signal_hub import SignalHub


__all__ = [
    "MainWindow",
    "SessionState",
    "SignalHub",
    "create_application",
    "main",
]
