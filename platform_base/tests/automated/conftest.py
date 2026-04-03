"""
Conftest unificado para a suíte de testes automatizados.
Fornece fixtures session/module/function para Qt offscreen,
carregamento de .ui, mocks de SessionState/SignalHub, e cleanup automático.
"""
from __future__ import annotations

import gc
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from xml.etree import ElementTree

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Garantir offscreen ANTES de qualquer import Qt
# ---------------------------------------------------------------------------
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_LOGGING_RULES"] = "*.debug=false"

from PyQt6.QtCore import QCoreApplication, Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402

# ---------------------------------------------------------------------------
# Caminho do projeto
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # platform_base/
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

UI_FILES_DIR = SRC_DIR / "platform_base" / "desktop" / "ui_files"
RESOURCES_DIR = SRC_DIR / "platform_base" / "desktop" / "resources"
CONFIGS_DIR = PROJECT_ROOT / "configs"
DATA_DIR = PROJECT_ROOT / "data"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


# ═══════════════════════════════════════════════════════════════════════════
# Hooks
# ═══════════════════════════════════════════════════════════════════════════
def pytest_configure(config):
    """Registra markers customizados."""
    config.addinivalue_line("markers", "automated: automated test suite")
    config.addinivalue_line("markers", "gui: GUI tests requiring Qt")
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "smoke: smoke tests (critical path)")


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures — Session scoped (uma vez por rodada)
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture(scope="session")
def qapp():
    """QApplication única compartilhada por todos os testes (offscreen)."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["test", "--platform", "offscreen"])
        app.setApplicationName("PlatformBaseTest")
    yield app
    # Não destrói — reutilizada entre sessões


@pytest.fixture(scope="session")
def ui_files_dir():
    """Caminho para diretório de arquivos .ui."""
    return UI_FILES_DIR


@pytest.fixture(scope="session")
def all_ui_files(ui_files_dir):
    """Lista de todos os arquivos .ui no diretório."""
    return sorted(ui_files_dir.glob("*.ui"))


@pytest.fixture(scope="session")
def ui_file_contents(all_ui_files):
    """Dicionário {nome_arquivo: ElementTree} com XML parseado de cada .ui."""
    contents = {}
    for ui_path in all_ui_files:
        try:
            tree = ElementTree.parse(str(ui_path))
            contents[ui_path.name] = tree
        except ElementTree.ParseError:
            contents[ui_path.name] = None
    return contents


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures — Module scoped
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def dataset_store():
    """Instância real de DatasetStore."""
    from platform_base.core.dataset_store import DatasetStore
    return DatasetStore()


@pytest.fixture(scope="module")
def session_state(dataset_store):
    """Instância real de SessionState."""
    from platform_base.core.session_state import SessionState
    return SessionState(dataset_store)


@pytest.fixture(scope="module")
def signal_hub():
    """Instância real de SignalHub."""
    from platform_base.core.signal_hub import SignalHub
    return SignalHub()


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures — Function scoped (mocks)
# ═══════════════════════════════════════════════════════════════════════════
SIGNAL_HUB_SIGNALS = [
    "dataset_loaded", "dataset_removed", "dataset_selected",
    "series_added", "series_removed", "series_selected",
    "series_deselected", "series_visibility_changed",
    "plot_created", "plot_updated", "plot_closed", "view_synchronized",
    "time_selection_changed", "value_selection_changed", "selection_cleared",
    "operation_started", "operation_progress", "operation_completed",
    "operation_failed", "operation_cancelled",
    "streaming_started", "streaming_stopped", "streaming_paused",
    "streaming_time_changed",
    "ui_mode_changed", "theme_changed", "layout_changed",
    "error_occurred", "status_updated", "progress_updated",
]

SESSION_STATE_SIGNALS = [
    "selection_changed", "view_state_changed", "processing_state_changed",
    "streaming_state_changed", "ui_state_changed", "dataset_changed",
    "operation_finished", "session_loaded", "session_saved", "session_cleared",
]


@pytest.fixture
def mock_session_state():
    """MagicMock de SessionState com signals mockados."""
    mock = MagicMock()
    mock.spec = "SessionState"
    for sig in SESSION_STATE_SIGNALS:
        signal_mock = MagicMock()
        signal_mock.connect = MagicMock()
        signal_mock.disconnect = MagicMock()
        signal_mock.emit = MagicMock()
        setattr(mock, sig, signal_mock)
    # Atributos de estado
    mock.selection = MagicMock()
    mock.selection.current_dataset = None
    mock.selection.selected_series = []
    mock.view = MagicMock()
    mock.processing = MagicMock()
    mock.processing.is_processing = False
    mock.streaming = MagicMock()
    mock.streaming.is_active = False
    mock.ui = MagicMock()
    mock.ui.theme_mode = "light"
    mock.dataset_store = MagicMock()
    mock.dataset_store.list_datasets.return_value = []
    return mock


@pytest.fixture
def mock_signal_hub():
    """MagicMock de SignalHub com todos os 30 signals mockados."""
    mock = MagicMock()
    mock.spec = "SignalHub"
    for sig in SIGNAL_HUB_SIGNALS:
        signal_mock = MagicMock()
        signal_mock.connect = MagicMock()
        signal_mock.disconnect = MagicMock()
        signal_mock.emit = MagicMock()
        setattr(mock, sig, signal_mock)
    return mock


@pytest.fixture
def widget_factory(qapp):
    """Factory que cria widgets e faz cleanup automático no teardown."""
    created = []

    def _create(widget_class, *args, **kwargs):
        w = widget_class(*args, **kwargs)
        created.append(w)
        return w

    yield _create

    # Teardown
    for w in reversed(created):
        try:
            w.close()
        except Exception:
            pass
        try:
            w.deleteLater()
        except Exception:
            pass
    qapp.processEvents()
    gc.collect()
    qapp.processEvents()


@pytest.fixture
def sample_dataframe():
    """DataFrame de exemplo com 1000 pontos (time + 3 séries)."""
    n = 1000
    t = np.linspace(0, 10, n)
    return pd.DataFrame({
        "time": t,
        "temperature": 20.0 + 5.0 * np.sin(2 * np.pi * t / 10) + np.random.normal(0, 0.5, n),
        "pressure": 1.0 + 0.1 * np.cos(2 * np.pi * t / 5) + np.random.normal(0, 0.01, n),
        "flow_rate": 100.0 + 10.0 * t / 10 + np.random.normal(0, 1.0, n),
    })


@pytest.fixture
def temp_dir(tmp_path):
    """Diretório temporário para cada teste."""
    return tmp_path


# ═══════════════════════════════════════════════════════════════════════════
# Cleanup automático após cada teste
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture(autouse=True)
def _cleanup_qt(qapp):
    """Processa eventos Qt pendentes após cada teste."""
    yield
    qapp.processEvents()
    gc.collect()
    qapp.processEvents()


# ═══════════════════════════════════════════════════════════════════════════
# Helpers — disponíveis para todos os módulos de teste
# ═══════════════════════════════════════════════════════════════════════════
def get_all_widgets(parent: QWidget) -> list[QWidget]:
    """Retorna todos os QWidgets filhos recursivamente."""
    return parent.findChildren(QWidget)


def get_widget_by_name(parent: QWidget, name: str) -> QWidget | None:
    """Busca widget filho por objectName."""
    return parent.findChild(QWidget, name)


def count_widgets_by_type(parent: QWidget, widget_type: type) -> int:
    """Conta widgets filhos de um tipo específico."""
    return len(parent.findChildren(widget_type))


def validate_ui_xml(ui_path: Path) -> tuple[bool, str]:
    """Valida estrutura básica de um arquivo .ui XML."""
    try:
        tree = ElementTree.parse(str(ui_path))
        root = tree.getroot()
        if root.tag != "ui":
            return False, f"Root tag is '{root.tag}', expected 'ui'"
        widget = root.find("widget")
        if widget is None:
            return False, "No <widget> element found"
        if "class" not in widget.attrib:
            return False, "Root <widget> missing 'class' attribute"
        if "name" not in widget.attrib:
            return False, "Root <widget> missing 'name' attribute"
        return True, "OK"
    except ElementTree.ParseError as e:
        return False, f"XML parse error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_widgets_from_ui_xml(tree: ElementTree.ElementTree) -> list[dict]:
    """Extrai informações de widgets de um XML .ui parseado."""
    widgets = []
    root = tree.getroot()
    for widget_elem in root.iter("widget"):
        info = {
            "class": widget_elem.get("class", ""),
            "name": widget_elem.get("name", ""),
        }
        widgets.append(info)
    return widgets


def get_connections_from_ui_xml(tree: ElementTree.ElementTree) -> list[dict]:
    """Extrai conexões signal/slot de um XML .ui parseado."""
    connections = []
    root = tree.getroot()
    for conn in root.iter("connection"):
        info = {
            "sender": conn.findtext("sender", ""),
            "signal": conn.findtext("signal", ""),
            "receiver": conn.findtext("receiver", ""),
            "slot": conn.findtext("slot", ""),
        }
        connections.append(info)
    return connections


def get_resources_from_ui_xml(tree: ElementTree.ElementTree) -> list[str]:
    """Extrai referências a recursos (iconset, pixmap) de um XML .ui."""
    resources = []
    root = tree.getroot()
    for elem in root.iter():
        if elem.tag in ("iconset", "pixmap") and elem.text:
            resources.append(elem.text.strip())
    return resources
