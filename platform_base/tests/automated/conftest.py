"""
Fixtures para testes automatizados PyQt6
"""

import pytest
import gc
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


@pytest.fixture(scope="session")
def qapp_args():
    """Argumentos para QApplication"""
    return []


@pytest.fixture(scope="session")
def qapp(qapp_args, pytestconfig):
    """
    Fixture para QApplication com offscreen rendering
    """
    # Forçar offscreen platform para testes sem display
    import os
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(qapp_args)
        app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    yield app
    
    # Cleanup
    app.quit()


@pytest.fixture
def clean_qapp():
    """Fixture para garantir cleanup após cada teste"""
    yield
    
    # Force garbage collection
    gc.collect()
    
    # Process events para garantir cleanup
    if QApplication.instance():
        QApplication.processEvents()


@pytest.fixture
def mock_dataset_store():
    """Mock para DatasetStore"""
    from platform_base.core.dataset_store import DatasetStore
    return DatasetStore()


@pytest.fixture
def mock_session_state(mock_dataset_store):
    """Mock para SessionState"""
    from platform_base.desktop.session_state import SessionState
    return SessionState(mock_dataset_store)


@pytest.fixture
def mock_signal_hub():
    """Mock para SignalHub"""
    from platform_base.desktop.signal_hub import SignalHub
    return SignalHub()
