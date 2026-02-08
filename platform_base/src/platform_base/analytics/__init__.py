"""
Analytics module for Platform Base.

Provides telemetry and metrics collection capabilities.
"""

from platform_base.analytics.telemetry import (
    TelemetryConfig,
    TelemetryEvent,
    TelemetryEventType,
    TelemetryManager,
    TelemetryStats,
    get_telemetry_manager,
    track_error,
    track_feature,
    track_operation,
)


__all__ = [
    "TelemetryConfig",
    "TelemetryEvent",
    "TelemetryEventType",
    "TelemetryManager",
    "TelemetryStats",
    "get_telemetry_manager",
    "track_error",
    "track_feature",
    "track_operation",
]
