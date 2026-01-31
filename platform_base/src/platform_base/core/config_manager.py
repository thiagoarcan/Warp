"""
Advanced Configuration Manager - Config-002

ConfigManager avançado com validação, hot-reload, schemas,
e integração completa com o sistema Platform Base.

Features:
- Validação automática com schemas Pydantic
- Hot-reload em tempo real
- Configurações hierárquicas por escopo
- Integration com logging e error handling
- Performance optimization e caching
- Backup automático e recovery
- Metrics e monitoring
"""

from __future__ import annotations

import copy
import threading
import time
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any


try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

import builtins

from platform_base.core.config import ConfigChange, ConfigFormat, get_config_manager
from platform_base.core.config import ConfigManager as BaseConfigManager
from platform_base.utils.errors import ConfigError
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

logger = get_logger(__name__)


# Configuration Schemas
if PYDANTIC_AVAILABLE:
    class LoggingConfig(BaseModel):
        """Schema para configuração de logging"""
        level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
        file_enabled: bool = True
        file_path: str = "logs/platform.log"
        max_file_size: int = Field(default=10*1024*1024, ge=1024)  # 10MB
        backup_count: int = Field(default=5, ge=1)
        console_enabled: bool = True
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        @validator("level")
        def validate_level(self, v):
            return v.upper()

    class UIConfig(BaseModel):
        """Schema para configuração de interface"""
        theme: str = Field(default="dark", regex="^(light|dark|auto)$")
        language: str = Field(default="en", regex="^[a-z]{2}$")
        auto_save_interval: int = Field(default=300, ge=60)  # 5 minutos
        max_recent_files: int = Field(default=10, ge=1)
        window_geometry: dict[str, int] | None = None
        performance_mode: bool = False

    class ProcessingConfig(BaseModel):
        """Schema para configuração de processamento"""
        max_workers: int = Field(default=4, ge=1, le=16)
        memory_limit_mb: int = Field(default=2048, ge=512)
        chunk_size: int = Field(default=10000, ge=100)
        enable_numba: bool = True
        cache_enabled: bool = True
        cache_size_mb: int = Field(default=256, ge=64)

    class VisualizationConfig(BaseModel):
        """Schema para configuração de visualização"""
        default_renderer: str = Field(default="opengl", regex="^(opengl|software)$")
        max_points_plot: int = Field(default=1000000, ge=1000)
        enable_antialiasing: bool = True
        fps_limit: int = Field(default=60, ge=30, le=120)
        background_color: str = Field(default="#2b2b2b", regex="^#[0-9a-fA-F]{6}$")
        grid_enabled: bool = True

    class PluginConfig(BaseModel):
        """Schema para configuração de plugins"""
        discovery_enabled: bool = True
        auto_load_trusted: bool = True
        sandbox_level: str = Field(default="moderate", regex="^(strict|moderate|relaxed)$")
        max_plugins: int = Field(default=50, ge=1)
        timeout_seconds: float = Field(default=30.0, ge=1.0)
        max_memory_mb: float = Field(default=256.0, ge=32.0)

    class PlatformConfig(BaseModel):
        """Schema principal da plataforma"""
        version: str = "2.0.0"

        logging: LoggingConfig = Field(default_factory=LoggingConfig)
        ui: UIConfig = Field(default_factory=UIConfig)
        processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
        visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
        plugins: PluginConfig = Field(default_factory=PluginConfig)

        # Environment specific
        development_mode: bool = False
        debug_enabled: bool = False
        telemetry_enabled: bool = True


@dataclass
class ConfigValidationResult:
    """Resultado de validação de configuração"""
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validated_data: dict[str, Any] | None = None
    schema_name: str | None = None


@dataclass
class ConfigPerformanceMetrics:
    """Métricas de performance da configuração"""
    load_time: float = 0.0
    validation_time: float = 0.0
    merge_time: float = 0.0
    total_reloads: int = 0
    validation_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


