"""
Tests for config_manager module - Advanced Configuration.
"""
import pytest
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from unittest.mock import Mock, patch

from platform_base.core.config_manager import (
    ConfigValidationResult,
    ConfigPerformanceMetrics,
    AdvancedConfigManager,
    PYDANTIC_AVAILABLE,
)


class TestConfigValidationResult:
    """Tests for ConfigValidationResult dataclass."""
    
    def test_create_valid_result(self):
        """Test creating valid result."""
        result = ConfigValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            validated_data={"key": "value"},
            schema_name="test_schema",
        )
        
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.validated_data == {"key": "value"}
        assert result.schema_name == "test_schema"
    
    def test_create_invalid_result(self):
        """Test creating invalid result."""
        result = ConfigValidationResult(
            valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )
        
        assert result.valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
    
    def test_default_values(self):
        """Test default values."""
        result = ConfigValidationResult(valid=True)
        
        assert result.errors == []
        assert result.warnings == []
        assert result.validated_data is None
        assert result.schema_name is None


class TestConfigPerformanceMetrics:
    """Tests for ConfigPerformanceMetrics dataclass."""
    
    def test_default_metrics(self):
        """Test default metrics values."""
        metrics = ConfigPerformanceMetrics()
        
        assert metrics.load_time == 0.0
        assert metrics.validation_time == 0.0
        assert metrics.merge_time == 0.0
        assert metrics.total_reloads == 0
        assert metrics.validation_errors == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
    
    def test_custom_metrics(self):
        """Test custom metrics values."""
        metrics = ConfigPerformanceMetrics(
            load_time=0.5,
            validation_time=0.1,
            merge_time=0.05,
            total_reloads=10,
            cache_hits=100,
            cache_misses=5,
        )
        
        assert metrics.load_time == 0.5
        assert metrics.validation_time == 0.1
        assert metrics.merge_time == 0.05
        assert metrics.total_reloads == 10
        assert metrics.cache_hits == 100
    
    def test_metrics_can_be_updated(self):
        """Test that metrics can be updated."""
        metrics = ConfigPerformanceMetrics()
        
        metrics.load_time = 1.5
        metrics.cache_hits = 50
        
        assert metrics.load_time == 1.5
        assert metrics.cache_hits == 50


class TestAdvancedConfigManager:
    """Tests for AdvancedConfigManager class."""
    
    def test_create_manager(self):
        """Test creating manager."""
        manager = AdvancedConfigManager()
        
        assert manager is not None
        assert manager.validation_enabled == PYDANTIC_AVAILABLE
        assert isinstance(manager.metrics, ConfigPerformanceMetrics)
    
    def test_manager_has_base_manager(self):
        """Test manager has base manager reference."""
        manager = AdvancedConfigManager()
        
        assert manager.base_manager is not None
    
    def test_manager_has_schemas(self):
        """Test manager has schemas dict."""
        manager = AdvancedConfigManager()
        
        assert isinstance(manager.schemas, dict)
    
    def test_manager_has_validation_cache(self):
        """Test manager has validation cache."""
        manager = AdvancedConfigManager()
        
        assert isinstance(manager.validation_cache, dict)
    
    def test_backup_settings(self):
        """Test backup settings."""
        manager = AdvancedConfigManager()
        
        assert manager.backup_enabled is True
        assert manager.backup_retention_days == 30
        assert manager.max_backup_files == 100
    
    def test_performance_monitoring(self):
        """Test performance monitoring setting."""
        manager = AdvancedConfigManager()
        
        assert manager.performance_monitoring is True
    
    def test_callbacks_lists(self):
        """Test callback lists exist."""
        manager = AdvancedConfigManager()
        
        assert isinstance(manager.validation_callbacks, list)
        assert isinstance(manager.error_callbacks, list)


class TestPydanticSchemas:
    """Tests for Pydantic schemas if available."""
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_logging_config_schema(self):
        """Test LoggingConfig schema."""
        from platform_base.core.config_manager import LoggingConfig
        
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.file_enabled is True
        assert config.console_enabled is True
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_ui_config_schema(self):
        """Test UIConfig schema."""
        from platform_base.core.config_manager import UIConfig
        
        config = UIConfig()
        
        assert config.theme == "dark"
        assert config.language == "en"
        assert config.auto_save_interval == 300
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_processing_config_schema(self):
        """Test ProcessingConfig schema."""
        from platform_base.core.config_manager import ProcessingConfig
        
        config = ProcessingConfig()
        
        assert config.max_workers == 4
        assert config.memory_limit_mb == 2048
        assert config.chunk_size == 10000
        assert config.cache_enabled is True
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_visualization_config_schema(self):
        """Test VisualizationConfig schema."""
        from platform_base.core.config_manager import VisualizationConfig
        
        config = VisualizationConfig()
        
        assert config.default_renderer == "opengl"
        assert config.max_points_plot == 1000000
        assert config.enable_antialiasing is True
        assert config.fps_limit == 60
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_plugin_config_schema(self):
        """Test PluginConfig schema."""
        from platform_base.core.config_manager import PluginConfig
        
        config = PluginConfig()
        
        assert config.discovery_enabled is True
        assert config.auto_load_trusted is True
        assert config.sandbox_level == "moderate"
        assert config.max_plugins == 50
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_platform_config_schema(self):
        """Test PlatformConfig schema."""
        from platform_base.core.config_manager import PlatformConfig
        
        config = PlatformConfig()
        
        assert config.version == "2.0.0"
        assert config.development_mode is False
        assert config.debug_enabled is False
        assert config.telemetry_enabled is True


class TestModuleAvailability:
    """Tests for module availability checks."""
    
    def test_pydantic_available_flag(self):
        """Test PYDANTIC_AVAILABLE flag exists."""
        from platform_base.core import config_manager
        
        assert hasattr(config_manager, 'PYDANTIC_AVAILABLE')
        assert isinstance(config_manager.PYDANTIC_AVAILABLE, bool)
    
    def test_module_has_logger(self):
        """Test module has logger."""
        from platform_base.core import config_manager
        
        assert hasattr(config_manager, 'logger')
