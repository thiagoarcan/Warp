"""
Testes unitários para sistema de profiling automático conforme PRD.
"""
import pytest
import tempfile
import time
import numpy as np
from pathlib import Path

from platform_base.profiling.profiler import AutoProfiler, create_auto_profiler_from_config
from platform_base.profiling.decorators import profile, performance_critical, set_global_profiler
from platform_base.profiling.reports import generate_html_report, generate_json_report
from platform_base.profiling.setup import create_test_profiler


class TestAutoProfiler:
    """Testa sistema de profiling automático"""
    
    def test_profiler_creation_from_config(self):
        """Testa criação do profiler a partir de configuração"""
        config = {
            "enabled": True,
            "automatic": True,
            "threshold_seconds": 0.1,
            "output_dir": "test_profiling",
            "targets": [
                {
                    "name": "test_op",
                    "operation": "test",
                    "max_time": 1.0
                }
            ],
            "memory": {
                "enabled": True,
                "threshold_mb": 10
            }
        }
        
        profiler = create_auto_profiler_from_config(config)
        
        assert profiler.enabled is True
        assert profiler.automatic is True
        assert profiler.threshold_seconds == 0.1
        assert "test_op" in profiler.targets
        
    def test_function_profiling(self):
        """Testa profiling de função"""
        profiler = create_test_profiler()
        
        def slow_function(n):
            time.sleep(0.1)  # Simula operação custosa
            return sum(range(n))
        
        # Executa com profiling
        result = profiler.profile_function(slow_function, 100)
        
        # Verifica resultado
        assert result == sum(range(100))
        
        # Verifica se foi registrado
        results = profiler.get_results()
        assert len(results) == 1
        assert results[0].duration_seconds >= 0.1
        assert "slow_function" in results[0].function_name
        
    def test_performance_targets(self):
        """Testa validação de performance targets"""
        config = {
            "enabled": True,
            "automatic": True,
            "threshold_seconds": 0.01,
            "output_dir": "test_profiling",
            "targets": [
                {
                    "name": "fast_target",
                    "operation": "fast",
                    "max_time": 1.0
                },
                {
                    "name": "slow_target", 
                    "operation": "slow",
                    "max_time": 0.05
                }
            ]
        }
        
        profiler = create_auto_profiler_from_config(config)
        
        def fast_function():
            time.sleep(0.01)
            return 42
            
        def slow_function():
            time.sleep(0.1)
            return 42
        
        # Testa target rápido (deve passar)
        profiler.profile_function(fast_function, target_name="fast_target")
        
        # Testa target lento (deve falhar)
        profiler.profile_function(slow_function, target_name="slow_target")
        
        results = profiler.get_results()
        
        # Verifica targets
        fast_result = [r for r in results if r.metadata.get("target_name") == "fast_target"][0]
        slow_result = [r for r in results if r.metadata.get("target_name") == "slow_target"][0]
        
        assert fast_result.performance_target_met is True
        assert slow_result.performance_target_met is False
        
    def test_memory_profiling(self):
        """Testa profiling de memory"""
        config = {
            "enabled": True,
            "threshold_seconds": 0.01,
            "output_dir": "test_profiling",
            "memory": {
                "enabled": True,
                "threshold_mb": 1,
                "track_allocations": True
            }
        }
        
        profiler = create_auto_profiler_from_config(config)
        
        def memory_intensive_function():
            # Cria array grande para consumir memória
            data = np.random.randn(100000)  # ~800KB
            return np.sum(data)
        
        result = profiler.profile_function(memory_intensive_function)
        
        profiling_results = profiler.get_results()
        assert len(profiling_results) == 1
        assert profiling_results[0].memory_peak_mb > 0
        
    def test_summary_report_generation(self):
        """Testa geração de relatório sumário"""
        profiler = create_test_profiler()
        
        def test_function(x):
            time.sleep(0.01)
            return x * 2
        
        # Executa várias vezes
        for i in range(3):
            profiler.profile_function(test_function, i)
        
        summary = profiler.generate_summary_report()
        
        assert summary["total_functions"] == 1
        assert summary["total_calls"] == 3
        # Function is registered with full module path
        assert "test_profiling.test_function" in summary["functions"]
        
        func_stats = summary["functions"]["test_profiling.test_function"]
        assert func_stats["call_count"] == 3
        assert "duration_stats" in func_stats
        assert "memory_stats" in func_stats


