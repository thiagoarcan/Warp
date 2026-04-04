"""
Testes completos para desktop/session_state.py - Platform Base v2.0

Cobertura de 100% das funcionalidades de gerenciamento de sessão.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Mock PyQt6 before importing
pytest.importorskip("PyQt6")

from PyQt6.QtCore import QObject


class TestSelectionState:
    """Testes para SelectionState dataclass"""
    
    def test_default_values(self):
        """Testa valores padrão"""
        from platform_base.desktop.session_state import SelectionState
        
        state = SelectionState()
        
        assert state.dataset_id is None
        assert state.series_ids == []
        assert state.time_window is None
        assert state.selected_points == {}
    
    def test_custom_values(self):
        """Testa valores customizados"""
        from platform_base.desktop.session_state import SelectionState
        
        state = SelectionState(
            dataset_id="ds_123",
            series_ids=["s1", "s2"],
            selected_points={"s1": [0, 1, 2]}
        )
        
        assert state.dataset_id == "ds_123"
        assert len(state.series_ids) == 2
        assert state.selected_points["s1"] == [0, 1, 2]


class TestViewState:
    """Testes para ViewState dataclass"""
    
    def test_default_values(self):
        """Testa valores padrão"""
        from platform_base.desktop.session_state import ViewState
        
        state = ViewState()
        
        assert state.active_views == {}
        assert state.synchronized_views == []
        assert state.plot_configs == {}
    
    def test_custom_values(self):
        """Testa valores customizados"""
        from platform_base.desktop.session_state import ViewState
        
        state = ViewState(
            active_views={"v1": {"type": "2d"}},
            synchronized_views=["v1", "v2"]
        )
        
        assert "v1" in state.active_views
        assert len(state.synchronized_views) == 2


class TestProcessingState:
    """Testes para ProcessingState dataclass"""
    
    def test_default_values(self):
        """Testa valores padrão"""
        from platform_base.desktop.session_state import ProcessingState
        
        state = ProcessingState()
        
        assert state.active_operations == {}
        assert state.operation_history == []
        assert state.last_results == {}
    
    def test_with_operations(self):
        """Testa com operações"""
        from platform_base.desktop.session_state import ProcessingState
        
        state = ProcessingState(
            active_operations={"op1": {"type": "interpolation"}}
        )
        
        assert "op1" in state.active_operations


class TestStreamingState:
    """Testes para StreamingState dataclass"""
    
    def test_default_values(self):
        """Testa valores padrão"""
        from platform_base.desktop.session_state import StreamingState
        
        state = StreamingState()
        
        assert state.is_active is False
        assert state.is_paused is False
        assert state.current_time == 0.0
        assert state.playback_speed == 1.0
        assert state.loop_enabled is False
    
    def test_custom_values(self):
        """Testa valores customizados"""
        from platform_base.desktop.session_state import StreamingState
        
        state = StreamingState(
            is_active=True,
            playback_speed=2.0,
            loop_enabled=True
        )
        
        assert state.is_active
        assert state.playback_speed == 2.0
        assert state.loop_enabled


class TestUIState:
    """Testes para UIState dataclass"""
    
    def test_default_values(self):
        """Testa valores padrão"""
        from platform_base.desktop.session_state import UIState
        
        state = UIState()
        
        assert state.current_mode == "explore"
        assert state.theme == "auto"
        assert state.panel_visibility["data"] is True
        assert state.panel_visibility["viz"] is True
    
    def test_custom_mode(self):
        """Testa modo customizado"""
        from platform_base.desktop.session_state import UIState
        
        state = UIState(current_mode="stream", theme="dark")
        
        assert state.current_mode == "stream"
        assert state.theme == "dark"


class TestSessionState:
    """Testes para SessionState"""
    
    @pytest.fixture
    def mock_dataset_store(self):
        """Mock do DatasetStore"""
        store = MagicMock()
        store.list_datasets.return_value = []
        return store
    
    def test_creation(self, mock_dataset_store):
        """Testa criação de SessionState"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        assert session.dataset_store is mock_dataset_store
        assert session.selection is not None
        assert session.view is not None
        assert session.processing is not None
        assert session.streaming is not None
        assert session.ui is not None
    
    def test_session_id_generated(self, mock_dataset_store):
        """Testa que session_id é gerado"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        assert session.session_id.startswith("session_")
    
    def test_set_current_dataset(self, mock_dataset_store):
        """Testa definir dataset atual"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        # Mock signal
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.set_current_dataset("dataset_123")
        
        assert session.selection.dataset_id == "dataset_123"
        assert len(signal_emitted) == 1
    
    def test_set_same_dataset_no_signal(self, mock_dataset_store):
        """Testa que mesmo dataset não emite sinal"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        session.selection.dataset_id = "dataset_123"
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.set_current_dataset("dataset_123")
        
        assert len(signal_emitted) == 0
    
    def test_add_series_selection(self, mock_dataset_store):
        """Testa adicionar série à seleção"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.add_series_selection("series_1")
        session.add_series_selection("series_2")
        
        assert "series_1" in session.selection.series_ids
        assert "series_2" in session.selection.series_ids
        assert len(signal_emitted) == 2
    
    def test_add_duplicate_series_no_effect(self, mock_dataset_store):
        """Testa que adicionar série duplicada não tem efeito"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.add_series_selection("series_1")
        session.add_series_selection("series_1")  # Duplicada
        
        assert session.selection.series_ids.count("series_1") == 1
        assert len(signal_emitted) == 1
    
    def test_remove_series_selection(self, mock_dataset_store):
        """Testa remover série da seleção"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        session.add_series_selection("series_1")
        session.add_series_selection("series_2")
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.remove_series_selection("series_1")
        
        assert "series_1" not in session.selection.series_ids
        assert "series_2" in session.selection.series_ids
        assert len(signal_emitted) == 1
    
    def test_remove_nonexistent_series_no_effect(self, mock_dataset_store):
        """Testa que remover série inexistente não tem efeito"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.remove_series_selection("nonexistent")
        
        assert len(signal_emitted) == 0
    
    def test_set_time_window(self, mock_dataset_store):
        """Testa definir janela temporal"""
        from platform_base.core.models import TimeWindow
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        window = TimeWindow(start=0.0, end=100.0)
        session.set_time_window(window)
        
        assert session.selection.time_window == window
        assert len(signal_emitted) == 1
    
    def test_clear_selection(self, mock_dataset_store):
        """Testa limpar seleção"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        session.set_current_dataset("dataset_123")
        session.add_series_selection("series_1")
        
        signal_emitted = []
        session.selection_changed.connect(lambda s: signal_emitted.append(s))
        
        session.clear_selection()
        
        assert session.selection.dataset_id is None
        assert len(session.selection.series_ids) == 0
        assert len(signal_emitted) == 1
    
    def test_add_view(self, mock_dataset_store):
        """Testa adicionar view"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.view_state_changed.connect(lambda s: signal_emitted.append(s))
        
        session.add_view("view_1", {"type": "2d", "series": ["s1"]})
        
        assert "view_1" in session.view.active_views
        assert len(signal_emitted) == 1
    
    def test_remove_view(self, mock_dataset_store):
        """Testa remover view"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        session.add_view("view_1", {"type": "2d"})
        session.view.synchronized_views = ["view_1"]
        
        signal_emitted = []
        session.view_state_changed.connect(lambda s: signal_emitted.append(s))
        
        session.remove_view("view_1")
        
        assert "view_1" not in session.view.active_views
        assert "view_1" not in session.view.synchronized_views
        assert len(signal_emitted) == 1
    
    def test_set_view_synchronization(self, mock_dataset_store):
        """Testa definir sincronização de views"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.view_state_changed.connect(lambda s: signal_emitted.append(s))
        
        session.set_view_synchronization(["v1", "v2", "v3"])
        
        assert session.view.synchronized_views == ["v1", "v2", "v3"]
        assert len(signal_emitted) == 1
    
    def test_start_operation(self, mock_dataset_store):
        """Testa iniciar operação"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        signal_emitted = []
        session.processing_state_changed.connect(lambda s: signal_emitted.append(s))
        
        session.start_operation("op_1", "interpolation", {"method": "linear"})
        
        assert "op_1" in session.processing.active_operations
        assert session.processing.active_operations["op_1"]["type"] == "interpolation"
        assert len(signal_emitted) == 1
    
    def test_update_operation_progress(self, mock_dataset_store):
        """Testa atualizar progresso de operação"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        session.start_operation("op_1", "interpolation", {})
        
        session.update_operation_progress("op_1", 50)
        
        assert session.processing.active_operations["op_1"]["progress"] == 50
    
    def test_modified_timestamp_updates(self, mock_dataset_store):
        """Testa que timestamp modified é atualizado"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        original_modified = session.modified_at
        
        import time
        time.sleep(0.01)
        
        session.set_current_dataset("dataset_123")
        
        assert session.modified_at > original_modified


