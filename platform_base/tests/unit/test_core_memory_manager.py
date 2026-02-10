"""
Tests for memory_manager module - Category 10.6.
"""
import pytest
import gc
from unittest.mock import Mock, patch, MagicMock

from platform_base.core.memory_manager import (
    MemoryLevel,
    MemoryStatus,
    MemoryConfig,
    MemoryManager,
)


class TestMemoryLevel:
    """Tests for MemoryLevel enum."""
    
    def test_normal_level(self):
        """Test NORMAL level exists."""
        assert MemoryLevel.NORMAL is not None
    
    def test_warning_level(self):
        """Test WARNING level exists."""
        assert MemoryLevel.WARNING is not None
    
    def test_high_level(self):
        """Test HIGH level exists."""
        assert MemoryLevel.HIGH is not None
    
    def test_critical_level(self):
        """Test CRITICAL level exists."""
        assert MemoryLevel.CRITICAL is not None
    
    def test_all_levels_unique(self):
        """Test all levels are unique."""
        levels = list(MemoryLevel)
        assert len(levels) == 4
        assert len(set(levels)) == 4


class TestMemoryStatus:
    """Tests for MemoryStatus dataclass."""
    
    def test_create_status(self):
        """Test creating MemoryStatus."""
        status = MemoryStatus(
            process_mb=512.0,
            total_mb=16384.0,
            available_mb=8192.0,
            percent=50.0,
            level=MemoryLevel.NORMAL,
            suggestions=[],
        )
        
        assert status.process_mb == 512.0
        assert status.total_mb == 16384.0
        assert status.available_mb == 8192.0
        assert status.percent == 50.0
        assert status.level == MemoryLevel.NORMAL
    
    def test_status_with_suggestions(self):
        """Test MemoryStatus with suggestions."""
        status = MemoryStatus(
            process_mb=2048.0,
            total_mb=4096.0,
            available_mb=512.0,
            percent=87.5,
            level=MemoryLevel.HIGH,
            suggestions=[
                "Close unused datasets",
                "Reduce decimation",
            ],
        )
        
        assert len(status.suggestions) == 2
        assert "Close unused datasets" in status.suggestions
    
    def test_status_to_dict(self):
        """Test converting status to dict."""
        status = MemoryStatus(
            process_mb=512.0,
            total_mb=16384.0,
            available_mb=8192.0,
            percent=50.0,
            level=MemoryLevel.NORMAL,
            suggestions=["Tip 1"],
        )
        
        data = status.to_dict()
        
        assert data["process_mb"] == 512.0
        assert data["total_mb"] == 16384.0
        assert data["level"] == "NORMAL"
        assert data["suggestions"] == ["Tip 1"]


class TestMemoryConfig:
    """Tests for MemoryConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = MemoryConfig()
        
        assert config.warning_threshold == 60.0
        assert config.high_threshold == 80.0
        assert config.critical_threshold == 95.0
        assert config.hard_limit_percent == 80.0
        assert config.enable_auto_gc is True
        assert config.enable_low_memory_mode is True
        assert config.monitor_interval_seconds == 5.0
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = MemoryConfig(
            warning_threshold=50.0,
            high_threshold=70.0,
            critical_threshold=90.0,
            hard_limit_percent=75.0,
            enable_auto_gc=False,
            monitor_interval_seconds=10.0,
        )
        
        assert config.warning_threshold == 50.0
        assert config.high_threshold == 70.0
        assert config.critical_threshold == 90.0
        assert config.hard_limit_percent == 75.0
        assert config.enable_auto_gc is False
        assert config.monitor_interval_seconds == 10.0


class TestMemoryManager:
    """Tests for MemoryManager class."""
    
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        MemoryManager._instance = None
        yield
        MemoryManager._instance = None
    
    def test_singleton_pattern(self):
        """Test that MemoryManager is a singleton."""
        manager1 = MemoryManager()
        manager2 = MemoryManager()
        
        assert manager1 is manager2
    
    def test_manager_attributes_exist(self):
        """Test that manager has expected attributes."""
        manager = MemoryManager()
        
        # Should have _initialized flag
        assert hasattr(manager, '_initialized')
    
    def test_module_has_psutil_available_flag(self):
        """Test that module has PSUTIL_AVAILABLE flag."""
        from platform_base.core import memory_manager
        
        assert hasattr(memory_manager, 'PSUTIL_AVAILABLE')


class TestMemoryLevelThresholds:
    """Tests for memory level threshold logic."""
    
    def test_normal_is_lowest(self):
        """Test NORMAL is the lowest severity."""
        assert MemoryLevel.NORMAL.value < MemoryLevel.WARNING.value
    
    def test_critical_is_highest(self):
        """Test CRITICAL is the highest severity."""
        assert MemoryLevel.CRITICAL.value > MemoryLevel.HIGH.value
    
    def test_level_order(self):
        """Test levels are in correct order."""
        levels = [
            MemoryLevel.NORMAL,
            MemoryLevel.WARNING,
            MemoryLevel.HIGH,
            MemoryLevel.CRITICAL,
        ]
        
        for i in range(len(levels) - 1):
            assert levels[i].value < levels[i + 1].value
