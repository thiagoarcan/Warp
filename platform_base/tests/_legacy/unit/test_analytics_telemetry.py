"""
Tests for telemetry module - Category 10.2.
"""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from platform_base.analytics.telemetry import (
    TelemetryConfig,
    TelemetryEvent,
    TelemetryEventType,
)


class TestTelemetryEventType:
    """Tests for TelemetryEventType enum."""
    
    def test_feature_used(self):
        """Test FEATURE_USED type exists."""
        assert TelemetryEventType.FEATURE_USED is not None
    
    def test_operation_completed(self):
        """Test OPERATION_COMPLETED type exists."""
        assert TelemetryEventType.OPERATION_COMPLETED is not None
    
    def test_error_occurred(self):
        """Test ERROR_OCCURRED type exists."""
        assert TelemetryEventType.ERROR_OCCURRED is not None
    
    def test_file_loaded(self):
        """Test FILE_LOADED type exists."""
        assert TelemetryEventType.FILE_LOADED is not None
    
    def test_file_exported(self):
        """Test FILE_EXPORTED type exists."""
        assert TelemetryEventType.FILE_EXPORTED is not None
    
    def test_session_start(self):
        """Test SESSION_START type exists."""
        assert TelemetryEventType.SESSION_START is not None
    
    def test_session_end(self):
        """Test SESSION_END type exists."""
        assert TelemetryEventType.SESSION_END is not None
    
    def test_performance_metric(self):
        """Test PERFORMANCE_METRIC type exists."""
        assert TelemetryEventType.PERFORMANCE_METRIC is not None
    
    def test_all_types_unique(self):
        """Test all event types are unique."""
        types = list(TelemetryEventType)
        assert len(types) == len(set(types))


class TestTelemetryEvent:
    """Tests for TelemetryEvent dataclass."""
    
    def test_create_event(self):
        """Test creating TelemetryEvent."""
        event = TelemetryEvent(
            event_type=TelemetryEventType.FEATURE_USED,
            timestamp=datetime(2026, 2, 1, 12, 0, 0),
        )
        
        assert event.event_type == TelemetryEventType.FEATURE_USED
        assert event.data == {}
        assert event.session_id == ""
    
    def test_create_event_with_data(self):
        """Test creating event with data."""
        event = TelemetryEvent(
            event_type=TelemetryEventType.FILE_LOADED,
            timestamp=datetime.now(),
            data={"file_size": 1024, "file_type": "csv"},
            session_id="session123",
        )
        
        assert event.data["file_size"] == 1024
        assert event.session_id == "session123"
    
    def test_event_to_dict(self):
        """Test converting event to dict."""
        event = TelemetryEvent(
            event_type=TelemetryEventType.FEATURE_USED,
            timestamp=datetime(2026, 2, 1, 12, 0, 0),
            data={"feature": "plot"},
            session_id="abc123",
        )
        
        data = event.to_dict()
        
        assert data["event_type"] == "FEATURE_USED"
        assert "2026-02-01" in data["timestamp"]
        assert data["data"]["feature"] == "plot"
        assert data["session_id"] == "abc123"
    
    def test_event_from_dict(self):
        """Test creating event from dict."""
        data = {
            "event_type": "OPERATION_COMPLETED",
            "timestamp": "2026-02-01T12:00:00",
            "data": {"operation": "calculate"},
            "session_id": "xyz789",
        }
        
        event = TelemetryEvent.from_dict(data)
        
        assert event.event_type == TelemetryEventType.OPERATION_COMPLETED
        assert event.data["operation"] == "calculate"
        assert event.session_id == "xyz789"
    
    def test_event_from_dict_minimal(self):
        """Test creating event from minimal dict."""
        data = {
            "event_type": "ERROR_OCCURRED",
            "timestamp": "2026-02-01T12:00:00",
        }
        
        event = TelemetryEvent.from_dict(data)
        
        assert event.event_type == TelemetryEventType.ERROR_OCCURRED
        assert event.data == {}
        assert event.session_id == ""


class TestTelemetryConfig:
    """Tests for TelemetryConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = TelemetryConfig()
        
        assert config.enabled is False
        assert config.collect_feature_usage is True
        assert config.collect_performance is True
        assert config.collect_errors is True
        assert config.collect_file_stats is True
        assert config.retention_days == 30
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = TelemetryConfig(
            enabled=True,
            collect_feature_usage=False,
            retention_days=7,
        )
        
        assert config.enabled is True
        assert config.collect_feature_usage is False
        assert config.retention_days == 7
    
    def test_config_to_dict(self):
        """Test converting config to dict."""
        config = TelemetryConfig(
            enabled=True,
            retention_days=14,
        )
        
        data = config.to_dict()
        
        assert data["enabled"] is True
        assert data["retention_days"] == 14
        assert "collect_feature_usage" in data
    
    def test_config_from_dict(self):
        """Test creating config from dict."""
        data = {
            "enabled": True,
            "collect_errors": False,
            "retention_days": 60,
        }
        
        config = TelemetryConfig.from_dict(data)
        
        assert config.enabled is True
        assert config.collect_errors is False
        assert config.retention_days == 60
    
    def test_config_from_dict_with_extra_fields(self):
        """Test that extra fields are ignored."""
        data = {
            "enabled": True,
            "unknown_field": "ignored",
        }
        
        config = TelemetryConfig.from_dict(data)
        assert config.enabled is True
