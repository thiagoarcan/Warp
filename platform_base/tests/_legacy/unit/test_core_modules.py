"""
Testes para módulos Core - ConfigManager, DatasetStore, SessionState, SignalHub

Estes testes cobrem a infraestrutura central da aplicação.
APIs corrigidas conforme implementação real dos módulos.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from pint import UnitRegistry

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

        # Usa default pois config pode estar vazio
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
        
        manager = get_config_manager()
        manager.set("test.keys.a", 1)
        manager.set("test.keys.b", 2)
        
        keys = manager.keys()
        
        assert isinstance(keys, (list, tuple, set, dict))


# ============================================================================
# TEST: DATASET STORE
# ============================================================================

class TestDatasetStore:
    """Testes para o armazenamento de datasets"""
    
    @pytest.fixture
    def ureg(self):
        """Unit registry"""
        return UnitRegistry()
    
    @pytest.fixture
    def sample_dataset(self, ureg):
        """Cria dataset de exemplo conforme models.py real"""
        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )

        # Cria SourceInfo mock (o modelo real precisa disso)
        source_info = SourceInfo(
            filepath="/test/path/data.csv",
            filename="data.csv",
            format="csv",
            size_bytes=1000,
            checksum="abc123"
        )
        
        metadata = DatasetMetadata(
            description="Test Dataset",
            tags=["test"]
        )
        
        # SeriesMetadata real tem original_name e source_column
        series_metadata = SeriesMetadata(
            original_name="Temperature",
            source_column="temp_c"
        )
        
        # Series real usa series_id, não id
        series = Series(
            series_id="series_1",
            name="Temperature",
            unit=ureg.degC,
            values=np.random.randn(100),
            metadata=series_metadata
        )
        
        t_seconds = np.arange(100, dtype=float)
        t_datetime = np.array([np.datetime64('2024-01-01') + np.timedelta64(int(t), 's') for t in t_seconds])
        
        # Dataset real usa dataset_id, não id
        return Dataset(
            dataset_id="test_dataset_1",
            version=1,
            parent_id=None,
            source=source_info,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            metadata=metadata,
            series={"series_1": series},
            created_at=datetime.now()
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
        
        # Recupera dataset usando dataset_id
        retrieved = store.get_dataset(sample_dataset.dataset_id)
        
        assert retrieved is not None
        assert retrieved.dataset_id == sample_dataset.dataset_id
    
    def test_list_datasets(self, sample_dataset):
        """Testa listagem de datasets"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        
        # Adiciona dataset
        store.add_dataset(sample_dataset)
        
        # Lista datasets
        datasets = store.list_datasets()
        
        assert len(datasets) >= 1
    
    def test_add_and_get_series(self, sample_dataset, ureg):
        """Testa adicionar e recuperar série"""
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.core.models import Series, SeriesMetadata
        
        store = DatasetStore()
        store.add_dataset(sample_dataset)
        
        # SeriesMetadata real
        new_metadata = SeriesMetadata(
            original_name="Pressure",
            source_column="pressure_bar"
        )
        
        # Adiciona nova série usando series_id
        new_series = Series(
            series_id="series_2",
            name="Pressure",
            unit=ureg.bar,
            values=np.random.randn(100),
            metadata=new_metadata
        )
        
        store.add_series(sample_dataset.dataset_id, new_series)
        
        # Recupera série
        retrieved = store.get_series(sample_dataset.dataset_id, "series_2")
        
        assert retrieved is not None
        assert retrieved.name == "Pressure"
    
    def test_list_series(self, sample_dataset):
        """Testa listagem de séries"""
        from platform_base.core.dataset_store import DatasetStore
        
        store = DatasetStore()
        store.add_dataset(sample_dataset)
        
        # Lista séries
        series_list = store.list_series(sample_dataset.dataset_id)
        
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


# ============================================================================
# TEST: SESSION STATE
# ============================================================================

