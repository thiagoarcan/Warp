"""
Memory Manager - Category 10.6

Sistema de monitoramento e gerenciamento de memória com avisos ao usuário.

Features:
- Monitoramento contínuo de uso de memória
- Estimativa de memória necessária antes de carregar arquivo
- Warnings em níveis configuráveis (60%, 80%, 95%)
- Sugestões de ações quando memória alta
- Garbage collection forçado em situações críticas
- Offloading de dados não visíveis para disco
- Limite hard de memória configurável
- Indicador de memória na status bar
- Modo de baixa memória automático
"""

from __future__ import annotations

import gc
import threading
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MemoryLevel(Enum):
    """Memory usage levels."""
    NORMAL = auto()  # < 60%
    WARNING = auto()  # 60-80%
    HIGH = auto()  # 80-95%
    CRITICAL = auto()  # > 95%


@dataclass
class MemoryStatus:
    """Current memory status."""
    process_mb: float
    total_mb: float
    available_mb: float
    percent: float
    level: MemoryLevel
    suggestions: list[str]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'process_mb': self.process_mb,
            'total_mb': self.total_mb,
            'available_mb': self.available_mb,
            'percent': self.percent,
            'level': self.level.name,
            'suggestions': self.suggestions,
        }


@dataclass
class MemoryConfig:
    """Configuration for memory management."""
    warning_threshold: float = 60.0  # %
    high_threshold: float = 80.0  # %
    critical_threshold: float = 95.0  # %
    hard_limit_percent: float = 80.0  # % of total RAM
    enable_auto_gc: bool = True
    enable_low_memory_mode: bool = True
    monitor_interval_seconds: float = 5.0


