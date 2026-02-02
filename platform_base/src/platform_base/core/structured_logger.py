"""
Structured Logger - Category 10.1

Logger estruturado com JSON output, correlation_id, rotation,
e todas as funcionalidades necessárias para debugging em produção.

Features:
- JSON structured output
- Correlation ID para rastrear operações
- Log levels dinâmicos configuráveis em runtime
- Context managers para logging automático
- Sanitização de dados sensíveis
- Rotating file handler com compressão
- Métricas de timing automáticas
- Log aggregation para múltiplas sessões
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import re
import shutil
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable, Generator


# Thread-local storage for correlation IDs
_correlation_id = threading.local()


def get_correlation_id() -> str:
    """Get the current correlation ID, or create a new one."""
    if not hasattr(_correlation_id, "value") or _correlation_id.value is None:
        _correlation_id.value = str(uuid.uuid4())[:8]
    return _correlation_id.value


def set_correlation_id(cid: str | None = None) -> str:
    """Set the correlation ID. If None, generates a new one."""
    _correlation_id.value = cid or str(uuid.uuid4())[:8]
    return _correlation_id.value


def clear_correlation_id() -> None:
    """Clear the correlation ID."""
    _correlation_id.value = None


# Sensitive data patterns for sanitization
SENSITIVE_PATTERNS = [
    (re.compile(r"([A-Za-z]:\\Users\\[^\\]+)", re.IGNORECASE), r"[USER_PATH]"),
    (re.compile(r"(/home/[^/]+)", re.IGNORECASE), r"[USER_PATH]"),
    (re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\',\s]+', re.IGNORECASE), r"password: [REDACTED]"),
    (re.compile(r'token["\']?\s*[:=]\s*["\']?[^"\',\s]+', re.IGNORECASE), r"token: [REDACTED]"),
    (re.compile(r'api_key["\']?\s*[:=]\s*["\']?[^"\',\s]+', re.IGNORECASE), r"api_key: [REDACTED]"),
    (re.compile(r'secret["\']?\s*[:=]\s*["\']?[^"\',\s]+', re.IGNORECASE), r"secret: [REDACTED]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), r"[EMAIL]"),
]


def sanitize_message(message: str) -> str:
    """Remove sensitive data from log messages."""
    result = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively sanitize sensitive data in a dictionary."""
    result = {}
    sensitive_keys = {"password", "token", "api_key", "secret", "credential", "auth"}

    for key, value in data.items():
        key_lower = key.lower()
        if any(s in key_lower for s in sensitive_keys):
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value)
        elif isinstance(value, str):
            result[key] = sanitize_message(value)
        elif isinstance(value, list):
            result[key] = [
                sanitize_dict(v) if isinstance(v, dict)
                else sanitize_message(v) if isinstance(v, str)
                else v
                for v in value
            ]
        else:
            result[key] = value
    return result


@dataclass
class LogRecord:
    """Structured log record with all required fields."""
    timestamp: str
    level: str
    message: str
    correlation_id: str
    component: str
    duration_ms: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "component": self.component,
        }
        if self.duration_ms is not None:
            data["duration_ms"] = self.duration_ms
        if self.extra:
            data.update(self.extra)
        return json.dumps(data, ensure_ascii=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "component": self.component,
        }
        if self.duration_ms is not None:
            data["duration_ms"] = self.duration_ms
        if self.extra:
            data.update(self.extra)
        return data


class CompressedRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler that compresses old log files."""

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 10 * 1024 * 1024,  # 10MB
        backupCount: int = 5,
        encoding: str | None = "utf-8",
        delay: bool = False,
    ):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)

    def doRollover(self) -> None:
        """Do rollover and compress the old file."""
        if self.stream:
            self.stream.close()
            self.stream = None

        # Rotate files
        for i in range(self.backupCount - 1, 0, -1):
            sfn = self.rotation_filename(f"{self.baseFilename}.{i}.gz")
            dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}.gz")
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)

        # Compress the current file
        dfn = self.rotation_filename(f"{self.baseFilename}.1.gz")
        if os.path.exists(dfn):
            os.remove(dfn)

        if os.path.exists(self.baseFilename):
            with open(self.baseFilename, "rb") as f_in, gzip.open(dfn, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(self.baseFilename)

        if not self.delay:
            self.stream = self._open()


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, sanitize: bool = True):
        super().__init__()
        self.sanitize = sanitize

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        message = record.getMessage()
        if self.sanitize:
            message = sanitize_message(message)

        log_record = LogRecord(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=record.levelname,
            message=message,
            correlation_id=get_correlation_id(),
            component=record.name,
            duration_ms=getattr(record, "duration_ms", None),
            extra=sanitize_dict(getattr(record, "extra", {})) if self.sanitize
                  else getattr(record, "extra", {}),
        )

        return log_record.to_json()


class ConsoleFormatter(logging.Formatter):
    """Colored console formatter."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        color = self.COLORS.get(record.levelname, "")
        correlation = get_correlation_id()
        duration = getattr(record, "duration_ms", None)

        msg = f"{color}[{record.levelname}]{self.RESET} "
        msg += f"\033[90m[{correlation}]\033[0m "
        msg += f"{record.name}: {record.getMessage()}"

        if duration is not None:
            msg += f" \033[90m({duration:.2f}ms)\033[0m"

        return msg