class AdvancedConfigManager:
    """ConfigManager avançado com recursos enterprise"""

    def __init__(self, base_config_manager: BaseConfigManager | None = None):
        self.base_manager = base_config_manager or get_config_manager()

        # Validation and schemas
        self.validation_enabled = PYDANTIC_AVAILABLE
        self.schemas: dict[str, type] = {}
        self.validation_cache: dict[str, ConfigValidationResult] = {}

        # Performance tracking
        self.metrics = ConfigPerformanceMetrics()
        self.performance_monitoring = True

        # Advanced features
        self.backup_enabled = True
        self.backup_retention_days = 30
        self.max_backup_files = 100

        # Threading
        self._lock = threading.RLock()
        self._validation_lock = threading.Lock()

        # Callbacks by category
        self.validation_callbacks: list[Callable[[ConfigValidationResult], None]] = []
        self.error_callbacks: list[Callable[[Exception, str], None]] = []

        # Register default schemas
        self._register_default_schemas()

        # Setup base manager integration
        self._setup_base_integration()

        logger.info("advanced_config_manager_initialized",
                   validation_enabled=self.validation_enabled,
                   schemas_count=len(self.schemas))

    def _register_default_schemas(self):
        """Registra schemas padrão do sistema"""
        if not PYDANTIC_AVAILABLE:
            logger.warning("pydantic_not_available_schemas_disabled")
            return

        default_schemas = {
            "platform": PlatformConfig,
            "logging": LoggingConfig,
            "ui": UIConfig,
            "processing": ProcessingConfig,
            "visualization": VisualizationConfig,
            "plugins": PluginConfig,
        }

        for name, schema_class in default_schemas.items():
            self.register_schema(name, schema_class)

    def _setup_base_integration(self):
        """Configura integração com ConfigManager base"""
        # Register our change handler
        self.base_manager.add_change_callback(self._on_config_change)

    def register_schema(self, name: str, schema_class: type):
        """Registra schema de validação"""
        if not PYDANTIC_AVAILABLE:
            logger.warning("pydantic_not_available_schema_ignored", name=name)
            return

        with self._validation_lock:
            self.schemas[name] = schema_class

            # Clear validation cache for this schema
            cache_keys = [k for k in self.validation_cache if k.startswith(f"{name}:")]
            for key in cache_keys:
                del self.validation_cache[key]

        logger.info("config_schema_registered", name=name, class_name=schema_class.__name__)

    def validate_config(self, schema_name: str, data: dict[str, Any],
                       use_cache: bool = True) -> ConfigValidationResult:
        """Valida configuração contra schema"""
        start_time = time.perf_counter()

        try:
            if not self.validation_enabled:
                return ConfigValidationResult(
                    valid=True,
                    warnings=["Validation disabled - Pydantic not available"],
                )

            # Check cache
            cache_key = f"{schema_name}:{hash(str(sorted(data.items())))}"
            if use_cache and cache_key in self.validation_cache:
                self.metrics.cache_hits += 1
                return self.validation_cache[cache_key]

            self.metrics.cache_misses += 1

            # Get schema
            if schema_name not in self.schemas:
                return ConfigValidationResult(
                    valid=False,
                    errors=[f"Schema '{schema_name}' not found"],
                    schema_name=schema_name,
                )

            schema_class = self.schemas[schema_name]

            try:
                # Validate data
                validated_instance = schema_class(**data)
                validated_data = validated_instance.dict()

                result = ConfigValidationResult(
                    valid=True,
                    validated_data=validated_data,
                    schema_name=schema_name,
                )

            except Exception as e:
                self.metrics.validation_errors += 1

                # Parse validation errors
                errors = []
                if hasattr(e, "errors"):
                    for error in e.errors():
                        field_path = " -> ".join(str(x) for x in error.get("loc", []))
                        message = error.get("msg", "Unknown error")
                        errors.append(f"{field_path}: {message}")
                else:
                    errors.append(str(e))

                result = ConfigValidationResult(
                    valid=False,
                    errors=errors,
                    schema_name=schema_name,
                )

            # Cache result
            if use_cache:
                self.validation_cache[cache_key] = result

            # Notify callbacks
            for callback in self.validation_callbacks:
                try:
                    callback(result)
                except Exception as cb_error:
                    logger.exception("validation_callback_failed", error=str(cb_error))

            return result

        finally:
            self.metrics.validation_time += time.perf_counter() - start_time

    def get_validated_config(self, schema_name: str, config_path: str = "",
                           default_factory: Callable | None = None) -> Any:
        """Obtém configuração validada"""
        # Get raw config
        raw_data = self.base_manager.get(config_path) if config_path else self.base_manager.config_data

        if raw_data is None:
            raw_data = default_factory() if default_factory else {}

        # Validate
        result = self.validate_config(schema_name, raw_data)

        if not result.valid:
            error_msg = f"Configuration validation failed for {schema_name}: {'; '.join(result.errors)}"

            # Notify error callbacks
            error = ConfigError(error_msg)
            for callback in self.error_callbacks:
                try:
                    callback(error, schema_name)
                except Exception as cb_error:
                    logger.exception("error_callback_failed", error=str(cb_error))

            raise ConfigError(error_msg)

        return result.validated_data

    def update_config_with_validation(self, config_path: str, updates: dict[str, Any],
                                    schema_name: str | None = None):
        """Atualiza configuração com validação"""
        with self._lock:
            # Get current config
            current = self.base_manager.get(config_path, {})
            if not isinstance(current, dict):
                current = {}

            # Merge updates
            merged = self._deep_merge(current, updates)

            # Validate if schema provided
            if schema_name:
                result = self.validate_config(schema_name, merged)
                if not result.valid:
                    raise ConfigError(f"Validation failed: {'; '.join(result.errors)}")
                merged = result.validated_data

            # Update config
            self.base_manager.set(config_path, merged)

            logger.info("config_updated_with_validation",
                       path=config_path,
                       schema=schema_name,
                       keys_updated=list(updates.keys()))

    def _deep_merge(self, base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        """Deep merge de dicionários"""
        result = base.copy()

        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _on_config_change(self, change: ConfigChange):
        """Handler para mudanças de configuração"""
        # Re-validate affected configs
        affected_schemas = self._get_affected_schemas(change.affected_keys)

        for schema_name in affected_schemas:
            try:
                # Get current config for this schema
                schema_data = self._extract_schema_data(schema_name)

                # Validate
                result = self.validate_config(schema_name, schema_data, use_cache=False)

                if not result.valid:
                    logger.warning("config_validation_failed_on_change",
                                 schema=schema_name,
                                 errors=result.errors)

            except Exception as e:
                logger.exception("config_change_validation_failed",
                           schema=schema_name, error=str(e))

    def _get_affected_schemas(self, changed_keys: list[str]) -> set[str]:
        """Identifica schemas afetados por mudanças"""
        affected = set()

        for key in changed_keys:
            # Simple heuristic: first part of key path
            top_level = key.split(".")[0]

            # Check if it matches a schema name
            if top_level in self.schemas:
                affected.add(top_level)

            # Also check root schema
            affected.add("platform")

        return affected

    def _extract_schema_data(self, schema_name: str) -> dict[str, Any]:
        """Extrai dados relevantes para um schema"""
        if schema_name == "platform":
            return self.base_manager.config_data
        return self.base_manager.get(schema_name, {})

    @contextmanager
    def atomic_update(self, schema_name: str | None = None):
        """Context manager para atualizações atômicas"""
        with self._lock:
            # Save current state
            backup_config = copy.deepcopy(self.base_manager.config_data)

            try:
                yield self

                # Validate final state if schema provided
                if schema_name:
                    schema_data = self._extract_schema_data(schema_name)
                    result = self.validate_config(schema_name, schema_data)

                    if not result.valid:
                        # Restore backup
                        self.base_manager.config_data = backup_config
                        raise ConfigError(f"Atomic update validation failed: {'; '.join(result.errors)}")

            except Exception:
                # Restore backup on any error
                self.base_manager.config_data = backup_config
                raise

    def backup_config(self, backup_dir: Path | None = None) -> Path:
        """Cria backup da configuração atual"""
        if backup_dir is None:
            backup_dir = self.base_manager.base_dir / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"config_backup_{timestamp}.yaml"

        # Save current config
        self.base_manager.save_to_file(backup_file, ConfigFormat.YAML)

        # Cleanup old backups
        self._cleanup_old_backups(backup_dir)

        logger.info("config_backup_created", path=str(backup_file))
        return backup_file

    def _cleanup_old_backups(self, backup_dir: Path):
        """Remove backups antigos"""
        if not self.backup_enabled:
            return

        try:
            backup_files = list(backup_dir.glob("config_backup_*.yaml"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Keep only recent files
            if len(backup_files) > self.max_backup_files:
                for old_file in backup_files[self.max_backup_files:]:
                    old_file.unlink()
                    logger.debug("old_backup_removed", path=str(old_file))

            # Remove files older than retention period
            import time
            cutoff_time = time.time() - (self.backup_retention_days * 24 * 3600)

            for backup_file in backup_files:
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    logger.debug("expired_backup_removed", path=str(backup_file))

        except Exception as e:
            logger.exception("backup_cleanup_failed", error=str(e))

    def restore_from_backup(self, backup_file: Path, validate: bool = True):
        """Restaura configuração de backup"""
        if not backup_file.exists():
            raise ConfigError(f"Backup file not found: {backup_file}")

        with self._lock:
            # Load backup
            import yaml
            backup_data = yaml.safe_load(backup_file.read_text())

            # Validate if requested
            if validate and self.validation_enabled:
                result = self.validate_config("platform", backup_data)
                if not result.valid:
                    raise ConfigError(f"Backup validation failed: {'; '.join(result.errors)}")
                backup_data = result.validated_data

            # Create current backup before restore
            current_backup = self.backup_config()

            try:
                # Restore configuration
                self.base_manager.config_data = backup_data

                # Trigger change notifications
                self.base_manager._notify_changes({}, backup_data)

                logger.info("config_restored_from_backup",
                           backup_file=str(backup_file),
                           current_backup=str(current_backup))

            except Exception as e:
                logger.exception("config_restore_failed", error=str(e))
                raise ConfigError(f"Failed to restore from backup: {e}")

    def add_validation_callback(self, callback: Callable[[ConfigValidationResult], None]):
        """Adiciona callback de validação"""
        self.validation_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[Exception, str], None]):
        """Adiciona callback de erro"""
        self.error_callbacks.append(callback)

    def get_validation_statistics(self) -> dict[str, Any]:
        """Retorna estatísticas de validação"""
        return {
            "schemas_registered": len(self.schemas),
            "validation_enabled": self.validation_enabled,
            "cache_size": len(self.validation_cache),
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "validation_errors": self.metrics.validation_errors,
            "performance_metrics": {
                "validation_time": self.metrics.validation_time,
                "total_reloads": self.metrics.total_reloads,
            },
        }

    def clear_validation_cache(self):
        """Limpa cache de validação"""
        with self._validation_lock:
            self.validation_cache.clear()
        logger.info("validation_cache_cleared")

    def set_performance_monitoring(self, enabled: bool):
        """Habilita/desabilita monitoramento de performance"""
        self.performance_monitoring = enabled
        logger.info("performance_monitoring_changed", enabled=enabled)

    def reset_metrics(self):
        """Reseta métricas de performance"""
        self.metrics = ConfigPerformanceMetrics()
        logger.info("config_metrics_reset")

    def cleanup(self):
        """Limpa recursos do manager"""
        # Remove callbacks from base manager
        with suppress(builtins.BaseException):
            self.base_manager.remove_change_callback(self._on_config_change)

        # Clear caches and callbacks
        self.validation_cache.clear()
        self.validation_callbacks.clear()
        self.error_callbacks.clear()

        logger.info("advanced_config_manager_cleanup_completed")


# Global advanced config manager
_global_advanced_config: AdvancedConfigManager | None = None


def get_advanced_config_manager() -> AdvancedConfigManager:
    """Retorna instância global do advanced config manager"""
    global _global_advanced_config
    if _global_advanced_config is None:
        _global_advanced_config = AdvancedConfigManager()
    return _global_advanced_config


def get_validated_config(schema_name: str, config_path: str = "",
                        default_factory: Callable | None = None) -> Any:
    """Conveniência para obter configuração validada"""
    return get_advanced_config_manager().get_validated_config(
        schema_name, config_path, default_factory)


def update_validated_config(config_path: str, updates: dict[str, Any],
                          schema_name: str | None = None):
    """Conveniência para atualizar configuração com validação"""
    return get_advanced_config_manager().update_config_with_validation(
        config_path, updates, schema_name)