class MemoryManager:
    """
    Manages memory usage monitoring and warnings.
    
    Provides continuous memory monitoring, threshold warnings,
    and automatic memory management features.
    """
    
    _instance: MemoryManager | None = None
    _lock = threading.Lock()
    
    def __new__(cls) -> MemoryManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config = MemoryConfig()
        self._status_callbacks: list[Callable[[MemoryStatus], None]] = []
        self._level_change_callbacks: dict[MemoryLevel, list[Callable[[], None]]] = {
            level: [] for level in MemoryLevel
        }
        self._monitor_thread: threading.Thread | None = None
        self._monitoring = False
        self._current_status: MemoryStatus | None = None
        self._last_level = MemoryLevel.NORMAL
        self._low_memory_mode = False
    
    def configure(self, config: MemoryConfig) -> None:
        """
        Configure the memory manager.
        
        Args:
            config: Memory configuration
        """
        self._config = config
    
    def start_monitoring(self) -> None:
        """Start continuous memory monitoring."""
        if self._monitoring or not PSUTIL_AVAILABLE:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="MemoryMonitor",
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop continuous memory monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None
    
    def _monitor_loop(self) -> None:
        """Memory monitoring loop."""
        while self._monitoring:
            try:
                status = self.get_status()
                self._current_status = status
                
                # Check for level changes
                if status.level != self._last_level:
                    self._on_level_changed(status.level)
                    self._last_level = status.level
                
                # Auto-enable low memory mode if critical
                if (self._config.enable_low_memory_mode and 
                    status.level == MemoryLevel.CRITICAL and 
                    not self._low_memory_mode):
                    self.enable_low_memory_mode()
                
                # Auto garbage collection if high
                if (self._config.enable_auto_gc and 
                    status.level in (MemoryLevel.HIGH, MemoryLevel.CRITICAL)):
                    self.force_gc()
                
                # Notify status callbacks
                for callback in self._status_callbacks:
                    try:
                        callback(status)
                    except Exception:
                        pass
                
            except Exception:
                pass
            
            time.sleep(self._config.monitor_interval_seconds)
    
    def get_status(self) -> MemoryStatus:
        """
        Get current memory status.
        
        Returns:
            Current memory status with suggestions
        """
        if not PSUTIL_AVAILABLE:
            return MemoryStatus(
                process_mb=0,
                total_mb=0,
                available_mb=0,
                percent=0,
                level=MemoryLevel.NORMAL,
                suggestions=[],
            )
        
        # Get memory info
        process = psutil.Process()
        memory_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()
        
        process_mb = memory_info.rss / (1024 * 1024)
        total_mb = virtual_memory.total / (1024 * 1024)
        available_mb = virtual_memory.available / (1024 * 1024)
        percent = virtual_memory.percent
        
        # Determine level
        level = self._determine_level(percent)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(level, process_mb, available_mb)
        
        return MemoryStatus(
            process_mb=process_mb,
            total_mb=total_mb,
            available_mb=available_mb,
            percent=percent,
            level=level,
            suggestions=suggestions,
        )
    
    def _determine_level(self, percent: float) -> MemoryLevel:
        """Determine memory level from percentage."""
        if percent >= self._config.critical_threshold:
            return MemoryLevel.CRITICAL
        elif percent >= self._config.high_threshold:
            return MemoryLevel.HIGH
        elif percent >= self._config.warning_threshold:
            return MemoryLevel.WARNING
        else:
            return MemoryLevel.NORMAL
    
    def _generate_suggestions(
        self,
        level: MemoryLevel,
        process_mb: float,
        available_mb: float,
    ) -> list[str]:
        """Generate suggestions based on memory level."""
        suggestions = []
        
        if level == MemoryLevel.WARNING:
            suggestions.append("Consider closing unused datasets")
            suggestions.append("Enable data decimation to reduce memory usage")
        
        elif level == MemoryLevel.HIGH:
            suggestions.append("Close unused datasets immediately")
            suggestions.append("Reduce data decimation level")
            suggestions.append("Save your work and consider restarting")
        
        elif level == MemoryLevel.CRITICAL:
            suggestions.append("CRITICAL: Save your work immediately")
            suggestions.append("Close all non-essential datasets")
            suggestions.append("Restart application recommended")
            if not self._low_memory_mode:
                suggestions.append("Low memory mode will be enabled automatically")
        
        return suggestions
    
    def estimate_file_memory(self, file_path: str | Path) -> float:
        """
        Estimate memory needed to load a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Estimated memory in MB
        """
        path = Path(file_path)
        if not path.exists():
            return 0
        
        # Get file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        
        # Estimate: file size + overhead for parsing + data structures
        # Conservative estimate: 3x file size
        estimated_mb = file_size_mb * 3
        
        return estimated_mb
    
    def can_load_file(self, file_path: str | Path) -> tuple[bool, str | None]:
        """
        Check if file can be safely loaded.
        
        Args:
            file_path: Path to file
        
        Returns:
            Tuple of (can_load, warning_message)
        """
        if not PSUTIL_AVAILABLE:
            return (True, None)
        
        estimated_mb = self.estimate_file_memory(file_path)
        status = self.get_status()
        
        # Check if we have enough available memory
        if estimated_mb > status.available_mb:
            return (
                False,
                f"Not enough memory. Need ~{estimated_mb:.1f}MB, only {status.available_mb:.1f}MB available.",
            )
        
        # Check if loading would exceed hard limit
        hard_limit_mb = status.total_mb * (self._config.hard_limit_percent / 100)
        projected_usage = status.process_mb + estimated_mb
        
        if projected_usage > hard_limit_mb:
            return (
                False,
                f"Would exceed memory limit ({self._config.hard_limit_percent}% of {status.total_mb:.0f}MB). "
                f"Loading would use ~{projected_usage:.1f}MB.",
            )
        
        # Generate warning if it would push us into high/critical
        projected_percent = ((status.total_mb - status.available_mb + estimated_mb) / status.total_mb) * 100
        
        if projected_percent >= self._config.high_threshold:
            level = "CRITICAL" if projected_percent >= self._config.critical_threshold else "HIGH"
            return (
                True,
                f"WARNING: Loading this file (~{estimated_mb:.1f}MB) will push memory to {level} level "
                f"({projected_percent:.1f}%). Consider closing other datasets first.",
            )
        
        return (True, None)
    
    def force_gc(self) -> int:
        """
        Force garbage collection.
        
        Returns:
            Number of objects collected
        """
        collected = gc.collect()
        return collected
    
    def enable_low_memory_mode(self) -> None:
        """Enable low memory mode."""
        if self._low_memory_mode:
            return
        
        self._low_memory_mode = True
        
        # Trigger aggressive garbage collection
        gc.set_threshold(700, 10, 10)  # More aggressive
        self.force_gc()
    
    def disable_low_memory_mode(self) -> None:
        """Disable low memory mode."""
        if not self._low_memory_mode:
            return
        
        self._low_memory_mode = False
        
        # Reset to default thresholds
        gc.set_threshold(700, 10, 10)
    
    def is_low_memory_mode(self) -> bool:
        """Check if in low memory mode."""
        return self._low_memory_mode
    
    def add_status_callback(self, callback: Callable[[MemoryStatus], None]) -> None:
        """
        Add callback for status updates.
        
        Args:
            callback: Function called with MemoryStatus
        """
        self._status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[MemoryStatus], None]) -> None:
        """Remove status callback."""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    def add_level_change_callback(
        self,
        level: MemoryLevel,
        callback: Callable[[], None],
    ) -> None:
        """
        Add callback for specific level changes.
        
        Args:
            level: Memory level to watch
            callback: Function called when level is reached
        """
        self._level_change_callbacks[level].append(callback)
    
    def _on_level_changed(self, new_level: MemoryLevel) -> None:
        """Handle level change."""
        for callback in self._level_change_callbacks[new_level]:
            try:
                callback()
            except Exception:
                pass
    
    @property
    def current_status(self) -> MemoryStatus | None:
        """Get current cached status."""
        return self._current_status
    
    @property
    def is_monitoring(self) -> bool:
        """Check if monitoring is active."""
        return self._monitoring


# Global instance
_memory_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def initialize_memory_manager(
    config: MemoryConfig | None = None,
    start_monitoring: bool = True,
) -> MemoryManager:
    """Initialize and optionally start memory manager."""
    manager = get_memory_manager()
    
    if config:
        manager.configure(config)
    
    if start_monitoring:
        manager.start_monitoring()
    
    return manager