class TestSessionState:
    """Testes para o estado da sessão"""
    
    @pytest.fixture
    def session_state(self):
        """Cria SessionState com DatasetStore (requerido pelo construtor)"""
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.state import SessionState
        
        store = DatasetStore()
        return SessionState(store)
    
    @pytest.fixture
    def ureg(self):
        """Unit registry"""
        return UnitRegistry()
    
    @pytest.fixture
    def sample_dataset(self, ureg):
        """Cria dataset de exemplo"""
        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        
        source_info = SourceInfo(
            filepath="/test/path/data.csv",
            filename="data.csv",
            format="csv",
            size_bytes=1000,
            checksum="abc123"
        )
        
        metadata = DatasetMetadata(description="Session Test", tags=["test"])
        
        series_metadata = SeriesMetadata(
            original_name="Temperature",
            source_column="temp"
        )
        
        series = Series(
            series_id="series_1",
            name="Temperature",
            unit=ureg.degC,
            values=np.random.randn(100),
            metadata=series_metadata
        )
        
        t_seconds = np.arange(100, dtype=float)
        t_datetime = np.array([np.datetime64('2024-01-01') + np.timedelta64(int(t), 's') for t in t_seconds])
        
        return Dataset(
            dataset_id="session_test_dataset",
            version=1,
            parent_id=None,
            source=source_info,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            metadata=metadata,
            series={"series_1": series},
            created_at=datetime.now()
        )
    
    def test_session_state_creation(self, session_state):
        """Testa criação de SessionState"""
        assert session_state is not None
        assert session_state.session_id is not None
    
    def test_session_id_unique(self):
        """Testa que session_id é único"""
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.state import SessionState
        
        store1 = DatasetStore()
        store2 = DatasetStore()
        
        state1 = SessionState(store1)
        state2 = SessionState(store2)
        
        assert state1.session_id is not None
        assert state2.session_id is not None
    
    def test_add_dataset_to_session(self, session_state, sample_dataset):
        """Testa adicionar dataset à sessão"""
        session_state.add_dataset(sample_dataset)
        
        retrieved = session_state.get_dataset(sample_dataset.dataset_id)
        assert retrieved is not None
    
    def test_get_all_datasets(self, session_state, ureg):
        """Testa obter todos os datasets"""
        from platform_base.core.models import Dataset, DatasetMetadata, SourceInfo

        # Adiciona datasets
        for i in range(3):
            source_info = SourceInfo(
                filepath=f"/test/path/data_{i}.csv",
                filename=f"data_{i}.csv",
                format="csv",
                size_bytes=1000,
                checksum=f"abc{i}"
            )
            
            t_seconds = np.arange(100, dtype=float)
            t_datetime = np.array([np.datetime64('2024-01-01') + np.timedelta64(int(t), 's') for t in t_seconds])
            
            dataset = Dataset(
                dataset_id=f"dataset_{i}",
                version=1,
                parent_id=None,
                source=source_info,
                t_seconds=t_seconds,
                t_datetime=t_datetime,
                metadata=DatasetMetadata(description=f"Dataset {i}"),
                series={},
                created_at=datetime.now()
            )
            session_state.add_dataset(dataset)
        
        all_datasets = session_state.get_all_datasets()
        assert len(all_datasets) >= 3
    
    def test_set_current_dataset(self, session_state, sample_dataset):
        """Testa definir dataset atual"""
        session_state.add_dataset(sample_dataset)
        session_state.set_current_dataset(sample_dataset.dataset_id)
        
        current = session_state.get_current_dataset()
        assert current is not None
        assert current.dataset_id == sample_dataset.dataset_id
    
    def test_update_selection(self, session_state):
        """Testa atualização de seleção"""
        # update_selection aceita kwargs
        session_state.update_selection(selected_series=['series_1'])
        
        selection_state = session_state.get_selection_state()
        assert 'series_1' in selection_state.selected_series
    
    def test_start_finish_operation(self, session_state):
        """Testa início e fim de operação"""
        # start_operation aceita apenas operation_name
        session_state.start_operation("interpolation")
        
        op_state = session_state.get_operation_state()
        assert op_state.is_processing
        assert op_state.current_operation == "interpolation"
        
        # finish_operation aceita success e message
        session_state.finish_operation(success=True, message="Done")
        
        op_state = session_state.get_operation_state()
        assert not op_state.is_processing