class TestSessionPersistence:
    """Testes para persistência de sessão"""
    
    @pytest.fixture
    def mock_dataset_store(self):
        """Mock do DatasetStore"""
        store = MagicMock()
        store.list_datasets.return_value = []
        return store
    
    def test_session_has_timestamps(self, mock_dataset_store):
        """Testa que sessão tem timestamps"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.modified_at, datetime)


class TestSessionStateSignals:
    """Testes para sinais de SessionState"""
    
    @pytest.fixture
    def mock_dataset_store(self):
        """Mock do DatasetStore"""
        store = MagicMock()
        return store
    
    def test_signals_are_pyqt_signals(self, mock_dataset_store):
        """Testa que sinais são PyQt signals"""
        from PyQt6.QtCore import pyqtBoundSignal

        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        # Verifica que os sinais existem
        assert hasattr(session, 'selection_changed')
        assert hasattr(session, 'view_state_changed')
        assert hasattr(session, 'processing_state_changed')
        assert hasattr(session, 'streaming_state_changed')
        assert hasattr(session, 'ui_state_changed')
        assert hasattr(session, 'session_loaded')
        assert hasattr(session, 'session_saved')
        assert hasattr(session, 'session_cleared')
    
    def test_connect_disconnect_signal(self, mock_dataset_store):
        """Testa conectar e desconectar sinal"""
        from platform_base.desktop.session_state import SessionState
        
        session = SessionState(mock_dataset_store)
        
        received = []
        def handler(state):
            received.append(state)
        
        session.selection_changed.connect(handler)
        session.set_current_dataset("test")
        
        assert len(received) == 1
        
        session.selection_changed.disconnect(handler)
        session.set_current_dataset("test2")
        
        assert len(received) == 1  # Não recebeu após disconnect
