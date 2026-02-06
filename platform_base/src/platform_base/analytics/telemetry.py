"""
Telemetry System - Category 10.2

Sistema de telemetria opt-in para coleta de métricas de uso.
Completamente opcional, com consentimento explícito do usuário.

Features:
- Opt-in com consentimento explícito
- Coleta de métricas de uso (features, frequência)
- Tracking de performance (tempos, tamanhos)
- Dashboard local de estatísticas
- Export de telemetria
- Configuração granular
- Data retention policy
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class TelemetryEventType(Enum):
    """Types of telemetry events."""
    FEATURE_USED = auto()
    OPERATION_COMPLETED = auto()
    ERROR_OCCURRED = auto()
    FILE_LOADED = auto()
    FILE_EXPORTED = auto()
    SESSION_START = auto()
    SESSION_END = auto()
    PERFORMANCE_METRIC = auto()


@dataclass
class TelemetryEvent:
    """A single telemetry event."""
    event_type: TelemetryEventType
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)
    session_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type.name,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'session_id': self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TelemetryEvent:
        """Create from dictionary."""
        return cls(
            event_type=TelemetryEventType[data['event_type']],
            timestamp=datetime.fromisoformat(data['timestamp']),
            data=data.get('data', {}),
            session_id=data.get('session_id', ''),
        )


@dataclass
class TelemetryConfig:
    """Configuration for telemetry collection."""
    enabled: bool = False
    collect_feature_usage: bool = True
    collect_performance: bool = True
    collect_errors: bool = True
    collect_file_stats: bool = True
    retention_days: int = 30

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'collect_feature_usage': self.collect_feature_usage,
            'collect_performance': self.collect_performance,
            'collect_errors': self.collect_errors,
            'collect_file_stats': self.collect_file_stats,
            'retention_days': self.retention_days,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TelemetryConfig:
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TelemetryStats:
    """Aggregated telemetry statistics."""
    total_sessions: int = 0
    total_events: int = 0
    features_used: dict[str, int] = field(default_factory=dict)
    avg_operation_time: dict[str, float] = field(default_factory=dict)
    error_counts: dict[str, int] = field(default_factory=dict)
    files_loaded: int = 0
    files_exported: int = 0
    total_usage_time_hours: float = 0.0


class TelemetryManager:
    """
    Main telemetry manager class.
    
    Handles opt-in telemetry collection, storage, and analysis.
    All data is stored locally by default.
    """

    _instance: TelemetryManager | None = None
    _lock = threading.Lock()

    def __new__(cls) -> TelemetryManager:
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
        self._config = TelemetryConfig()
        self._db_path: Path | None = None
        self._session_id = ""
        self._session_start: datetime | None = None
        self._conn: sqlite3.Connection | None = None
        self._listeners: list[Callable[[TelemetryEvent], None]] = []
        self._lock = threading.Lock()

    def initialize(self, data_dir: str | Path) -> None:
        """
        Initialize telemetry storage.
        
        Args:
            data_dir: Directory for telemetry data
        """
        data_path = Path(data_dir)
        data_path.mkdir(parents=True, exist_ok=True)

        self._db_path = data_path / "telemetry.db"
        self._config_path = data_path / "telemetry_config.json"

        # Load config
        if self._config_path.exists():
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = TelemetryConfig.from_dict(json.load(f))

        # Initialize database
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database."""
        if self._db_path is None:
            return

        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)
        """)

        self._conn.commit()

    def _save_config(self) -> None:
        """Save configuration to file."""
        if self._config_path:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)

    @property
    def config(self) -> TelemetryConfig:
        """Get current configuration."""
        return self._config

    @property
    def is_enabled(self) -> bool:
        """Check if telemetry is enabled."""
        return self._config.enabled

    def set_consent(self, enabled: bool) -> None:
        """
        Set user consent for telemetry.
        
        Args:
            enabled: Whether user consents to telemetry
        """
        self._config.enabled = enabled
        self._save_config()

    def configure(
        self,
        collect_feature_usage: bool | None = None,
        collect_performance: bool | None = None,
        collect_errors: bool | None = None,
        collect_file_stats: bool | None = None,
        retention_days: int | None = None,
    ) -> None:
        """
        Configure telemetry collection options.
        
        Args:
            collect_feature_usage: Collect feature usage data
            collect_performance: Collect performance metrics
            collect_errors: Collect error information
            collect_file_stats: Collect file statistics
            retention_days: Days to retain data
        """
        if collect_feature_usage is not None:
            self._config.collect_feature_usage = collect_feature_usage
        if collect_performance is not None:
            self._config.collect_performance = collect_performance
        if collect_errors is not None:
            self._config.collect_errors = collect_errors
        if collect_file_stats is not None:
            self._config.collect_file_stats = collect_file_stats
        if retention_days is not None:
            self._config.retention_days = retention_days

        self._save_config()

    def start_session(self) -> str:
        """
        Start a new telemetry session.
        
        Returns:
            Session ID
        """
        self._session_id = hashlib.sha256(
            f"{time.time()}-{id(self)}".encode()
        ).hexdigest()[:16]
        self._session_start = datetime.now()

        self.track_event(TelemetryEventType.SESSION_START)
        return self._session_id

    def end_session(self) -> None:
        """End the current session."""
        if self._session_start:
            duration = (datetime.now() - self._session_start).total_seconds()
            self.track_event(
                TelemetryEventType.SESSION_END,
                {'duration_seconds': duration}
            )

        self._session_id = ""
        self._session_start = None

    def track_event(
        self,
        event_type: TelemetryEventType,
        data: dict[str, Any] | None = None,
    ) -> None:
        """
        Track a telemetry event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if not self._config.enabled:
            return

        # Check if this type of event should be collected
        if event_type == TelemetryEventType.FEATURE_USED:
            if not self._config.collect_feature_usage:
                return
        elif event_type == TelemetryEventType.PERFORMANCE_METRIC:
            if not self._config.collect_performance:
                return
        elif event_type == TelemetryEventType.ERROR_OCCURRED:
            if not self._config.collect_errors:
                return
        elif event_type in (TelemetryEventType.FILE_LOADED, TelemetryEventType.FILE_EXPORTED):
            if not self._config.collect_file_stats:
                return

        event = TelemetryEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            data=data or {},
            session_id=self._session_id,
        )

        # Store event
        self._store_event(event)

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass

    def _store_event(self, event: TelemetryEvent) -> None:
        """Store event in database."""
        if self._conn is None:
            return

        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (event_type, timestamp, session_id, data)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event.event_type.name,
                    event.timestamp.isoformat(),
                    event.session_id,
                    json.dumps(event.data),
                )
            )
            self._conn.commit()

    def track_feature(self, feature_name: str, **extra: Any) -> None:
        """
        Track feature usage.
        
        Args:
            feature_name: Name of the feature
            **extra: Additional data
        """
        self.track_event(
            TelemetryEventType.FEATURE_USED,
            {'feature': feature_name, **extra}
        )

    def track_operation(
        self,
        operation_name: str,
        duration_ms: float,
        success: bool = True,
        **extra: Any,
    ) -> None:
        """
        Track operation completion.
        
        Args:
            operation_name: Name of the operation
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            **extra: Additional data
        """
        self.track_event(
            TelemetryEventType.OPERATION_COMPLETED,
            {
                'operation': operation_name,
                'duration_ms': duration_ms,
                'success': success,
                **extra,
            }
        )

    def track_error(
        self,
        error_type: str,
        error_message: str,
        **extra: Any,
    ) -> None:
        """
        Track error occurrence (anonymized).
        
        Args:
            error_type: Type of error
            error_message: Error message (will be hashed)
            **extra: Additional data
        """
        # Hash error message for anonymity
        message_hash = hashlib.sha256(error_message.encode()).hexdigest()[:8]

        self.track_event(
            TelemetryEventType.ERROR_OCCURRED,
            {
                'error_type': error_type,
                'message_hash': message_hash,
                **extra,
            }
        )

    def track_file_operation(
        self,
        operation: str,  # 'load' or 'export'
        file_format: str,
        file_size_bytes: int,
        duration_ms: float,
    ) -> None:
        """
        Track file operations.
        
        Args:
            operation: 'load' or 'export'
            file_format: File format (csv, xlsx, etc.)
            file_size_bytes: File size
            duration_ms: Duration in milliseconds
        """
        event_type = (
            TelemetryEventType.FILE_LOADED
            if operation == 'load'
            else TelemetryEventType.FILE_EXPORTED
        )

        self.track_event(
            event_type,
            {
                'format': file_format,
                'size_bytes': file_size_bytes,
                'duration_ms': duration_ms,
            }
        )

    def get_stats(self, days: int = 30) -> TelemetryStats:
        """
        Get aggregated statistics.
        
        Args:
            days: Number of days to include
        
        Returns:
            Aggregated statistics
        """
        if self._conn is None:
            return TelemetryStats()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self._conn.cursor()

        stats = TelemetryStats()

        # Total sessions
        cursor.execute(
            "SELECT COUNT(DISTINCT session_id) FROM events WHERE timestamp > ?",
            (cutoff,)
        )
        stats.total_sessions = cursor.fetchone()[0]

        # Total events
        cursor.execute(
            "SELECT COUNT(*) FROM events WHERE timestamp > ?",
            (cutoff,)
        )
        stats.total_events = cursor.fetchone()[0]

        # Features used
        cursor.execute(
            """
            SELECT data FROM events 
            WHERE event_type = 'FEATURE_USED' AND timestamp > ?
            """,
            (cutoff,)
        )
        features = Counter()
        for row in cursor.fetchall():
            data = json.loads(row[0])
            features[data.get('feature', 'unknown')] += 1
        stats.features_used = dict(features)

        # Average operation times
        cursor.execute(
            """
            SELECT data FROM events 
            WHERE event_type = 'OPERATION_COMPLETED' AND timestamp > ?
            """,
            (cutoff,)
        )
        operation_times: dict[str, list[float]] = {}
        for row in cursor.fetchall():
            data = json.loads(row[0])
            op = data.get('operation', 'unknown')
            duration = data.get('duration_ms', 0)
            if op not in operation_times:
                operation_times[op] = []
            operation_times[op].append(duration)

        stats.avg_operation_time = {
            op: sum(times) / len(times)
            for op, times in operation_times.items()
            if times
        }

        # Error counts
        cursor.execute(
            """
            SELECT data FROM events 
            WHERE event_type = 'ERROR_OCCURRED' AND timestamp > ?
            """,
            (cutoff,)
        )
        errors = Counter()
        for row in cursor.fetchall():
            data = json.loads(row[0])
            errors[data.get('error_type', 'unknown')] += 1
        stats.error_counts = dict(errors)

        # File counts
        cursor.execute(
            "SELECT COUNT(*) FROM events WHERE event_type = 'FILE_LOADED' AND timestamp > ?",
            (cutoff,)
        )
        stats.files_loaded = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM events WHERE event_type = 'FILE_EXPORTED' AND timestamp > ?",
            (cutoff,)
        )
        stats.files_exported = cursor.fetchone()[0]

        # Total usage time
        cursor.execute(
            """
            SELECT data FROM events 
            WHERE event_type = 'SESSION_END' AND timestamp > ?
            """,
            (cutoff,)
        )
        total_seconds = 0.0
        for row in cursor.fetchall():
            data = json.loads(row[0])
            total_seconds += data.get('duration_seconds', 0)
        stats.total_usage_time_hours = total_seconds / 3600

        return stats

    def cleanup_old_data(self) -> int:
        """
        Remove data older than retention period.
        
        Returns:
            Number of records deleted
        """
        if self._conn is None:
            return 0

        cutoff = (
            datetime.now() - timedelta(days=self._config.retention_days)
        ).isoformat()

        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                "DELETE FROM events WHERE timestamp < ?",
                (cutoff,)
            )
            deleted = cursor.rowcount
            self._conn.commit()

        return deleted

    def export_data(
        self,
        output_path: str | Path,
        format: str = "json",
        days: int | None = None,
    ) -> int:
        """
        Export telemetry data.
        
        Args:
            output_path: Output file path
            format: Output format (json, csv)
            days: Days to include (None = all)
        
        Returns:
            Number of records exported
        """
        if self._conn is None:
            return 0

        output_path = Path(output_path)
        cursor = self._conn.cursor()

        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute(
                "SELECT * FROM events WHERE timestamp > ? ORDER BY timestamp",
                (cutoff,)
            )
        else:
            cursor.execute("SELECT * FROM events ORDER BY timestamp")

        rows = cursor.fetchall()

        if format == "json":
            data = []
            for row in rows:
                data.append({
                    'id': row[0],
                    'event_type': row[1],
                    'timestamp': row[2],
                    'session_id': row[3],
                    'data': json.loads(row[4]) if row[4] else {},
                })

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format == "csv":
            import csv
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'event_type', 'timestamp', 'session_id', 'data'])
                for row in rows:
                    writer.writerow(row)

        return len(rows)

    def add_listener(self, callback: Callable[[TelemetryEvent], None]) -> None:
        """Add event listener."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[TelemetryEvent], None]) -> None:
        """Remove event listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# Global instance
_telemetry_manager: TelemetryManager | None = None


def get_telemetry_manager() -> TelemetryManager:
    """Get global telemetry manager instance."""
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
    return _telemetry_manager


def track_feature(feature_name: str, **extra: Any) -> None:
    """Convenience function to track feature usage."""
    get_telemetry_manager().track_feature(feature_name, **extra)


def track_operation(
    operation_name: str,
    duration_ms: float,
    success: bool = True,
    **extra: Any,
) -> None:
    """Convenience function to track operation."""
    get_telemetry_manager().track_operation(
        operation_name, duration_ms, success, **extra
    )


def track_error(error_type: str, error_message: str, **extra: Any) -> None:
    """Convenience function to track error."""
    get_telemetry_manager().track_error(error_type, error_message, **extra)