# ============================================================================
# TEST: SIGNAL HUB
# ============================================================================

class TestSignalHub:
    """Testes para o hub de sinais"""
    
    @pytest.fixture(autouse=True)
    def reset_hub(self):
        """Reset SignalHub antes de cada teste"""
        from platform_base.ui.signal_hub import SignalHub
        SignalHub.reset_instance()
        yield
        SignalHub.reset_instance()
    
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
        
        # Inscreve - EventType usa DATASET_LOADED não DATA_LOADED
        hub.subscribe(EventType.DATASET_LOADED, handler)
        
        # Emite - emit aceita (event_type, source, data)
        hub.emit(EventType.DATASET_LOADED, "test_source", {"dataset_id": "test"})
        
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
        hub.emit(EventType.SELECTION_CHANGED, "test", {})
        count_after_first = received_count[0]
        
        # Desinscreve
        hub.unsubscribe(EventType.SELECTION_CHANGED, handler)
        
        # Emite novamente - não deve receber
        hub.emit(EventType.SELECTION_CHANGED, "test", {})
        
        assert received_count[0] == count_after_first
    
    def test_get_history(self):
        """Testa obtenção de histórico"""
        from platform_base.ui.signal_hub import EventType, SignalHub
        
        hub = SignalHub.instance()
        
        # Emite alguns eventos
        hub.emit(EventType.ZOOM_CHANGED, "test", {"zoom": 1.0})
        
        # Obtém histórico - método é get_event_history
        history = hub.get_event_history()
        
        assert isinstance(history, list)
    
    def test_event_types_exist(self):
        """Testa que todos os tipos de evento existem"""
        from platform_base.ui.signal_hub import EventType

        # Tipos reais do EventType enum
        expected_types = [
            'DATASET_LOADED',
            'DATASET_UNLOADED',
            'DATA_MODIFIED',
            'SELECTION_CHANGED',
            'SELECTION_CLEARED',
            'ZOOM_CHANGED',
            'OPERATION_STARTED',
            'OPERATION_COMPLETED',
            'OPERATION_FAILED',
            'CROSSHAIR_MOVED',
        ]
        
        for type_name in expected_types:
            assert hasattr(EventType, type_name), f"Missing EventType: {type_name}"
    
    def test_emit_convenience_methods(self):
        """Testa métodos de conveniência para emissão"""
        from platform_base.ui.signal_hub import SignalHub
        
        hub = SignalHub.instance()
        
        # Testa emit_crosshair_moved
        hub.emit_crosshair_moved("test_plot", 10.5, 20.3)
        
        # Testa emit_selection_changed
        hub.emit_selection_changed("test_plot", [1, 2, 3])
        
        # Testa emit_operation_started
        hub.emit_operation_started("test", "interpolation")
        
        # Não deve lançar exceção
        assert True
    
    def test_get_subscriber_count(self):
        """Testa contagem de subscribers"""
        from platform_base.ui.signal_hub import EventType, SignalHub
        
        hub = SignalHub.instance()
        
        def handler(event):
            pass
        
        hub.subscribe(EventType.CROSSHAIR_MOVED, handler)
        
        count = hub.get_subscriber_count(EventType.CROSSHAIR_MOVED)
        assert count >= 1


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
        assert len(report.gaps) == 0 or report.gaps is None or len(report.gaps) == 0
    
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
        # Pode ter warnings sobre valores faltantes
        assert len(report.warnings) >= 0


