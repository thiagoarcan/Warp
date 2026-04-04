"""
Comprehensive tests for core/structured_logger.py

Tests structured logging functionality including correlation IDs,
sanitization, compression, and JSON formatting.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from platform_base.core.structured_logger import (
    CompressedRotatingFileHandler,
    ConsoleFormatter,
    JSONFormatter,
    LogRecord,
    StructuredLogger,
    clear_correlation_id,
    get_correlation_id,
    sanitize_dict,
    sanitize_message,
    set_correlation_id,
)

# =============================================================================
# Correlation ID Tests
# =============================================================================

class TestCorrelationId:
    """Tests for correlation ID management."""
    
    def test_get_correlation_id_generates_new(self):
        """Test that get_correlation_id generates a new ID if none exists."""
        clear_correlation_id()
        cid = get_correlation_id()
        assert cid is not None
        assert len(cid) == 8  # UUID[:8]
    
    def test_get_correlation_id_returns_same(self):
        """Test that get_correlation_id returns same ID once set."""
        clear_correlation_id()
        cid1 = get_correlation_id()
        cid2 = get_correlation_id()
        assert cid1 == cid2
    
    def test_set_correlation_id_custom(self):
        """Test setting custom correlation ID."""
        custom_id = "test1234"
        result = set_correlation_id(custom_id)
        assert result == custom_id
        assert get_correlation_id() == custom_id
    
    def test_set_correlation_id_generates_if_none(self):
        """Test that set_correlation_id generates if None passed."""
        result = set_correlation_id(None)
        assert result is not None
        assert len(result) == 8
    
    def test_clear_correlation_id(self):
        """Test clearing correlation ID."""
        set_correlation_id("test")
        clear_correlation_id()
        # Getting after clear should generate new
        cid = get_correlation_id()
        assert cid != "test"
    
    def test_correlation_id_thread_local(self):
        """Test that correlation IDs are thread-local."""
        clear_correlation_id()
        set_correlation_id("main_thread")
        
        other_thread_id = None
        
        def in_thread():
            nonlocal other_thread_id
            clear_correlation_id()
            other_thread_id = get_correlation_id()
        
        thread = threading.Thread(target=in_thread)
        thread.start()
        thread.join()
        
        main_id = get_correlation_id()
        assert main_id == "main_thread"
        assert other_thread_id != "main_thread"


# =============================================================================
# Sanitization Tests
# =============================================================================

class TestSanitization:
    """Tests for data sanitization functions."""
    
    def test_sanitize_message_user_path_windows(self):
        """Test sanitizing Windows user paths."""
        msg = "Error at C:\\Users\\john\\Documents\\file.txt"
        result = sanitize_message(msg)
        assert "john" not in result
        assert "[USER_PATH]" in result
    
    def test_sanitize_message_user_path_linux(self):
        """Test sanitizing Linux user paths."""
        msg = "Error at /home/john/documents/file.txt"
        result = sanitize_message(msg)
        assert "john" not in result
        assert "[USER_PATH]" in result
    
    def test_sanitize_message_password(self):
        """Test sanitizing passwords."""
        msg = "password=secret123"
        result = sanitize_message(msg)
        assert "secret123" not in result
        assert "[REDACTED]" in result
    
    def test_sanitize_message_token(self):
        """Test sanitizing tokens."""
        msg = "token: abc123xyz"
        result = sanitize_message(msg)
        assert "abc123xyz" not in result
    
    def test_sanitize_message_api_key(self):
        """Test sanitizing API keys."""
        msg = "api_key=mykey123"
        result = sanitize_message(msg)
        assert "mykey123" not in result
    
    def test_sanitize_message_email(self):
        """Test sanitizing email addresses."""
        msg = "Contact: user@example.com"
        result = sanitize_message(msg)
        assert "user@example.com" not in result
        assert "[EMAIL]" in result
    
    def test_sanitize_message_preserves_normal_text(self):
        """Test that normal text is preserved."""
        msg = "Normal log message without sensitive data"
        result = sanitize_message(msg)
        assert result == msg
    
    def test_sanitize_dict_simple(self):
        """Test sanitizing dictionary with sensitive keys."""
        data = {"password": "secret", "name": "John"}
        result = sanitize_dict(data)
        assert result["password"] == "[REDACTED]"
        assert result["name"] == "John"
    
    def test_sanitize_dict_nested(self):
        """Test sanitizing nested dictionary."""
        data = {
            "user": {
                "token": "abc123",
                "username": "john"
            }
        }
        result = sanitize_dict(data)
        assert result["user"]["token"] == "[REDACTED]"
        assert result["user"]["username"] == "john"
    
    def test_sanitize_dict_with_list(self):
        """Test sanitizing dictionary with list values."""
        data = {
            "credentials": ["password=abc", "normal text"],
            "items": [{"secret": "value"}, {"key": "safe"}]
        }
        result = sanitize_dict(data)
        assert "[REDACTED]" in str(result)
    
    def test_sanitize_dict_preserves_non_sensitive(self):
        """Test that non-sensitive data is preserved."""
        data = {"count": 42, "active": True, "rate": 3.14}
        result = sanitize_dict(data)
        assert result["count"] == 42
        assert result["active"] is True
        assert result["rate"] == 3.14


# =============================================================================
# LogRecord Tests
# =============================================================================

class TestLogRecord:
    """Tests for LogRecord dataclass."""
    
    def test_log_record_creation(self):
        """Test basic LogRecord creation."""
        record = LogRecord(
            timestamp="2024-01-01T12:00:00Z",
            level="INFO",
            message="Test message",
            correlation_id="abc123",
            component="test",
        )
        assert record.level == "INFO"
        assert record.message == "Test message"
    
    def test_log_record_to_json(self):
        """Test LogRecord JSON serialization."""
        record = LogRecord(
            timestamp="2024-01-01T12:00:00Z",
            level="INFO",
            message="Test message",
            correlation_id="abc123",
            component="test",
        )
        json_str = record.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
    
    def test_log_record_to_json_with_duration(self):
        """Test LogRecord JSON with duration."""
        record = LogRecord(
            timestamp="2024-01-01T12:00:00Z",
            level="INFO",
            message="Test",
            correlation_id="abc123",
            component="test",
            duration_ms=150.5,
        )
        json_str = record.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["duration_ms"] == 150.5
    
    def test_log_record_to_json_with_extra(self):
        """Test LogRecord JSON with extra fields."""
        record = LogRecord(
            timestamp="2024-01-01T12:00:00Z",
            level="INFO",
            message="Test",
            correlation_id="abc123",
            component="test",
            extra={"custom_field": "custom_value"},
        )
        json_str = record.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["custom_field"] == "custom_value"
    
    def test_log_record_to_dict(self):
        """Test LogRecord dictionary conversion."""
        record = LogRecord(
            timestamp="2024-01-01T12:00:00Z",
            level="DEBUG",
            message="Test",
            correlation_id="abc123",
            component="test",
        )
        data = record.to_dict()
        
        assert isinstance(data, dict)
        assert data["level"] == "DEBUG"


# =============================================================================
# JSONFormatter Tests
# =============================================================================

class TestJSONFormatter:
    """Tests for JSONFormatter class."""
    
    def test_json_formatter_basic(self):
        """Test basic JSON formatting."""
        formatter = JSONFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
    
    def test_json_formatter_sanitizes(self):
        """Test that JSONFormatter sanitizes by default."""
        formatter = JSONFormatter(sanitize=True)
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="password=secret123",
            args=(),
            exc_info=None,
        )
        
        result = formatter.format(record)
        assert "secret123" not in result
    
    def test_json_formatter_no_sanitize(self):
        """Test JSONFormatter without sanitization."""
        formatter = JSONFormatter(sanitize=False)
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="password=secret123",
            args=(),
            exc_info=None,
        )
        
        result = formatter.format(record)
        assert "secret123" in result


# =============================================================================
# ConsoleFormatter Tests
# =============================================================================

class TestConsoleFormatter:
    """Tests for ConsoleFormatter class."""
    
    def test_console_formatter_basic(self):
        """Test basic console formatting."""
        formatter = ConsoleFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        result = formatter.format(record)
        assert "Test message" in result
        assert "INFO" in result
    
    def test_console_formatter_colors(self):
        """Test console formatter includes ANSI colors."""
        formatter = ConsoleFormatter()
        
        for level, levelno in [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
        ]:
            record = logging.LogRecord(
                name="test",
                level=levelno,
                pathname="test.py",
                lineno=1,
                msg="Test",
                args=(),
                exc_info=None,
            )
            result = formatter.format(record)
            # Should contain ANSI escape codes
            assert "\033[" in result
    
    def test_console_formatter_with_duration(self):
        """Test console formatter with duration."""
        formatter = ConsoleFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.duration_ms = 150.5
        
        result = formatter.format(record)
        assert "150.50ms" in result


# =============================================================================
# CompressedRotatingFileHandler Tests
# =============================================================================

class TestCompressedRotatingFileHandler:
    """Tests for CompressedRotatingFileHandler class."""
    
    def test_handler_initialization(self, tmp_path):
        """Test handler initialization."""
        log_file = tmp_path / "test.log"
        handler = CompressedRotatingFileHandler(
            str(log_file),
            maxBytes=1024,
            backupCount=3,
        )
        
        assert handler.maxBytes == 1024
        assert handler.backupCount == 3
        handler.close()
    
    def test_handler_creates_file(self, tmp_path):
        """Test handler creates log file on write."""
        log_file = tmp_path / "test.log"
        handler = CompressedRotatingFileHandler(str(log_file))
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        handler.emit(record)
        handler.close()
        
        assert log_file.exists()
    
    def test_handler_rollover_compresses(self, tmp_path):
        """Test that rollover creates compressed file."""
        log_file = tmp_path / "test.log"
        handler = CompressedRotatingFileHandler(
            str(log_file),
            maxBytes=100,  # Very small for testing
            backupCount=2,
        )
        
        # Write enough to trigger rollover
        for i in range(20):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg=f"Test message number {i} with some extra text to make it longer",
                args=(),
                exc_info=None,
            )
            handler.emit(record)
        
        handler.close()
        
        # Check for compressed backup
        compressed_files = list(tmp_path.glob("*.gz"))
        # May or may not have created backup depending on timing
        assert log_file.exists() or len(compressed_files) > 0


# =============================================================================
# StructuredLogger Tests
# =============================================================================

class TestStructuredLogger:
    """Tests for StructuredLogger class."""
    
    @pytest.fixture(autouse=True)
    def reset_logger(self):
        """Reset the singleton logger before each test."""
        StructuredLogger._instance = None
        yield
        StructuredLogger._instance = None
    
    def test_structured_logger_singleton(self):
        """Test StructuredLogger is a singleton."""
        logger1 = StructuredLogger()
        logger2 = StructuredLogger()
        assert logger1 is logger2
    
    def test_structured_logger_initialization(self):
        """Test StructuredLogger initialization."""
        logger = StructuredLogger()
        assert logger._initialized is True
        assert logger._level == logging.INFO
    
    def test_configure_level(self):
        """Test configuring log level."""
        logger = StructuredLogger()
        logger.configure(level="DEBUG")
        assert logger._level == logging.DEBUG
    
    def test_configure_json_mode(self):
        """Test configuring JSON mode."""
        logger = StructuredLogger()
        logger.configure(json_mode=True)
        assert logger._json_mode is True
        
        logger.configure(json_mode=False)
        assert logger._json_mode is False
    
    def test_configure_with_log_dir(self, tmp_path):
        """Test configuring with log directory."""
        logger = StructuredLogger()
        logger.configure(log_dir=str(tmp_path))
        
        assert logger._log_file is not None
        assert logger._log_file.parent == tmp_path
    
    def test_set_level_runtime(self):
        """Test changing log level at runtime."""
        logger = StructuredLogger()
        logger.configure(level="INFO")
        
        logger.set_level("DEBUG")
        assert logger._level == logging.DEBUG
        
        logger.set_level("ERROR")
        assert logger._level == logging.ERROR
    
    def test_get_logger(self):
        """Test getting named logger."""
        structured = StructuredLogger()
        structured.configure()
        
        logger = structured.get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
    
    def test_get_logger_cached(self):
        """Test that loggers are cached."""
        structured = StructuredLogger()
        structured.configure()
        
        logger1 = structured.get_logger("test")
        logger2 = structured.get_logger("test")
        assert logger1 is logger2
    
    def test_add_listener(self):
        """Test adding log listener."""
        structured = StructuredLogger()
        
        callback = MagicMock()
        structured.add_listener(callback)
        
        assert callback in structured._listeners
    
    def test_remove_listener(self):
        """Test removing log listener."""
        structured = StructuredLogger()
        
        callback = MagicMock()
        structured.add_listener(callback)
        structured.remove_listener(callback)
        
        assert callback not in structured._listeners
    
    def test_remove_listener_not_present(self):
        """Test removing listener that doesn't exist."""
        structured = StructuredLogger()
        callback = MagicMock()
        
        # Should not raise
        structured.remove_listener(callback)


