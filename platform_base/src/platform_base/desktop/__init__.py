"""
Desktop UI Module - Platform Base v2.0

PyQt6 Desktop interface implementation.
"""

from importlib import import_module

from .app import create_application, main
from .session_state import SessionState
from .signal_hub import SignalHub


__all__ = [
    "MainWindow",
    "panels",
    "SessionState",
    "SignalHub",
    "create_application",
    "main",
]


def __getattr__(name: str):
    if name == "panels":
        return import_module("platform_base.desktop.panels")
    if name == "MainWindow":
        from .main_window import MainWindow
        return MainWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
