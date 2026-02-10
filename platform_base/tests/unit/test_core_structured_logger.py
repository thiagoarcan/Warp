"""
Tests for structured_logger module - Category 10.1.
"""
import gzip
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from platform_base.core.structured_logger import (
    SENSITIVE_PATTERNS,
    CompressedRotatingFileHandler,
    JSONFormatter,
    LogRecord,
    clear_correlation_id,
    get_correlation_id,
    sanitize_dict,
    sanitize_message,
    set_correlation_id,
)


class TestCorrelationId:
    """Tests for correlation ID functions."""
    
    def setup_method(self):
        """Clear correlation ID before each test."""
        clear_correlation_id()
    
    def test_get_correlation_id_creates_new(self):
        """Test that get_correlation_id creates new ID if none exists."""
        cid = get_correlation_id()
        
        assert cid is not None
        assert len(cid) == 8
    
    def test_get_correlation_id_returns_same(self):
        """Test that get_correlation_id returns same ID on subsequent calls."""
        cid1 = get_correlation_id()
        cid2 = get_correlation_id()
        
        assert cid1 == cid2
    
    def test_set_correlation_id(self):
        """Test setting correlation ID."""
        set_correlation_id("test1234")
        cid = get_correlation_id()
        
        assert cid == "test1234"
    
    def test_set_correlation_id_generates_if_none(self):
        """Test set_correlation_id generates ID if None."""
        cid = set_correlation_id(None)
        
        assert cid is not None
        assert len(cid) == 8
    
    def test_clear_correlation_id(self):
        """Test clearing correlation ID."""
        set_correlation_id("test1234")
        clear_correlation_id()
        
        # Should generate new one
        cid = get_correlation_id()
        assert cid != "test1234"


class TestSanitizeMessage:
    """Tests for sanitize_message function."""
    
    def test_sanitize_windows_path(self):
        """Test sanitizing Windows user path."""
        msg = "Error at C:\\Users\\john\\project\\file.py"
        result = sanitize_message(msg)
        
        assert "john" not in result
        assert "[USER_PATH]" in result
    
    def test_sanitize_linux_path(self):
        """Test sanitizing Linux user path."""
        msg = "Error at /home/john/project/file.py"
        result = sanitize_message(msg)
        
        assert "john" not in result
        assert "[USER_PATH]" in result
    
    def test_sanitize_password(self):
        """Test sanitizing password."""
        msg = "password: secret123"
        result = sanitize_message(msg)
        
        assert "secret123" not in result
        assert "[REDACTED]" in result
    
    def test_sanitize_token(self):
        """Test sanitizing token."""
        msg = "token=abc123xyz"
        result = sanitize_message(msg)
        
        assert "abc123xyz" not in result
    
    def test_sanitize_api_key(self):
        """Test sanitizing API key."""
        msg = "api_key: sk-abcdef123456"
        result = sanitize_message(msg)
        
        assert "sk-abcdef123456" not in result
    
    def test_sanitize_email(self):
        """Test sanitizing email."""
        msg = "Contact: user@example.com"
        result = sanitize_message(msg)
        
        assert "user@example.com" not in result
        assert "[EMAIL]" in result
    
    def test_no_sanitization_needed(self):
        """Test message that doesn't need sanitization."""
        msg = "This is a normal log message"
        result = sanitize_message(msg)
        
        assert result == msg


class TestSanitizeDict:
    """Tests for sanitize_dict function."""
    
    def test_sanitize_sensitive_keys(self):
        """Test sanitizing sensitive keys."""
        data = {
            "password": "secret123",
            "token": "abc123",
            "api_key": "key123",
            "normal": "value",
        }
        result = sanitize_dict(data)
        
        assert result["password"] == "[REDACTED]"
        assert result["token"] == "[REDACTED]"
        assert result["api_key"] == "[REDACTED]"
        assert result["normal"] == "value"
    
    def test_sanitize_nested_dict(self):
        """Test sanitizing nested dictionary."""
        data = {
            "config": {
                "password": "secret",
                "name": "test",
            }
        }
        result = sanitize_dict(data)
        
        assert result["config"]["password"] == "[REDACTED]"
        assert result["config"]["name"] == "test"
    
    def test_sanitize_list_in_dict(self):
        """Test sanitizing list values in dict."""
        data = {
            "paths": [
                "C:\\Users\\john\\file.py",
                "normal_path.py",
            ]
        }
        result = sanitize_dict(data)
        
        assert "john" not in str(result)
    
    def test_sanitize_mixed_types(self):
        """Test sanitizing mixed types."""
        data = {
            "string": "C:\\Users\\john\\file.py",
            "number": 42,
            "list": ["item1", "item2"],
            "dict": {"key": "value"},
        }
        result = sanitize_dict(data)
        
        assert "john" not in result["string"]
        assert result["number"] == 42


