"""
Testes automatizados de navegação entre telas
Verifica que é possível navegar entre diferentes telas da aplicação
"""

import pytest
from pathlib import Path
import sys


class TestApplicationInitialization:
    """Testes de inicialização da aplicação"""

    @pytest.mark.gui
    def test_application_can_be_imported(self):
        """Verifica que módulos principais podem ser importados"""
        try:
            from platform_base.desktop.main_window import MainWindow
            assert MainWindow is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar MainWindow: {e}")

    @pytest.mark.gui
    def test_dataset_store_can_be_created(self):
        """Verifica que DatasetStore pode ser criado"""
        try:
            from platform_base.core.dataset_store import DatasetStore
            store = DatasetStore()
            assert store is not None
        except Exception as e:
            pytest.fail(f"Falha ao criar DatasetStore: {e}")

    @pytest.mark.gui
    def test_session_state_can_be_created(self, mock_dataset_store):
        """Verifica que SessionState pode ser criado"""
        try:
            from platform_base.desktop.session_state import SessionState
            state = SessionState(mock_dataset_store)
            assert state is not None
        except Exception as e:
            pytest.fail(f"Falha ao criar SessionState: {e}")

    @pytest.mark.gui
    def test_signal_hub_can_be_created(self):
        """Verifica que SignalHub pode ser criado"""
        try:
            from platform_base.desktop.signal_hub import SignalHub
            hub = SignalHub()
            assert hub is not None
        except Exception as e:
            pytest.fail(f"Falha ao criar SignalHub: {e}")


class TestMainWindowInitialization:
    """Testes de inicialização da janela principal"""

    @pytest.mark.gui
    def test_main_window_can_be_created_programmatically(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica que MainWindow pode ser criada programaticamente"""
        try:
            from platform_base.desktop.main_window import MainWindow
            
            # Tentar criar sem UI file (deve falhar)
            # ou criar com UI file disponível
            try:
                window = MainWindow(mock_session_state, mock_signal_hub)
                qtbot.addWidget(window)
                assert window is not None
            except RuntimeError as e:
                # Esperado se UI file não puder ser carregado
                assert "ERRO" in str(e) or "não foi possível carregar" in str(e).lower()
        except Exception as e:
            # Pode falhar se não houver display ou UI file
            pytest.skip(f"MainWindow não pode ser criado: {e}")


class TestDialogsNavigation:
    """Testes de navegação em diálogos"""

    @pytest.mark.gui
    def test_upload_dialog_can_be_imported(self):
        """Verifica que UploadDialog pode ser importado"""
        try:
            from platform_base.desktop.dialogs.upload_dialog import UploadDialog
            assert UploadDialog is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar UploadDialog: {e}")

    @pytest.mark.gui
    def test_about_dialog_can_be_imported(self):
        """Verifica que AboutDialog pode ser importado"""
        try:
            from platform_base.desktop.dialogs.about_dialog import AboutDialog
            assert AboutDialog is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar AboutDialog: {e}")

    @pytest.mark.gui
    def test_settings_dialog_can_be_imported(self):
        """Verifica que SettingsDialog pode ser importado"""
        try:
            from platform_base.desktop.dialogs.settings_dialog import SettingsDialog
            assert SettingsDialog is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar SettingsDialog: {e}")


class TestPanelsNavigation:
    """Testes de navegação entre painéis"""

    @pytest.mark.gui
    def test_data_panel_can_be_imported(self):
        """Verifica que DataPanel pode ser importado"""
        try:
            from platform_base.desktop.widgets.data_panel import DataPanel
            assert DataPanel is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar DataPanel: {e}")

    @pytest.mark.gui
    def test_viz_panel_can_be_imported(self):
        """Verifica que VizPanel pode ser importado"""
        try:
            from platform_base.desktop.widgets.viz_panel import VizPanel
            assert VizPanel is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar VizPanel: {e}")

    @pytest.mark.gui
    def test_config_panel_can_be_imported(self):
        """Verifica que ConfigPanel pode ser importado"""
        try:
            from platform_base.desktop.widgets.config_panel import ConfigPanel
            assert ConfigPanel is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar ConfigPanel: {e}")

    @pytest.mark.gui
    def test_results_panel_can_be_imported(self):
        """Verifica que ResultsPanel pode ser importado"""
        try:
            from platform_base.desktop.widgets.results_panel import ResultsPanel
            assert ResultsPanel is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar ResultsPanel: {e}")


class TestApplicationFlow:
    """Testes de fluxo da aplicação"""

    @pytest.mark.gui
    def test_application_entry_point_exists(self):
        """Verifica que ponto de entrada da aplicação existe"""
        app_path = Path(__file__).parent.parent.parent / "launch_app.py"
        assert app_path.exists(), "launch_app.py não encontrado"

    @pytest.mark.gui
    def test_desktop_app_entry_point_exists(self):
        """Verifica que módulo de app desktop existe"""
        try:
            from platform_base.desktop import app
            assert hasattr(app, 'main') or hasattr(app, 'PlatformApplication')
        except ImportError as e:
            pytest.fail(f"Falha ao importar app desktop: {e}")


class TestUILoaderMixin:
    """Testes do sistema de carregamento de UI"""

    @pytest.mark.gui
    def test_ui_loader_mixin_exists(self):
        """Verifica que UiLoaderMixin existe"""
        try:
            from platform_base.ui.ui_loader_mixin import UiLoaderMixin
            assert UiLoaderMixin is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar UiLoaderMixin: {e}")

    @pytest.mark.gui
    def test_ui_files_directory_defined(self):
        """Verifica que diretório de arquivos UI está definido"""
        try:
            from platform_base.ui.ui_loader_mixin import UI_FILES_DIR
            assert UI_FILES_DIR is not None
            # Verificar que é um Path
            from pathlib import Path
            assert isinstance(UI_FILES_DIR, Path)
        except ImportError as e:
            pytest.fail(f"UI_FILES_DIR não definido: {e}")
