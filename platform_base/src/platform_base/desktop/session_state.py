"""
Session State - Compatibility wrapper.

Canonical ownership moved to platform_base.core.session_state.
This module re-exports symbols for backward compatibility.
"""

from platform_base.core.session_state import (
    ProcessingState,
    SelectionState,
    SessionState,
    StreamingState,
    UIState,
    ViewState,
)


__all__ = [
    "ProcessingState",
    "SelectionState",
    "SessionState",
    "StreamingState",
    "UIState",
    "ViewState",
]
