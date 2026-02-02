"""
Auto-Save System - Category 10.4

Sistema de backup automático de sessão com versionamento.

Features:
- Auto-save periódico configurável
- Backup incremental
- Versionamento de backups
- Indicador visual de status
- Recuperação de sessão
- Limpeza automática
- Backup antes de operações destrutivas
"""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class BackupInfo:
    """Information about a backup."""
    path: Path
    timestamp: datetime
    version: int
    size_bytes: int
    checksum: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BackupInfo:
        """Create from dictionary."""
        return cls(
            path=Path(data["path"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data["version"],
            size_bytes=data["size_bytes"],
            checksum=data["checksum"],
            description=data.get("description", ""),
        )


class AutoSaveStatus:
    """Status of auto-save system."""

    def __init__(self) -> None:
        self.last_save: datetime | None = None
        self.next_save: datetime | None = None
        self.is_saving = False
        self.last_error: str | None = None
        self.unsaved_changes = False


class AutoSaveManager:
    """
    Manages automatic saving and backup of sessions.
    
    Provides periodic auto-save, versioned backups, and
    recovery capabilities.
    """

    _instance: AutoSaveManager | None = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> AutoSaveManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._backup_dir: Path | None = None
        self._interval_seconds = 300  # 5 minutes
        self._max_versions = 5
        self._retention_days = 7
        self._save_callback: Callable[[Path], bool] | None = None
        self._load_callback: Callable[[Path], bool] | None = None
        self._status_callback: Callable[[AutoSaveStatus], None] | None = None
        self._timer: threading.Timer | None = None
        self._status = AutoSaveStatus()
        self._enabled = False
        self._current_version = 0
        self._lock = threading.Lock()

    def initialize(
        self,
        backup_dir: str | Path,
        interval_minutes: int = 5,
        max_versions: int = 5,
        retention_days: int = 7,
    ) -> None:
        """
        Initialize the auto-save manager.
        
        Args:
            backup_dir: Directory for backups
            interval_minutes: Auto-save interval (1-30 minutes)
            max_versions: Maximum backup versions to keep
            retention_days: Days to retain backups
        """
        self._backup_dir = Path(backup_dir)
        self._backup_dir.mkdir(parents=True, exist_ok=True)

        self._interval_seconds = max(60, min(1800, interval_minutes * 60))
        self._max_versions = max(1, max_versions)
        self._retention_days = max(1, retention_days)

        # Load backup metadata
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load backup metadata from file."""
        if self._backup_dir is None:
            return

        metadata_path = self._backup_dir / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._current_version = data.get("current_version", 0)
            except Exception:
                pass

    def _save_metadata(self) -> None:
        """Save backup metadata to file."""
        if self._backup_dir is None:
            return

        metadata_path = self._backup_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({"current_version": self._current_version}, f)

    def set_save_callback(self, callback: Callable[[Path], bool]) -> None:
        """
        Set callback for saving session.
        
        Args:
            callback: Function that saves to given path, returns True on success
        """
        self._save_callback = callback

    def set_load_callback(self, callback: Callable[[Path], bool]) -> None:
        """
        Set callback for loading session.
        
        Args:
            callback: Function that loads from given path, returns True on success
        """
        self._load_callback = callback

    def set_status_callback(self, callback: Callable[[AutoSaveStatus], None]) -> None:
        """
        Set callback for status updates.
        
        Args:
            callback: Function called when status changes
        """
        self._status_callback = callback

    def set_interval(self, minutes: int) -> None:
        """
        Change auto-save interval.
        
        Args:
            minutes: Interval in minutes (1-30)
        """
        self._interval_seconds = max(60, min(1800, minutes * 60))

        # Restart timer if running
        if self._enabled:
            self.stop()
            self.start()

    def mark_unsaved(self) -> None:
        """Mark that there are unsaved changes."""
        self._status.unsaved_changes = True
        self._notify_status()

    def mark_saved(self) -> None:
        """Mark that changes have been saved."""
        self._status.unsaved_changes = False
        self._notify_status()

    def start(self) -> None:
        """Start auto-save timer."""
        if self._enabled:
            return

        self._enabled = True
        self._schedule_next_save()

    def stop(self) -> None:
        """Stop auto-save timer."""
        self._enabled = False

        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _schedule_next_save(self) -> None:
        """Schedule the next auto-save."""
        if not self._enabled:
            return

        self._status.next_save = datetime.now() + timedelta(seconds=self._interval_seconds)
        self._notify_status()

        self._timer = threading.Timer(self._interval_seconds, self._auto_save)
        self._timer.daemon = True
        self._timer.start()

    def _auto_save(self) -> None:
        """Perform automatic save."""
        if not self._enabled:
            return

        try:
            self.save_backup(description="Auto-save")
        except Exception as e:
            self._status.last_error = str(e)
        finally:
            self._schedule_next_save()

    def _notify_status(self) -> None:
        """Notify status callback."""
        if self._status_callback:
            try:
                self._status_callback(self._status)
            except Exception:
                pass

    def save_backup(
        self,
        description: str = "",
        force: bool = False,
    ) -> BackupInfo | None:
        """
        Save a backup.
        
        Args:
            description: Description of the backup
            force: Force save even if no changes
        
        Returns:
            BackupInfo if saved, None otherwise
        """
        if self._backup_dir is None or self._save_callback is None:
            return None

        if not force and not self._status.unsaved_changes:
            return None

        with self._lock:
            self._status.is_saving = True
            self._notify_status()

            try:
                # Increment version
                self._current_version += 1

                # Create backup filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"backup_{timestamp}_v{self._current_version}.warp"
                backup_path = self._backup_dir / filename

                # Save using callback
                if not self._save_callback(backup_path):
                    self._current_version -= 1
                    return None

                # Calculate checksum
                checksum = self._calculate_checksum(backup_path)

                # Create backup info
                info = BackupInfo(
                    path=backup_path,
                    timestamp=datetime.now(),
                    version=self._current_version,
                    size_bytes=backup_path.stat().st_size,
                    checksum=checksum,
                    description=description,
                )

                # Save info file
                info_path = backup_path.with_suffix(".json")
                with open(info_path, "w", encoding="utf-8") as f:
                    json.dump(info.to_dict(), f, indent=2)

                # Update status
                self._status.last_save = datetime.now()
                self._status.unsaved_changes = False
                self._status.last_error = None

                # Save metadata
                self._save_metadata()

                # Cleanup old backups
                self._cleanup_old_backups()

                return info

            except Exception as e:
                self._status.last_error = str(e)
                raise

            finally:
                self._status.is_saving = False
                self._notify_status()

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _cleanup_old_backups(self) -> None:
        """Remove old backups exceeding limits."""
        if self._backup_dir is None:
            return

        # Get all backups
        backups = self.get_backups()

        # Remove by version count
        for old_backup in backups[self._max_versions:]:
            try:
                old_backup.path.unlink()
                info_path = old_backup.path.with_suffix(".json")
                if info_path.exists():
                    info_path.unlink()
            except Exception:
                pass

        # Remove by age
        cutoff = datetime.now() - timedelta(days=self._retention_days)
        for backup in backups:
            if backup.timestamp < cutoff:
                try:
                    backup.path.unlink()
                    info_path = backup.path.with_suffix(".json")
                    if info_path.exists():
                        info_path.unlink()
                except Exception:
                    pass

    def get_backups(self) -> list[BackupInfo]:
        """
        Get list of available backups.
        
        Returns:
            List of BackupInfo sorted by timestamp (newest first)
        """
        if self._backup_dir is None:
            return []

        backups = []
        for info_path in self._backup_dir.glob("backup_*.json"):
            try:
                with open(info_path, encoding="utf-8") as f:
                    data = json.load(f)
                    backup_path = Path(data["path"])
                    if backup_path.exists():
                        backups.append(BackupInfo.from_dict(data))
            except Exception:
                continue

        return sorted(backups, key=lambda b: b.timestamp, reverse=True)

    def restore_backup(self, backup: BackupInfo | Path) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup: BackupInfo or path to backup file
        
        Returns:
            True if successful
        """
        if self._load_callback is None:
            return False

        path = backup.path if isinstance(backup, BackupInfo) else Path(backup)

        if not path.exists():
            return False

        return self._load_callback(path)

    def get_latest_backup(self) -> BackupInfo | None:
        """Get the most recent backup."""
        backups = self.get_backups()
        return backups[0] if backups else None

    def emergency_save(self) -> bool:
        """
        Perform emergency save (for crash situations).
        
        Returns:
            True if successful
        """
        try:
            result = self.save_backup(description="Emergency save", force=True)
            return result is not None
        except Exception:
            return False

    def save_before_operation(self, operation_name: str) -> BackupInfo | None:
        """
        Save backup before a destructive operation.
        
        Args:
            operation_name: Name of the operation
        
        Returns:
            BackupInfo if saved
        """
        return self.save_backup(
            description=f"Before: {operation_name}",
            force=True,
        )

    @property
    def status(self) -> AutoSaveStatus:
        """Get current auto-save status."""
        return self._status

    @property
    def is_enabled(self) -> bool:
        """Check if auto-save is enabled."""
        return self._enabled


# Global instance
_auto_save_manager: AutoSaveManager | None = None


def get_auto_save_manager() -> AutoSaveManager:
    """Get global auto-save manager instance."""
    global _auto_save_manager
    if _auto_save_manager is None:
        _auto_save_manager = AutoSaveManager()
    return _auto_save_manager


def initialize_auto_save(
    backup_dir: str | Path,
    interval_minutes: int = 5,
    **kwargs: Any,
) -> AutoSaveManager:
    """Initialize and return auto-save manager."""
    manager = get_auto_save_manager()
    manager.initialize(backup_dir, interval_minutes, **kwargs)
    return manager