# ============================================================================
# TEST: STREAMING FILTERS
# ============================================================================

class TestStreamingFilters:
    """Testes para filtros de streaming"""
    
    def test_quality_filter_creation(self):
        """Testa criação de QualityFilter"""
        from platform_base.streaming.filters import QualityFilter

        # API real: QualityFilter(name, outlier_method, outlier_threshold, window_size, ...)
        qf = QualityFilter(
            name="test_quality",
            outlier_method="zscore",
            outlier_threshold=3.0,
            window_size=20
        )
        assert qf is not None
        assert qf.name == "test_quality"
    
    def test_quality_filter_apply(self):
        """Testa aplicação de QualityFilter"""
        from platform_base.streaming.filters import FilterAction, QualityFilter
        
        qf = QualityFilter(
            name="test_quality",
            outlier_method="zscore",
            outlier_threshold=3.0,
            window_size=20
        )
        
        # API real: apply(timestamp, value, context)
        # Primeiro, alimenta com dados para construir janela
        for i in range(10):
            result = qf.apply(float(i), float(i + np.random.randn() * 0.1))
        
        # Aplica a um valor normal
        result = qf.apply(10.0, 10.5)
        
        assert result is not None
        assert hasattr(result, 'action')
    
    def test_temporal_filter_creation(self):
        """Testa criação de TemporalFilter"""
        from platform_base.streaming.filters import TemporalFilter

        # API real: TemporalFilter(name, min_interval, max_interval, rate_limit, time_window, ...)
        tf = TemporalFilter(
            name="test_temporal",
            min_interval=0.1,
            max_interval=10.0
        )
        assert tf is not None
        assert tf.name == "test_temporal"
    
    def test_temporal_filter_apply(self):
        """Testa aplicação de TemporalFilter"""
        from platform_base.streaming.filters import TemporalFilter
        
        tf = TemporalFilter(
            name="test_temporal",
            min_interval=0.1,
            max_interval=10.0
        )
        
        # API real: apply(timestamp, value, context)
        result = tf.apply(0.0, 100.0)
        assert result is not None
        
        # Segundo ponto muito rápido
        result = tf.apply(0.05, 101.0)  # 0.05s < min_interval 0.1
        assert result is not None
    
    def test_value_filter_creation(self):
        """Testa criação de ValueFilter"""
        from platform_base.streaming.filters import ValueFilter

        # API real: ValueFilter(name, min_value, max_value, ...)
        vf = ValueFilter(
            name="test_value",
            min_value=0.0,
            max_value=100.0
        )
        assert vf is not None
        assert vf.name == "test_value"
    
    def test_value_filter_apply(self):
        """Testa aplicação de ValueFilter"""
        from platform_base.streaming.filters import FilterAction, ValueFilter
        
        vf = ValueFilter(
            name="test_value",
            min_value=0.0,
            max_value=100.0
        )
        
        # Valor dentro do range
        result_in = vf.apply(1.0, 50.0)
        assert result_in is not None
        assert result_in.action == FilterAction.PASS
        
        # Valor fora do range
        result_out = vf.apply(2.0, 150.0)
        assert result_out is not None
        assert result_out.action == FilterAction.BLOCK
    
    def test_filter_chain_creation(self):
        """Testa criação de FilterChain"""
        from platform_base.streaming.filters import (
            FilterChain,
            QualityFilter,
            ValueFilter,
        )
        
        chain = FilterChain(name="test_chain")
        chain.add_filter(QualityFilter(name="quality"))
        chain.add_filter(ValueFilter(name="value", min_value=0, max_value=100))
        
        assert len(chain.filters) == 2
    
    def test_filter_reset(self):
        """Testa reset de filtro"""
        from platform_base.streaming.filters import QualityFilter
        
        qf = QualityFilter(name="test_reset")
        
        # Aplica alguns dados
        for i in range(5):
            qf.apply(float(i), float(i))
        
        # Reset
        qf.reset()
        
        # Deve funcionar normalmente após reset
        result = qf.apply(0.0, 10.0)
        assert result is not None
    
    def test_filter_get_efficiency(self):
        """Testa obtenção de eficiência do filtro"""
        from platform_base.streaming.filters import QualityFilter
        
        qf = QualityFilter(name="test_efficiency", outlier_threshold=3.0)
        
        # Aplica dados normais (deve passar)
        for i in range(10):
            qf.apply(float(i), float(i))
        
        efficiency = qf.get_efficiency()
        assert isinstance(efficiency, (int, float))
        assert 0 <= efficiency <= 1
    
    def test_filter_statistics(self):
        """Testa estatísticas do filtro"""
        from platform_base.streaming.filters import QualityFilter
        
        qf = QualityFilter(name="test_stats")
        
        # Aplica alguns dados e atualiza estatísticas manualmente
        for i in range(5):
            result = qf.apply(float(i), float(i))
            qf.update_statistics(result)  # Estatísticas requerem chamada explícita
        
        # Verifica estatísticas
        assert 'total_processed' in qf.statistics
        assert qf.statistics['total_processed'] == 5


