from __future__ import annotations

from typing import Any

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class PlatformError(Exception):
    """Base class for platform errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)


class DataLoadError(PlatformError):
    pass


class SchemaDetectionError(PlatformError):
    pass


class ValidationError(PlatformError):
    pass


class InterpolationError(PlatformError):
    pass


class CalculusError(PlatformError):
    pass


class PluginError(PlatformError):
    pass


class ExportError(PlatformError):
    pass


class CacheError(PlatformError):
    pass


class DownsampleError(PlatformError):
    pass


class ConfigError(PlatformError):
    """Error for configuration issues."""
    pass


class StreamingError(PlatformError):
    """Error for streaming operations."""
    pass


def handle_error(error: PlatformError) -> None:
    logger.error(
        "platform_error",
        error_type=type(error).__name__,
        message=error.message,
        context=error.context,
    )
