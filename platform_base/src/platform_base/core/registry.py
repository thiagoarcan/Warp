from __future__ import annotations

import importlib.util
import inspect
import json
import os
import psutil
import resource
import signal
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union, Generator, Set, Tuple

from platform_base.core.protocols import PluginProtocol
from platform_base.utils.errors import PluginError
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)

# Platform version constants
PLATFORM_VERSION = "2.0.0"
PLUGIN_API_VERSION = "1.0.0"


class VersionCompatibility:
    """Utilitários para verificação de compatibilidade de versões"""
    
    @staticmethod
    def parse_version(version_str: str) -> Tuple[int, int, int]:
        """Parse version string to (major, minor, patch) tuple"""
        try:
            parts = version_str.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    @staticmethod
    def compare_versions(version1: str, version2: str) -> int:
        """Compare two versions. Returns -1, 0, or 1"""
        v1 = VersionCompatibility.parse_version(version1)
        v2 = VersionCompatibility.parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    @staticmethod
    def satisfies_requirement(version: str, requirement: str) -> bool:
        """Check if version satisfies requirement (e.g., '>=1.0.0', '~=1.2.0')"""
        requirement = requirement.strip()
        
        if requirement.startswith(">="):
            req_version = requirement[2:].strip()
            return VersionCompatibility.compare_versions(version, req_version) >= 0
        elif requirement.startswith("<="):
            req_version = requirement[2:].strip()
            return VersionCompatibility.compare_versions(version, req_version) <= 0
        elif requirement.startswith(">"):
            req_version = requirement[1:].strip()
            return VersionCompatibility.compare_versions(version, req_version) > 0
        elif requirement.startswith("<"):
            req_version = requirement[1:].strip()
            return VersionCompatibility.compare_versions(version, req_version) < 0
        elif requirement.startswith("=="):
            req_version = requirement[2:].strip()
            return VersionCompatibility.compare_versions(version, req_version) == 0
        elif requirement.startswith("~="):
            # Compatible release (~=1.2.0 means >=1.2.0, <1.3.0)
            req_version = requirement[2:].strip()
            req_parts = VersionCompatibility.parse_version(req_version)
            version_parts = VersionCompatibility.parse_version(version)
            
            if len(req_parts) >= 2:
                # Same major.minor, any patch
                return (version_parts[0] == req_parts[0] and 
                       version_parts[1] == req_parts[1] and
                       version_parts[2] >= req_parts[2])
            else:
                # Same major, any minor/patch
                return (version_parts[0] == req_parts[0] and
                       version_parts >= req_parts)
        else:
            # Exact match
            return VersionCompatibility.compare_versions(version, requirement) == 0
    
    @staticmethod
    def is_compatible_api_version(plugin_api_version: str, 
                                 min_version: Optional[str] = None,
                                 max_version: Optional[str] = None) -> bool:
        """Check if plugin API version is compatible"""
        current_api = PLUGIN_API_VERSION
        
        # Check plugin's API version against platform's current API
        if VersionCompatibility.compare_versions(plugin_api_version, current_api) > 0:
            return False  # Plugin requires newer API
        
        # Check against min/max if specified
        if min_version and VersionCompatibility.compare_versions(plugin_api_version, min_version) < 0:
            return False
        
        if max_version and VersionCompatibility.compare_versions(plugin_api_version, max_version) > 0:
            return False
        
        return True


@dataclass
class CompatibilityCheck:
    """Resultado de verificação de compatibilidade"""
    compatible: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, message: str):
        """Adiciona erro de compatibilidade"""
        self.compatible = False
        self.issues.append(message)
    
    def add_warning(self, message: str):
        """Adiciona aviso de compatibilidade"""
        self.warnings.append(message)