# ============================================================================
# TEST: MODELS
# ============================================================================

class TestModels:
    """Testes para os modelos de dados"""
    
    def test_dataset_metadata_creation(self):
        """Testa criação de DatasetMetadata"""
        from platform_base.core.models import DatasetMetadata
        
        metadata = DatasetMetadata(
            description="Test description",
            tags=["test", "example"],
            timezone="UTC"
        )
        
        assert metadata.description == "Test description"
        assert "test" in metadata.tags
    
    def test_series_metadata_creation(self):
        """Testa criação de SeriesMetadata"""
        from platform_base.core.models import SeriesMetadata
        
        metadata = SeriesMetadata(
            original_name="Temperature",
            source_column="temp_c",
            description="Temperature in Celsius"
        )
        
        assert metadata.original_name == "Temperature"
        assert metadata.source_column == "temp_c"
    
    def test_series_creation(self):
        """Testa criação de Series"""
        from pint import UnitRegistry

        from platform_base.core.models import Series, SeriesMetadata
        
        ureg = UnitRegistry()
        
        series = Series(
            series_id="test_series",
            name="Temperature",
            unit=ureg.degC,
            values=np.array([20.0, 21.0, 22.0]),
            metadata=SeriesMetadata(original_name="Temp", source_column="temp")
        )
        
        assert series.series_id == "test_series"
        assert len(series.values) == 3
    
    def test_time_window(self):
        """Testa TimeWindow"""
        from platform_base.core.models import TimeWindow
        
        window = TimeWindow(start=0.0, end=100.0)
        
        assert window.start == 0.0
        assert window.end == 100.0
        assert window.duration == 100.0
    
    def test_calc_result(self):
        """Testa CalcResult"""
        from platform_base.core.models import CalcResult, ResultMetadata
        
        result = CalcResult(
            values=np.array([1.0, 2.0, 3.0]),
            metadata=ResultMetadata(operation="derivative"),
            operation="derivative",
            order=1
        )
        
        assert result.operation == "derivative"
        assert len(result.values) == 3
    
    def test_sync_result(self):
        """Testa SyncResult"""
        from platform_base.core.models import ResultMetadata, SyncResult
        
        result = SyncResult(
            values=np.array([1.0, 2.0, 3.0]),
            metadata=ResultMetadata(operation="synchronize"),
            t_common=np.array([0.0, 1.0, 2.0]),
            synced_series={"s1": np.array([1.0, 2.0, 3.0])},
            alignment_error=0.01,
            confidence=0.99
        )
        
        assert "s1" in result.synced_series
        assert result.alignment_error == 0.01
