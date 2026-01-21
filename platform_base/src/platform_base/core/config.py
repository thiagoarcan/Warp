"""
Configuration Management System - Seção 15

Sistema avançado de configuração com suporte a YAML/TOML, validação,
hot-reload, e configurações hierárquicas por usuário e projeto.

Features:
- Suporte a YAML e TOML
- Validação de schema com Pydantic
- Hot-reload com file watching
- Configurações por usuário e projeto
- Merge hierárquico de configurações
- Environment variable substitution
- Configuração encrypted para secrets
- Backup automático e versionamento
"""

from __future__ import annotations

import os
import sys
import time
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from datetime import datetime

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import tomli
    import tomli_w
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

try:
    from pydantic import BaseModel, ValidationError, Field
    from pydantic.dataclasses import dataclass as pydantic_dataclass
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from platform_base.utils.logging import get_logger
from platform_base.utils.errors import ConfigError

logger = get_logger(__name__)


class ConfigFormat(Enum):
    """Formatos de configuração suportados"""
    YAML = "yaml"
    TOML = "toml" 
    JSON = "json"


class ConfigScope(Enum):
    """Escopo da configuração"""
    SYSTEM = "system"        # Configuração global do sistema
    USER = "user"           # Configuração por usuário
    PROJECT = "project"     # Configuração por projeto
    RUNTIME = "runtime"     # Configuração em tempo de execução


@dataclass
class ConfigSource:
    """Fonte de configuração"""
    path: Path
    format: ConfigFormat
    scope: ConfigScope
    priority: int = 0  # Prioridade para merge (maior = mais importante)
    watch: bool = True
    encrypted: bool = False
    
    # Metadata
    last_modified: Optional[float] = None
    last_loaded: Optional[float] = None
    checksum: Optional[str] = None
    

@dataclass 
class ConfigChange:
    """Evento de mudança de configuração"""
    source: ConfigSource
    timestamp: float = field(default_factory=time.time)
    change_type: str = "modified"  # created, modified, deleted
    affected_keys: List[str] = field(default_factory=list)
    old_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)


class ConfigWatcher(FileSystemEventHandler):
    """File watcher para hot-reload de configurações"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.debounce_time = 0.5  # Segundos
        self.pending_changes: Dict[str, float] = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Check if it's a config file we're watching
        for source in self.config_manager.sources:
            if source.path == file_path and source.watch:
                current_time = time.time()
                
                # Debounce rapid changes
                if file_path.name in self.pending_changes:
                    if current_time - self.pending_changes[file_path.name] < self.debounce_time:
                        continue
                
                self.pending_changes[file_path.name] = current_time
                
                # Schedule reload
                threading.Timer(self.debounce_time, 
                              self._reload_source, 
                              args=[source]).start()
    
    def _reload_source(self, source: ConfigSource):
        """Recarrega fonte de configuração"""
        try:
            self.config_manager._reload_source(source)
        except Exception as e:
            logger.error("config_reload_failed", source=str(source.path), error=str(e))


class ConfigValidator:
    """Validador de configurações usando schemas"""
    
    def __init__(self):
        self.schemas: Dict[str, Type[BaseModel]] = {}
        
    def register_schema(self, name: str, schema: Type[BaseModel]):
        """Registra schema de validação"""
        self.schemas[name] = schema
        logger.info("config_schema_registered", name=name)
        
    def validate(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados contra schema"""
        if name not in self.schemas:
            logger.warning("config_schema_not_found", name=name)
            return data
            
        try:
            schema = self.schemas[name]
            validated = schema(**data)
            return validated.dict() if hasattr(validated, 'dict') else validated
            
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed for {name}: {e}")