class PluginState(Enum):
    """Estados de um plugin"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginManifest:
    """Manifesto de plugin com metadados"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    website: str = ""
    license: str = ""
    
    # Dependencies and compatibility
    requires_platform_version: str = ">=1.0.0"
    dependencies: List[str] = field(default_factory=list)
    python_requires: str = ">=3.8"
    
    # Version compatibility
    min_compatible_version: Optional[str] = None  # Minimum compatible plugin API version
    max_compatible_version: Optional[str] = None  # Maximum compatible plugin API version
    api_version: str = "1.0.0"  # Plugin API version this plugin implements
    
    # Plugin dependencies (other plugins)
    plugin_dependencies: Dict[str, str] = field(default_factory=dict)  # name -> version_spec
    conflicts_with: List[str] = field(default_factory=list)  # Plugin names that conflict
    
    # Plugin configuration
    entry_point: str = "plugin.py"
    main_class: str = "Plugin"
    category: str = "general"
    
    # Security and sandboxing
    trusted: bool = False
    permissions: List[str] = field(default_factory=list)
    sandbox_level: str = "strict"  # strict, moderate, relaxed
    
    # Runtime configuration
    timeout_seconds: float = 30.0
    max_memory_mb: Optional[float] = None
    max_cpu_percent: Optional[float] = None
    allowed_modules: List[str] = field(default_factory=lambda: [
        "numpy", "pandas", "scipy", "matplotlib", "math", "statistics", "json"
    ])
    forbidden_modules: List[str] = field(default_factory=lambda: [
        "os", "subprocess", "socket", "urllib", "requests", "sys", "eval", "exec"
    ])
    
    @classmethod
    def from_file(cls, manifest_path: Path) -> 'PluginManifest':
        """Carrega manifesto de arquivo JSON"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            raise PluginError(f"Failed to load manifest from {manifest_path}: {e}")


@dataclass
class PluginInfo:
    """Informações completas de um plugin"""
    manifest: PluginManifest
    plugin_path: Path
    state: PluginState = PluginState.UNLOADED
    instance: Optional[PluginProtocol] = None
    load_time: Optional[float] = None
    error_message: Optional[str] = None
    last_used: Optional[float] = None
    call_count: int = 0
    
    # Resource monitoring
    peak_memory_mb: float = 0.0
    total_cpu_time: float = 0.0
    last_cpu_usage: float = 0.0
    error_count: int = 0
    last_error_time: Optional[float] = None


@dataclass
class ResourceLimits:
    """Limites de recursos para sandbox"""
    max_memory_mb: float = 100.0
    max_cpu_percent: float = 80.0
    max_execution_time: float = 30.0
    max_file_descriptors: int = 20
    max_threads: int = 5


@dataclass 
class SecurityViolation:
    """Violação de segurança detectada"""
    plugin_name: str
    violation_type: str
    description: str
    timestamp: float = field(default_factory=time.time)
    severity: str = "warning"  # warning, error, critical


class AdvancedPluginSandbox:
    """Sistema avançado de sandbox para plugins com isolamento rigoroso"""
    
    def __init__(self, plugin_info: PluginInfo):
        self.plugin_info = plugin_info
        self.plugin_name = plugin_info.manifest.name
        
        # Resource limits
        self.resource_limits = ResourceLimits(
            max_memory_mb=plugin_info.manifest.max_memory_mb or 100.0,
            max_cpu_percent=plugin_info.manifest.max_cpu_percent or 80.0,
            max_execution_time=plugin_info.manifest.timeout_seconds
        )
        
        # Thread pool com limites
        max_workers = min(2, self.resource_limits.max_threads)
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, 
            thread_name_prefix=f"plugin_{self.plugin_name}_sandbox"
        )
        
        # Resource monitoring
        self._monitoring_active = False
        self._resource_thread: Optional[threading.Thread] = None
        self._violation_callbacks: List[Callable[[SecurityViolation], None]] = []
        
        # Security state
        self.security_violations: List[SecurityViolation] = []
        self._imported_modules: Set[str] = set()
        
        # Statistics
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.last_execution_stats = {}
        
        logger.info("advanced_sandbox_created", plugin=self.plugin_name)
    
    def add_violation_callback(self, callback: Callable[[SecurityViolation], None]):
        """Adiciona callback para violações de segurança"""
        self._violation_callbacks.append(callback)
    
    def execute_with_isolation(self, func: Callable, *args, 
                             timeout: Optional[float] = None, 
                             monitor_resources: bool = True, **kwargs) -> Any:
        """Executa função com isolamento completo e monitoramento"""
        
        execution_timeout = timeout or self.resource_limits.max_execution_time
        self.execution_count += 1
        
        logger.debug("sandbox_execution_start", 
                    plugin=self.plugin_name,
                    execution_id=self.execution_count,
                    timeout=execution_timeout)
        
        # Prepare isolated execution environment
        isolated_func = self._prepare_isolated_execution(func, monitor_resources)
        
        # Submit to thread pool
        future = self.executor.submit(isolated_func, *args, **kwargs)
        
        start_time = time.perf_counter()
        
        try:
            # Start resource monitoring if enabled
            if monitor_resources:
                self._start_resource_monitoring()
            
            result = future.result(timeout=execution_timeout)
            execution_time = time.perf_counter() - start_time
            self.total_execution_time += execution_time
            
            # Update stats
            self.last_execution_stats = {
                'execution_time': execution_time,
                'success': True,
                'timestamp': time.time()
            }
            
            logger.debug("sandbox_execution_success", 
                        plugin=self.plugin_name,
                        execution_time=execution_time)
            
            return result
            
        except FuturesTimeoutError:
            execution_time = time.perf_counter() - start_time
            
            # Try to cancel
            future.cancel()
            
            # Report timeout violation
            violation = SecurityViolation(
                plugin_name=self.plugin_name,
                violation_type="timeout",
                description=f"Execution exceeded {execution_timeout}s timeout",
                severity="error"
            )
            self._report_violation(violation)
            
            self.last_execution_stats = {
                'execution_time': execution_time,
                'success': False,
                'error': 'timeout',
                'timestamp': time.time()
            }
            
            raise PluginError(f"Plugin '{self.plugin_name}' timed out after {execution_timeout}s")
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            
            # Report execution error
            violation = SecurityViolation(
                plugin_name=self.plugin_name,
                violation_type="execution_error",
                description=f"Execution failed: {str(e)[:200]}",
                severity="error"
            )
            self._report_violation(violation)
            
            self.last_execution_stats = {
                'execution_time': execution_time,
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
            
            logger.error("sandbox_execution_failed", 
                        plugin=self.plugin_name,
                        error=str(e),
                        execution_time=execution_time)
            
            raise PluginError(f"Plugin '{self.plugin_name}' execution failed: {e}") from e
            
        finally:
            if monitor_resources:
                self._stop_resource_monitoring()
    
    def _prepare_isolated_execution(self, func: Callable, monitor_resources: bool) -> Callable:
        """Prepara ambiente isolado para execução"""
        
        def isolated_wrapper(*args, **kwargs):
            # Set resource limits
            self._apply_resource_limits()
            
            # Install import hook for module restrictions
            original_import = __builtins__['__import__']
            __builtins__['__import__'] = self._restricted_import
            
            try:
                # Execute with monitoring
                if monitor_resources:
                    with self._resource_monitoring_context():
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            finally:
                # Restore original import
                __builtins__['__import__'] = original_import
        
        return isolated_wrapper
    
    def _restricted_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Import hook com restrições de segurança"""
        
        # Check if module is forbidden
        if name in self.plugin_info.manifest.forbidden_modules:
            violation = SecurityViolation(
                plugin_name=self.plugin_name,
                violation_type="forbidden_import",
                description=f"Attempted to import forbidden module: {name}",
                severity="critical"
            )
            self._report_violation(violation)
            raise ImportError(f"Module '{name}' is forbidden for security reasons")
        
        # Check if module is in allowed list (for strict mode)
        if (self.plugin_info.manifest.sandbox_level == "strict" and 
            name not in self.plugin_info.manifest.allowed_modules and
            not any(name.startswith(allowed) for allowed in self.plugin_info.manifest.allowed_modules)):
            
            violation = SecurityViolation(
                plugin_name=self.plugin_name,
                violation_type="unauthorized_import",
                description=f"Attempted to import non-whitelisted module: {name}",
                severity="warning"
            )
            self._report_violation(violation)
            
            if not self.plugin_info.manifest.trusted:
                raise ImportError(f"Module '{name}' not in allowed list")
        
        # Track imported modules
        self._imported_modules.add(name)
        
        # Use original import
        original_import = __import__
        return original_import(name, globals, locals, fromlist, level)
    
    def _apply_resource_limits(self):
        """Aplica limites de recursos ao processo atual"""
        try:
            # Memory limit (soft limit)
            if self.resource_limits.max_memory_mb:
                memory_bytes = int(self.resource_limits.max_memory_mb * 1024 * 1024)
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # CPU time limit
            cpu_limit = int(self.resource_limits.max_execution_time * 1.5)  # Buffer
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            
            # File descriptor limit
            resource.setrlimit(resource.RLIMIT_NOFILE, 
                             (self.resource_limits.max_file_descriptors, 
                              self.resource_limits.max_file_descriptors))
        
        except Exception as e:
            logger.warning("resource_limits_failed", plugin=self.plugin_name, error=str(e))
    
    @contextmanager
    def _resource_monitoring_context(self) -> Generator[None, None, None]:
        """Context manager para monitoramento de recursos"""
        process = psutil.Process()
        start_memory = process.memory_info().rss / (1024 * 1024)  # MB
        start_cpu_time = process.cpu_times().user + process.cpu_times().system
        
        yield
        
        # Check final resource usage
        end_memory = process.memory_info().rss / (1024 * 1024)
        end_cpu_time = process.cpu_times().user + process.cpu_times().system
        
        memory_used = end_memory - start_memory
        cpu_used = end_cpu_time - start_cpu_time
        
        # Update plugin stats
        self.plugin_info.peak_memory_mb = max(self.plugin_info.peak_memory_mb, memory_used)
        self.plugin_info.total_cpu_time += cpu_used
        
        # Check for violations
        if memory_used > self.resource_limits.max_memory_mb:
            violation = SecurityViolation(
                plugin_name=self.plugin_name,
                violation_type="memory_limit",
                description=f"Memory usage {memory_used:.1f}MB exceeded limit {self.resource_limits.max_memory_mb}MB",
                severity="warning"
            )
            self._report_violation(violation)
    
    def _start_resource_monitoring(self):
        """Inicia monitoramento de recursos em background"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._resource_thread = threading.Thread(
            target=self._resource_monitor_loop,
            daemon=True,
            name=f"resource_monitor_{self.plugin_name}"
        )
        self._resource_thread.start()
    
    def _stop_resource_monitoring(self):
        """Para monitoramento de recursos"""
        self._monitoring_active = False
        if self._resource_thread and self._resource_thread.is_alive():
            self._resource_thread.join(timeout=1.0)
    
    def _resource_monitor_loop(self):
        """Loop de monitoramento de recursos"""
        try:
            process = psutil.Process()
            
            while self._monitoring_active:
                try:
                    # Check memory
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    if memory_mb > self.resource_limits.max_memory_mb * 0.9:  # 90% warning
                        violation = SecurityViolation(
                            plugin_name=self.plugin_name,
                            violation_type="memory_warning",
                            description=f"High memory usage: {memory_mb:.1f}MB",
                            severity="warning"
                        )
                        self._report_violation(violation)
                    
                    # Check CPU
                    cpu_percent = process.cpu_percent(interval=0.1)
                    if cpu_percent > self.resource_limits.max_cpu_percent:
                        violation = SecurityViolation(
                            plugin_name=self.plugin_name,
                            violation_type="cpu_limit",
                            description=f"CPU usage {cpu_percent:.1f}% exceeded limit {self.resource_limits.max_cpu_percent}%",
                            severity="warning"
                        )
                        self._report_violation(violation)
                    
                    time.sleep(0.5)  # Monitor every 500ms
                    
                except psutil.NoSuchProcess:
                    break
                except Exception as e:
                    logger.warning("resource_monitor_error", plugin=self.plugin_name, error=str(e))
                    break
        
        except Exception as e:
            logger.error("resource_monitor_failed", plugin=self.plugin_name, error=str(e))
    
    def _report_violation(self, violation: SecurityViolation):
        """Reporta violação de segurança"""
        self.security_violations.append(violation)
        
        # Update plugin error count
        if violation.severity in ["error", "critical"]:
            self.plugin_info.error_count += 1
            self.plugin_info.last_error_time = violation.timestamp
        
        # Log violation
        logger.warning("security_violation",
                      plugin=self.plugin_name,
                      type=violation.violation_type,
                      severity=violation.severity,
                      description=violation.description)
        
        # Notify callbacks
        for callback in self._violation_callbacks:
            try:
                callback(violation)
            except Exception as e:
                logger.error("violation_callback_failed", error=str(e))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sandbox"""
        return {
            'plugin_name': self.plugin_name,
            'execution_count': self.execution_count,
            'total_execution_time': self.total_execution_time,
            'avg_execution_time': (self.total_execution_time / max(1, self.execution_count)),
            'peak_memory_mb': self.plugin_info.peak_memory_mb,
            'total_cpu_time': self.plugin_info.total_cpu_time,
            'error_count': self.plugin_info.error_count,
            'security_violations': len(self.security_violations),
            'imported_modules': list(self._imported_modules),
            'last_execution': self.last_execution_stats,
            'resource_limits': {
                'max_memory_mb': self.resource_limits.max_memory_mb,
                'max_cpu_percent': self.resource_limits.max_cpu_percent,
                'max_execution_time': self.resource_limits.max_execution_time
            }
        }
    
    def cleanup(self):
        """Limpa recursos do sandbox"""
        logger.info("sandbox_cleanup_start", plugin=self.plugin_name)
        
        self._stop_resource_monitoring()
        
        # Shutdown executor
        self.executor.shutdown(wait=False)
        
        # Clear violation callbacks
        self._violation_callbacks.clear()
        
        logger.info("sandbox_cleanup_complete", plugin=self.plugin_name)


