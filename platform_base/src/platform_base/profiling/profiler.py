"""
Sistema de profiling automático conforme PRD seção 10.6

Features:
- Profiling automático com thresholds
- Monitoramento de memory usage  
- Relatórios detalhados
- Performance targets validation
"""

import cProfile
import pstats
import time
import tracemalloc
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from contextlib import contextmanager
from dataclasses import dataclass

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProfilingResult:
    """Resultado de uma sessão de profiling"""
    function_name: str
    duration_seconds: float
    memory_peak_mb: float
    memory_current_mb: float
    cpu_stats: Dict[str, Any]
    performance_target_met: bool
    metadata: Dict[str, Any]


class Profiler:
    """
    Profiler base para análise de performance
    
    Suporta profiling de CPU e memory com thresholds configuráveis
    """
    
    def __init__(self, output_dir: str = "profiling_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self._active = False
        
    @contextmanager
    def profile_cpu(self, name: str):
        """Context manager para profiling de CPU"""
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.perf_counter()
        
        try:
            yield profiler
        finally:
            end_time = time.perf_counter()
            profiler.disable()
            
            duration = end_time - start_time
            
            # Salva stats se duração excede threshold
            if duration > 0.1:  # Default threshold
                stats_file = self.output_dir / f"{name}_{int(time.time())}.prof"
                profiler.dump_stats(str(stats_file))
                logger.info("cpu_profile_saved", 
                          name=name, 
                          duration=duration,
                          file=str(stats_file))
                
    @contextmanager 
    def profile_memory(self, name: str):
        """Context manager para profiling de memory"""
        tracemalloc.start()
        
        try:
            yield
        finally:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            current_mb = current / 1024 / 1024
            peak_mb = peak / 1024 / 1024
            
            # Log se memory usage significativo
            if peak_mb > 10:  # Default threshold 10MB
                logger.info("memory_profile", 
                          name=name,
                          peak_mb=peak_mb,
                          current_mb=current_mb)

    def analyze_stats(self, stats_file: str) -> Dict[str, Any]:
        """Analisa arquivo de stats e retorna métricas"""
        stats = pstats.Stats(stats_file)
        stats.sort_stats('cumulative')
        
        # Top 10 funções mais custosas
        top_functions = []
        for func_info, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:10]:
            filename, line, func_name = func_info
            top_functions.append({
                "function": func_name,
                "filename": filename,
                "line": line,
                "total_time": tt,
                "cumulative_time": ct,
                "calls": nc
            })
            
        return {
            "total_time": stats.total_tt,
            "function_count": len(stats.stats),
            "top_functions": top_functions
        }


