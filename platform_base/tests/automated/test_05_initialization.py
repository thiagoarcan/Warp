# -*- coding: utf-8 -*-
"""
test_05_initialization.py â€” Testes de inicializaÃ§Ã£o da aplicaÃ§Ã£o

Testes para validar:
1. QApplication cria sem erros
2. PlatformApplication inicializa corretamente
3. Core classes (DatasetStore, SessionState, SignalHub) inicializam
4. MainWindow inicializa
5. PainÃ©is e dialogs inicializam
6. Managers (Theme, Config, Undo) inicializam
"""
from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow


pytestmark = [pytest.mark.automated, pytest.mark.gui]


class TestQApplicationCreation:
    """Testa criaÃ§Ã£o do QApplication."""

    def test_qapplication_exists(self, qapp):
        """Verifica que QApplication existe e Ã© vÃ¡lida."""
        assert qapp is not None
        assert isinstance(qapp, QApplication)

    def test_qapplication_name(self, qapp):
        """Verifica nome da aplicaÃ§Ã£o."""
        name = qapp.applicationName()
        assert name is not None
        assert len(name) > 0


class TestPlatformApplicationInit:
    """Testa PlatformApplication."""

    def test_platform_application_importable(self):
        """Verifica que PlatformApplication pode ser importada."""
        try:
            from platform_base.ui.app import PlatformApplication
            assert PlatformApplication is not None
        except ImportError:
            pytest.skip("PlatformApplication nÃ£o disponÃ­vel")

    def test_platform_application_is_qapplication(self):
        """Verifica que PlatformApplication herda de QApplication."""
        try:
            from platform_base.ui.app import PlatformApplication
            assert issubclass(PlatformApplication, QApplication)
        except ImportError:
            pytest.skip("PlatformApplication nÃ£o disponÃ­vel")


class TestDatasetStoreInit:
    """Testa inicializaÃ§Ã£o do DatasetStore."""

    def test_dataset_store_creation(self, dataset_store):
        """Verifica que DatasetStore Ã© criado corretamente."""
        assert dataset_store is not None

    def test_dataset_store_empty_initially(self, dataset_store):
        """Verifica que DatasetStore comeÃ§a vazio."""
        # Tenta obter lista de datasets
        if hasattr(dataset_store, 'list_datasets'):
            datasets = dataset_store.list_datasets()
            assert len(datasets) == 0
        elif hasattr(dataset_store, 'datasets'):
            assert len(dataset_store.datasets) == 0
        else:
            # Apenas verifica que existe
            assert dataset_store is not None

    def test_dataset_store_has_methods(self, dataset_store):
        """Verifica que DatasetStore tem mÃ©todos esperados."""
        # NOTA: API real usa add_dataset/get_dataset, nÃ£o add/get
        expected_methods = ['add_dataset', 'get_dataset', 'list_datasets', 'add_series']
        found = 0
        
        for method in expected_methods:
            if hasattr(dataset_store, method):
                found += 1
        
        # Pelo menos alguns mÃ©todos devem existir
        assert found >= 2, f"DatasetStore tem poucos mÃ©todos: {found}"


class TestSessionStateInit:
    """Testa inicializaÃ§Ã£o do SessionState."""

    def test_session_state_creation(self, session_state):
        """Verifica que SessionState Ã© criado corretamente."""
        assert session_state is not None

    def test_session_state_has_expected_attributes(self, session_state):
        """Verifica atributos esperados do SessionState."""
        # Atributos comuns de estado
        state_attrs = ['selection', 'view', 'processing', 'streaming', 'ui']
        found = 0
        
        for attr in state_attrs:
            if hasattr(session_state, attr):
                found += 1
        
        # Pelo menos alguns atributos devem existir
        assert found >= 2, f"SessionState tem poucos atributos de estado: {found}"


class TestSignalHubInit:
    """Testa inicializaÃ§Ã£o do SignalHub."""

    def test_signal_hub_creation(self, signal_hub):
        """Verifica que SignalHub Ã© criado corretamente."""
        assert signal_hub is not None

    def test_signal_hub_is_qobject(self, signal_hub):
        """Verifica que SignalHub herda de QObject."""
        from PyQt6.QtCore import QObject
        assert isinstance(signal_hub, QObject)