class ConfigManager:
    """Manager principal do sistema de configuração"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd() / ".platform_config"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration sources
        self.sources: List[ConfigSource] = []
        self.config_data: Dict[str, Any] = {}
        self.raw_data: Dict[str, Dict[str, Any]] = {}  # Por source
        
        # Validation
        self.validator = ConfigValidator()
        
        # File watching
        self.observer: Optional[Observer] = None
        self.watcher: Optional[ConfigWatcher] = None
        self._watching = False
        
        # Callbacks
        self.change_callbacks: List[Callable[[ConfigChange], None]] = []
        
        # Environment variable prefix
        self.env_prefix = "PLATFORM_"
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        logger.info("config_manager_initialized", base_dir=str(self.base_dir))
    
    def add_source(self, source: ConfigSource):
        """Adiciona fonte de configuração"""
        with self._lock:
            # Check if source already exists
            existing = next((s for s in self.sources if s.path == source.path), None)
            if existing:
                logger.warning("config_source_already_exists", path=str(source.path))
                return
            
            self.sources.append(source)
            self.sources.sort(key=lambda x: x.priority)  # Sort by priority
            
            # Load source immediately
            self._load_source(source)
            
            # Setup watching if enabled
            if source.watch and WATCHDOG_AVAILABLE and not self._watching:
                self._setup_watching()
            
            logger.info("config_source_added", 
                       path=str(source.path), 
                       format=source.format.value,
                       scope=source.scope.value)
    
    def _load_source(self, source: ConfigSource):
        """Carrega dados de uma fonte"""
        if not source.path.exists():
            logger.warning("config_source_not_found", path=str(source.path))
            return
        
        try:
            # Read file content
            content = source.path.read_text(encoding='utf-8')
            
            # Calculate checksum
            new_checksum = hashlib.md5(content.encode()).hexdigest()
            
            # Skip if unchanged
            if source.checksum == new_checksum:
                return
            
            # Parse content based on format
            if source.format == ConfigFormat.YAML:
                if not YAML_AVAILABLE:
                    raise ConfigError("YAML support not available")
                data = yaml.safe_load(content)
                
            elif source.format == ConfigFormat.TOML:
                if not TOML_AVAILABLE:
                    raise ConfigError("TOML support not available") 
                data = tomli.loads(content)
                
            elif source.format == ConfigFormat.JSON:
                data = json.loads(content)
                
            else:
                raise ConfigError(f"Unsupported config format: {source.format}")
            
            # Environment variable substitution
            data = self._substitute_env_vars(data)
            
            # Store raw data
            self.raw_data[str(source.path)] = data
            
            # Update source metadata
            source.last_loaded = time.time()
            source.last_modified = source.path.stat().st_mtime
            source.checksum = new_checksum
            
            # Merge into main config
            self._merge_configs()
            
            logger.info("config_source_loaded", 
                       path=str(source.path),
                       keys=len(data) if isinstance(data, dict) else 0)
            
        except Exception as e:
            logger.error("config_source_load_failed", 
                        path=str(source.path), error=str(e))
            raise ConfigError(f"Failed to load config from {source.path}: {e}")
    
    def _substitute_env_vars(self, data: Any) -> Any:
        """Substitui variáveis de ambiente recursivamente"""
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            # Simple ${VAR} substitution
            import re
            def replace_env(match):
                var_name = match.group(1)
                # Try with prefix first, then without
                return os.getenv(f"{self.env_prefix}{var_name}", 
                               os.getenv(var_name, match.group(0)))
            
            return re.sub(r'\$\{([^}]+)\}', replace_env, data)
        else:
            return data
    
    def _merge_configs(self):
        """Merge configurations por prioridade"""
        merged = {}
        
        # Sort sources by priority (lower first)
        sorted_sources = sorted(self.sources, key=lambda x: x.priority)
        
        for source in sorted_sources:
            source_key = str(source.path)
            if source_key in self.raw_data:
                source_data = self.raw_data[source_key]
                if isinstance(source_data, dict):
                    merged = self._deep_merge(merged, source_data)
        
        # Update main config
        old_config = self.config_data.copy()
        self.config_data = merged
        
        # Notify callbacks of changes
        self._notify_changes(old_config, merged)
    
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge de dicionários"""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _notify_changes(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Notifica callbacks sobre mudanças"""
        if not self.change_callbacks:
            return
        
        # Find changed keys
        all_keys = set(old_config.keys()) | set(new_config.keys())
        changed_keys = []
        old_values = {}
        new_values = {}
        
        for key in all_keys:
            old_val = old_config.get(key)
            new_val = new_config.get(key)
            
            if old_val != new_val:
                changed_keys.append(key)
                old_values[key] = old_val
                new_values[key] = new_val
        
        if changed_keys:
            change = ConfigChange(
                source=self.sources[0] if self.sources else None,  # TODO: track actual source
                affected_keys=changed_keys,
                old_values=old_values,
                new_values=new_values
            )
            
            for callback in self.change_callbacks:
                try:
                    callback(change)
                except Exception as e:
                    logger.error("config_callback_failed", error=str(e))
    
    def _setup_watching(self):
        """Configura file watching para hot-reload"""
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog_not_available")
            return
        
        self.watcher = ConfigWatcher(self)
        self.observer = Observer()
        
        # Watch all source directories
        watched_dirs = set()
        for source in self.sources:
            if source.watch and source.path.exists():
                watch_dir = source.path.parent
                if watch_dir not in watched_dirs:
                    self.observer.schedule(self.watcher, str(watch_dir), recursive=False)
                    watched_dirs.add(watch_dir)
        
        self.observer.start()
        self._watching = True
        
        logger.info("config_watching_started", directories=len(watched_dirs))
    
    def _reload_source(self, source: ConfigSource):
        """Recarrega fonte específica"""
        with self._lock:
            old_data = self.config_data.copy()
            self._load_source(source)
            
            logger.info("config_source_reloaded", path=str(source.path))
    
    def get(self, key: str, default: Any = None, validate_schema: Optional[str] = None) -> Any:
        """Obtém valor de configuração"""
        with self._lock:
            # Support nested keys with dot notation
            keys = key.split('.')
            value = self.config_data
            
            try:
                for k in keys:
                    value = value[k]
                
                # Validate if schema provided
                if validate_schema and isinstance(value, dict):
                    value = self.validator.validate(validate_schema, value)
                
                return value
                
            except (KeyError, TypeError):
                return default
    
    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.RUNTIME):
        """Define valor de configuração"""
        with self._lock:
            # Support nested keys with dot notation
            keys = key.split('.')
            target = self.config_data
            
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            
            old_value = target.get(keys[-1])
            target[keys[-1]] = value
            
            # Notify change
            if old_value != value:
                change = ConfigChange(
                    source=None,  # Runtime change
                    affected_keys=[key],
                    old_values={key: old_value},
                    new_values={key: value}
                )
                
                for callback in self.change_callbacks:
                    try:
                        callback(change)
                    except Exception as e:
                        logger.error("config_callback_failed", error=str(e))
            
            logger.debug("config_value_set", key=key, value=str(value)[:100])
    
    def has(self, key: str) -> bool:
        """Verifica se chave existe"""
        return self.get(key, None) is not None
    
    def keys(self, prefix: str = "") -> List[str]:
        """Lista chaves de configuração"""
        with self._lock:
            if not prefix:
                return list(self.config_data.keys())
            
            # Filter keys by prefix
            return [k for k in self.config_data.keys() if k.startswith(prefix)]
    
    def save_to_file(self, path: Path, format: ConfigFormat = ConfigFormat.YAML, 
                    scope_filter: Optional[ConfigScope] = None):
        """Salva configuração atual em arquivo"""
        # Filter data by scope if specified
        data_to_save = self.config_data
        if scope_filter:
            # TODO: implement scope filtering
            pass
        
        content = ""
        if format == ConfigFormat.YAML:
            if not YAML_AVAILABLE:
                raise ConfigError("YAML support not available")
            content = yaml.dump(data_to_save, default_flow_style=False, 
                              allow_unicode=True, sort_keys=True)
            
        elif format == ConfigFormat.TOML:
            if not TOML_AVAILABLE:
                raise ConfigError("TOML support not available")
            content = tomli_w.dumps(data_to_save)
            
        elif format == ConfigFormat.JSON:
            content = json.dumps(data_to_save, indent=2, ensure_ascii=False)
        
        # Backup existing file
        if path.exists():
            backup_path = path.with_suffix(f"{path.suffix}.backup.{int(time.time())}")
            path.rename(backup_path)
            logger.info("config_file_backed_up", original=str(path), backup=str(backup_path))
        
        # Write new content
        path.write_text(content, encoding='utf-8')
        logger.info("config_saved", path=str(path), format=format.value)
    
    def add_change_callback(self, callback: Callable[[ConfigChange], None]):
        """Adiciona callback para mudanças"""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[ConfigChange], None]):
        """Remove callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def get_schema_registry(self) -> ConfigValidator:
        """Retorna registry de schemas"""
        return self.validator
    
    def reload_all(self):
        """Recarrega todas as fontes"""
        with self._lock:
            logger.info("config_reload_all_started")
            
            for source in self.sources:
                try:
                    self._load_source(source)
                except Exception as e:
                    logger.error("config_source_reload_failed", 
                                source=str(source.path), error=str(e))
            
            logger.info("config_reload_all_completed")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de configuração"""
        with self._lock:
            return {
                'sources_count': len(self.sources),
                'watching': self._watching,
                'config_keys': len(self.config_data),
                'callbacks_count': len(self.change_callbacks),
                'schemas_registered': len(self.validator.schemas),
                'sources': [
                    {
                        'path': str(s.path),
                        'format': s.format.value,
                        'scope': s.scope.value,
                        'priority': s.priority,
                        'last_loaded': s.last_loaded,
                        'exists': s.path.exists()
                    }
                    for s in self.sources
                ]
            }
    
    def cleanup(self):
        """Limpa recursos"""
        if self.observer and self._watching:
            self.observer.stop()
            self.observer.join()
            self._watching = False
        
        self.change_callbacks.clear()
        self.sources.clear()
        self.config_data.clear()
        self.raw_data.clear()
        
        logger.info("config_manager_cleanup_completed")


# Global config manager instance
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Retorna instância global do config manager"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def get_config(key: str, default: Any = None, validate_schema: Optional[str] = None) -> Any:
    """Conveniência para obter configuração"""
    return get_config_manager().get(key, default, validate_schema)


def set_config(key: str, value: Any, scope: ConfigScope = ConfigScope.RUNTIME):
    """Conveniência para definir configuração"""
    return get_config_manager().set(key, value, scope)


def reload_config():
    """Conveniência para recarregar configurações"""
    return get_config_manager().reload_all()


# Configuration utilities
def create_default_sources(base_dir: Path) -> List[ConfigSource]:
    """Cria fontes de configuração padrão"""
    sources = []
    
    # System config
    system_config = base_dir / "system" / "platform.yaml"
    if system_config.exists():
        sources.append(ConfigSource(
            path=system_config,
            format=ConfigFormat.YAML,
            scope=ConfigScope.SYSTEM,
            priority=10
        ))
    
    # User config
    user_config = base_dir / "user" / f"{os.getenv('USER', 'default')}.yaml"
    if user_config.exists():
        sources.append(ConfigSource(
            path=user_config,
            format=ConfigFormat.YAML,
            scope=ConfigScope.USER,
            priority=20
        ))
    
    # Project config
    project_config = Path.cwd() / ".platform.yaml"
    if project_config.exists():
        sources.append(ConfigSource(
            path=project_config,
            format=ConfigFormat.YAML,
            scope=ConfigScope.PROJECT,
            priority=30
        ))
    
    return sources