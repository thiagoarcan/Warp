"""
Memory Monitor - Category 10.6

Monitors memory usage and provides warnings when approaching limits.

Features:
- Continuous memory monitoring
- Configurable warning thresholds
- Memory estimation before loading files
- Suggestions for memory reduction
- Auto-save trigger on high memory
- Low memory mode
"""

from __future__ import annotations

import gc
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)

# Try to import psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil_not_available", message="Memory monitoring will be limited")


@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a point in time."""
    timestamp: datetime
    used_mb: float
    available_mb: float
    total_mb: float
    percent_used: float
    process_mb: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "used_mb": self.used_mb,
            "available_mb": self.available_mb,
            "total_mb": self.total_mb,
            "percent_used": self.percent_used,
            "process_mb": self.process_mb,
        }


@dataclass
class MemoryWarning:
    """Memory warning event."""
    level: str  # "caution" (60%), "warning" (80%), "critical" (95%)
    percent_used: float
    used_mb: float
    available_mb: float
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level,
            "percent_used": self.percent_used,
            "used_mb": self.used_mb,
            "available_mb": self.available_mb,
            "suggestions": self.suggestions,
        }


class MemoryMonitor:
    """
    Memory usage monitor with warnings and auto-save.
    
    Monitors memory usage and triggers warnings/actions at configurable thresholds.
    """

    _instance: MemoryMonitor | None = None
    _lock = threading.Lock()

    def __new__(cls) -> MemoryMonitor:
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
        self._running = False
        self._monitor_thread: threading.Thread | None = None
        self._callbacks: dict[str, list[Callable[[MemoryWarning], None]]] = {
            "caution": [],
            "warning": [],
            "critical": [],
        }

        # Configuration
        self.caution_threshold = 0.60  # 60%
        self.warning_threshold = 0.80  # 80%
        self.critical_threshold = 0.95  # 95%
        self.hard_limit_mb: float | None = None  # Hard limit in MB (None = use threshold)
        self.check_interval = 5.0  # Check every 5 seconds

        # State
        self.current_snapshot: MemorySnapshot | None = None
        self.last_warning: MemoryWarning | None = None
        self.low_memory_mode = False

        # History
        self.snapshots: list[MemorySnapshot] = []
        self.max_history = 100  # Keep last 100 snapshots

        logger.debug("memory_monitor_initialized")

    def start(self):
        """Start monitoring thread."""
        if self._running:
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        logger.info("memory_monitoring_started")

    def stop(self):
        """Stop monitoring thread."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

        logger.info("memory_monitoring_stopped")

    def get_current_usage(self) -> MemorySnapshot:
        """Get current memory usage."""
        if not PSUTIL_AVAILABLE:
            # Fallback to basic info
            return MemorySnapshot(
                timestamp=datetime.now(),
                used_mb=0.0,
                available_mb=0.0,
                total_mb=0.0,
                percent_used=0.0,
                process_mb=0.0,
            )

        # System memory
        mem = psutil.virtual_memory()

        # Process memory
        process = psutil.Process()
        process_mb = process.memory_info().rss / 1024 / 1024

        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            used_mb=mem.used / 1024 / 1024,
            available_mb=mem.available / 1024 / 1024,
            total_mb=mem.total / 1024 / 1024,
            percent_used=mem.percent / 100.0,
            process_mb=process_mb,
        )

        return snapshot

    def estimate_file_memory(self, file_size_bytes: int) -> float:
        """
        Estimate memory needed to load a file.
        
        Args:
            file_size_bytes: Size of file in bytes
            
        Returns:
            Estimated memory in MB
        """
        # Rule of thumb: pandas DataFrame uses ~2-3x file size
        # Add some overhead for processing
        multiplier = 3.5
        estimated_mb = (file_size_bytes / 1024 / 1024) * multiplier

        return estimated_mb

    def can_load_file(self, file_size_bytes: int) -> tuple[bool, str]:
        """
        Check if file can be loaded without exceeding memory limits.
        
        Args:
            file_size_bytes: Size of file in bytes
            
        Returns:
            Tuple of (can_load, reason)
        """
        estimated_mb = self.estimate_file_memory(file_size_bytes)
        snapshot = self.get_current_usage()

        available_mb = snapshot.available_mb

        if estimated_mb > available_mb:
            return False, (
                f"Insufficient memory: file needs ~{estimated_mb:.1f} MB, "
                f"but only {available_mb:.1f} MB available"
            )

        # Check if loading would exceed warning threshold
        new_percent = (snapshot.used_mb + estimated_mb) / snapshot.total_mb
        if new_percent > self.warning_threshold:
            return False, (
                f"Loading would use {new_percent*100:.1f}% of memory "
                f"(threshold: {self.warning_threshold*100:.0f}%)"
            )

        return True, "OK"

    def add_callback(self, level: str, callback: Callable[[MemoryWarning], None]):
        """Add callback for memory warnings."""
        if level in self._callbacks:
            self._callbacks[level].append(callback)

    def remove_callback(self, level: str, callback: Callable[[MemoryWarning], None]):
        """Remove callback."""
        if level in self._callbacks and callback in self._callbacks[level]:
            self._callbacks[level].remove(callback)

    def force_garbage_collection(self):
        """Force garbage collection."""
        collected = gc.collect()
        logger.debug("garbage_collected", objects=collected)
        return collected

    def enable_low_memory_mode(self):
        """Enable low memory mode."""
        self.low_memory_mode = True

        # Force GC
        self.force_garbage_collection()

        logger.info("low_memory_mode_enabled")

    def disable_low_memory_mode(self):
        """Disable low memory mode."""
        self.low_memory_mode = False
        logger.info("low_memory_mode_disabled")

    def get_memory_reduction_suggestions(self, snapshot: MemorySnapshot) -> list[str]:
        """Get suggestions for reducing memory usage."""
        suggestions = []

        if snapshot.percent_used > self.caution_threshold:
            suggestions.append("Close unused datasets to free memory")

        if snapshot.percent_used > self.warning_threshold:
            suggestions.append("Reduce data decimation for visualization")
            suggestions.append("Save session and restart application")

        if snapshot.percent_used > self.critical_threshold:
            suggestions.append("CRITICAL: Close datasets immediately")
            suggestions.append("Auto-save will be triggered")

        if not self.low_memory_mode:
            suggestions.append("Enable Low Memory Mode in settings")

        return suggestions

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                snapshot = self.get_current_usage()
                self.current_snapshot = snapshot

                # Add to history
                self.snapshots.append(snapshot)
                if len(self.snapshots) > self.max_history:
                    self.snapshots.pop(0)

                # Check thresholds
                self._check_thresholds(snapshot)

            except Exception as e:
                logger.exception("memory_monitoring_error", error=str(e))

            time.sleep(self.check_interval)

    def _check_thresholds(self, snapshot: MemorySnapshot):
        """Check if thresholds are exceeded."""
        percent = snapshot.percent_used

        # Determine warning level
        level = None
        threshold = 0.0

        if percent >= self.critical_threshold:
            level = "critical"
            threshold = self.critical_threshold
        elif percent >= self.warning_threshold:
            level = "warning"
            threshold = self.warning_threshold
        elif percent >= self.caution_threshold:
            level = "caution"
            threshold = self.caution_threshold

        # If threshold exceeded, create warning
        if level:
            # Don't spam warnings - only if level changed or 30s passed
            if (
                self.last_warning is None
                or self.last_warning.level != level
                or (datetime.now() - self.current_snapshot.timestamp).seconds > 30
            ):
                warning = MemoryWarning(
                    level=level,
                    percent_used=percent,
                    used_mb=snapshot.used_mb,
                    available_mb=snapshot.available_mb,
                    suggestions=self.get_memory_reduction_suggestions(snapshot),
                )

                self.last_warning = warning

                # Log warning
                logger.warning(
                    f"memory_{level}",
                    percent=f"{percent*100:.1f}%",
                    used_mb=snapshot.used_mb,
                    available_mb=snapshot.available_mb,
                )

                # Call callbacks
                for callback in self._callbacks.get(level, []):
                    try:
                        callback(warning)
                    except Exception as e:
                        logger.exception("memory_callback_error", error=str(e))

                # Auto-enable low memory mode at warning
                if level == "warning" and not self.low_memory_mode:
                    self.enable_low_memory_mode()

                # Force GC at critical
                if level == "critical":
                    self.force_garbage_collection()


# Global instance
_memory_monitor: MemoryMonitor | None = None


def get_memory_monitor() -> MemoryMonitor:
    """Get global memory monitor instance."""
    global _memory_monitor
    if _memory_monitor is None:
        _memory_monitor = MemoryMonitor()
    return _memory_monitor


def start_memory_monitoring():
    """Start memory monitoring."""
    get_memory_monitor().start()


def stop_memory_monitoring():
    """Stop memory monitoring."""
    get_memory_monitor().stop()