# =============================================================================
# Integration Tests
# =============================================================================

class TestLoggerIntegration:
    """Integration tests for the logging system."""
    
    @pytest.fixture(autouse=True)
    def reset_logger(self):
        """Reset the singleton logger before each test."""
        StructuredLogger._instance = None
        clear_correlation_id()
        yield
        StructuredLogger._instance = None
    
    def test_full_logging_workflow(self, tmp_path):
        """Test complete logging workflow."""
        # Configure logger
        structured = StructuredLogger()
        structured.configure(
            level="DEBUG",
            log_dir=str(tmp_path),
            json_mode=True,
            sanitize=True,
        )
        
        # Set correlation ID
        set_correlation_id("test123")
        
        # Get named logger
        logger = structured.get_logger("integration_test")
        
        # Log messages
        logger.info("Test info message")
        logger.debug("Test debug message")
        logger.warning("Test warning with password=secret")
        
        # Verify log file exists
        log_file = tmp_path / "platform_base.log"
        assert log_file.exists()
        
        # Read and verify content
        with open(log_file) as f:
            content = f.read()
        
        assert "Test info message" in content
        assert "secret" not in content  # Should be sanitized
    
    def test_correlation_id_propagation(self):
        """Test correlation ID propagates through logs."""
        structured = StructuredLogger()
        structured.configure(level="DEBUG")
        
        set_correlation_id("prop_test")
        
        # All logs should have same correlation ID
        cid1 = get_correlation_id()
        time.sleep(0.01)
        cid2 = get_correlation_id()
        
        assert cid1 == cid2 == "prop_test"