class TestLogRecord:
    """Tests for LogRecord dataclass."""
    
    def test_create_log_record(self):
        """Test creating LogRecord."""
        record = LogRecord(
            timestamp="2026-02-01T12:00:00",
            level="INFO",
            message="Test message",
            correlation_id="abc123",
            component="test_component",
        )
        
        assert record.timestamp == "2026-02-01T12:00:00"
        assert record.level == "INFO"
        assert record.message == "Test message"
    
    def test_log_record_to_json(self):
        """Test converting LogRecord to JSON."""
        record = LogRecord(
            timestamp="2026-02-01T12:00:00",
            level="INFO",
            message="Test message",
            correlation_id="abc123",
            component="test_component",
            duration_ms=100.5,
        )
        
        json_str = record.to_json()
        data = json.loads(json_str)
        
        assert data["timestamp"] == "2026-02-01T12:00:00"
        assert data["level"] == "INFO"
        assert data["duration_ms"] == 100.5
    
    def test_log_record_to_dict(self):
        """Test converting LogRecord to dict."""
        record = LogRecord(
            timestamp="2026-02-01T12:00:00",
            level="INFO",
            message="Test message",
            correlation_id="abc123",
            component="test_component",
            extra={"custom": "value"},
        )
        
        data = record.to_dict()
        
        assert data["timestamp"] == "2026-02-01T12:00:00"
        assert data["custom"] == "value"
    
    def test_log_record_without_duration(self):
        """Test LogRecord without duration."""
        record = LogRecord(
            timestamp="2026-02-01T12:00:00",
            level="INFO",
            message="Test message",
            correlation_id="abc123",
            component="test_component",
        )
        
        data = record.to_dict()
        assert "duration_ms" not in data


class TestCompressedRotatingFileHandler:
    """Tests for CompressedRotatingFileHandler class."""
    
    def test_create_handler(self, tmp_path):
        """Test creating handler."""
        log_file = tmp_path / "test.log"
        handler = CompressedRotatingFileHandler(
            str(log_file),
            maxBytes=1024,
            backupCount=3,
        )
        
        assert handler.maxBytes == 1024
        assert handler.backupCount == 3
    
    def test_handler_writes_to_file(self, tmp_path):
        """Test handler writes to file."""
        log_file = tmp_path / "test.log"
        handler = CompressedRotatingFileHandler(
            str(log_file),
            maxBytes=10240,
            backupCount=3,
        )
        
        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        logger.info("Test message")
        handler.flush()
        
        assert log_file.exists()
        logger.removeHandler(handler)
        handler.close()


class TestJSONFormatter:
    """Tests for JSONFormatter class."""
    
    def test_create_formatter(self):
        """Test creating formatter."""
        formatter = JSONFormatter(sanitize=True)
        
        assert formatter.sanitize is True
    
    def test_formatter_no_sanitize(self):
        """Test formatter without sanitization."""
        formatter = JSONFormatter(sanitize=False)
        
        assert formatter.sanitize is False


class TestSensitivePatterns:
    """Tests for sensitive patterns."""
    
    def test_patterns_exist(self):
        """Test that patterns are defined."""
        assert len(SENSITIVE_PATTERNS) > 0
    
    def test_patterns_are_tuples(self):
        """Test that patterns are tuples."""
        for pattern in SENSITIVE_PATTERNS:
            assert isinstance(pattern, tuple)
            assert len(pattern) == 2