# Alias for backward compatibility
PluginSandbox = AdvancedPluginSandbox


class PluginRegistry:
    """Registry avançado com validation, isolation e discovery seguro conforme seção 14"""

    def __init__(self, plugin_directories: Optional[List[Path]] = None):
        self._plugins: Dict[str, PluginInfo] = {}
        self._sandboxes: Dict[str, PluginSandbox] = {}
        self._plugin_directories = plugin_directories or []
        self._discovery_lock = threading.Lock()
        
        # Security settings
        self._allow_untrusted_plugins = False
        self._max_plugins = 100
        self._global_timeout = 60.0
        
        # Advanced monitoring and security
        self.security_violations: List[SecurityViolation] = []
        self._quarantined_plugins: Set[str] = set()
        self._violation_callbacks: List[Callable[[SecurityViolation], None]] = []
        self._monitoring_enabled = True
        
        # Plugin health monitoring
        self._health_monitor_thread: Optional[threading.Thread] = None
        self._health_monitoring_active = False
        
        # Start health monitoring
        if self._monitoring_enabled:
            self._start_health_monitoring()
        
        logger.info("plugin_registry_initialized", 
                   directories=len(self._plugin_directories),
                   monitoring_enabled=self._monitoring_enabled)

    def add_plugin_directory(self, directory: Path):
        """Adiciona diretório para descoberta de plugins"""
        if directory.exists() and directory.is_dir():
            self._plugin_directories.append(directory)
            logger.info("plugin_directory_added", path=str(directory))
    
    def discover_plugins(self, auto_load: bool = False) -> List[PluginInfo]:
        """
        Descobre plugins nos diretórios configurados conforme seção 14
        
        Args:
            auto_load: Se deve carregar automaticamente plugins confiáveis
        
        Returns:
            Lista de plugins descobertos
        """
        with self._discovery_lock:
            discovered = []
            
            for directory in self._plugin_directories:
                try:
                    discovered.extend(self._discover_in_directory(directory, auto_load))
                except Exception as e:
                    logger.error("plugin_discovery_failed", directory=str(directory), error=str(e))
            
            logger.info("plugin_discovery_complete", 
                       discovered_count=len(discovered),
                       total_plugins=len(self._plugins))
            
            return discovered
    
    def _discover_in_directory(self, directory: Path, auto_load: bool) -> List[PluginInfo]:
        """Descobre plugins em diretório específico"""
        discovered = []
        
        # Look for manifest files
        manifest_files = list(directory.glob("**/manifest.json"))
        
        for manifest_file in manifest_files:
            try:
                # Load manifest
                manifest = PluginManifest.from_file(manifest_file)
                plugin_dir = manifest_file.parent
                
                # Validate plugin structure
                if not self._validate_plugin_structure(plugin_dir, manifest):
                    continue
                
                # Create plugin info
                plugin_info = PluginInfo(
                    manifest=manifest,
                    plugin_path=plugin_dir,
                    state=PluginState.UNLOADED
                )
                
                # Check if already registered
                if manifest.name in self._plugins:
                    logger.warning("plugin_already_registered", name=manifest.name)
                    continue
                
                # Security checks
                if not self._validate_plugin_security(plugin_info):
                    plugin_info.state = PluginState.ERROR
                    plugin_info.error_message = "Failed security validation"
                    continue
                
                # Compatibility checks
                compatibility = self._check_plugin_compatibility(plugin_info)
                if not compatibility.compatible:
                    plugin_info.state = PluginState.ERROR
                    plugin_info.error_message = f"Compatibility issues: {'; '.join(compatibility.issues)}"
                    logger.error("plugin_compatibility_failed", 
                               name=manifest.name,
                               issues=compatibility.issues)
                    continue
                
                # Log compatibility warnings
                if compatibility.warnings:
                    logger.warning("plugin_compatibility_warnings",
                                 name=manifest.name, 
                                 warnings=compatibility.warnings)
                
                # Register plugin
                self._plugins[manifest.name] = plugin_info
                discovered.append(plugin_info)
                
                logger.info("plugin_discovered", 
                           name=manifest.name,
                           version=manifest.version,
                           path=str(plugin_dir))
                
                # Auto-load if requested and trusted
                if auto_load and manifest.trusted:
                    try:
                        self.load_plugin(manifest.name)
                    except Exception as e:
                        logger.error("plugin_autoload_failed", 
                                   name=manifest.name, error=str(e))
                
            except Exception as e:
                logger.error("plugin_manifest_load_failed", 
                           manifest=str(manifest_file), error=str(e))
        
        return discovered
    
    def _validate_plugin_structure(self, plugin_dir: Path, manifest: PluginManifest) -> bool:
        """Valida estrutura do plugin"""
        # Check entry point exists
        entry_point = plugin_dir / manifest.entry_point
        if not entry_point.exists():
            logger.warning("plugin_entry_point_missing", 
                         name=manifest.name, 
                         entry_point=str(entry_point))
            return False
        
        # Validate manifest fields
        required_fields = ['name', 'version', 'entry_point', 'main_class']
        for field in required_fields:
            if not getattr(manifest, field, None):
                logger.warning("plugin_manifest_missing_field", 
                             name=manifest.name, field=field)
                return False
        
        return True
    
    def _validate_plugin_security(self, plugin_info: PluginInfo) -> bool:
        """Valida segurança do plugin"""
        manifest = plugin_info.manifest
        
        # Check if untrusted plugins are allowed
        if not manifest.trusted and not self._allow_untrusted_plugins:
            logger.warning("untrusted_plugin_blocked", name=manifest.name)
            return False
        
        # Validate sandbox level
        valid_sandbox_levels = ['strict', 'moderate', 'relaxed']
        if manifest.sandbox_level not in valid_sandbox_levels:
            logger.warning("invalid_sandbox_level", 
                         name=manifest.name, 
                         level=manifest.sandbox_level)
            return False
        
        # Check plugin limit
        if len(self._plugins) >= self._max_plugins:
            logger.warning("plugin_limit_exceeded", limit=self._max_plugins)
            return False
        
        return True
    
    def _check_plugin_compatibility(self, plugin_info: PluginInfo) -> CompatibilityCheck:
        """Verifica compatibilidade completa do plugin"""
        manifest = plugin_info.manifest
        check = CompatibilityCheck(compatible=True)
        
        # Check platform version requirement
        if not VersionCompatibility.satisfies_requirement(PLATFORM_VERSION, manifest.requires_platform_version):
            check.add_error(f"Platform version {PLATFORM_VERSION} does not satisfy requirement {manifest.requires_platform_version}")
        
        # Check plugin API version
        if not VersionCompatibility.is_compatible_api_version(
            manifest.api_version, 
            manifest.min_compatible_version,
            manifest.max_compatible_version
        ):
            check.add_error(f"Plugin API version {manifest.api_version} is not compatible with platform API {PLUGIN_API_VERSION}")
        
        # Check Python version (basic check - could be enhanced)
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if not VersionCompatibility.satisfies_requirement(python_version, manifest.python_requires):
            check.add_error(f"Python version {python_version} does not satisfy requirement {manifest.python_requires}")
        
        # Check plugin dependencies
        for dep_name, dep_version in manifest.plugin_dependencies.items():
            if dep_name not in self._plugins:
                check.add_error(f"Required plugin dependency '{dep_name}' not found")
            else:
                dep_plugin = self._plugins[dep_name]
                if not VersionCompatibility.satisfies_requirement(dep_plugin.manifest.version, dep_version):
                    check.add_error(f"Plugin dependency '{dep_name}' version {dep_plugin.manifest.version} does not satisfy requirement {dep_version}")
        
        # Check for conflicts
        for conflict_name in manifest.conflicts_with:
            if conflict_name in self._plugins:
                conflict_plugin = self._plugins[conflict_name]
                if conflict_plugin.state in [PluginState.LOADED, PluginState.LOADING]:
                    check.add_error(f"Plugin conflicts with loaded plugin '{conflict_name}'")
                else:
                    check.add_warning(f"Plugin conflicts with registered plugin '{conflict_name}' (not loaded)")
        
        # Additional compatibility checks
        if manifest.trusted and not self._allow_untrusted_plugins:
            # If plugin claims to be trusted but we don't allow untrusted plugins,
            # it's suspicious unless it's actually been verified
            pass
        
        # Warn about version downgrades
        if manifest.name in self._plugins:
            existing_version = self._plugins[manifest.name].manifest.version
            if VersionCompatibility.compare_versions(manifest.version, existing_version) < 0:
                check.add_warning(f"Attempting to register older version {manifest.version} over {existing_version}")
        
        return check
    
    def load_plugin(self, name: str) -> PluginProtocol:
        """
        Carrega plugin com isolamento e error handling conforme seção 14
        
        Args:
            name: Nome do plugin para carregar
            
        Returns:
            Instância do plugin carregado
        """
        if name not in self._plugins:
            raise PluginError(f"Plugin '{name}' not found")
        
        # Check if plugin is quarantined
        if name in self._quarantined_plugins:
            raise PluginError(f"Plugin '{name}' is quarantined and cannot be loaded")
        
        plugin_info = self._plugins[name]
        
        if plugin_info.state == PluginState.LOADED:
            return plugin_info.instance
        
        if plugin_info.state == PluginState.ERROR:
            raise PluginError(f"Plugin '{name}' in error state: {plugin_info.error_message}")
        
        plugin_info.state = PluginState.LOADING
        
        try:
            # Load plugin module
            plugin_instance = self._load_plugin_module(plugin_info)
            
            # Validate protocol compliance
            if not isinstance(plugin_instance, PluginProtocol):
                raise PluginError(f"Plugin '{name}' does not implement PluginProtocol")
            
            # Create sandbox
            sandbox = PluginSandbox(plugin_info)
            
            # Add violation callback to sandbox
            sandbox.add_violation_callback(self._on_security_violation)
            
            # Initialize plugin in sandbox
            try:
                sandbox.execute_with_isolation(plugin_instance.initialize)
            except Exception as e:
                sandbox.cleanup()
                raise PluginError(f"Plugin '{name}' initialization failed: {e}") from e
            
            # Success
            plugin_info.instance = plugin_instance
            plugin_info.state = PluginState.LOADED
            plugin_info.load_time = time.time()
            self._sandboxes[name] = sandbox
            
            logger.info("plugin_loaded", name=name, version=plugin_instance.version)
            return plugin_instance
            
        except Exception as e:
            plugin_info.state = PluginState.ERROR
            plugin_info.error_message = str(e)
            logger.error("plugin_load_failed", name=name, error=str(e))
            raise PluginError(f"Failed to load plugin '{name}': {e}") from e
    
    def _load_plugin_module(self, plugin_info: PluginInfo) -> PluginProtocol:
        """Carrega módulo do plugin"""
        manifest = plugin_info.manifest
        entry_point = plugin_info.plugin_path / manifest.entry_point
        
        # Create module spec
        module_name = f"plugin_{manifest.name}_{int(time.time())}"
        spec = importlib.util.spec_from_file_location(module_name, entry_point)
        
        if spec is None or spec.loader is None:
            raise PluginError(f"Failed to create module spec for {entry_point}")
        
        # Load module
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules temporarily
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
            
            # Get main class
            if not hasattr(module, manifest.main_class):
                raise PluginError(f"Plugin class '{manifest.main_class}' not found in {entry_point}")
            
            plugin_class = getattr(module, manifest.main_class)
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            
            return plugin_instance
            
        finally:
            # Cleanup from sys.modules
            sys.modules.pop(module_name, None)
    
    def unload_plugin(self, name: str):
        """Descarrega plugin e limpa recursos"""
        if name not in self._plugins:
            return
        
        plugin_info = self._plugins[name]
        
        # Cleanup sandbox
        if name in self._sandboxes:
            sandbox = self._sandboxes[name]
            try:
                # Call plugin cleanup if available
                if plugin_info.instance and hasattr(plugin_info.instance, 'cleanup'):
                    sandbox.execute_with_isolation(plugin_info.instance.cleanup, timeout=5.0)
            except Exception as e:
                logger.warning("plugin_cleanup_failed", name=name, error=str(e))
            finally:
                sandbox.cleanup()
                del self._sandboxes[name]
        
        # Update plugin state
        plugin_info.instance = None
        plugin_info.state = PluginState.UNLOADED
        
        logger.info("plugin_unloaded", name=name)

    def register(self, plugin: PluginProtocol) -> None:
        """Registra plugin manualmente (backward compatibility)"""
        if not isinstance(plugin, PluginProtocol):
            raise PluginError("Plugin does not implement protocol", {"plugin": str(plugin)})
        if plugin.name in self._plugins:
            raise PluginError("Plugin already registered", {"name": plugin.name})
        
        # Create synthetic plugin info
        manifest = PluginManifest(
            name=plugin.name,
            version=plugin.version,
            description=getattr(plugin, 'description', ''),
            trusted=True,  # Manually registered plugins are trusted
            entry_point="<manual>",
            main_class="<manual>"
        )
        
        plugin_info = PluginInfo(
            manifest=manifest,
            plugin_path=Path(),
            state=PluginState.LOADED,
            instance=plugin,
            load_time=time.time()
        )
        
        self._plugins[plugin.name] = plugin_info
        logger.info("plugin_registered_manually", name=plugin.name, version=plugin.version)

    def unregister(self, name: str) -> None:
        """Remove plugin do registry"""
        if name in self._plugins:
            self.unload_plugin(name)
            del self._plugins[name]
            logger.info("plugin_unregistered", name=name)

    def get(self, name: str) -> PluginProtocol:
        """Retorna plugin carregado"""
        if name not in self._plugins:
            raise PluginError("Plugin not found", {"name": name})
        
        plugin_info = self._plugins[name]
        
        if plugin_info.state != PluginState.LOADED or plugin_info.instance is None:
            # Try to load plugin
            return self.load_plugin(name)
        
        # Update last used
        plugin_info.last_used = time.time()
        return plugin_info.instance

    def list_plugins(self) -> List[str]:
        """Lista todos os plugins registrados"""
        return sorted(self._plugins.keys())
    
    def get_plugin_info(self, name: str) -> PluginInfo:
        """Retorna informações do plugin"""
        if name not in self._plugins:
            raise PluginError(f"Plugin '{name}' not found")
        return self._plugins[name]
    
    def get_loaded_plugins(self) -> List[str]:
        """Lista plugins carregados"""
        return [name for name, info in self._plugins.items() 
                if info.state == PluginState.LOADED]
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos plugins"""
        states = {}
        for info in self._plugins.values():
            states[info.state.value] = states.get(info.state.value, 0) + 1
        
        return {
            'total_plugins': len(self._plugins),
            'loaded_plugins': len(self.get_loaded_plugins()),
            'plugin_states': states,
            'discovery_directories': len(self._plugin_directories),
            'sandboxes_active': len(self._sandboxes)
        }

    def safe_call(self, name: str, method: str, *args, timeout: Optional[float] = None, **kwargs):
        """
        Chama método de plugin com isolamento e timeout conforme seção 14
        
        Args:
            name: Nome do plugin
            method: Método a chamar
            timeout: Timeout personalizado
            *args, **kwargs: Argumentos para o método
        """
        plugin = self.get(name)
        plugin_info = self._plugins[name]
        
        if not hasattr(plugin, method):
            raise PluginError(f"Plugin '{name}' does not have method '{method}'")
        
        # Get sandbox
        if name not in self._sandboxes:
            raise PluginError(f"Plugin '{name}' sandbox not available")
        
        sandbox = self._sandboxes[name]
        
        try:
            func = getattr(plugin, method)
            result = sandbox.execute_with_isolation(func, *args, timeout=timeout, **kwargs)
            
            # Update statistics
            plugin_info.call_count += 1
            plugin_info.last_used = time.time()
            
            logger.debug("plugin_method_called", name=name, method=method)
            return result
            
        except Exception as exc:
            logger.error("plugin_call_failed", name=name, method=method, error=str(exc))
            raise PluginError("Plugin call failed", {"name": name, "method": method}) from exc
    
    def set_security_settings(self, allow_untrusted: bool = False, 
                            max_plugins: int = 100, 
                            global_timeout: float = 60.0):
        """Configura settings de segurança"""
        self._allow_untrusted_plugins = allow_untrusted
        self._max_plugins = max_plugins
        self._global_timeout = global_timeout
        
        logger.info("plugin_security_settings_updated",
                   allow_untrusted=allow_untrusted,
                   max_plugins=max_plugins,
                   global_timeout=global_timeout)
    
    # Advanced security and monitoring methods
    
    def add_violation_callback(self, callback: Callable[[SecurityViolation], None]):
        """Adiciona callback para violações de segurança"""
        self._violation_callbacks.append(callback)
    
    def _on_security_violation(self, violation: SecurityViolation):
        """Callback para violações de segurança dos plugins"""
        self.security_violations.append(violation)
        
        # Check if plugin should be quarantined
        plugin_name = violation.plugin_name
        if violation.severity == "critical":
            self._quarantine_plugin(plugin_name, f"Critical violation: {violation.description}")
        elif violation.severity == "error":
            # Check error count
            if plugin_name in self._plugins:
                plugin_info = self._plugins[plugin_name]
                if plugin_info.error_count >= 5:  # 5 errors = quarantine
                    self._quarantine_plugin(plugin_name, "Excessive error count")
        
        # Notify external callbacks
        for callback in self._violation_callbacks:
            try:
                callback(violation)
            except Exception as e:
                logger.error("violation_callback_failed", error=str(e))
        
        logger.warning("plugin_security_violation", 
                      plugin=plugin_name,
                      type=violation.violation_type,
                      severity=violation.severity)
    
    def _quarantine_plugin(self, plugin_name: str, reason: str):
        """Coloca plugin em quarentena"""
        if plugin_name in self._quarantined_plugins:
            return
        
        self._quarantined_plugins.add(plugin_name)
        
        # Unload plugin if loaded
        if plugin_name in self._plugins:
            try:
                self.unload_plugin(plugin_name)
                self._plugins[plugin_name].state = PluginState.DISABLED
            except Exception as e:
                logger.error("quarantine_unload_failed", plugin=plugin_name, error=str(e))
        
        logger.warning("plugin_quarantined", plugin=plugin_name, reason=reason)
    
    def release_from_quarantine(self, plugin_name: str) -> bool:
        """Remove plugin da quarentena"""
        if plugin_name not in self._quarantined_plugins:
            return False
        
        self._quarantined_plugins.remove(plugin_name)
        
        # Reset plugin state
        if plugin_name in self._plugins:
            self._plugins[plugin_name].state = PluginState.UNLOADED
            self._plugins[plugin_name].error_count = 0
        
        logger.info("plugin_released_from_quarantine", plugin=plugin_name)
        return True
    
    def get_quarantined_plugins(self) -> List[str]:
        """Retorna lista de plugins em quarentena"""
        return list(self._quarantined_plugins)
    
    def _start_health_monitoring(self):
        """Inicia monitoramento de saúde dos plugins"""
        if self._health_monitoring_active:
            return
        
        self._health_monitoring_active = True
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True,
            name="plugin_health_monitor"
        )
        self._health_monitor_thread.start()
        logger.info("plugin_health_monitoring_started")
    
    def _stop_health_monitoring(self):
        """Para monitoramento de saúde"""
        self._health_monitoring_active = False
        if self._health_monitor_thread and self._health_monitor_thread.is_alive():
            self._health_monitor_thread.join(timeout=2.0)
    
    def _health_monitor_loop(self):
        """Loop principal do monitor de saúde"""
        while self._health_monitoring_active:
            try:
                self._check_plugin_health()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error("health_monitor_error", error=str(e))
                time.sleep(5)  # Shorter sleep on error
    
    def _check_plugin_health(self):
        """Verifica saúde dos plugins carregados"""
        for plugin_name, plugin_info in self._plugins.items():
            if plugin_info.state != PluginState.LOADED:
                continue
            
            if plugin_name in self._quarantined_plugins:
                continue
            
            try:
                # Check if plugin has been inactive for too long
                if (plugin_info.last_used and 
                    time.time() - plugin_info.last_used > 3600):  # 1 hour
                    
                    logger.info("plugin_inactive_detected", 
                               plugin=plugin_name,
                               inactive_time=time.time() - plugin_info.last_used)
                
                # Check error rate
                if plugin_info.error_count > 0 and plugin_info.call_count > 0:
                    error_rate = plugin_info.error_count / plugin_info.call_count
                    if error_rate > 0.5:  # 50% error rate
                        logger.warning("high_plugin_error_rate", 
                                     plugin=plugin_name,
                                     error_rate=error_rate)
                
                # Check sandbox statistics if available
                if plugin_name in self._sandboxes:
                    sandbox = self._sandboxes[plugin_name]
                    stats = sandbox.get_statistics()
                    
                    # Check for resource usage issues
                    if stats['peak_memory_mb'] > 200:  # High memory usage
                        logger.warning("high_plugin_memory_usage",
                                     plugin=plugin_name,
                                     peak_memory=stats['peak_memory_mb'])
                    
                    if len(sandbox.security_violations) > 10:  # Many violations
                        logger.warning("high_plugin_violation_count",
                                     plugin=plugin_name,
                                     violation_count=len(sandbox.security_violations))
            
            except Exception as e:
                logger.error("plugin_health_check_failed", 
                           plugin=plugin_name, error=str(e))
    
    def get_security_report(self) -> Dict[str, Any]:
        """Retorna relatório de segurança completo"""
        total_violations = len(self.security_violations)
        
        # Count violations by type and severity
        violation_types = {}
        violation_severities = {}
        
        for violation in self.security_violations:
            violation_types[violation.violation_type] = violation_types.get(violation.violation_type, 0) + 1
            violation_severities[violation.severity] = violation_severities.get(violation.severity, 0) + 1
        
        # Recent violations (last 24h)
        recent_violations = [
            v for v in self.security_violations 
            if time.time() - v.timestamp < 86400
        ]
        
        # Plugin risk assessment
        plugin_risks = {}
        for plugin_name, plugin_info in self._plugins.items():
            risk_score = 0
            
            if plugin_info.error_count > 0:
                risk_score += min(plugin_info.error_count * 10, 50)
            
            if not plugin_info.manifest.trusted:
                risk_score += 20
            
            if plugin_name in self._quarantined_plugins:
                risk_score += 100
            
            # Count violations for this plugin
            plugin_violations = [v for v in self.security_violations if v.plugin_name == plugin_name]
            risk_score += len(plugin_violations) * 5
            
            plugin_risks[plugin_name] = {
                'risk_score': risk_score,
                'level': 'high' if risk_score > 80 else 'medium' if risk_score > 40 else 'low',
                'error_count': plugin_info.error_count,
                'violation_count': len(plugin_violations),
                'trusted': plugin_info.manifest.trusted,
                'quarantined': plugin_name in self._quarantined_plugins
            }
        
        return {
            'total_violations': total_violations,
            'recent_violations': len(recent_violations),
            'violation_types': violation_types,
            'violation_severities': violation_severities,
            'quarantined_plugins': len(self._quarantined_plugins),
            'total_plugins': len(self._plugins),
            'loaded_plugins': len(self.get_loaded_plugins()),
            'plugin_risks': plugin_risks,
            'monitoring_enabled': self._monitoring_enabled,
            'untrusted_allowed': self._allow_untrusted_plugins
        }
    
    def get_sandbox_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos sandboxes"""
        sandbox_stats = {}
        
        for plugin_name, sandbox in self._sandboxes.items():
            try:
                sandbox_stats[plugin_name] = sandbox.get_statistics()
            except Exception as e:
                logger.error("sandbox_stats_failed", plugin=plugin_name, error=str(e))
                sandbox_stats[plugin_name] = {'error': str(e)}
        
        return {
            'active_sandboxes': len(self._sandboxes),
            'sandbox_details': sandbox_stats
        }
    
    # Version management methods
    
    def check_plugin_compatibility(self, plugin_name: str) -> CompatibilityCheck:
        """Verifica compatibilidade de plugin específico"""
        if plugin_name not in self._plugins:
            check = CompatibilityCheck(compatible=False)
            check.add_error(f"Plugin '{plugin_name}' not found")
            return check
        
        return self._check_plugin_compatibility(self._plugins[plugin_name])
    
    def get_plugin_dependencies(self, plugin_name: str) -> List[str]:
        """Retorna lista de dependências de um plugin"""
        if plugin_name not in self._plugins:
            return []
        
        manifest = self._plugins[plugin_name].manifest
        return list(manifest.plugin_dependencies.keys())
    
    def get_plugin_dependents(self, plugin_name: str) -> List[str]:
        """Retorna lista de plugins que dependem do plugin especificado"""
        dependents = []
        
        for name, plugin_info in self._plugins.items():
            if plugin_name in plugin_info.manifest.plugin_dependencies:
                dependents.append(name)
        
        return dependents
    
    def resolve_plugin_load_order(self, plugin_names: List[str]) -> List[str]:
        """Resolve ordem de carregamento baseada em dependências"""
        load_order = []
        remaining = set(plugin_names)
        loaded = set()
        
        # Simple topological sort
        max_iterations = len(plugin_names) * 2  # Prevent infinite loop
        iterations = 0
        
        while remaining and iterations < max_iterations:
            iterations += 1
            made_progress = False
            
            for plugin_name in list(remaining):
                if plugin_name not in self._plugins:
                    # Skip missing plugins
                    remaining.remove(plugin_name)
                    made_progress = True
                    continue
                
                # Check if all dependencies are already loaded or will be loaded
                dependencies = self.get_plugin_dependencies(plugin_name)
                unresolved_deps = []
                
                for dep in dependencies:
                    if dep not in loaded and dep in remaining:
                        unresolved_deps.append(dep)
                
                # If no unresolved dependencies, can load this plugin
                if not unresolved_deps:
                    load_order.append(plugin_name)
                    loaded.add(plugin_name)
                    remaining.remove(plugin_name)
                    made_progress = True
            
            # If we couldn't make progress, there might be circular dependencies
            if not made_progress:
                logger.warning("circular_plugin_dependencies_detected", 
                             remaining_plugins=list(remaining))
                # Add remaining plugins in alphabetical order
                load_order.extend(sorted(remaining))
                break
        
        return load_order
    
    def upgrade_plugin(self, plugin_name: str, new_manifest_path: Path) -> bool:
        """Atualiza plugin para nova versão"""
        try:
            # Load new manifest
            new_manifest = PluginManifest.from_file(new_manifest_path)
            
            if new_manifest.name != plugin_name:
                raise PluginError(f"Plugin name mismatch: expected '{plugin_name}', got '{new_manifest.name}'")
            
            # Check if plugin is currently registered
            if plugin_name not in self._plugins:
                raise PluginError(f"Plugin '{plugin_name}' not registered")
            
            current_plugin = self._plugins[plugin_name]
            current_version = current_plugin.manifest.version
            new_version = new_manifest.version
            
            # Check if it's actually an upgrade
            if VersionCompatibility.compare_versions(new_version, current_version) <= 0:
                logger.warning("plugin_downgrade_attempt", 
                             plugin=plugin_name,
                             current_version=current_version,
                             new_version=new_version)
            
            # Unload current plugin if loaded
            was_loaded = current_plugin.state == PluginState.LOADED
            if was_loaded:
                self.unload_plugin(plugin_name)
            
            # Create new plugin info
            new_plugin_info = PluginInfo(
                manifest=new_manifest,
                plugin_path=new_manifest_path.parent,
                state=PluginState.UNLOADED
            )
            
            # Check compatibility
            compatibility = self._check_plugin_compatibility(new_plugin_info)
            if not compatibility.compatible:
                # Restore old plugin
                logger.error("plugin_upgrade_compatibility_failed",
                           plugin=plugin_name,
                           issues=compatibility.issues)
                return False
            
            # Update registry
            self._plugins[plugin_name] = new_plugin_info
            
            # Reload if it was previously loaded
            if was_loaded:
                try:
                    self.load_plugin(plugin_name)
                except Exception as e:
                    logger.error("plugin_upgrade_reload_failed",
                               plugin=plugin_name, error=str(e))
                    return False
            
            logger.info("plugin_upgraded",
                       plugin=plugin_name,
                       old_version=current_version,
                       new_version=new_version)
            
            return True
            
        except Exception as e:
            logger.error("plugin_upgrade_failed", 
                        plugin=plugin_name, error=str(e))
            return False
    
    def get_version_info(self) -> Dict[str, Any]:
        """Retorna informações de versão da plataforma e plugins"""
        plugin_versions = {}
        
        for name, plugin_info in self._plugins.items():
            plugin_versions[name] = {
                'version': plugin_info.manifest.version,
                'api_version': plugin_info.manifest.api_version,
                'state': plugin_info.state.value,
                'requires_platform': plugin_info.manifest.requires_platform_version,
                'python_requires': plugin_info.manifest.python_requires,
                'dependencies': plugin_info.manifest.plugin_dependencies,
                'conflicts': plugin_info.manifest.conflicts_with
            }
        
        import sys
        return {
            'platform_version': PLATFORM_VERSION,
            'plugin_api_version': PLUGIN_API_VERSION,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'total_plugins': len(self._plugins),
            'loaded_plugins': len(self.get_loaded_plugins()),
            'plugins': plugin_versions
        }
    
    def cleanup(self):
        """Limpa todos os recursos do registry"""
        logger.info("plugin_registry_cleanup_start")
        
        # Stop health monitoring
        self._stop_health_monitoring()
        
        # Unload all plugins
        for name in list(self._plugins.keys()):
            self.unload_plugin(name)
        
        # Clear data structures
        self._plugins.clear()
        self._sandboxes.clear()
        self.security_violations.clear()
        self._quarantined_plugins.clear()
        self._violation_callbacks.clear()
        
        logger.info("plugin_registry_cleanup_complete")