class TestProfilingDecorators:
    """Testa decoradores de profiling"""
    
    def test_profile_decorator(self):
        """Testa decorator @profile"""
        profiler = create_test_profiler()
        set_global_profiler(profiler)
        
        @profile(target_name="test_interpolation")
        def decorated_function(n):
            time.sleep(0.01)
            return n ** 2
        
        result = decorated_function(5)
        
        assert result == 25
        
        results = profiler.get_results()
        assert len(results) == 1
        assert results[0].metadata.get("target_name") == "test_interpolation"
        
    def test_performance_critical_decorator(self):
        """Testa decorator @performance_critical"""
        
        @performance_critical(max_time_seconds=0.05, operation_name="test_op")
        def fast_function():
            time.sleep(0.01)
            return "fast"
        
        @performance_critical(max_time_seconds=0.05, operation_name="test_op")
        def slow_function():
            time.sleep(0.1)
            return "slow"
        
        # Estas devem executar sem erro
        # Os warnings/logs serão verificados pelos testes de logging
        result1 = fast_function()
        result2 = slow_function()
        
        assert result1 == "fast"
        assert result2 == "slow"


class TestProfilingReports:
    """Testa geração de relatórios"""
    
    def test_html_report_generation(self):
        """Testa geração de relatório HTML"""
        profiler = create_test_profiler()
        
        def test_func():
            time.sleep(0.01)
            return 42
        
        # Gera alguns resultados
        for _ in range(3):
            profiler.profile_function(test_func)
        
        results = profiler.get_results()
        
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            generate_html_report(results, f.name)
            
            # Verifica que arquivo foi criado
            html_path = Path(f.name)
            assert html_path.exists()
            
            # Verifica conteúdo básico
            content = html_path.read_text(encoding='utf-8')
            assert "Platform Base" in content
            assert "Profiling Report" in content
            assert "test_func" in content
            
        # Cleanup
        html_path.unlink()
        
    def test_json_report_generation(self):
        """Testa geração de relatório JSON"""
        profiler = create_test_profiler()
        
        def test_func():
            time.sleep(0.01) 
            return 42
        
        # Gera resultados
        profiler.profile_function(test_func)
        results = profiler.get_results()
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            generate_json_report(results, f.name)
            
            # Verifica que arquivo foi criado
            json_path = Path(f.name)
            assert json_path.exists()
            
            # Verifica que é JSON válido
            import json
            with open(json_path) as jf:
                data = json.load(jf)
            
            assert "generated_at" in data
            assert "total_functions" in data
            assert "functions" in data
            
        # Cleanup
        json_path.unlink()


class TestPerformanceTargets:
    """Testa validação de performance targets específicos do PRD"""
    
    def test_interpolation_target_1m_points(self):
        """Testa target de interpolação: 1M pontos < 2s"""
        # Este é um teste conceitual - na prática precisa de dados reais
        config = {
            "enabled": True,
            "targets": [
                {
                    "name": "interpolation_1m",
                    "operation": "interpolate",
                    "points": 1000000,
                    "max_time": 2.0
                }
            ]
        }
        
        profiler = create_auto_profiler_from_config(config)
        
        def mock_interpolation():
            # Simula interpolação rápida
            time.sleep(0.5)  # 500ms - dentro do target
            return np.random.randn(1000000)
        
        profiler.profile_function(
            mock_interpolation, 
            target_name="interpolation_1m"
        )
        
        results = profiler.get_results()
        assert len(results) == 1
        assert results[0].performance_target_met is True
        
    def test_derivative_target_1m_points(self):
        """Testa target de derivada: 1M pontos < 1s"""
        config = {
            "enabled": True,
            "targets": [
                {
                    "name": "derivative_1m",
                    "operation": "derivative", 
                    "points": 1000000,
                    "max_time": 1.0
                }
            ]
        }
        
        profiler = create_auto_profiler_from_config(config)
        
        def mock_derivative():
            # Simula derivada rápida
            time.sleep(0.2)  # 200ms - dentro do target
            return np.random.randn(1000000)
        
        profiler.profile_function(
            mock_derivative,
            target_name="derivative_1m"
        )
        
        results = profiler.get_results()
        assert len(results) == 1
        assert results[0].performance_target_met is True
        
    def test_target_validation_summary(self):
        """Testa validação sumária de todos os targets"""
        config = {
            "enabled": True,
            "targets": [
                {
                    "name": "fast_op",
                    "max_time": 1.0
                },
                {
                    "name": "slow_op", 
                    "max_time": 0.1
                }
            ]
        }
        
        profiler = create_auto_profiler_from_config(config)
        
        # Op rápida (passa)
        def fast_op():
            time.sleep(0.05)
            return True
            
        # Op lenta (falha) 
        def slow_op():
            time.sleep(0.2)
            return True
        
        profiler.profile_function(fast_op, target_name="fast_op")
        profiler.profile_function(slow_op, target_name="slow_op") 
        
        target_results = profiler.validate_performance_targets()
        
        assert target_results["fast_op"] is True
        assert target_results["slow_op"] is False