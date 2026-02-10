"""
Fixtures compartilhadas para testes de UI.

Fornece fixtures para QApplication, mocks de SessionState/SignalHub,
e configurações comuns para testes de interface.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock
import numpy as np
import pandas as pd


@pytest.fixture(scope="session")
def qapp():
    """QApplication para todos os testes UI."""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Não fechar a aplicação para permitir múltiplos testes


@pytest.fixture
def mock_session_state():
    """Mock robusto do SessionState para testes."""
    from platform_base.core.models import Dataset, TimeSeries
    
    state = MagicMock()
    
    # Dados de exemplo
    t = np.linspace(0, 10, 100)
    y = np.sin(t) + 0.1 * np.random.randn(100)
    
    sample_series = TimeSeries(
        id="series_1",
        name="Test Series",
        time=t,
        values=y,
        unit="m/s"
    )
    
    sample_dataset = Dataset(
        id="dataset_1",
        name="Test Dataset",
        series={"series_1": sample_series}
    )
    
    # Configurar state
    state.datasets = {"dataset_1": sample_dataset}
    state.current_dataset = sample_dataset
    state.current_series = sample_series
    state.get_dataset.return_value = sample_dataset
    state.get_series.return_value = sample_series
    
    # Signals mock
    state.dataset_loaded = MagicMock()
    state.series_selected = MagicMock()
    state.selection_changed = MagicMock()
    state.processing_state_changed = MagicMock()
    
    return state


@pytest.fixture
def mock_signal_hub():
    """Mock robusto do SignalHub para testes."""
    hub = MagicMock()
    
    # Signals de dados
    hub.dataset_loaded = MagicMock()
    hub.dataset_removed = MagicMock()
    hub.series_selected = MagicMock()
    hub.series_visibility_changed = MagicMock()
    
    # Signals de operações
    hub.operation_started = MagicMock()
    hub.operation_progress = MagicMock()
    hub.operation_completed = MagicMock()
    hub.operation_failed = MagicMock()
    
    # Signals de visualização
    hub.plot_created = MagicMock()
    hub.plot_updated = MagicMock()
    hub.time_selection_changed = MagicMock()
    
    # Signals de erro
    hub.error_occurred = MagicMock()
    hub.status_updated = MagicMock()
    
    # Métodos de emissão
    hub.emit_dataset_loaded = MagicMock()
    hub.emit_operation_started = MagicMock()
    hub.emit_time_selection = MagicMock()
    
    return hub


@pytest.fixture
def ui_files_dir():
    """Diretório dos arquivos .ui."""
    return Path(__file__).parent.parent.parent.parent / "src/platform_base/desktop/ui_files"


@pytest.fixture
def sample_csv_file(tmp_path):
    """Cria arquivo CSV de exemplo para testes."""
    csv_file = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        'time': np.linspace(0, 10, 100),
        'value1': np.sin(np.linspace(0, 10, 100)),
        'value2': np.cos(np.linspace(0, 10, 100))
    })
    df.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def sample_excel_file(tmp_path):
    """Cria arquivo Excel de exemplo para testes."""
    excel_file = tmp_path / "test_data.xlsx"
    df = pd.DataFrame({
        'time': np.linspace(0, 10, 100),
        'value1': np.sin(np.linspace(0, 10, 100)),
        'value2': np.cos(np.linspace(0, 10, 100))
    })
    df.to_excel(excel_file, index=False)
    return excel_file


@pytest.fixture
def large_dataset():
    """Dataset grande para testes de performance."""
    t = np.linspace(0, 1000, 100000)
    y = np.sin(2 * np.pi * 0.1 * t) + 0.1 * np.random.randn(100000)
    return {"time": t, "values": y}


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons entre testes para evitar contaminação."""
    yield
    # Cleanup após cada teste
    from PyQt6.QtCore import QCoreApplication
    QCoreApplication.processEvents()
