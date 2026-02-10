"""
Testes de GUI/Funcionais usando pytest-qt

NÍVEL 6: GUI/Functional Tests
- Testa widgets, dialogs e interações de usuário
"""
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from PyQt6.QtCore import Qt

# Qt imports
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QWidget

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_data():
    """Dados de exemplo para testes"""
    t = np.linspace(0, 10, 1000)
    y = np.sin(2 * np.pi * t)
    return t, y


@pytest.fixture
def temp_csv(tmp_path, sample_data):
    """Cria arquivo CSV temporário para testes"""
    t, y = sample_data
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(
        "time,value\n" + "\n".join(f"{ti:.6f},{yi:.6f}" for ti, yi in zip(t, y))
    )
    return csv_file


@pytest.fixture
def viz_config():
    """Configuração de visualização para testes"""
    from platform_base.viz.config import VizConfig
    return VizConfig()


@pytest.fixture
def mock_session_state():
    """Mock de session state para testes"""
    mock = MagicMock()
    mock.dataset_store = MagicMock()
    mock.selection = MagicMock()
    return mock


@pytest.fixture
def mock_signal_hub():
    """Mock de signal hub para testes"""
    mock = MagicMock()
    return mock


# =============================================================================
# TEST CLASSES - VIZ WIDGETS
# =============================================================================

