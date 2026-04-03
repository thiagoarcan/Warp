"""
Signal Hub - Compatibility wrapper.

Canonical ownership moved to platform_base.core.signal_hub.
This module re-exports symbols for backward compatibility.
"""

from platform_base.core.signal_hub import SignalHub


__all__ = [
    "SignalHub",
]
