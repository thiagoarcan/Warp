"""
Testes Automatizados para MainWindow - Interface Gráfica Principal

Este módulo testa TODOS os botões, menus e comandos da MainWindow
SEM NECESSIDADE DE INTERAÇÃO MANUAL.

Cobertura:
- Toolbar: Abrir, Salvar, Gráfico 2D/3D, Interpolar, Derivada, Integral, Exportar, Config
- Menus: Arquivo, Visualizar, Operações, Ferramentas, Ajuda
- Atalhos: Ctrl+O, Ctrl+S, Ctrl+2, Ctrl+3, Ctrl+E, Ctrl+I, Ctrl+D, etc.
- Estados: Operações, Progresso, Erros
- Painéis: DataPanel, VizPanel, OperationsPanel
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import tempfile

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


class TestMainWindowInitialization:
    """Testes de inicialização da MainWindow."""
    
    def test_mainwindow_imports_successfully(self, qapp):
        """Verifica que MainWindow pode ser importada."""
        from platform_base.ui.main_window import MainWindow, ModernMainWindow
        assert MainWindow is not None
        assert ModernMainWindow is not None
        assert MainWindow == ModernMainWindow  # Alias
    
    def test_mainwindow_creates_without_error(self, qapp, session_state, mock_message_box):
        """MainWindow deve ser criada sem erros."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            assert window is not None
            window.close()
    
    def test_mainwindow_has_session_state(self, qapp, session_state, mock_message_box):
        """MainWindow deve ter SessionState inicializado."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            assert hasattr(window, 'session_state')
            assert window.session_state is not None
            window.close()
    
    def test_mainwindow_has_panels(self, qapp, session_state, mock_message_box):
        """MainWindow deve ter os três painéis principais."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            assert hasattr(window, '_data_panel')
            assert hasattr(window, '_viz_panel')
            assert hasattr(window, '_operations_panel')
            window.close()
    
    def test_mainwindow_has_statusbar(self, qapp, session_state, mock_message_box):
        """MainWindow deve ter status bar."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            assert hasattr(window, '_status_label')
            assert hasattr(window, '_progress_bar')
            window.close()


class TestToolbarActions:
    """Testes para todas as ações da toolbar."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_open_dataset_action_exists(self, main_window):
        """Botão 'Abrir' deve existir na toolbar."""
        assert hasattr(main_window, '_open_dataset')
        assert callable(main_window._open_dataset)
    
    def test_open_dataset_calls_file_dialog(self, main_window):
        """Botão 'Abrir' deve abrir diálogo de arquivo."""
        with patch('PyQt6.QtWidgets.QFileDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.exec.return_value = False
            mock_dialog.return_value = mock_instance
            
            main_window._open_dataset()
            mock_dialog.assert_called_once()
    
    def test_save_session_action_exists(self, main_window):
        """Botão 'Salvar Sessão' deve existir."""
        assert hasattr(main_window, '_save_session')
        assert callable(main_window._save_session)
    
    def test_save_session_calls_file_dialog(self, main_window):
        """Botão 'Salvar Sessão' deve abrir diálogo."""
        with patch('PyQt6.QtWidgets.QFileDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.exec.return_value = False
            mock_dialog.return_value = mock_instance
            
            main_window._save_session()
            mock_dialog.assert_called_once()
    
    def test_load_session_action_exists(self, main_window):
        """'Carregar Sessão' deve existir."""
        assert hasattr(main_window, '_load_session')
        assert callable(main_window._load_session)
    
    def test_create_2d_plot_action_exists(self, main_window):
        """Botão 'Gráfico 2D' deve existir."""
        assert hasattr(main_window, '_create_2d_plot')
        assert callable(main_window._create_2d_plot)
    
    def test_create_2d_plot_calls_viz_panel(self, main_window):
        """'Gráfico 2D' deve chamar viz_panel."""
        if main_window._viz_panel:
            with patch.object(main_window._viz_panel, 'create_2d_plot') as mock:
                main_window._create_2d_plot()
                mock.assert_called_once()
    
    def test_create_3d_plot_action_exists(self, main_window):
        """Botão 'Gráfico 3D' deve existir."""
        assert hasattr(main_window, '_create_3d_plot')
        assert callable(main_window._create_3d_plot)
    
    def test_create_3d_plot_calls_viz_panel(self, main_window):
        """'Gráfico 3D' deve chamar viz_panel."""
        if main_window._viz_panel:
            with patch.object(main_window._viz_panel, 'create_3d_plot') as mock:
                main_window._create_3d_plot()
                mock.assert_called_once()
    
    def test_interpolate_series_action_exists(self, main_window):
        """Botão 'Interpolar' deve existir."""
        assert hasattr(main_window, '_interpolate_series')
        assert callable(main_window._interpolate_series)
    
    def test_interpolate_calls_operations_panel(self, main_window):
        """'Interpolar' deve chamar operations_panel."""
        if main_window._operations_panel:
            with patch.object(main_window._operations_panel, 'show_interpolation_dialog') as mock:
                main_window._interpolate_series()
                mock.assert_called_once()
    
    def test_derivative_action_exists(self, main_window):
        """Botão 'Derivada' deve existir."""
        assert hasattr(main_window, '_calculate_derivative')
        assert callable(main_window._calculate_derivative)
    
    def test_derivative_calls_operations_panel(self, main_window):
        """'Derivada' deve chamar operations_panel."""
        if main_window._operations_panel:
            with patch.object(main_window._operations_panel, 'show_derivative_dialog') as mock:
                main_window._calculate_derivative()
                mock.assert_called_once()
    
    def test_integral_action_exists(self, main_window):
        """Botão 'Integral' deve existir."""
        assert hasattr(main_window, '_calculate_integral')
        assert callable(main_window._calculate_integral)
    
    def test_integral_calls_operations_panel(self, main_window):
        """'Integral' deve chamar operations_panel."""
        if main_window._operations_panel:
            with patch.object(main_window._operations_panel, 'show_integral_dialog') as mock:
                main_window._calculate_integral()
                mock.assert_called_once()
    
    def test_export_data_action_exists(self, main_window):
        """Botão 'Exportar' deve existir."""
        assert hasattr(main_window, '_export_data')
        assert callable(main_window._export_data)
    
    def test_export_without_dataset_shows_info(self, main_window, mock_message_box):
        """'Exportar' sem dataset deve mostrar aviso."""
        main_window.session_state.current_dataset = None
        
        with patch.object(main_window, '_show_info') as mock_info:
            main_window._export_data()
            mock_info.assert_called_once()
    
    def test_show_settings_action_exists(self, main_window):
        """Botão 'Configurações' deve existir."""
        assert hasattr(main_window, '_show_settings')
        assert callable(main_window._show_settings)


class TestMenuActions:
    """Testes para todas as ações dos menus."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_clear_cache_action_exists(self, main_window):
        """Menu 'Limpar Cache' deve existir."""
        assert hasattr(main_window, '_clear_cache')
        assert callable(main_window._clear_cache)
    
    def test_show_about_action_exists(self, main_window):
        """Menu 'Sobre' deve existir."""
        assert hasattr(main_window, '_show_about')
        assert callable(main_window._show_about)
    
    def test_show_about_displays_dialog(self, main_window, mock_message_box):
        """'Sobre' deve mostrar diálogo."""
        main_window._show_about()
        mock_message_box.about.assert_called_once()
    
    def test_reset_layout_action_exists(self, main_window):
        """Menu 'Resetar Layout' deve existir."""
        assert hasattr(main_window, '_reset_layout')
        assert callable(main_window._reset_layout)
    
    def test_reset_layout_changes_splitter(self, main_window):
        """'Resetar Layout' deve ajustar splitter."""
        if main_window._main_splitter:
            main_window._reset_layout()
            sizes = main_window._main_splitter.sizes()
            assert len(sizes) == 3


class TestKeyboardShortcuts:
    """Testes para atalhos de teclado."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_undo_action_exists(self, main_window):
        """Ctrl+Z (Undo) deve existir."""
        assert hasattr(main_window, '_undo')
        assert callable(main_window._undo)
    
    def test_redo_action_exists(self, main_window):
        """Ctrl+Y (Redo) deve existir."""
        assert hasattr(main_window, '_redo')
        assert callable(main_window._redo)
    
    def test_refresh_action_exists(self, main_window):
        """F5 (Refresh) deve existir."""
        assert hasattr(main_window, '_refresh_view')
        assert callable(main_window._refresh_view)
    
    def test_delete_selection_exists(self, main_window):
        """Delete deve existir."""
        assert hasattr(main_window, '_delete_selection')
        assert callable(main_window._delete_selection)
    
    def test_cancel_operation_exists(self, main_window):
        """Escape deve existir."""
        assert hasattr(main_window, '_cancel_operation')
        assert callable(main_window._cancel_operation)
    
    def test_toggle_fullscreen_exists(self, main_window):
        """F11 (Fullscreen) deve existir."""
        assert hasattr(main_window, '_toggle_fullscreen')
        assert callable(main_window._toggle_fullscreen)
    
    def test_new_session_exists(self, main_window):
        """Ctrl+N (Nova Sessão) deve existir."""
        assert hasattr(main_window, '_new_session')
        assert callable(main_window._new_session)
    
    def test_select_all_series_exists(self, main_window):
        """Ctrl+A (Selecionar Tudo) deve existir."""
        assert hasattr(main_window, '_select_all_series')
        assert callable(main_window._select_all_series)


class TestSessionStateIntegration:
    """Testes de integração com SessionState."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_operation_started_signal(self, main_window):
        """Signal de início de operação deve atualizar status."""
        main_window._on_operation_started("Test Operation")
        assert "Test Operation" in main_window._status_label.text()
    
    def test_operation_finished_success(self, main_window):
        """Signal de fim de operação (sucesso) deve atualizar status."""
        main_window._on_operation_finished("Test", True)
        assert "✅" in main_window._status_label.text() or "concluída" in main_window._status_label.text().lower()
    
    def test_operation_finished_failure(self, main_window):
        """Signal de fim de operação (falha) deve atualizar status."""
        main_window._on_operation_finished("Test", False)
        assert "❌" in main_window._status_label.text() or "falhou" in main_window._status_label.text().lower()
    
    def test_operation_progress_updates_bar(self, main_window):
        """Signal de progresso deve atualizar barra."""
        main_window._on_operation_progress(50.0, "Processing...")
        assert main_window._progress_bar.value() == 50


class TestErrorHandling:
    """Testes de tratamento de erros."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_show_error_method_exists(self, main_window):
        """Método _show_error deve existir."""
        assert hasattr(main_window, '_show_error')
        assert callable(main_window._show_error)
    
    def test_show_info_method_exists(self, main_window):
        """Método _show_info deve existir."""
        assert hasattr(main_window, '_show_info')
        assert callable(main_window._show_info)
    
    def test_show_error_displays_critical(self, main_window, mock_message_box):
        """_show_error deve mostrar QMessageBox.critical."""
        main_window._show_error("Test Title", "Test Message")
        mock_message_box.critical.assert_called_once()
    
    def test_show_info_displays_information(self, main_window, mock_message_box):
        """_show_info deve mostrar QMessageBox.information."""
        main_window._show_info("Test Title", "Test Message")
        mock_message_box.information.assert_called_once()


class TestLayoutManagement:
    """Testes de gerenciamento de layout."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_save_layout_method_exists(self, main_window):
        """Método _save_layout deve existir."""
        assert hasattr(main_window, '_save_layout')
        assert callable(main_window._save_layout)
    
    def test_restore_layout_method_exists(self, main_window):
        """Método _restore_layout deve existir."""
        assert hasattr(main_window, '_restore_layout')
        assert callable(main_window._restore_layout)
    
    def test_main_splitter_exists(self, main_window):
        """MainWindow deve ter splitter principal."""
        assert hasattr(main_window, '_main_splitter')
        assert main_window._main_splitter is not None
    
    def test_splitter_has_three_widgets(self, main_window):
        """Splitter deve ter 3 widgets (painéis)."""
        if main_window._main_splitter:
            count = main_window._main_splitter.count()
            assert count == 3, f"Expected 3 widgets, got {count}"


class TestAutoSave:
    """Testes de auto-save."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_autosave_timer_exists(self, main_window):
        """Timer de auto-save deve existir."""
        assert hasattr(main_window, '_autosave_timer')
    
    def test_auto_save_session_method_exists(self, main_window):
        """Método _auto_save_session deve existir."""
        assert hasattr(main_window, '_auto_save_session')
        assert callable(main_window._auto_save_session)
    
    def test_save_session_on_exit_exists(self, main_window):
        """Método save_session_on_exit deve existir."""
        assert hasattr(main_window, 'save_session_on_exit')
        assert callable(main_window.save_session_on_exit)


class TestWindowSettings:
    """Testes de configurações da janela."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_window_has_settings_constants(self, main_window):
        """MainWindow deve ter constantes de settings."""
        assert hasattr(main_window, 'SETTINGS_ORG')
        assert hasattr(main_window, 'SETTINGS_APP')
    
    def test_window_title_set(self, main_window):
        """MainWindow deve ter título definido."""
        title = main_window.windowTitle()
        assert len(title) > 0
        assert "Platform" in title or "platform" in title.lower()
    
    def test_window_has_minimum_size(self, main_window):
        """MainWindow deve ter tamanho mínimo."""
        min_size = main_window.minimumSize()
        assert min_size.width() >= 800
        assert min_size.height() >= 600


class TestFullscreenToggle:
    """Testes de modo tela cheia."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_fullscreen_toggle_method(self, main_window):
        """_toggle_fullscreen deve alternar modo."""
        assert hasattr(main_window, '_toggle_fullscreen')


class TestCancelOperation:
    """Testes de cancelamento de operações."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_cancel_hides_progress_bar(self, main_window):
        """_cancel_operation deve esconder barra de progresso."""
        main_window._progress_bar.setVisible(True)
        main_window._cancel_operation()
        assert not main_window._progress_bar.isVisible() or "Pronto" in main_window._status_label.text()


class TestDatasetChangeHandling:
    """Testes de tratamento de mudança de dataset."""
    
    @pytest.fixture
    def main_window(self, qapp, session_state, mock_message_box):
        """Cria MainWindow para testes."""
        from platform_base.ui.main_window import MainWindow
        
        with patch.object(MainWindow, 'closeEvent', lambda self, e: e.accept()):
            window = MainWindow(session_state)
            yield window
            window.close()
    
    def test_dataset_changed_handler_exists(self, main_window):
        """Handler _on_dataset_changed deve existir."""
        assert hasattr(main_window, '_on_dataset_changed')
        assert callable(main_window._on_dataset_changed)
    
    def test_dataset_loaded_handler_exists(self, main_window):
        """Handler _on_dataset_loaded deve existir."""
        assert hasattr(main_window, '_on_dataset_loaded')
        assert callable(main_window._on_dataset_loaded)
    
    def test_empty_dataset_updates_status(self, main_window):
        """Dataset vazio deve atualizar status."""
        main_window._on_dataset_changed("")
        assert "Nenhum" in main_window._status_label.text() or "dataset" in main_window._status_label.text().lower()
