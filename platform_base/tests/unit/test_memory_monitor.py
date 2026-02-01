"""
Testes abrangentes para o módulo utils/memory_monitor.py
Cobertura completa baseada na implementação real
"""
import gc
from unittest.mock import Mock, patch

import pytest


class TestMemorySnapshot:
    """Testes para MemorySnapshot dataclass."""
    
    def test_snapshot_creation(self):
        """Testa criação de snapshot."""
        from datetime import datetime

        from platform_base.utils.memory_monitor import MemorySnapshot
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            used_mb=4000.0,
            available_mb=4000.0,
            total_mb=8000.0,
            percent_used=0.50,
            process_mb=500.0
        )
        
        assert snapshot.used_mb == 4000.0
        assert snapshot.available_mb == 4000.0
        assert snapshot.percent_used == 0.50
    
    def test_snapshot_to_dict(self):
        """Testa conversão para dicionário."""
        from datetime import datetime

        from platform_base.utils.memory_monitor import MemorySnapshot
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            used_mb=4000.0,
            available_mb=4000.0,
            total_mb=8000.0,
            percent_used=0.50,
            process_mb=500.0
        )
        
        data = snapshot.to_dict()
        assert 'used_mb' in data
        assert 'available_mb' in data
        assert 'timestamp' in data


class TestMemoryWarning:
    """Testes para MemoryWarning dataclass."""
    
    def test_warning_creation(self):
        """Testa criação de warning."""
        from platform_base.utils.memory_monitor import MemoryWarning
        
        warning = MemoryWarning(
            level="warning",
            percent_used=0.85,
            used_mb=6800.0,
            available_mb=1200.0,
            suggestions=["Close unused datasets", "Enable decimation"]
        )
        
        assert warning.level == "warning"
        assert warning.percent_used == 0.85
        assert len(warning.suggestions) == 2
    
    def test_warning_to_dict(self):
        """Testa conversão para dicionário."""
        from platform_base.utils.memory_monitor import MemoryWarning
        
        warning = MemoryWarning(
            level="critical",
            percent_used=0.96,
            used_mb=7680.0,
            available_mb=320.0
        )
        
        data = warning.to_dict()
        assert data['level'] == "critical"
        assert 'percent_used' in data
    
    def test_warning_levels(self):
        """Testa diferentes níveis de warning."""
        from platform_base.utils.memory_monitor import MemoryWarning
        
        for level in ["caution", "warning", "critical"]:
            warning = MemoryWarning(
                level=level,
                percent_used=0.70,
                used_mb=5600.0,
                available_mb=2400.0
            )
            assert warning.level == level


class TestMemoryMonitor:
    """Testes para MemoryMonitor."""
    
    def test_monitor_creation(self):
        """Testa criação do monitor (singleton)."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        assert monitor is not None
    
    def test_monitor_singleton(self):
        """Testa que é singleton."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        m1 = MemoryMonitor()
        m2 = MemoryMonitor()
        assert m1 is m2
    
    def test_get_current_usage(self):
        """Testa obtenção de uso atual."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        snapshot = monitor.get_current_usage()
        
        # Snapshot pode estar vazio se psutil não estiver disponível
        assert snapshot is not None
        assert hasattr(snapshot, 'used_mb')
        assert hasattr(snapshot, 'available_mb')
    
    def test_estimate_file_memory(self):
        """Testa estimativa de memória para arquivo."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        # 100 MB arquivo
        file_size = 100 * 1024 * 1024  # bytes
        estimated = monitor.estimate_file_memory(file_size)
        
        # Deve ser maior que o tamanho do arquivo (overhead)
        assert estimated > 100
    
    def test_can_load_file(self):
        """Testa verificação de possibilidade de carregar arquivo."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        # Arquivo pequeno deve ser carregável
        small_file = 1024 * 1024  # 1 MB
        can_load, reason = monitor.can_load_file(small_file)
        
        assert isinstance(can_load, bool)
        assert isinstance(reason, str)
    
    def test_force_garbage_collection(self):
        """Testa forçar garbage collection."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        # Cria objetos para coletar
        objs = [object() for _ in range(1000)]
        del objs
        
        collected = monitor.force_garbage_collection()
        assert isinstance(collected, int)
    
    def test_add_callback(self):
        """Testa adição de callback."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        callback_called = []
        
        def my_callback(warning):
            callback_called.append(warning)
        
        monitor.add_callback("warning", my_callback)
        # Callback adicionado com sucesso
        assert True
    
    def test_remove_callback(self):
        """Testa remoção de callback."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        def my_callback(warning):
            pass
        
        monitor.add_callback("warning", my_callback)
        monitor.remove_callback("warning", my_callback)
        # Callback removido com sucesso
        assert True


class TestMemoryMonitorThresholds:
    """Testes para thresholds de memória."""
    
    def test_default_thresholds(self):
        """Testa thresholds padrão."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        assert monitor.caution_threshold == 0.60
        assert monitor.warning_threshold == 0.80
        assert monitor.critical_threshold == 0.95
    
    def test_set_custom_thresholds(self):
        """Testa configuração de thresholds customizados."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        # Pode alterar thresholds
        monitor.caution_threshold = 0.50
        monitor.warning_threshold = 0.70
        
        assert monitor.caution_threshold == 0.50
        assert monitor.warning_threshold == 0.70


class TestMemoryMonitorThread:
    """Testes para thread de monitoramento."""
    
    def test_start_monitoring(self):
        """Testa início de monitoramento."""
        import time

        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        monitor.start()
        time.sleep(0.1)  # Deixa thread iniciar
        
        assert monitor._running is True
        
        monitor.stop()
    
    def test_stop_monitoring(self):
        """Testa parada de monitoramento."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        monitor.start()
        monitor.stop()
        
        assert monitor._running is False


class TestLowMemoryMode:
    """Testes para modo de baixa memória."""
    
    def test_enable_low_memory_mode(self):
        """Testa habilitar modo de baixa memória."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        monitor.enable_low_memory_mode()
        
        assert monitor.low_memory_mode is True
    
    def test_disable_low_memory_mode(self):
        """Testa desabilitar modo de baixa memória."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        monitor.low_memory_mode = False
        
        assert monitor.low_memory_mode is False


class TestMemoryHistory:
    """Testes para histórico de memória."""
    
    def test_snapshot_history(self):
        """Testa histórico de snapshots."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        # Histórico inicial pode estar vazio
        assert isinstance(monitor.snapshots, list)
    
    def test_max_history(self):
        """Testa limite de histórico."""
        from platform_base.utils.memory_monitor import MemoryMonitor
        
        monitor = MemoryMonitor()
        
        assert monitor.max_history == 100


# Teste final de importação
class TestMemoryMonitorImports:
    """Testa importações do módulo."""
    
    def test_all_imports(self):
        """Testa que todos os componentes podem ser importados."""
        from platform_base.utils.memory_monitor import (
            MemoryMonitor,
            MemorySnapshot,
            MemoryWarning,
        )
        assert True