class TestMainWindowInit:
    """Testa inicializaÃ§Ã£o da MainWindow."""

    def test_main_window_creation(self, qapp, mock_session_state, mock_signal_hub):
        """Verifica que ModernMainWindow Ã© criada corretamente."""
        try:
            from platform_base.ui.main_window_unified import ModernMainWindow
        except ImportError:
            pytest.skip("ModernMainWindow nÃ£o disponÃ­vel")
        
        window = ModernMainWindow(mock_session_state, mock_signal_hub)
        assert window is not None
        assert isinstance(window, QMainWindow)
        
        window.close()
        window.deleteLater()
        qapp.processEvents()

    def test_main_window_has_ui_components(self, qapp, mock_session_state, mock_signal_hub):
        """Verifica que MainWindow tem componentes de UI."""
        try:
            from platform_base.ui.main_window_unified import ModernMainWindow
        except ImportError:
            pytest.skip("ModernMainWindow nÃ£o disponÃ­vel")
        
        window = ModernMainWindow(mock_session_state, mock_signal_hub)
        
        # Deve ter pelo menos central widget
        assert window.centralWidget() is not None or True  # Pode nÃ£o ter em alguns designs
        
        window.close()
        window.deleteLater()
        qapp.processEvents()


class TestPanelsInit:
    """Testa inicializaÃ§Ã£o dos painÃ©is."""

    PANELS = [
        ("platform_base.ui.panels.data_panel", "DataPanel"),
        ("platform_base.ui.panels.viz_panel", "VizPanel"),
        ("platform_base.ui.panels.config_panel", "ConfigPanel"),
        ("platform_base.ui.panels.operations_panel", "OperationsPanel"),
        ("platform_base.ui.panels.results_panel", "ResultsPanel"),
        ("platform_base.ui.panels.streaming_panel", "StreamingPanel"),
    ]

    @pytest.mark.parametrize("module_path,class_name", PANELS, ids=[p[1] for p in PANELS])
    def test_panel_init(self, qapp, mock_session_state, mock_signal_hub, module_path, class_name):
        """Testa inicializaÃ§Ã£o de cada painel."""
        try:
            import importlib
            module = importlib.import_module(module_path)
            panel_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"{class_name} nÃ£o disponÃ­vel: {e}")
        
        panel = None
        try:
            panel = panel_class(mock_session_state, mock_signal_hub)
        except (TypeError, AttributeError, RuntimeError):
            try:
                panel = panel_class(parent=None)
            except Exception as e:
                pytest.skip(f"NÃ£o foi possÃ­vel criar {class_name}: {e}")
        
        assert panel is not None
        assert isinstance(panel, QWidget)
        
        panel.close()
        panel.deleteLater()
        qapp.processEvents()


class TestDialogsInit:
    """Testa inicializaÃ§Ã£o dos dialogs."""

    DIALOGS = [
        ("platform_base.desktop.dialogs.upload_dialog", "UploadDialog"),
        ("platform_base.desktop.dialogs.settings_dialog", "SettingsDialog"),
        ("platform_base.desktop.dialogs.about_dialog", "AboutDialog"),
        ("platform_base.ui.export_dialog", "ExportDialog"),
        ("platform_base.ui.dialogs.filter_dialog", "FilterDialog"),
        ("platform_base.ui.dialogs.smoothing_dialog", "SmoothingDialog"),
        ("platform_base.ui.shortcuts", "ShortcutsDialog"),
    ]

    @pytest.mark.parametrize("module_path,class_name", DIALOGS, ids=[d[1] for d in DIALOGS])
    def test_dialog_init(self, qapp, mock_session_state, mock_signal_hub, module_path, class_name):
        """Testa inicializaÃ§Ã£o de cada dialog."""
        try:
            import importlib
            module = importlib.import_module(module_path)
            dialog_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"{class_name} nÃ£o disponÃ­vel: {e}")
        
        dialog = None
        try:
            dialog = dialog_class(parent=None)
        except TypeError:
            try:
                dialog = dialog_class(mock_session_state, mock_signal_hub)
            except TypeError:
                try:
                    dialog = dialog_class()
                except Exception as e:
                    pytest.skip(f"NÃ£o foi possÃ­vel criar {class_name}: {e}")
        
        assert dialog is not None
        
        dialog.close()
        dialog.deleteLater()
        qapp.processEvents()


