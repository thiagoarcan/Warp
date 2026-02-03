"""
Session State - Re-export from desktop module.

This module provides backward compatibility by re-exporting SessionState
from the desktop module.
"""

from platform_base.desktop.session_state import (
    ProcessingState,
    SelectionState,
    SessionState,
    StreamingState,
    UIState,
    ViewState,
)

__all__ = [
    "SessionState",
    "SelectionState",
    "ViewState",
    "ProcessingState",
    "StreamingState",
    "UIState",
]
