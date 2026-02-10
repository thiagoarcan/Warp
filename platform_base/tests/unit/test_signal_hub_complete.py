"""
Testes completos para desktop/signal_hub.py - Platform Base v2.0

Cobertura de 100% das funcionalidades do hub de sinais.
"""

from unittest.mock import MagicMock

import pytest

# Mock PyQt6 before importing
pytest.importorskip("PyQt6")


class TestSignalHub:
    """Testes para SignalHub"""
    
    def test_creation(self):
        """Testa criação de SignalHub"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        assert hub is not None
        assert hub._signal_counts == {}
    
    def test_creation_with_parent(self):
        """Testa criação com parent"""
        from PyQt6.QtCore import QObject

        from platform_base.desktop.signal_hub import SignalHub
        
        parent = QObject()
        hub = SignalHub(parent)
        
        assert hub.parent() is parent
    
    def test_emit_dataset_loaded(self):
        """Testa emissão de dataset_loaded"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.dataset_loaded.connect(lambda x: received.append(x))
        
        hub.emit_dataset_loaded("dataset_123")
        
        assert len(received) == 1
        assert received[0] == "dataset_123"
        assert hub._signal_counts.get("dataset_loaded", 0) == 1
    
    def test_emit_series_selected(self):
        """Testa emissão de series_selected"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.series_selected.connect(lambda d, s: received.append((d, s)))
        
        hub.emit_series_selected("dataset_1", "series_1")
        
        assert len(received) == 1
        assert received[0] == ("dataset_1", "series_1")
    
    def test_emit_time_selection(self):
        """Testa emissão de time_selection_changed"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.time_selection_changed.connect(lambda s, e: received.append((s, e)))
        
        hub.emit_time_selection(0.0, 100.0)
        
        assert len(received) == 1
        assert received[0] == (0.0, 100.0)
    
    def test_emit_operation_started(self):
        """Testa emissão de operation_started"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.operation_started.connect(lambda t, i: received.append((t, i)))
        
        hub.emit_operation_started("interpolation", "op_123")
        
        assert len(received) == 1
        assert received[0] == ("interpolation", "op_123")
    
    def test_emit_operation_progress(self):
        """Testa emissão de operation_progress (não loga)"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.operation_progress.connect(lambda i, p: received.append((i, p)))
        
        hub.emit_operation_progress("op_123", 50)
        
        assert len(received) == 1
        assert received[0] == ("op_123", 50)
        # Não deve incrementar contador (para evitar spam)
    
    def test_emit_operation_completed(self):
        """Testa emissão de operation_completed"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.operation_completed.connect(lambda i, r: received.append((i, r)))
        
        result = {"status": "success", "data": [1, 2, 3]}
        hub.emit_operation_completed("op_123", result)
        
        assert len(received) == 1
        assert received[0][0] == "op_123"
        assert received[0][1]["status"] == "success"
    
    def test_emit_error(self):
        """Testa emissão de error"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.error_occurred.connect(lambda t, m: received.append((t, m)))
        
        hub.emit_error("ValidationError", "Invalid data format")
        
        assert len(received) == 1
        assert received[0] == ("ValidationError", "Invalid data format")
    
    def test_emit_status_update(self):
        """Testa emissão de status_update (não loga)"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        received = []
        hub.status_updated.connect(lambda m: received.append(m))
        
        hub.emit_status_update("Processing...")
        
        assert len(received) == 1
        assert received[0] == "Processing..."
    
    def test_get_signal_stats(self):
        """Testa obtenção de estatísticas de sinais"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        hub.emit_dataset_loaded("d1")
        hub.emit_dataset_loaded("d2")
        hub.emit_series_selected("d1", "s1")
        
        stats = hub.get_signal_stats()
        
        assert stats["dataset_loaded"] == 2
        assert stats["series_selected"] == 1
    
    def test_signal_stats_is_copy(self):
        """Testa que stats é cópia"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        hub.emit_dataset_loaded("d1")
        
        stats1 = hub.get_signal_stats()
        stats1["dataset_loaded"] = 999  # Modifica cópia
        
        stats2 = hub.get_signal_stats()
        assert stats2["dataset_loaded"] == 1  # Original não alterado


class TestSignalHubSignals:
    """Testes para todos os sinais definidos"""
    
    def test_all_signals_exist(self):
        """Testa que todos os sinais existem"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        # Dataset management signals
        assert hasattr(hub, 'dataset_loaded')
        assert hasattr(hub, 'dataset_removed')
        assert hasattr(hub, 'dataset_selected')
        
        # Series management signals
        assert hasattr(hub, 'series_added')
        assert hasattr(hub, 'series_removed')
        assert hasattr(hub, 'series_selected')
        assert hasattr(hub, 'series_deselected')
        
        # Visualization signals
        assert hasattr(hub, 'plot_created')
        assert hasattr(hub, 'plot_updated')
        assert hasattr(hub, 'plot_closed')
        assert hasattr(hub, 'view_synchronized')
        
        # Selection signals
        assert hasattr(hub, 'time_selection_changed')
        assert hasattr(hub, 'value_selection_changed')
        assert hasattr(hub, 'selection_cleared')
        
        # Processing signals
        assert hasattr(hub, 'operation_started')
        assert hasattr(hub, 'operation_progress')
        assert hasattr(hub, 'operation_completed')
        assert hasattr(hub, 'operation_failed')
        
        # Streaming signals
        assert hasattr(hub, 'streaming_started')
        assert hasattr(hub, 'streaming_stopped')
        assert hasattr(hub, 'streaming_paused')
        assert hasattr(hub, 'streaming_time_changed')
        
        # UI state signals
        assert hasattr(hub, 'ui_mode_changed')
        assert hasattr(hub, 'theme_changed')
        assert hasattr(hub, 'layout_changed')
        
        # Error/status signals
        assert hasattr(hub, 'error_occurred')
        assert hasattr(hub, 'status_updated')
        assert hasattr(hub, 'progress_updated')
    
    def test_direct_signal_emission(self):
        """Testa emissão direta de sinais"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        received = []
        hub.dataset_removed.connect(lambda x: received.append(x))
        hub.dataset_removed.emit("dataset_123")
        
        assert len(received) == 1
        assert received[0] == "dataset_123"
    
    def test_streaming_signals(self):
        """Testa sinais de streaming"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        started = []
        stopped = []
        paused = []
        time_changed = []
        
        hub.streaming_started.connect(lambda: started.append(True))
        hub.streaming_stopped.connect(lambda: stopped.append(True))
        hub.streaming_paused.connect(lambda: paused.append(True))
        hub.streaming_time_changed.connect(lambda t: time_changed.append(t))
        
        hub.streaming_started.emit()
        hub.streaming_time_changed.emit(50.0)
        hub.streaming_paused.emit()
        hub.streaming_stopped.emit()
        
        assert len(started) == 1
        assert len(paused) == 1
        assert len(stopped) == 1
        assert time_changed == [50.0]
    
    def test_ui_signals(self):
        """Testa sinais de UI"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        modes = []
        themes = []
        layouts = []
        
        hub.ui_mode_changed.connect(lambda m: modes.append(m))
        hub.theme_changed.connect(lambda t: themes.append(t))
        hub.layout_changed.connect(lambda l: layouts.append(l))
        
        hub.ui_mode_changed.emit("stream")
        hub.theme_changed.emit("dark")
        hub.layout_changed.emit("compact")
        
        assert modes == ["stream"]
        assert themes == ["dark"]
        assert layouts == ["compact"]


class TestSignalHubMultipleConnections:
    """Testes para múltiplas conexões"""
    
    def test_multiple_handlers(self):
        """Testa múltiplos handlers para mesmo sinal"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        received1 = []
        received2 = []
        
        hub.dataset_loaded.connect(lambda x: received1.append(x))
        hub.dataset_loaded.connect(lambda x: received2.append(x))
        
        hub.emit_dataset_loaded("dataset_123")
        
        assert len(received1) == 1
        assert len(received2) == 1
    
    def test_disconnect_specific_handler(self):
        """Testa desconectar handler específico"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        received1 = []
        received2 = []
        
        handler1 = lambda x: received1.append(x)
        handler2 = lambda x: received2.append(x)
        
        hub.dataset_loaded.connect(handler1)
        hub.dataset_loaded.connect(handler2)
        
        hub.dataset_loaded.disconnect(handler1)
        
        hub.emit_dataset_loaded("dataset_123")
        
        assert len(received1) == 0
        assert len(received2) == 1


class TestSignalHubCounting:
    """Testes para contagem de sinais"""
    
    def test_counting_increments(self):
        """Testa que contagem incrementa"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        for i in range(10):
            hub.emit_dataset_loaded(f"dataset_{i}")
        
        stats = hub.get_signal_stats()
        assert stats["dataset_loaded"] == 10
    
    def test_different_signals_counted_separately(self):
        """Testa que diferentes sinais são contados separadamente"""
        from platform_base.desktop.signal_hub import SignalHub
        
        hub = SignalHub()
        
        for i in range(5):
            hub.emit_dataset_loaded(f"d{i}")
        
        for i in range(3):
            hub.emit_series_selected(f"d{i}", f"s{i}")
        
        stats = hub.get_signal_stats()
        assert stats["dataset_loaded"] == 5
        assert stats["series_selected"] == 3
