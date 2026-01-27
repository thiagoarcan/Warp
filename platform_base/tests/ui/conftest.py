"""
Fixtures compartilhadas para testes de UI.

Fornece QApplication, SessionState, DatasetStore e componentes mock.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


@pytest.fixture(scope="session")
def qapp():
    """Cria QApplication para toda a sessão de testes."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication

    # Desabilitar janelas reais em testes
    app = QApplication.instance()
    if app is None:
        # Set attributes before creating app
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
        app = QApplication(['--platform', 'offscreen'])
    
    yield app
    # Não fechar app aqui para permitir múltiplos testes


@pytest.fixture
def dataset_store():
    """Cria DatasetStore para testes."""
    from platform_base.core.dataset_store import DatasetStore
    return DatasetStore()


@pytest.fixture
def session_state(dataset_store):
    """Cria SessionState para testes."""
    from platform_base.ui.state import SessionState
    return SessionState(dataset_store)


@pytest.fixture
def mock_file_dialog():
    """Mock para QFileDialog que retorna caminhos predefinidos."""
    with patch('PyQt6.QtWidgets.QFileDialog') as mock:
        yield mock


@pytest.fixture
def mock_message_box():
    """Mock para QMessageBox para evitar diálogos bloqueantes."""
    with patch('PyQt6.QtWidgets.QMessageBox') as mock:
        mock.StandardButton = Mock()
        mock.StandardButton.Yes = 1
        mock.StandardButton.No = 2
        mock.StandardButton.Save = 3
        mock.StandardButton.Discard = 4
        mock.StandardButton.Cancel = 5
        mock.question = Mock(return_value=mock.StandardButton.Yes)
        mock.information = Mock()
        mock.warning = Mock()
        mock.critical = Mock()
        mock.about = Mock()
        yield mock


@pytest.fixture
def sample_csv_file():
    """Cria arquivo CSV temporário para testes."""
    import numpy as np
    import pandas as pd

    # Criar DataFrame de teste
    np.random.seed(42)
    n_points = 100
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=n_points, freq='1min'),
        'sensor_1': np.random.randn(n_points) * 10 + 50,
        'sensor_2': np.random.randn(n_points) * 5 + 25,
        'sensor_3': np.sin(np.linspace(0, 4*np.pi, n_points)) * 100
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        df.to_csv(f, index=False)
        filepath = f.name
    
    yield filepath
    
    # Cleanup
    try:
        Path(filepath).unlink()
    except:
        pass


@pytest.fixture
def sample_excel_file():
    """Cria arquivo Excel temporário para testes."""
    import numpy as np
    import pandas as pd
    
    np.random.seed(42)
    n_points = 50
    df = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=n_points, freq='5min'),
        'value_a': np.random.randn(n_points) * 20,
        'value_b': np.cumsum(np.random.randn(n_points))
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        filepath = f.name
    
    df.to_excel(filepath, index=False)
    
    yield filepath
    
    # Cleanup
    try:
        Path(filepath).unlink()
    except:
        pass


@pytest.fixture
def mock_dataset():
    """Cria Dataset mock para testes."""
    import numpy as np
    import pandas as pd

    from platform_base.core.models import Dataset, Series, SeriesID
    
    np.random.seed(42)
    n_points = 100
    
    series_list = [
        Series(
            id=SeriesID(name="sensor_1", source="test"),
            timestamps=pd.date_range('2024-01-01', periods=n_points, freq='1min').to_numpy(),
            values=np.random.randn(n_points) * 10 + 50,
            unit="°C",
            metadata={"description": "Temperature sensor"}
        ),
        Series(
            id=SeriesID(name="sensor_2", source="test"),
            timestamps=pd.date_range('2024-01-01', periods=n_points, freq='1min').to_numpy(),
            values=np.random.randn(n_points) * 5 + 25,
            unit="bar",
            metadata={"description": "Pressure sensor"}
        )
    ]
    
    return Dataset(
        id="test_dataset",
        series=series_list,
        metadata={"source": "test", "filename": "test.csv"}
    )
