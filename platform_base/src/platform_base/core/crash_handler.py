"""
Crash Handler - Category 10.3

Sistema de crash reporting automático para diagnóstico em produção.

Features:
- Global exception handler para PyQt6
- Crash dumps com informações de sistema
- Diálogo de crash recovery amigável
- Auto-save de emergência
- Sistema de crash reports locais
- Mecanismo de recuperação pós-crash
"""

from __future__ import annotations

import faulthandler
import json
import os
import platform
import sys
import threading
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class CrashReport:
    """Structured crash report."""
    timestamp: str
    app_version: str
    python_version: str
    os_info: str
    exception_type: str
    exception_message: str
    stack_trace: str
    last_actions: list[str] = field(default_factory=list)
    memory_info: dict[str, Any] = field(default_factory=dict)
    thread_info: list[dict[str, Any]] = field(default_factory=list)
    extra_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'app_version': self.app_version,
            'python_version': self.python_version,
            'os_info': self.os_info,
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'stack_trace': self.stack_trace,
            'last_actions': self.last_actions,
            'memory_info': self.memory_info,
            'thread_info': self.thread_info,
            'extra_info': self.extra_info,
        }

    def to_json(self, sanitize: bool = True) -> str:
        """Convert to JSON string."""
        data = self.to_dict()

        if sanitize:
            # Remove sensitive paths
            data = _sanitize_crash_data(data)

        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    def save(self, path: str | Path, sanitize: bool = True) -> None:
        """Save crash report to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json(sanitize=sanitize))


def _sanitize_crash_data(data: dict[str, Any]) -> dict[str, Any]:
    """Remove sensitive information from crash data."""
    import re

    sensitive_patterns = [
        (re.compile(r'([A-Za-z]:\\Users\\[^\\]+)', re.IGNORECASE), r'[USER_PATH]'),
        (re.compile(r'(/home/[^/]+)', re.IGNORECASE), r'[USER_PATH]'),
        (re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\',\s]+', re.IGNORECASE), r'password: [REDACTED]'),
        (re.compile(r'token["\']?\s*[:=]\s*["\']?[^"\',\s]+', re.IGNORECASE), r'token: [REDACTED]'),
    ]

    def sanitize_value(value: Any) -> Any:
        if isinstance(value, str):
            result = value
            for pattern, replacement in sensitive_patterns:
                result = pattern.sub(replacement, result)
            return result
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(v) for v in value]
        return value

    return sanitize_value(data)


class CrashHandler:
    """
    Global crash handler for the application.
    
    Captures all unhandled exceptions and creates crash reports.
    """

    _instance: CrashHandler | None = None
    _lock = threading.Lock()

    def __new__(cls) -> CrashHandler:
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
        self._crash_dir: Path | None = None
        self._app_version = "unknown"
        self._max_reports = 20
        self._last_actions: list[str] = []
        self._max_actions = 10
        self._emergency_save_callback: Callable[[], bool] | None = None
        self._recovery_callback: Callable[[Path], None] | None = None
        self._original_excepthook: Callable[..., Any] | None = None
        self._qt_app = None
        self._enabled = False

    def initialize(
        self,
        crash_dir: str | Path,
        app_version: str = "unknown",
        max_reports: int = 20,
    ) -> None:
        """
        Initialize the crash handler.
        
        Args:
            crash_dir: Directory for crash reports
            app_version: Application version string
            max_reports: Maximum number of reports to keep
        """
        self._crash_dir = Path(crash_dir)
        self._crash_dir.mkdir(parents=True, exist_ok=True)
        self._app_version = app_version
        self._max_reports = max_reports

        # Enable faulthandler for segfaults
        faulthandler.enable()

        # Save original excepthook
        self._original_excepthook = sys.excepthook

    def enable(self) -> None:
        """Enable global exception handling."""
        if self._enabled:
            return

        # Install Python exception hook
        sys.excepthook = self._handle_exception

        # Install threading exception hook
        threading.excepthook = self._handle_thread_exception

        self._enabled = True

    def disable(self) -> None:
        """Disable global exception handling."""
        if not self._enabled:
            return

        if self._original_excepthook:
            sys.excepthook = self._original_excepthook

        self._enabled = False

    def set_emergency_save(self, callback: Callable[[], bool]) -> None:
        """
        Set callback for emergency save before crash.
        
        Args:
            callback: Function that saves current state, returns True on success
        """
        self._emergency_save_callback = callback

    def set_recovery_callback(self, callback: Callable[[Path], None]) -> None:
        """
        Set callback for recovery dialog.
        
        Args:
            callback: Function that handles recovery (receives crash report path)
        """
        self._recovery_callback = callback

    def record_action(self, action: str) -> None:
        """
        Record a user action for crash context.
        
        Args:
            action: Description of the action
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._last_actions.append(f"[{timestamp}] {action}")

        # Keep only last N actions
        if len(self._last_actions) > self._max_actions:
            self._last_actions = self._last_actions[-self._max_actions:]

    def _get_memory_info(self) -> dict[str, Any]:
        """Get current memory information."""
        if not PSUTIL_AVAILABLE:
            return {}

        try:
            process = psutil.Process()
            memory = process.memory_info()
            vm = psutil.virtual_memory()

            return {
                'process_rss_mb': memory.rss / (1024 * 1024),
                'process_vms_mb': memory.vms / (1024 * 1024),
                'system_total_mb': vm.total / (1024 * 1024),
                'system_available_mb': vm.available / (1024 * 1024),
                'system_percent': vm.percent,
            }
        except Exception:
            return {}

    def _get_thread_info(self) -> list[dict[str, Any]]:
        """Get information about active threads."""
        threads = []
        for thread in threading.enumerate():
            threads.append({
                'name': thread.name,
                'daemon': thread.daemon,
                'alive': thread.is_alive(),
                'ident': thread.ident,
            })
        return threads

    def _create_crash_report(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> CrashReport:
        """Create a crash report from exception info."""
        return CrashReport(
            timestamp=datetime.now().isoformat(),
            app_version=self._app_version,
            python_version=sys.version,
            os_info=f"{platform.system()} {platform.release()} ({platform.machine()})",
            exception_type=exc_type.__name__,
            exception_message=str(exc_value),
            stack_trace=''.join(traceback.format_exception(exc_type, exc_value, exc_tb)),
            last_actions=list(self._last_actions),
            memory_info=self._get_memory_info(),
            thread_info=self._get_thread_info(),
        )

    def _save_crash_report(self, report: CrashReport) -> Path:
        """Save crash report and cleanup old reports."""
        if self._crash_dir is None:
            raise RuntimeError("Crash handler not initialized")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crash_{timestamp}.json"
        filepath = self._crash_dir / filename

        # Save report
        report.save(filepath)

        # Cleanup old reports
        self._cleanup_old_reports()

        return filepath

    def _cleanup_old_reports(self) -> None:
        """Remove old crash reports exceeding max_reports."""
        if self._crash_dir is None:
            return

        reports = sorted(
            self._crash_dir.glob("crash_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for old_report in reports[self._max_reports:]:
            try:
                old_report.unlink()
            except Exception:
                pass

    def _handle_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        """Handle uncaught exception."""
        # Don't handle keyboard interrupt
        if issubclass(exc_type, KeyboardInterrupt):
            if self._original_excepthook:
                self._original_excepthook(exc_type, exc_value, exc_tb)
            return

        try:
            # Emergency save
            if self._emergency_save_callback:
                try:
                    self._emergency_save_callback()
                except Exception:
                    pass

            # Create and save crash report
            report = self._create_crash_report(exc_type, exc_value, exc_tb)

            if self._crash_dir:
                report_path = self._save_crash_report(report)

                # Show recovery dialog if available
                if self._recovery_callback:
                    try:
                        self._recovery_callback(report_path)
                    except Exception:
                        pass

            # Print to stderr for debugging
            print("\n" + "=" * 60, file=sys.stderr)
            print("CRASH REPORT", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(f"Exception: {exc_type.__name__}: {exc_value}", file=sys.stderr)
            print(f"Report saved to: {report_path if self._crash_dir else 'N/A'}", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)

        except Exception as e:
            print(f"Error in crash handler: {e}", file=sys.stderr)

        # Call original excepthook
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_tb)

    def _handle_thread_exception(self, args: threading.ExceptHookArgs) -> None:
        """Handle uncaught exception in thread."""
        self._handle_exception(args.exc_type, args.exc_value, args.exc_traceback)

    def get_crash_reports(self) -> list[Path]:
        """Get list of crash report files."""
        if self._crash_dir is None:
            return []

        return sorted(
            self._crash_dir.glob("crash_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    def get_latest_crash(self) -> CrashReport | None:
        """Get the most recent crash report."""
        reports = self.get_crash_reports()
        if not reports:
            return None

        with open(reports[0], 'r', encoding='utf-8') as f:
            data = json.load(f)

        return CrashReport(
            timestamp=data['timestamp'],
            app_version=data['app_version'],
            python_version=data['python_version'],
            os_info=data['os_info'],
            exception_type=data['exception_type'],
            exception_message=data['exception_message'],
            stack_trace=data['stack_trace'],
            last_actions=data.get('last_actions', []),
            memory_info=data.get('memory_info', {}),
            thread_info=data.get('thread_info', []),
            extra_info=data.get('extra_info', {}),
        )

    def check_for_crash_recovery(self) -> Path | None:
        """
        Check if there's a recent crash to recover from.
        
        Returns:
            Path to crash report if recovery needed, None otherwise
        """
        reports = self.get_crash_reports()
        if not reports:
            return None

        # Check if the most recent crash is less than 5 minutes old
        latest = reports[0]
        age = datetime.now().timestamp() - latest.stat().st_mtime

        if age < 300:  # 5 minutes
            return latest

        return None


# Global instance
_crash_handler: CrashHandler | None = None


def get_crash_handler() -> CrashHandler:
    """Get global crash handler instance."""
    global _crash_handler
    if _crash_handler is None:
        _crash_handler = CrashHandler()
    return _crash_handler


def initialize_crash_handler(
    crash_dir: str | Path,
    app_version: str = "unknown",
    enable: bool = True,
) -> CrashHandler:
    """Initialize and optionally enable crash handler."""
    handler = get_crash_handler()
    handler.initialize(crash_dir, app_version)

    if enable:
        handler.enable()

    return handler


def record_action(action: str) -> None:
    """Convenience function to record user action."""
    get_crash_handler().record_action(action)