class AutoProfiler:
    """
    Profiler automático que monitora performance targets conforme PRD
    
    Features:
    - Profiling automático baseado em thresholds
    - Validação de performance targets
    - Geração automática de relatórios
    - Integração com configurações YAML
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.automatic = config.get("automatic", True)
        self.threshold_seconds = config.get("threshold_seconds", 1.0)
        self.output_dir = Path(config.get("output_dir", "profiling_reports"))
        self.targets = {t["name"]: t for t in config.get("targets", [])}
        self.memory_config = config.get("memory", {})
        
        self.output_dir.mkdir(exist_ok=True)
        self.profiler = Profiler(str(self.output_dir))
        
        self._results: List[ProfilingResult] = []
        
        if self.enabled:
            logger.info("auto_profiler_enabled", 
                       threshold=self.threshold_seconds,
                       targets=list(self.targets.keys()))
    
    def profile_function(self, 
                        func: Callable, 
                        *args, 
                        target_name: Optional[str] = None,
                        **kwargs) -> Any:
        """
        Executa função com profiling automático
        
        Args:
            func: Função a ser executada
            target_name: Nome do target de performance (opcional)
            *args, **kwargs: Argumentos da função
        """
        if not self.enabled:
            return func(*args, **kwargs)
            
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Setup memory profiling se habilitado
        memory_enabled = self.memory_config.get("enabled", False)
        memory_threshold_mb = self.memory_config.get("threshold_mb", 100)
        
        if memory_enabled:
            tracemalloc.start()
            
        # Setup CPU profiling
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            profiler.disable()
            
            duration = end_time - start_time
            
            # Memory stats
            memory_peak_mb = 0
            memory_current_mb = 0
            if memory_enabled:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                memory_current_mb = current / 1024 / 1024
                memory_peak_mb = peak / 1024 / 1024
            
            # Verifica se deve fazer profiling detalhado
            should_profile = (
                self.automatic and 
                duration >= self.threshold_seconds
            ) or (
                memory_enabled and 
                memory_peak_mb >= memory_threshold_mb
            )
            
            if should_profile:
                self._save_detailed_profile(
                    func_name, profiler, duration, 
                    memory_peak_mb, memory_current_mb
                )
            
            # Verifica performance targets
            target_met = True
            if target_name and target_name in self.targets:
                target = self.targets[target_name]
                max_time = target.get("max_time", float("inf"))
                target_met = duration <= max_time
                
                if not target_met:
                    logger.warning("performance_target_missed",
                                 target=target_name,
                                 expected_max=max_time,
                                 actual=duration)
            
            # Salva resultado
            prof_result = ProfilingResult(
                function_name=func_name,
                duration_seconds=duration,
                memory_peak_mb=memory_peak_mb,
                memory_current_mb=memory_current_mb,
                cpu_stats=self._extract_cpu_stats(profiler),
                performance_target_met=target_met,
                metadata={
                    "target_name": target_name,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
            )
            
            self._results.append(prof_result)
            
            # Log básico sempre
            logger.info("function_profiled",
                       function=func_name,
                       duration=duration,
                       memory_peak_mb=memory_peak_mb,
                       target_met=target_met)
        
        return result
    
    def _save_detailed_profile(self, 
                              func_name: str, 
                              profiler: cProfile.Profile,
                              duration: float,
                              memory_peak_mb: float,
                              memory_current_mb: float):
        """Salva profiling detalhado para análise posterior"""
        timestamp = int(time.time())
        base_name = f"{func_name.replace('.', '_')}_{timestamp}"
        
        # Salva stats raw
        stats_file = self.output_dir / f"{base_name}.prof"
        profiler.dump_stats(str(stats_file))
        
        # Gera relatório text se configurado
        if "stats" in self.config.get("formats", []):
            text_file = self.output_dir / f"{base_name}.txt"
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                stats.print_stats()
                with open(text_file, 'w') as f:
                    f.write(sys.stdout.getvalue())
            finally:
                sys.stdout = old_stdout
        
        logger.debug("detailed_profile_saved",
                    function=func_name,
                    stats_file=str(stats_file),
                    duration=duration,
                    memory_peak_mb=memory_peak_mb)
    
    def _extract_cpu_stats(self, profiler: cProfile.Profile) -> Dict[str, Any]:
        """Extrai estatísticas básicas do profiler"""
        stats = pstats.Stats(profiler)
        
        return {
            "total_time": stats.total_tt,
            "function_count": len(stats.stats),
            "primitive_call_count": stats.prim_calls,
            "total_call_count": stats.total_calls
        }
    
    def get_results(self, function_name: Optional[str] = None) -> List[ProfilingResult]:
        """Obtém resultados de profiling"""
        if function_name:
            return [r for r in self._results if r.function_name == function_name]
        return self._results.copy()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Gera relatório sumário de performance"""
        if not self._results:
            return {"message": "No profiling data available"}
            
        # Agrupa por função
        by_function = {}
        for result in self._results:
            fname = result.function_name
            if fname not in by_function:
                by_function[fname] = []
            by_function[fname].append(result)
        
        # Calcula estatísticas
        summary = {}
        for fname, results in by_function.items():
            durations = [r.duration_seconds for r in results]
            memory_peaks = [r.memory_peak_mb for r in results]
            
            summary[fname] = {
                "call_count": len(results),
                "duration_stats": {
                    "min": min(durations),
                    "max": max(durations),
                    "avg": sum(durations) / len(durations),
                    "total": sum(durations)
                },
                "memory_stats": {
                    "min_peak": min(memory_peaks) if memory_peaks else 0,
                    "max_peak": max(memory_peaks) if memory_peaks else 0,
                    "avg_peak": sum(memory_peaks) / len(memory_peaks) if memory_peaks else 0
                },
                "targets_met": sum(1 for r in results if r.performance_target_met),
                "targets_missed": sum(1 for r in results if not r.performance_target_met)
            }
        
        return {
            "total_functions": len(by_function),
            "total_calls": len(self._results),
            "functions": summary
        }
    
    def validate_performance_targets(self) -> Dict[str, bool]:
        """Valida se todos os performance targets estão sendo atendidos"""
        target_results = {}
        
        for target_name, target_config in self.targets.items():
            # Encontra resultados relacionados a este target
            target_results_list = [
                r for r in self._results 
                if r.metadata.get("target_name") == target_name
            ]
            
            if not target_results_list:
                target_results[target_name] = None  # Não testado ainda
                continue
            
            # Verifica se todos os resultados recentes atendem o target
            recent_results = target_results_list[-10:]  # Últimos 10
            all_met = all(r.performance_target_met for r in recent_results)
            target_results[target_name] = all_met
        
        return target_results
    
    def clear_results(self):
        """Limpa resultados armazenados"""
        self._results.clear()
        logger.info("profiling_results_cleared")


# Factory function
def create_auto_profiler_from_config(config: Dict[str, Any]) -> AutoProfiler:
    """Cria AutoProfiler a partir de configuração YAML"""
    return AutoProfiler(config)