class StructuredLogger:
    """
    Main structured logger class.
    
    Provides JSON structured logging with correlation IDs,
    automatic timing, and sanitization.
    """

    _instance: StructuredLogger | None = None
    _lock = threading.Lock()

    def __new__(cls) -> StructuredLogger:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._level = logging.INFO
        self._handlers: list[logging.Handler] = []
        self._loggers: dict[str, logging.Logger] = {}
        self._log_file: Path | None = None
        self._json_mode = True
        self._sanitize = True
        self._slow_threshold_ms = 100.0
        self._listeners: list[Callable[[LogRecord], None]] = []

    def configure(
        self,
        level: str = "INFO",
        log_dir: str | Path | None = None,
        json_mode: bool = True,
        sanitize: bool = True,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        slow_threshold_ms: float = 100.0,
    ) -> None:
        """
        Configure the structured logger.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            json_mode: If True, output JSON format
            sanitize: If True, sanitize sensitive data
            max_bytes: Max size per log file
            backup_count: Number of backup files to keep
            slow_threshold_ms: Threshold for slow operation warnings
        """
        self._level = getattr(logging, level.upper(), logging.INFO)
        self._json_mode = json_mode
        self._sanitize = sanitize
        self._slow_threshold_ms = slow_threshold_ms

        # Clear existing handlers
        for handler in self._handlers:
            handler.close()
        self._handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if json_mode:
            console_handler.setFormatter(JSONFormatter(sanitize=sanitize))
        else:
            console_handler.setFormatter(ConsoleFormatter())
        console_handler.setLevel(self._level)
        self._handlers.append(console_handler)

        # File handler
        if log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            self._log_file = log_path / "platform_base.log"

            file_handler = CompressedRotatingFileHandler(
                str(self._log_file),
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler.setFormatter(JSONFormatter(sanitize=sanitize))
            file_handler.setLevel(self._level)
            self._handlers.append(file_handler)

        # Update all loggers
        for logger in self._loggers.values():
            logger.handlers = []
            for handler in self._handlers:
                logger.addHandler(handler)
            logger.setLevel(self._level)

    def set_level(self, level: str) -> None:
        """Change log level at runtime."""
        self._level = getattr(logging, level.upper(), logging.INFO)
        for handler in self._handlers:
            handler.setLevel(self._level)
        for logger in self._loggers.values():
            logger.setLevel(self._level)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger."""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.handlers = []
            for handler in self._handlers:
                logger.addHandler(handler)
            logger.setLevel(self._level)
            logger.propagate = False
            self._loggers[name] = logger
        return self._loggers[name]

    def add_listener(self, callback: Callable[[LogRecord], None]) -> None:
        """Add a listener for log events (for LogViewer)."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[LogRecord], None]) -> None:
        """Remove a log listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self, record: LogRecord) -> None:
        """Notify all listeners of a log event."""
        for listener in self._listeners:
            try:
                listener(record)
            except Exception:
                pass  # Don't let listener errors affect logging

    @contextmanager
    def operation(
        self,
        name: str,
        component: str = "operation",
        log_start: bool = True,
        log_end: bool = True,
        **extra: Any,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Context manager for logging operations with timing.
        
        Args:
            name: Operation name
            component: Component name
            log_start: Log when operation starts
            log_end: Log when operation ends
            **extra: Additional fields to log
        
        Yields:
            Context dict that can be updated with additional info
        """
        context: dict[str, Any] = {"operation": name, **extra}
        logger = self.get_logger(component)
        correlation = set_correlation_id()

        start_time = time.perf_counter()

        if log_start:
            logger.info(f"Starting: {name}", extra={"extra": context})

        try:
            yield context

            duration_ms = (time.perf_counter() - start_time) * 1000

            if log_end:
                log_record = logging.LogRecord(
                    name=component,
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"Completed: {name}",
                    args=(),
                    exc_info=None,
                )
                log_record.duration_ms = duration_ms
                log_record.extra = context
                logger.handle(log_record)

                if duration_ms > self._slow_threshold_ms:
                    logger.warning(
                        f"Slow operation: {name} took {duration_ms:.2f}ms",
                        extra={"extra": {"threshold": self._slow_threshold_ms, **context}},
                    )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            context["error"] = str(e)
            context["error_type"] = type(e).__name__

            log_record = logging.LogRecord(
                name=component,
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg=f"Failed: {name}",
                args=(),
                exc_info=True,
            )
            log_record.duration_ms = duration_ms
            log_record.extra = context
            logger.handle(log_record)
            raise

    @contextmanager
    def correlation_scope(self, correlation_id: str | None = None) -> Generator[str, None, None]:
        """
        Context manager for correlation ID scope.
        
        Args:
            correlation_id: Optional specific correlation ID
        
        Yields:
            The correlation ID being used
        """
        old_id = getattr(_correlation_id, "value", None)
        new_id = set_correlation_id(correlation_id)
        try:
            yield new_id
        finally:
            _correlation_id.value = old_id

    def export_logs(
        self,
        output_path: str | Path,
        format: str = "json",
        level_filter: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """
        Export logs to file.
        
        Args:
            output_path: Output file path
            format: Output format (json, csv)
            level_filter: Filter by level
            start_date: Filter by start date
            end_date: Filter by end date
        
        Returns:
            Number of records exported
        """
        if self._log_file is None or not self._log_file.exists():
            return 0

        output_path = Path(output_path)
        records = []

        # Read main log file
        with open(self._log_file, encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())

                    # Apply filters
                    if level_filter and record.get("level") != level_filter.upper():
                        continue

                    if start_date:
                        record_date = datetime.fromisoformat(record["timestamp"].rstrip("Z"))
                        if record_date < start_date:
                            continue

                    if end_date:
                        record_date = datetime.fromisoformat(record["timestamp"].rstrip("Z"))
                        if record_date > end_date:
                            continue

                    records.append(record)
                except json.JSONDecodeError:
                    continue

        # Write output
        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
        elif format == "csv":
            import csv
            if records:
                with open(output_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

        return len(records)


# Global instance
_structured_logger: StructuredLogger | None = None


def get_structured_logger() -> StructuredLogger:
    """Get the global structured logger instance."""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredLogger()
    return _structured_logger


def configure_logging(
    level: str = "INFO",
    log_dir: str | Path | None = None,
    json_mode: bool = True,
    **kwargs: Any,
) -> StructuredLogger:
    """Configure and return the structured logger."""
    logger = get_structured_logger()
    logger.configure(level=level, log_dir=log_dir, json_mode=json_mode, **kwargs)
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger from the structured logger."""
    return get_structured_logger().get_logger(name)


@contextmanager
def log_operation(
    name: str,
    component: str = "operation",
    **extra: Any,
) -> Generator[dict[str, Any], None, None]:
    """Convenience function for operation logging."""
    with get_structured_logger().operation(name, component, **extra) as ctx:
        yield ctx


@contextmanager
def correlation_scope(correlation_id: str | None = None) -> Generator[str, None, None]:
    """Convenience function for correlation scope."""
    with get_structured_logger().correlation_scope(correlation_id) as cid:
        yield cid
