"""
Tests for crash_handler module - Category 10.3.
"""
import json
import sys
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from platform_base.core.crash_handler import (
    CrashHandler,
    CrashReport,
    _sanitize_crash_data,
)


class TestCrashReport:
    """Tests for CrashReport dataclass."""
    
    def test_create_crash_report(self):
        """Test creating CrashReport."""
        report = CrashReport(
            timestamp="2026-02-01T12:00:00",
            app_version="1.0.0",
            python_version="3.12.0",
            os_info="Windows 10",
            exception_type="ValueError",
            exception_message="Test error",
            stack_trace="Traceback...",
        )
        
        assert report.timestamp == "2026-02-01T12:00:00"
        assert report.app_version == "1.0.0"
        assert report.exception_type == "ValueError"
        assert report.exception_message == "Test error"
    
    def test_crash_report_to_dict(self):
        """Test converting CrashReport to dict."""
        report = CrashReport(
            timestamp="2026-02-01T12:00:00",
            app_version="1.0.0",
            python_version="3.12.0",
            os_info="Windows 10",
            exception_type="ValueError",
            exception_message="Test error",
            stack_trace="Traceback...",
            last_actions=["action1", "action2"],
            memory_info={"used": 1024},
        )
        
        data = report.to_dict()
        
        assert data['timestamp'] == "2026-02-01T12:00:00"
        assert data['app_version'] == "1.0.0"
        assert data['last_actions'] == ["action1", "action2"]
        assert data['memory_info'] == {"used": 1024}
    
    def test_crash_report_to_json(self):
        """Test converting CrashReport to JSON."""
        report = CrashReport(
            timestamp="2026-02-01T12:00:00",
            app_version="1.0.0",
            python_version="3.12.0",
            os_info="Windows 10",
            exception_type="ValueError",
            exception_message="Test error",
            stack_trace="Traceback...",
        )
        
        json_str = report.to_json()
        data = json.loads(json_str)
        
        assert data['timestamp'] == "2026-02-01T12:00:00"
        assert data['app_version'] == "1.0.0"
    
    def test_crash_report_save(self, tmp_path):
        """Test saving CrashReport to file."""
        report = CrashReport(
            timestamp="2026-02-01T12:00:00",
            app_version="1.0.0",
            python_version="3.12.0",
            os_info="Windows 10",
            exception_type="ValueError",
            exception_message="Test error",
            stack_trace="Traceback...",
        )
        
        path = tmp_path / "crash_report.json"
        report.save(path)
        
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data['app_version'] == "1.0.0"
    
    def test_crash_report_with_extra_info(self):
        """Test CrashReport with extra info."""
        report = CrashReport(
            timestamp="2026-02-01T12:00:00",
            app_version="1.0.0",
            python_version="3.12.0",
            os_info="Windows 10",
            exception_type="ValueError",
            exception_message="Test error",
            stack_trace="Traceback...",
            extra_info={"custom_field": "value"},
        )
        
        data = report.to_dict()
        assert data['extra_info'] == {"custom_field": "value"}


class TestSanitizeCrashData:
    """Tests for _sanitize_crash_data function."""
    
    def test_sanitize_user_path_windows(self):
        """Test sanitizing Windows user paths."""
        data = {"message": "Error at C:\\Users\\john\\project\\file.py"}
        result = _sanitize_crash_data(data)
        
        assert "john" not in result['message']
        assert "[USER_PATH]" in result['message']
    
    def test_sanitize_user_path_linux(self):
        """Test sanitizing Linux user paths."""
        data = {"message": "Error at /home/john/project/file.py"}
        result = _sanitize_crash_data(data)
        
        assert "john" not in result['message']
        assert "[USER_PATH]" in result['message']
    
    def test_sanitize_password(self):
        """Test sanitizing passwords."""
        data = {"message": "password: secret123"}
        result = _sanitize_crash_data(data)
        
        assert "secret123" not in result['message']
    
    def test_sanitize_token(self):
        """Test sanitizing tokens."""
        data = {"message": "token=abc123xyz"}
        result = _sanitize_crash_data(data)
        
        assert "abc123xyz" not in result['message']
    
    def test_sanitize_nested_dict(self):
        """Test sanitizing nested dictionary."""
        data = {
            "outer": {
                "inner": {"path": "C:\\Users\\john\\file.py"}
            }
        }
        result = _sanitize_crash_data(data)
        
        assert "john" not in str(result)
    
    def test_sanitize_list(self):
        """Test sanitizing list values."""
        data = {
            "paths": [
                "C:\\Users\\john\\file1.py",
                "C:\\Users\\jane\\file2.py",
            ]
        }
        result = _sanitize_crash_data(data)
        
        assert "john" not in str(result)
        assert "jane" not in str(result)


class TestCrashHandler:
    """Tests for CrashHandler class."""
    
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        CrashHandler._instance = None
        yield
        CrashHandler._instance = None
    
    def test_singleton_pattern(self):
        """Test that CrashHandler is a singleton."""
        handler1 = CrashHandler()
        handler2 = CrashHandler()
        
        assert handler1 is handler2
    
    def test_initialize(self, tmp_path):
        """Test initialization."""
        handler = CrashHandler()
        handler.initialize(
            crash_dir=tmp_path / "crashes",
            app_version="1.0.0",
            max_reports=10,
        )
        
        assert handler._crash_dir == tmp_path / "crashes"
        assert handler._crash_dir.exists()
        assert handler._app_version == "1.0.0"
        assert handler._max_reports == 10
    
    def test_enable_disable(self, tmp_path):
        """Test enabling and disabling handler."""
        handler = CrashHandler()
        handler.initialize(tmp_path / "crashes")
        
        original_hook = sys.excepthook
        
        handler.enable()
        assert handler._enabled is True
        assert sys.excepthook != original_hook
        
        handler.disable()
        assert handler._enabled is False
    
    def test_set_emergency_save(self, tmp_path):
        """Test setting emergency save callback."""
        handler = CrashHandler()
        handler.initialize(tmp_path / "crashes")
        
        callback = Mock(return_value=True)
        handler.set_emergency_save(callback)
        
        assert handler._emergency_save_callback is callback
    
    def test_default_values(self):
        """Test default values."""
        handler = CrashHandler()
        
        assert handler._app_version == "unknown"
        assert handler._max_reports == 20
        assert handler._enabled is False
    
    def test_last_actions_tracking(self, tmp_path):
        """Test that last actions are tracked."""
        handler = CrashHandler()
        handler.initialize(tmp_path / "crashes")
        
        assert handler._last_actions == []
        assert handler._max_actions == 10