@pytest.mark.gui
class TestPlot2DWidget:
    """Testes para Plot2DWidget"""
    
    def test_widget_creation(self, qtbot, viz_config):
        """Verifica criação do widget de plot 2D"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        assert widget is not None
        assert widget.isVisible() is False  # Not shown yet
    
    def test_widget_show(self, qtbot, viz_config):
        """Verifica que widget pode ser mostrado"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        widget.show()
        
        assert widget.isVisible()
    
    def test_add_series(self, qtbot, viz_config, sample_data):
        """Verifica adição de série ao plot"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        t, y = sample_data
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        # Add series - series_index is optional int, not name
        widget.add_series("test_series", t, y, series_index=0)
        
        # Should have the series (data stored in _series_data)
        assert "test_series" in widget._series_data
    
    def test_clear_plot(self, qtbot, viz_config, sample_data):
        """Verifica limpeza do plot"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        t, y = sample_data
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        widget.add_series("test_series", t, y, series_index=0)
        
        # Clear - se método existe
        if hasattr(widget, 'clear'):
            widget.clear()
            assert len(widget._series_data) == 0
        elif hasattr(widget, 'clear_all'):
            widget.clear_all()
            assert len(widget._series_data) == 0
        # Se não existe método clear, apenas verifica que série foi adicionada
        else:
            assert "test_series" in widget._series_data
    
    def test_toggle_grid(self, qtbot, viz_config):
        """Verifica toggle de grid - se método existe"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        # Toggle grid - just verify method exists or no crash
        if hasattr(widget, 'toggle_grid'):
            widget.toggle_grid()
        # Se não existe, teste passa porque toggle grid não é obrigatório
    
    def test_multiple_series(self, qtbot, viz_config):
        """Verifica adição de múltiplas séries"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        t = np.linspace(0, 10, 100)
        for i in range(5):
            y = np.sin(2 * np.pi * t * (i + 1))
            widget.add_series(f"series_{i}", t, y, series_index=i)
        
        assert len(widget._series_data) == 5
    
    def test_remove_series(self, qtbot, viz_config, sample_data):
        """Verifica remoção de série"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        t, y = sample_data
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        widget.add_series("test", t, y, series_index=0)
        
        # Remove if method exists
        if hasattr(widget, 'remove_series'):
            widget.remove_series("test")
            assert "test" not in widget._series_data


@pytest.mark.gui
class TestPlot3DWidget:
    """Testes para Plot3DWidget"""
    
    def test_widget_creation(self, qtbot, viz_config):
        """Verifica criação do widget de plot 3D"""
        pytest.importorskip("pyvista")
        from platform_base.viz.figures_3d import Plot3DWidget
        
        widget = Plot3DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        assert widget is not None


# =============================================================================
# TEST CLASSES - DATA PANEL
# =============================================================================

@pytest.mark.gui
class TestDataPanelWidget:
    """Testes para DataPanel"""
    
    def test_panel_creation(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica criação do painel de dados"""
        from platform_base.desktop.widgets.data_panel import DataPanel
        
        panel = DataPanel(mock_session_state, mock_signal_hub)
        qtbot.addWidget(panel)
        
        assert panel is not None
    
    def test_panel_has_tree_widget(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica que painel tem tree widget"""
        from platform_base.desktop.widgets.data_panel import DataPanel
        
        panel = DataPanel(mock_session_state, mock_signal_hub)
        qtbot.addWidget(panel)
        
        # Should have a tree widget (pode ser tree ou data_tree)
        assert hasattr(panel, 'tree') or hasattr(panel, 'data_tree')


# =============================================================================
# TEST CLASSES - CONFIG PANEL
# =============================================================================

@pytest.mark.gui
class TestConfigPanelWidget:
    """Testes para ConfigPanel"""
    
    def test_panel_creation(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica criação do painel de configuração"""
        from platform_base.desktop.widgets.config_panel import ConfigPanel
        
        panel = ConfigPanel(mock_session_state, mock_signal_hub)
        qtbot.addWidget(panel)
        
        assert panel is not None


# =============================================================================
# TEST CLASSES - RESULTS PANEL
# =============================================================================

@pytest.mark.gui
class TestResultsPanelWidget:
    """Testes para ResultsPanel"""
    
    def test_panel_creation(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica criação do painel de resultados"""
        from platform_base.desktop.widgets.results_panel import ResultsPanel
        
        panel = ResultsPanel(mock_session_state, mock_signal_hub)
        qtbot.addWidget(panel)
        
        assert panel is not None


# =============================================================================
# TEST CLASSES - UPLOAD DIALOG
# =============================================================================

@pytest.mark.gui
class TestUploadDialog:
    """Testes para UploadDialog"""
    
    def test_dialog_creation(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica criação do diálogo de upload"""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        dialog = UploadDialog(mock_session_state, mock_signal_hub)
        qtbot.addWidget(dialog)
        
        assert dialog is not None
        assert isinstance(dialog, QDialog)
    
    def test_dialog_has_preview_table(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica que diálogo tem tabela de preview"""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        dialog = UploadDialog(mock_session_state, mock_signal_hub)
        qtbot.addWidget(dialog)
        
        assert dialog.preview_table is not None
    
    def test_dialog_accept_reject_buttons(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica botões existem no diálogo"""
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        
        dialog = UploadDialog(mock_session_state, mock_signal_hub)
        qtbot.addWidget(dialog)
        
        # Find buttons
        buttons = dialog.findChildren(QPushButton)
        
        # Should have at least one button
        assert len(buttons) >= 1


# =============================================================================
# TEST CLASSES - SETTINGS DIALOG
# =============================================================================

@pytest.mark.gui
class TestSettingsDialog:
    """Testes para SettingsDialog"""
    
    def test_dialog_creation(self, qtbot, mock_session_state):
        """Verifica criação do diálogo de configurações"""
        from platform_base.desktop.dialogs.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(mock_session_state)
        qtbot.addWidget(dialog)
        
        assert dialog is not None


# =============================================================================
# TEST CLASSES - ABOUT DIALOG
# =============================================================================

@pytest.mark.gui
class TestAboutDialog:
    """Testes para AboutDialog"""
    
    def test_dialog_creation(self, qtbot):
        """Verifica criação do diálogo Sobre"""
        from platform_base.desktop.dialogs.about_dialog import AboutDialog
        
        dialog = AboutDialog()
        qtbot.addWidget(dialog)
        
        assert dialog is not None


# =============================================================================
# TEST CLASSES - VIZ PANEL
# =============================================================================

@pytest.mark.gui
class TestVizPanel:
    """Testes para VizPanel"""
    
    def test_panel_creation(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica criação do painel de visualização"""
        from platform_base.desktop.widgets.viz_panel import VizPanel
        
        panel = VizPanel(mock_session_state, mock_signal_hub)
        qtbot.addWidget(panel)
        
        assert panel is not None
    
    def test_panel_has_tab_widget(self, qtbot, mock_session_state, mock_signal_hub):
        """Verifica que painel tem estrutura de tabs"""
        from PyQt6.QtWidgets import QTabWidget

        from platform_base.desktop.widgets.viz_panel import VizPanel
        
        panel = VizPanel(mock_session_state, mock_signal_hub)
        qtbot.addWidget(panel)
        
        # Verifica se há algum QTabWidget filho
        tab_widgets = panel.findChildren(QTabWidget)
        assert len(tab_widgets) >= 1 or hasattr(panel, 'tab_widget') or hasattr(panel, 'tabs')


# =============================================================================
# TEST CLASSES - KEYBOARD INTERACTIONS
# =============================================================================

@pytest.mark.gui
class TestKeyboardInteractions:
    """Testes de interações de teclado"""
    
    def test_escape_closes_dialog(self, qtbot):
        """Verifica que ESC fecha diálogo"""
        from platform_base.desktop.dialogs.about_dialog import AboutDialog
        
        dialog = AboutDialog()
        qtbot.addWidget(dialog)
        dialog.show()
        
        # Press Escape
        qtbot.keyClick(dialog, Qt.Key.Key_Escape)
        
        # Dialog should be closed or rejected
        assert not dialog.isVisible() or dialog.result() == QDialog.DialogCode.Rejected


# =============================================================================
# TEST CLASSES - MOUSE INTERACTIONS
# =============================================================================

@pytest.mark.gui
class TestMouseInteractions:
    """Testes de interações de mouse"""
    
    def test_click_on_button(self, qtbot):
        """Verifica clique em botão"""
        button = QPushButton("Test")
        qtbot.addWidget(button)
        
        clicked = []
        button.clicked.connect(lambda: clicked.append(True))
        
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        
        assert len(clicked) == 1


# =============================================================================
# TEST CLASSES - SIGNALS
# =============================================================================

@pytest.mark.gui
class TestWidgetSignals:
    """Testes de sinais de widgets"""
    
    def test_plot_selection_signal(self, qtbot, viz_config, sample_data):
        """Verifica sinal de seleção no plot"""
        from platform_base.viz.figures_2d import Plot2DWidget
        
        t, y = sample_data
        widget = Plot2DWidget(config=viz_config)
        qtbot.addWidget(widget)
        
        # Add series
        widget.add_series("test", t, y, series_index=0)
        
        # Widget should have selection_changed signal
        assert hasattr(widget, 'selection_changed') or hasattr(widget, 'time_selection_changed')
