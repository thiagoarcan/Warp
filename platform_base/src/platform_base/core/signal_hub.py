"""
Signal Hub - Re-export from desktop module.

This module provides backward compatibility by re-exporting SignalHub
from the desktop module.
"""

from platform_base.desktop.signal_hub import SignalHub

__all__ = [
    "SignalHub",
]
