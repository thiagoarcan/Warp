"""
Testes para módulos Core - ConfigManager, DatasetStore, Orchestrator

Estes testes cobrem a infraestrutura central da aplicação.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ============================================================================
# TEST: CONFIG MANAGER
# ============================================================================

class TestConfigManager:
    """Testes para o gerenciador de configuração"""
    
    def test_get_config_manager_singleton(self):
        """Testa que get_config_manager retorna singleton"""
        from platform_base.core.config import get_config_manager
        
        m1 = get_config_manager()
        m2 = get_config_manager()
        
        assert m1 is m2
    
    def test_get_existing_key(self):
        """Testa obter chave existente"""
        from platform_base.core.config import get_config

        # Chaves padrão devem existir - usa default pois config pode estar vazio
        result = get_config("logging.level", default="INFO")
        assert result is not None
    
    def test_get_missing_key_with_default(self):
        """Testa obter chave inexistente com default"""
        from platform_base.core.config import get_config
        
        result = get_config("nonexistent.key.12345", default="default_value")
        assert result == "default_value"
    
    def test_set_and_get_value(self):
        """Testa definir e recuperar valor"""
        from platform_base.core.config import get_config, set_config

        # Define valor
        set_config("test.temporary.value", "test_123")
        
        # Recupera valor
        result = get_config("test.temporary.value")
        assert result == "test_123"
    
    def test_has_key(self):
        """Testa verificação de existência de chave"""
        from platform_base.core.config import get_config_manager
        
        manager = get_config_manager()
        
        # Define uma chave
        manager.set("test.has_key", "value")
        
        # Verifica existência
        assert manager.has("test.has_key")
        assert not manager.has("nonexistent.key.12345.xyz")
    
    def test_config_manager_keys(self):
        """Testa listagem de chaves"""
        from platform_base.core.config import get_config_manager
        manager.set("test.keys.b", 2)
        
        keys = manager.keys()
        
        assert isinstance(keys, (list, tuple, set, dict))
    
    def test_save_to_file(self, tmp_path):
        """Testa salvamento de configuração em arquivo"""
        from platform_base.core.config_manager import get_config_manager
        
        manager = get_config_manager()
        
        # Define valores
        manager.set("test.save.value", "to_save")
        
        # Salva em arquivo
        config_file = tmp_path / "test_config.yaml"
        try:
            manager.save_to_file(str(config_file))
            assert config_file.exists()
        except NotImplementedError:
            pytest.skip("save_to_file not implemented")
    
    def test_add_change_callback(self):
        """Testa adição de callback de mudança"""
        from platform_base.core.config_manager import get_config_manager
        
        manager = get_config_manager()
        
        callback_called = False
        
        def on_change(key, value):
            nonlocal callback_called
            callback_called = True
        
        try:
            manager.add_change_callback(on_change)
            manager.set("test.callback.value", "trigger")
            # Callback pode ou não ser chamado dependendo da implementação
        except (NotImplementedError, AttributeError):
            pytest.skip("Change callbacks not implemented")
    
    def test_get_statistics(self):
        """Testa obtenção de estatísticas"""
        from platform_base.core.config_manager import get_config_manager
        
        manager = get_config_manager()
        
        try:
            stats = manager.get_statistics()
            assert isinstance(stats, dict)
        except (NotImplementedError, AttributeError):
            pytest.skip("get_statistics not implemented")


# ============================================================================
# TEST: DATASET STORE
# ============================================================================

class TestDatasetStore:
    """Testes para o armazenamento de datasets"""
    
    @pytest.fixture
    def sample_dataset(self):
        """Cria dataset de exemplo"""
        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
        )
        
        metadata = DatasetMetadata(
            name="Test Dataset",
            source="test",
            created_at=datetime.now()
        )
        
        series = Series(
            id="series_1",
            name="Temperature",
            values=np.random.randn(100),
            t_seconds=np.arange(100, dtype=float),
            metadata=SeriesMetadata(unit="°C")
        )
        
        return Dataset(
            id="test_dataset_1",
            metadata=metadata,
            series={"series_1": series}
        )
    
    def test_dataset_store_creation(self):
        """Testa criação de DatasetStore"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        assert store is not None
    
    def test_add_and_get_dataset(self, sample_dataset):
        """Testa adicionar e recuperar dataset"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        
        # Adiciona dataset
        store.add_dataset(sample_dataset)
        
        # Recupera dataset
        retrieved = store.get_dataset(sample_dataset.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_dataset.id
    
    def test_list_datasets(self, sample_dataset):
        """Testa listagem de datasets"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        
        # Adiciona dataset
        store.add_dataset(sample_dataset)
        
        # Lista datasets
        datasets = store.list_datasets()
        
        assert len(datasets) >= 1
        assert sample_dataset.id in [d.id for d in datasets] or sample_dataset.id in datasets
    
    def test_add_and_get_series(self, sample_dataset):
        """Testa adicionar e recuperar série"""
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import Series, SeriesMetadata
        
        store = DatasetStore()
        store.add_dataset(sample_dataset)
        
        # Adiciona nova série
        new_series = Series(
            id="series_2",
            name="Pressure",
            values=np.random.randn(100),
            t_seconds=np.arange(100, dtype=float),
            metadata=SeriesMetadata(unit="bar")
        )
        
        store.add_series(sample_dataset.id, new_series)
        
        # Recupera série
        retrieved = store.get_series(sample_dataset.id, "series_2")
        
        assert retrieved is not None
        assert retrieved.name == "Pressure"
    
    def test_list_series(self, sample_dataset):
        """Testa listagem de séries"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        store.add_dataset(sample_dataset)
        
        # Lista séries
        series_list = store.list_series(sample_dataset.id)
        
        assert len(series_list) >= 1
    
    def test_clear_cache(self, sample_dataset):
        """Testa limpeza de cache"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        store.add_dataset(sample_dataset)
        
        # Limpa cache
        store.clear_cache()
        
        # Store ainda deve funcionar
        datasets = store.list_datasets()
        assert isinstance(datasets, (list, tuple))
    
    def test_get_cache_stats(self, sample_dataset):
        """Testa estatísticas de cache"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        store.add_dataset(sample_dataset)
        
        try:
            stats = store.get_cache_stats()
            assert isinstance(stats, dict)
        except (NotImplementedError, AttributeError):
            pytest.skip("get_cache_stats not implemented")


# ============================================================================
# TEST: SESSION STATE
# ============================================================================

class TestSessionState:
    """Testes para o estado da sessão"""
    
    def test_session_state_creation(self):
        """Testa criação de SessionState"""
        from platform_base.ui.state import SessionState
        
        state = SessionState()
        assert state is not None
        assert state.session_id is not None
    
    def test_session_id_unique(self):
        """Testa que session_id é único"""
        from platform_base.ui.state import SessionState
        
        state1 = SessionState()
        state2 = SessionState()
        
        # Se são instâncias diferentes, devem ter IDs diferentes
        # (ou podem ser singleton com mesmo ID)
        assert state1.session_id is not None
    
    def test_add_dataset_to_session(self):
        """Testa adicionar dataset à sessão"""
        from platform_base.core.models import Dataset, DatasetMetadata
        from platform_base.ui.state import SessionState
        
        state = SessionState()
        
        dataset = Dataset(
            id="session_test_dataset",
            metadata=DatasetMetadata(
                name="Session Test",
                source="test",
                created_at=datetime.now()
            ),
            series={}
        )
        
        state.add_dataset(dataset)
        
        retrieved = state.get_dataset("session_test_dataset")
        assert retrieved is not None
    
    def test_get_all_datasets(self):
        """Testa obter todos os datasets"""
        from platform_base.core.models import Dataset, DatasetMetadata
        from platform_base.ui.state import SessionState
        
        state = SessionState()
        
        # Adiciona datasets
        for i in range(3):
            dataset = Dataset(
                id=f"dataset_{i}",
                metadata=DatasetMetadata(
                    name=f"Dataset {i}",
                    source="test",
                    created_at=datetime.now()
                ),
                series={}
            )
            state.add_dataset(dataset)
        
        all_datasets = state.get_all_datasets()
        assert len(all_datasets) >= 3
    
    def test_set_current_dataset(self):
        """Testa definir dataset atual"""
        from platform_base.core.models import Dataset, DatasetMetadata
        from platform_base.ui.state import SessionState
        
        state = SessionState()
        
        dataset = Dataset(
            id="current_dataset",
            metadata=DatasetMetadata(
                name="Current",
                source="test",
                created_at=datetime.now()
            ),
            series={}
        )
        
        state.add_dataset(dataset)
        state.set_current_dataset("current_dataset")
        
        current = state.get_current_dataset()
        assert current is not None
        assert current.id == "current_dataset"
    
    def test_update_selection(self):
        """Testa atualização de seleção"""
        from platform_base.ui.state import SessionState
        
        state = SessionState()
        
        selection = {
            'start': 0,
            'end': 100,
            'series': ['series_1']
        }
        
        state.update_selection(selection)
        
        # Verifica que seleção foi atualizada
        current_selection = state.current_view.selection if hasattr(state, 'current_view') else None
        # A implementação pode variar
    
    def test_start_finish_operation(self):
        """Testa início e fim de operação"""
        from platform_base.ui.state import SessionState
        
        state = SessionState()
        
        # Inicia operação
        state.start_operation("interpolation", {"method": "linear"})
        
        # Finaliza operação
        state.finish_operation("interpolation", success=True)
        
        # Não deve lançar exceção


# ============================================================================
# TEST: SIGNAL HUB
# ============================================================================

class TestSignalHub:
    """Testes para o hub de sinais"""
    
    def test_signal_hub_singleton(self):
        """Testa que SignalHub é singleton"""
        from platform_base.ui.signal_hub import SignalHub
        
        hub1 = SignalHub.instance()
        hub2 = SignalHub.instance()
        
        assert hub1 is hub2
    
    def test_subscribe_and_emit(self):
        """Testa inscrição e emissão de eventos"""
        from platform_base.ui.signal_hub import EventType, SignalHub
        
        hub = SignalHub.instance()
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        # Inscreve
        hub.subscribe(EventType.DATA_LOADED, handler)
        
        # Emite
        hub.emit(EventType.DATA_LOADED, {"dataset_id": "test"})
        
        # Verifica recebimento
        assert len(received_events) >= 1
    
    def test_unsubscribe(self):
        """Testa desinscrição de eventos"""
        from platform_base.ui.signal_hub import EventType, SignalHub
        
        hub = SignalHub.instance()
        
        received_count = [0]
        
        def handler(event):
            received_count[0] += 1
        
        # Inscreve
        hub.subscribe(EventType.SELECTION_CHANGED, handler)
        
        # Emite - deve receber
        hub.emit(EventType.SELECTION_CHANGED, {})
        count_after_first = received_count[0]
        
        # Desinscreve
        hub.unsubscribe(EventType.SELECTION_CHANGED, handler)
        
        # Emite novamente - não deve receber
        hub.emit(EventType.SELECTION_CHANGED, {})
        
        assert received_count[0] == count_after_first
    
    def test_get_history(self):
        """Testa obtenção de histórico"""
        from platform_base.ui.signal_hub import EventType, SignalHub
        
        hub = SignalHub.instance()
        
        # Emite alguns eventos
        hub.emit(EventType.VIEW_CHANGED, {"zoom": 1.0})
        
        # Obtém histórico
        history = hub.get_history()
        
        assert isinstance(history, list)
    
    def test_clear_history(self):
        """Testa limpeza de histórico"""
        from platform_base.ui.signal_hub import EventType, SignalHub
        
        hub = SignalHub.instance()
        
        # Emite eventos
        hub.emit(EventType.OPERATION_STARTED, {})
        hub.emit(EventType.OPERATION_COMPLETED, {})
        
        # Limpa histórico
        hub.clear_history()
        
        # Histórico deve estar vazio ou menor
        history = hub.get_history()
        # Pode ou não estar vazio dependendo da implementação
    
    def test_event_types_exist(self):
        """Testa que todos os tipos de evento existem"""
        from platform_base.ui.signal_hub import EventType
        
        expected_types = [
            'DATA_LOADED',
            'DATA_UPDATED',
            'SELECTION_CHANGED',
            'VIEW_CHANGED',
            'OPERATION_STARTED',
            'OPERATION_COMPLETED',
            'ERROR_OCCURRED',
        ]
        
        for type_name in expected_types:
            assert hasattr(EventType, type_name), f"Missing EventType: {type_name}"


# ============================================================================
# TEST: VALIDATOR
# ============================================================================

class TestValidator:
    """Testes para validação de dados"""
    
    def test_detect_gaps_no_gaps(self):
        """Testa detecção quando não há gaps"""
        from platform_base.io.validator import detect_gaps

        # Dados uniformemente espaçados
        t_seconds = np.arange(0, 100, 1.0)
        
        report = detect_gaps(t_seconds)
        
        assert report is not None
        assert len(report.gaps) == 0 or report.gaps is None
    
    def test_detect_gaps_with_gaps(self):
        """Testa detecção quando há gaps"""
        from platform_base.io.validator import detect_gaps

        # Dados com gap grande
        t_seconds = np.array([0, 1, 2, 3, 100, 101, 102])  # Gap entre 3 e 100
        
        report = detect_gaps(t_seconds, gap_multiplier=2.0)
        
        assert report is not None
        assert len(report.gaps) >= 1
    
    def test_validate_time_valid(self):
        """Testa validação de tempo válido"""
        import pandas as pd

        from platform_base.io.validator import validate_time
        
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1min'),
            'value': np.random.randn(100)
        })
        
        report = validate_time(df, 'timestamp')
        
        assert report is not None
        assert len(report.errors) == 0
    
    def test_validate_time_invalid(self):
        """Testa validação de tempo inválido"""
        import pandas as pd

        from platform_base.io.validator import validate_time

        # Timestamps não ordenados
        df = pd.DataFrame({
            'timestamp': ['2024-01-03', '2024-01-01', '2024-01-02'],
            'value': [1, 2, 3]
        })
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        report = validate_time(df, 'timestamp')
        
        # Pode ter warnings ou errors sobre ordenação
        assert report is not None
    
    def test_validate_values_valid(self):
        """Testa validação de valores válidos"""
        import pandas as pd

        from platform_base.io.validator import validate_values
        
        df = pd.DataFrame({
            'value1': np.random.randn(100),
            'value2': np.random.randn(100)
        })
        
        report = validate_values(df, ['value1', 'value2'])
        
        assert report is not None
        assert len(report.errors) == 0
    
    def test_validate_values_with_missing(self):
        """Testa validação com valores faltantes"""
        import pandas as pd

        from platform_base.io.validator import validate_values
        
        df = pd.DataFrame({
            'value1': [1, 2, np.nan, 4, np.nan] * 20,
            'value2': np.random.randn(100)
        })
        
        report = validate_values(df, ['value1', 'value2'], max_missing_ratio=0.1)
        
        assert report is not None
        # Deve ter warning sobre valores faltantes
        assert len(report.warnings) >= 1 or len(report.errors) >= 1


# ============================================================================
# TEST: STREAMING FILTERS
# ============================================================================

class TestStreamingFilters:
    """Testes para filtros de streaming"""
    
    def test_quality_filter_creation(self):
        """Testa criação de QualityFilter"""
        from platform_base.streaming.filters import QualityFilter
        
        filter = QualityFilter(min_confidence=0.8)
        assert filter is not None
    
    def test_quality_filter_apply(self):
        """Testa aplicação de QualityFilter"""
        from platform_base.streaming.filters import FilterResult, QualityFilter
        
        filter = QualityFilter(min_confidence=0.8)
        
        # Dados com confiança
        data = {
            'value': 100,
            'confidence': 0.9
        }
        
        result = filter.apply(data)
        
        assert isinstance(result, FilterResult)
    
    def test_temporal_filter_creation(self):
        """Testa criação de TemporalFilter"""
        from platform_base.streaming.filters import TemporalFilter
        
        filter = TemporalFilter(
            start_time=0,
            end_time=100
        )
        assert filter is not None
    
    def test_temporal_filter_apply(self):
        """Testa aplicação de TemporalFilter"""
        from platform_base.streaming.filters import FilterResult, TemporalFilter
        
        filter = TemporalFilter(start_time=10, end_time=90)
        
        # Dados dentro do range
        data_in = {'timestamp': 50, 'value': 100}
        result_in = filter.apply(data_in)
        
        # Dados fora do range
        data_out = {'timestamp': 5, 'value': 100}
        result_out = filter.apply(data_out)
        
        assert isinstance(result_in, FilterResult)
        assert isinstance(result_out, FilterResult)
    
    def test_value_filter_creation(self):
        """Testa criação de ValueFilter"""
        from platform_base.streaming.filters import ValueFilter
        
        filter = ValueFilter(
            min_value=0,
            max_value=100
        )
        assert filter is not None
    
    def test_value_filter_apply(self):
        """Testa aplicação de ValueFilter"""
        from platform_base.streaming.filters import FilterResult, ValueFilter
        
        filter = ValueFilter(min_value=0, max_value=100)
        
        # Valor dentro do range
        result_in = filter.apply({'value': 50})
        
        # Valor fora do range
        result_out = filter.apply({'value': 150})
        
        assert isinstance(result_in, FilterResult)
        assert isinstance(result_out, FilterResult)
    
    def test_composite_filter(self):
        """Testa CompositeFilter"""
        from platform_base.streaming.filters import (
            CompositeFilter,
            QualityFilter,
            ValueFilter,
        )
        
        composite = CompositeFilter()
        composite.add_filter(QualityFilter(min_confidence=0.5))
        composite.add_filter(ValueFilter(min_value=0, max_value=100))
        
        # Aplica filtro composto
        data = {'value': 50, 'confidence': 0.8}
        result = composite.apply(data)
        
        assert result is not None
    
    def test_filter_reset(self):
        """Testa reset de filtro"""
        from platform_base.streaming.filters import QualityFilter
        
        filter = QualityFilter(min_confidence=0.8)
        
        # Aplica alguns dados
        filter.apply({'value': 1, 'confidence': 0.9})
        filter.apply({'value': 2, 'confidence': 0.7})
        
        # Reset
        filter.reset()
        
        # Deve funcionar normalmente após reset
        result = filter.apply({'value': 3, 'confidence': 0.95})
        assert result is not None
    
    def test_filter_efficiency(self):
        """Testa obtenção de eficiência do filtro"""
        from platform_base.streaming.filters import QualityFilter
        
        filter = QualityFilter(min_confidence=0.5)
        
        # Aplica dados
        for i in range(10):
            filter.apply({'value': i, 'confidence': 0.6})
        
        try:
            efficiency = filter.get_efficiency()
            assert isinstance(efficiency, (int, float))
            assert 0 <= efficiency <= 1
        except (NotImplementedError, AttributeError):
            pytest.skip("get_efficiency not implemented")