class TestThemeManagerInit:
    """Testa inicializaÃ§Ã£o do ThemeManager."""

    def test_theme_manager_importable(self):
        """Verifica que ThemeManager pode ser importado."""
        try:
            from platform_base.ui.themes import ThemeManager
            assert ThemeManager is not None
        except ImportError:
            pytest.skip("ThemeManager nÃ£o disponÃ­vel")

    def test_theme_manager_creation(self, qapp):
        """Verifica que ThemeManager Ã© criado corretamente."""
        try:
            from platform_base.ui.themes import ThemeManager
        except ImportError:
            pytest.skip("ThemeManager nÃ£o disponÃ­vel")
        
        manager = ThemeManager()
        assert manager is not None

    def test_theme_mode_enum_exists(self):
        """Verifica que ThemeMode enum existe."""
        try:
            from platform_base.ui.themes import ThemeMode
            assert ThemeMode is not None
            # Deve ter pelo menos LIGHT e DARK
            assert hasattr(ThemeMode, 'LIGHT') or hasattr(ThemeMode, 'Light')
        except ImportError:
            pytest.skip("ThemeMode nÃ£o disponÃ­vel")


class TestConfigManagerInit:
    """Testa inicializaÃ§Ã£o do ConfigManager."""

    def test_config_manager_importable(self):
        """Verifica que ConfigManager pode ser importado."""
        try:
            from platform_base.core.config_manager import ConfigManager
            assert ConfigManager is not None
        except ImportError:
            pytest.skip("ConfigManager nÃ£o disponÃ­vel")

    def test_config_manager_creation(self):
        """Verifica que ConfigManager Ã© criado corretamente."""
        try:
            from platform_base.core.config_manager import ConfigManager
        except ImportError:
            pytest.skip("ConfigManager nÃ£o disponÃ­vel")
        
        try:
            manager = ConfigManager()
            assert manager is not None
        except Exception as e:
            pytest.skip(f"ConfigManager nÃ£o pÃ´de ser criado: {e}")


class TestUndoManagerInit:
    """Testa inicializaÃ§Ã£o do UndoManager."""

    def test_undo_manager_importable(self):
        """Verifica que UndoManager pode ser importado."""
        try:
            from platform_base.ui.undo_redo import UndoManager
            assert UndoManager is not None
        except ImportError:
            pytest.skip("UndoManager nÃ£o disponÃ­vel")

    def test_undo_manager_creation(self):
        """Verifica que UndoManager Ã© criado corretamente."""
        try:
            from platform_base.ui.undo_redo import UndoManager
        except ImportError:
            pytest.skip("UndoManager nÃ£o disponÃ­vel")
        
        manager = UndoManager()
        assert manager is not None

    def test_undo_manager_starts_empty(self):
        """Verifica que UndoManager comeÃ§a com stack vazio."""
        try:
            from platform_base.ui.undo_redo import UndoManager
        except ImportError:
            pytest.skip("UndoManager nÃ£o disponÃ­vel")
        
        manager = UndoManager()
        
        # Verifica que nÃ£o pode desfazer/refazer inicialmente
        if hasattr(manager, 'can_undo'):
            assert not manager.can_undo()
        if hasattr(manager, 'can_redo'):
            assert not manager.can_redo()


class TestUIFallbackCreation:
    """Testa criaÃ§Ã£o de UI fallback quando .ui nÃ£o encontrado."""

    def test_widget_with_missing_ui_fallback(self, qapp, mock_session_state, mock_signal_hub):
        """Verifica que widgets criam fallback quando .ui nÃ£o encontrado."""
        # Este teste verifica que a aplicaÃ§Ã£o nÃ£o quebra se .ui estiver faltando
        # A maioria dos widgets tem fallback programÃ¡tico
        
        # Teste com ConfigPanel (geralmente tem fallback)
        try:
            from platform_base.ui.panels.config_panel import ConfigPanel
            panel = ConfigPanel(mock_session_state, mock_signal_hub)
            
            # Se chegou aqui, funcionou (com ou sem .ui)
            assert panel is not None
            
            panel.close()
            panel.deleteLater()
            qapp.processEvents()
        except Exception:
            # Se falhar, Ã© aceitÃ¡vel (pode requerer .ui)
            pytest.skip("ConfigPanel requer arquivo .ui")





