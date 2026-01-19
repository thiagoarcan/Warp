"""
Decoradores para profiling automático conforme PRD

Provides decorators for automatic function profiling
"""

import functools
from typing import Optional, Dict, Any, Callable

from .profiler import AutoProfiler


# Global profiler instance - será inicializado pela aplicação
_global_profiler: Optional[AutoProfiler] = None


def set_global_profiler(profiler: AutoProfiler):
    """Define o profiler global para uso nos decoradores"""
    global _global_profiler
    _global_profiler = profiler


def profile(target_name: Optional[str] = None, 
           enabled: bool = True):
    """
    Decorator para profiling automático de funções
    
    Args:
        target_name: Nome do target de performance para validação
        enabled: Se o profiling está habilitado (permite desabilitar via config)
    
    Usage:
        @profile(target_name="interpolation_1m")
        def interpolate_large_dataset():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not enabled or _global_profiler is None:
                return func(*args, **kwargs)
            
            return _global_profiler.profile_function(
                func, *args, target_name=target_name, **kwargs
            )
        
        return wrapper
    return decorator


def memory_profile(threshold_mb: float = 100.0):
    """
    Decorator específico para profiling de memory
    
    Args:
        threshold_mb: Threshold de memory para logging detalhado
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import tracemalloc
            
            if _global_profiler is None or not _global_profiler.memory_config.get("enabled"):
                return func(*args, **kwargs)
            
            tracemalloc.start()
            
            try:
                result = func(*args, **kwargs)
            finally:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                current_mb = current / 1024 / 1024
                peak_mb = peak / 1024 / 1024
                
                if peak_mb > threshold_mb:
                    from platform_base.utils.logging import get_logger
                    logger = get_logger(__name__)
                    logger.warning("high_memory_usage",
                                 function=f"{func.__module__}.{func.__name__}",
                                 peak_mb=peak_mb,
                                 current_mb=current_mb,
                                 threshold_mb=threshold_mb)
            
            return result
        
        return wrapper
    return decorator


def performance_critical(max_time_seconds: float, 
                        operation_name: Optional[str] = None):
    """
    Decorator para funções críticas de performance
    
    Args:
        max_time_seconds: Tempo máximo esperado
        operation_name: Nome da operação para logging
    
    Usage:
        @performance_critical(max_time_seconds=2.0, operation_name="interpolation")
        def interpolate():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            from platform_base.utils.logging import get_logger
            
            logger = get_logger(__name__)
            op_name = operation_name or func.__name__
            
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start_time
                
                if duration > max_time_seconds:
                    logger.warning("performance_critical_exceeded",
                                 operation=op_name,
                                 function=f"{func.__module__}.{func.__name__}",
                                 duration=duration,
                                 max_expected=max_time_seconds,
                                 ratio=duration / max_time_seconds)
                else:
                    logger.debug("performance_critical_ok",
                               operation=op_name,
                               function=f"{func.__module__}.{func.__name__}",
                               duration=duration,
                               max_expected=max_time_seconds)
            
            return result
        
        return wrapper
    return decorator