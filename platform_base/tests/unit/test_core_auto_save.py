"""
Tests for auto_save module - Category 10.4.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from platform_base.core.auto_save import AutoSaveManager, AutoSaveStatus, BackupInfo


class TestBackupInfo:
    """Tests for BackupInfo dataclass."""
    
    def test_create_backup_info(self, tmp_path):
        """Test creating BackupInfo."""
        path = tmp_path / "backup.json"
        info = BackupInfo(
            path=path,
            timestamp=datetime(2026, 2, 1, 12, 0, 0),
            version=1,
            size_bytes=1024,
            checksum="abc123",
            description="Test backup",
        )
        
        assert info.path == path
        assert info.version == 1
        assert info.size_bytes == 1024
        assert info.checksum == "abc123"
        assert info.description == "Test backup"
    
    def test_backup_info_to_dict(self, tmp_path):
        """Test converting BackupInfo to dict."""
        path = tmp_path / "backup.json"
        info = BackupInfo(
            path=path,
            timestamp=datetime(2026, 2, 1, 12, 0, 0),
            version=1,
            size_bytes=1024,
            checksum="abc123",
        )
        
        data = info.to_dict()
        
        assert data['path'] == str(path)
        assert data['version'] == 1
        assert data['size_bytes'] == 1024
        assert data['checksum'] == "abc123"
        assert '2026-02-01' in data['timestamp']
    
    def test_backup_info_from_dict(self, tmp_path):
        """Test creating BackupInfo from dict."""
        data = {
            'path': str(tmp_path / "backup.json"),
            'timestamp': '2026-02-01T12:00:00',
            'version': 2,
            'size_bytes': 2048,
            'checksum': 'def456',
            'description': 'Restored backup',
        }
        
        info = BackupInfo.from_dict(data)
        
        assert info.version == 2
        assert info.size_bytes == 2048
        assert info.checksum == 'def456'
        assert info.description == 'Restored backup'
    
    def test_backup_info_from_dict_no_description(self, tmp_path):
        """Test BackupInfo from dict without description."""
        data = {
            'path': str(tmp_path / "backup.json"),
            'timestamp': '2026-02-01T12:00:00',
            'version': 1,
            'size_bytes': 1024,
            'checksum': 'abc123',
        }
        
        info = BackupInfo.from_dict(data)
        assert info.description == ''


class TestAutoSaveStatus:
    """Tests for AutoSaveStatus class."""
    
    def test_default_status(self):
        """Test default status values."""
        status = AutoSaveStatus()
        
        assert status.last_save is None
        assert status.next_save is None
        assert status.is_saving is False
        assert status.last_error is None
        assert status.unsaved_changes is False
    
    def test_status_modification(self):
        """Test modifying status."""
        status = AutoSaveStatus()
        
        status.last_save = datetime.now()
        status.is_saving = True
        status.unsaved_changes = True
        
        assert status.last_save is not None
        assert status.is_saving is True
        assert status.unsaved_changes is True


class TestAutoSaveManager:
    """Tests for AutoSaveManager class."""
    
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        AutoSaveManager._instance = None
        yield
        AutoSaveManager._instance = None
    
    def test_singleton_pattern(self):
        """Test that AutoSaveManager is a singleton."""
        manager1 = AutoSaveManager()
        manager2 = AutoSaveManager()
        
        assert manager1 is manager2
    
    def test_initialize(self, tmp_path):
        """Test initialization."""
        manager = AutoSaveManager()
        manager.initialize(
            backup_dir=tmp_path / "backups",
            interval_minutes=10,
            max_versions=3,
            retention_days=5,
        )
        
        assert manager._backup_dir == tmp_path / "backups"
        assert manager._backup_dir.exists()
        assert manager._interval_seconds == 600  # 10 minutes
        assert manager._max_versions == 3
        assert manager._retention_days == 5
    
    def test_initialize_clamps_interval(self, tmp_path):
        """Test that interval is clamped to valid range."""
        manager = AutoSaveManager()
        
        # Too short
        manager.initialize(tmp_path / "backups", interval_minutes=0)
        assert manager._interval_seconds >= 60
        
        # Reset singleton
        AutoSaveManager._instance = None
        
        # Too long
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups2", interval_minutes=60)
        assert manager._interval_seconds <= 1800
    
    def test_set_save_callback(self, tmp_path):
        """Test setting save callback."""
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups")
        
        callback = Mock(return_value=True)
        manager.set_save_callback(callback)
        
        assert manager._save_callback is callback
    
    def test_set_load_callback(self, tmp_path):
        """Test setting load callback."""
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups")
        
        callback = Mock(return_value=True)
        manager.set_load_callback(callback)
        
        assert manager._load_callback is callback
    
    def test_set_status_callback(self, tmp_path):
        """Test setting status callback."""
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups")
        
        callback = Mock()
        manager.set_status_callback(callback)
        
        assert manager._status_callback is callback
    
    def test_set_interval(self, tmp_path):
        """Test changing interval."""
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups")
        
        manager.set_interval(15)
        assert manager._interval_seconds == 900
    
    def test_metadata_save_load(self, tmp_path):
        """Test metadata persistence."""
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups")
        
        manager._current_version = 5
        manager._save_metadata()
        
        # Reset and reload
        AutoSaveManager._instance = None
        manager2 = AutoSaveManager()
        manager2.initialize(tmp_path / "backups")
        
        assert manager2._current_version == 5
    
    def test_status_property(self, tmp_path):
        """Test status property."""
        manager = AutoSaveManager()
        manager.initialize(tmp_path / "backups")
        
        status = manager._status
        
        assert isinstance(status, AutoSaveStatus)
