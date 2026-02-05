# Plano de Migração Completa para .ui

## TL;DR
Migração sistemática de 55 classes programáticas para usar arquivos .ui via `UiLoaderMixin`, iniciando pela conexão dos 99 arquivos .ui órfãos existentes, seguida de criação dos 6 faltantes. Finaliza com suite completa de testes de integração automatizados.

---

## Fase 0: Limpeza e Preparação (1-2 dias)

### 0.1 Remover Arquivos .ui Inválidos
Arquivos .ui para classes não-visuais (Workers, Enums, Managers) devem ser removidos:

| Remover | Motivo |
|---------|--------|
| fileLoadWorker.ui | Worker thread - não tem UI |
| exportWorkerThread.ui | Worker thread - não tem UI |
| videoExportWorker.ui | Worker thread - não tem UI |
| operationType.ui | Enum - não tem UI |
| selectionMode.ui | Enum - não tem UI |
| plotType.ui | Enum - não tem UI |
| dataType.ui | Enum - não tem UI |
| sessionState.ui | Manager/State - não tem UI |
| signalHub.ui | Signal manager - não tem UI |

### 0.2 Padronizar Caminhos UI_FILE
Normalizar todos os `UI_FILE` para usar caminho relativo a `desktop/ui_files/`:
```python
UI_FILE = "nomeDoArquivo.ui"  # Padrão correto
```

### 0.3 Criar Script de Validação
Script para verificar integridade da migração:
- Verificar que cada classe com `UiLoaderMixin` tem `UI_FILE` definido
- Verificar que cada `UI_FILE` aponta para arquivo existente
- Verificar que cada .ui tem classe correspondente

---

## Fase 1: Integrar Arquivos .ui Órfãos (5-7 dias)

Conectar os 99 arquivos .ui existentes às suas classes correspondentes.

### 1.1 Painéis Principais (Prioridade Alta)
| Classe | Arquivo .py | Arquivo .ui | Linhas a Remover |
|--------|-------------|-------------|------------------|
| OperationsPanel | ui/panels/operations_panel.py | operationsPanel.ui | ~1500 |
| StreamingPanel | ui/panels/streaming_panel.py | streamingPanel.ui | ~400 |
| SelectionPanel | ui/panels/selection_panel.py | selectionPanel.ui | ~300 |

**Padrão de Migração:**
1. Adicionar herança de `UiLoaderMixin`
2. Definir `UI_FILE = "operationsPanel.ui"`
3. Substituir `_setup_ui()` por `self._load_ui()`
4. Criar `_setup_ui_from_file()` para configurações pós-carregamento
5. Remover código de criação programática de widgets

### 1.2 Diálogos de Operações (Prioridade Alta)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| FilterDialog | desktop/dialogs/filter_dialog.py | filterDialog.ui |
| SmoothingDialog | desktop/dialogs/smoothing_dialog.py | smoothingDialog.ui |
| DerivativeDialog | desktop/dialogs/derivative_dialog.py | derivativeDialog.ui |
| IntegralDialog | desktop/dialogs/integral_dialog.py | integralDialog.ui |
| InterpolationDialog | desktop/dialogs/interpolation_dialog.py | interpolationDialog.ui |
| SynchronizationDialog | desktop/dialogs/synchronization_dialog.py | synchronizationDialog.ui |

### 1.3 Diálogos Auxiliares (Prioridade Média)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| ExportDialog | desktop/dialogs/export_dialog.py | exportDialog.ui |
| VideoExportDialog | desktop/dialogs/video_export_dialog.py | videoExportDialog.ui |
| OperationPreviewDialog | desktop/dialogs/operation_preview_dialog.py | operationPreviewDialog.ui |
| ShortcutsDialog | desktop/dialogs/shortcuts_dialog.py | shortcutsDialog.ui |
| AnnotationDialog | desktop/dialogs/annotation_dialog.py | annotationDialog.ui |
| CompareSeriesDialog | desktop/dialogs/compare_series_dialog.py | compareSeriesDialog.ui |
| AboutDialog | desktop/dialogs/about_dialog.py | aboutDialog.ui |

### 1.4 Widgets de Seleção (Prioridade Média)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| SelectionManagerWidget | ui/widgets/selection/selection_manager_widget.py | selectionManagerWidget.ui |
| RangePickerWidget | ui/widgets/selection/range_picker_widget.py | rangePickerWidget.ui |
| BrushSelectionWidget | ui/widgets/selection/brush_selection_widget.py | brushSelectionWidget.ui |
| QueryBuilderWidget | ui/widgets/selection/query_builder_widget.py | queryBuilderWidget.ui |
| SelectionHistoryWidget | ui/widgets/selection/selection_history_widget.py | selectionHistoryWidget.ui |
| SelectionToolbar | ui/widgets/selection/selection_toolbar.py | selectionToolbar.ui |
| SelectionInfo | ui/widgets/selection/selection_info.py | selectionInfo.ui |
| StatisticsWidget | ui/widgets/selection/statistics_widget.py | statisticsWidget.ui |
| SelectionSynchronizer | ui/widgets/selection/selection_synchronizer.py | selectionSynchronizer.ui |

### 1.5 Widgets de Streaming (Prioridade Média)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| StreamingControlWidget | ui/widgets/streaming/streaming_control_widget.py | streamingControlWidget.ui |
| StreamingControls | ui/widgets/streaming/streaming_controls.py | streamingControls.ui |
| MinimapWidget | ui/widgets/streaming/minimap_widget.py | minimapWidget.ui |
| TimeIntervalWidget | ui/widgets/streaming/time_interval_widget.py | timeIntervalWidget.ui |
| ValuePredicateWidget | ui/widgets/streaming/value_predicate_widget.py | valuePredicateWidget.ui |
| StreamFiltersWidget | ui/widgets/streaming/stream_filters_widget.py | streamFiltersWidget.ui |
| TimelineSlider | ui/widgets/streaming/timeline_slider.py | timelineSlider.ui |

### 1.6 Widgets de Configuração (Prioridade Baixa)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| InterpolationConfigWidget | ui/widgets/config/interpolation_config_widget.py | interpolationConfigWidget.ui |
| CalculusConfigWidget | ui/widgets/config/calculus_config_widget.py | calculusConfigWidget.ui |
| ParameterWidget | ui/widgets/parameters/parameter_widget.py | parameterWidget.ui |
| NumericParameterWidget | ui/widgets/parameters/numeric_parameter_widget.py | numericParameterWidget.ui |
| ChoiceParameterWidget | ui/widgets/parameters/choice_parameter_widget.py | choiceParameterWidget.ui |
| BooleanParameterWidget | ui/widgets/parameters/boolean_parameter_widget.py | booleanParameterWidget.ui |

### 1.7 Tabs de Settings (Prioridade Baixa)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| GeneralSettingsTab | ui/widgets/settings/general_settings_tab.py | generalSettingsTab.ui |
| PerformanceSettingsTab | ui/widgets/settings/performance_settings_tab.py | performanceSettingsTab.ui |
| LoggingSettingsTab | ui/widgets/settings/logging_settings_tab.py | loggingSettingsTab.ui |

### 1.8 Widgets Auxiliares (Prioridade Baixa)
| Classe | Arquivo .py | Arquivo .ui |
|--------|-------------|-------------|
| LogWidget | ui/widgets/log_widget.py | logWidget.ui |
| ResultsTable | ui/widgets/results_table.py | resultsTable.ui |
| RichTooltip | ui/widgets/rich_tooltip.py | richTooltip.ui |
| MemoryIndicator | ui/widgets/indicators/memory_indicator.py | memoryIndicator.ui |
| AutoSaveIndicator | ui/widgets/indicators/autosave_indicator.py | autoSaveIndicator.ui |
| PlotContextMenu | ui/widgets/plot_context_menu.py | plotContextMenu.ui |

---

## Fase 2: Casos Híbridos - Visualização (3-5 dias)

Widgets que usam bibliotecas externas (matplotlib, pyqtgraph, pyvista) requerem abordagem especial.

### 2.1 Padrão para Widgets Híbridos

**Estrutura do .ui:**
```xml
<widget class="QWidget" name="plotPlaceholder">
  <property name="objectName">
    <string>plotPlaceholder</string>
  </property>
</widget>
```

**Padrão de código:**
```python
class Plot2DWidget(QWidget, UiLoaderMixin):
    UI_FILE = "plot2DWidget.ui"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_ui()
        self._insert_plot_widget()
    
    def _insert_plot_widget(self):
        """Insere widget pyqtgraph no placeholder."""
        placeholder = self._find_widget("plotPlaceholder")
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
```

### 2.2 Widgets Matplotlib
| Classe | Arquivo .ui | Biblioteca |
|--------|-------------|------------|
| MatplotlibWidget | matplotlibWidget.ui | matplotlib.backends.backend_qtagg |
| PreviewCanvas | previewCanvas.ui | matplotlib.backends.backend_qtagg |
| PreviewWidget | previewWidget.ui | matplotlib.backends.backend_qtagg |
| PreviewVisualizationWidget | previewVisualizationWidget.ui | matplotlib.backends.backend_qtagg |

### 2.3 Widgets PyQtGraph
| Classe | Arquivo .ui | Biblioteca |
|--------|-------------|------------|
| Plot2DWidget | plot2DWidget.ui | pyqtgraph.PlotWidget |
| RangePickerWidget | rangePickerWidget.ui | pyqtgraph.PlotWidget |
| HeatmapWidget | heatmapWidget.ui | pyqtgraph.ImageView |
| BrushSelectionWidget | brushSelectionWidget.ui | pyqtgraph.PlotWidget |

### 2.4 Widgets PyVista
| Classe | Arquivo .ui | Biblioteca |
|--------|-------------|------------|
| Plot3DWidget | plot3DWidget.ui | pyvistaqt.QtInteractor |
| VizPanel (aba 3D) | vizPanel.ui | pyvistaqt.QtInteractor |

---

## Fase 3: Criar Arquivos .ui Faltantes (2-3 dias)

| Arquivo a Criar | Classe | Estrutura Principal |
|-----------------|--------|---------------------|
| mathAnalysisDialog.ui | MathAnalysisDialog | QDialog + QFormLayout |
| conditionalSelectionDialog.ui | ConditionalSelectionDialog | QDialog + QListWidget |
| selectionStatsWidget.ui | SelectionStatsWidget | QWidget + QTableWidget |
| syncSettingsWidget.ui | SyncSettingsWidget | QWidget + QFormLayout |
| heatmapWidget.ui | HeatmapWidget | QWidget + placeholder |
| matplotlibWidget.ui | MatplotlibWidget | QWidget + placeholder |

---

## Fase 4: Limpeza Final (1-2 dias)

### 4.1 Remover Fallbacks
Eliminar todos os métodos `_setup_ui_fallback()` das classes migradas.

### 4.2 Remover Código Programático
Eliminar blocos de criação programática de widgets:
- `QVBoxLayout()`, `QHBoxLayout()`, `QGridLayout()` inline
- `QPushButton()`, `QLabel()`, `QComboBox()` criados no código
- Chamadas a `setLayout()` programáticas

### 4.3 Atualizar Imports
Remover imports não utilizados após remoção de código programático.

### 4.4 Atualizar Documentação
- Atualizar `docs/UI_MIGRATION.md`
- Atualizar `README.md` com nova estrutura

---

## Fase 5: Testes de Integração Automatizados

### 5.1 Estrutura de Testes

```
tests/
├── integration/
│   └── ui/
│       ├── conftest.py              # Fixtures específicas para testes UI
│       ├── test_ui_loading.py       # Testes de carregamento .ui
│       ├── test_panels.py           # Testes de painéis
│       ├── test_dialogs.py          # Testes de diálogos
│       ├── test_widgets.py          # Testes de widgets
│       ├── test_hybrid_widgets.py   # Testes de widgets híbridos
│       └── test_full_integration.py # Testes end-to-end
```

### 5.2 Fixtures Compartilhadas

```python
# tests/integration/ui/conftest.py

import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """QApplication para todos os testes UI."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def mock_session_state():
    """Mock do SessionState para testes."""
    from unittest.mock import MagicMock
    state = MagicMock()
    state.series = {}
    state.current_series = None
    return state

@pytest.fixture
def mock_signal_hub():
    """Mock do SignalHub para testes."""
    from unittest.mock import MagicMock
    hub = MagicMock()
    return hub

@pytest.fixture
def ui_files_dir():
    """Diretório dos arquivos .ui."""
    return Path(__file__).parent.parent.parent.parent / "src/platform_base/desktop/ui_files"
```

### 5.3 Testes de Carregamento .ui (test_ui_loading.py)

```python
"""Testes de carregamento de arquivos .ui."""

import pytest
from pathlib import Path
from PyQt6 import uic

class TestUiFilesExist:
    """Verifica que todos os arquivos .ui existem."""
    
    UI_FILES = [
        "mainWindow.ui", "dataPanel.ui", "vizPanel.ui", "configPanel.ui",
        "resultsPanel.ui", "operationsPanel.ui", "streamingPanel.ui",
        "settingsDialog.ui", "uploadDialog.ui", "filterDialog.ui",
        "smoothingDialog.ui", "derivativeDialog.ui", "integralDialog.ui",
        "interpolationDialog.ui", "synchronizationDialog.ui", "exportDialog.ui",
        "videoExportDialog.ui", "aboutDialog.ui", "shortcutsDialog.ui",
        "annotationDialog.ui", "compareSeriesDialog.ui", "operationPreviewDialog.ui",
        "selectionPanel.ui", "selectionManagerWidget.ui", "rangePickerWidget.ui",
        "brushSelectionWidget.ui", "queryBuilderWidget.ui", "selectionHistoryWidget.ui",
        "selectionToolbar.ui", "selectionInfo.ui", "statisticsWidget.ui",
        "selectionSynchronizer.ui", "streamingControlWidget.ui", "streamingControls.ui",
        "minimapWidget.ui", "timeIntervalWidget.ui", "valuePredicateWidget.ui",
        "streamFiltersWidget.ui", "timelineSlider.ui", "interpolationConfigWidget.ui",
        "calculusConfigWidget.ui", "parameterWidget.ui", "numericParameterWidget.ui",
        "choiceParameterWidget.ui", "booleanParameterWidget.ui", "generalSettingsTab.ui",
        "performanceSettingsTab.ui", "loggingSettingsTab.ui", "logWidget.ui",
        "resultsTable.ui", "richTooltip.ui", "memoryIndicator.ui", "autoSaveIndicator.ui",
        "plot2DWidget.ui", "plot3DWidget.ui", "previewCanvas.ui", "previewWidget.ui",
    ]
    
    @pytest.mark.parametrize("ui_file", UI_FILES)
    def test_ui_file_exists(self, ui_files_dir, ui_file):
        """Verifica que arquivo .ui existe."""
        path = ui_files_dir / ui_file
        assert path.exists(), f"Arquivo .ui não encontrado: {ui_file}"
    
    @pytest.mark.parametrize("ui_file", UI_FILES)
    def test_ui_file_valid_xml(self, ui_files_dir, ui_file):
        """Verifica que arquivo .ui é XML válido."""
        import xml.etree.ElementTree as ET
        path = ui_files_dir / ui_file
        if path.exists():
            try:
                ET.parse(path)
            except ET.ParseError as e:
                pytest.fail(f"XML inválido em {ui_file}: {e}")
    
    @pytest.mark.parametrize("ui_file", UI_FILES)
    def test_ui_file_loadable(self, qapp, ui_files_dir, ui_file):
        """Verifica que arquivo .ui pode ser carregado pelo PyQt6."""
        from PyQt6.QtWidgets import QWidget
        path = ui_files_dir / ui_file
        if path.exists():
            widget = QWidget()
            try:
                uic.loadUi(str(path), widget)
            except Exception as e:
                pytest.fail(f"Falha ao carregar {ui_file}: {e}")
```

### 5.4 Testes de Painéis (test_panels.py)

```python
"""Testes de integração para painéis."""

import pytest
from PyQt6.QtWidgets import QWidget

class TestDataPanel:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.data_panel import DataPanel
        panel = DataPanel(mock_session_state, mock_signal_hub)
        assert panel is not None
        assert isinstance(panel, QWidget)
    
    def test_loads_ui(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.data_panel import DataPanel
        panel = DataPanel(mock_session_state, mock_signal_hub)
        assert panel._ui_loaded

class TestVizPanel:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.viz_panel import VizPanel
        panel = VizPanel(mock_session_state, mock_signal_hub)
        assert panel is not None

class TestOperationsPanel:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.operations_panel import OperationsPanel
        panel = OperationsPanel(mock_session_state, mock_signal_hub)
        assert panel is not None

class TestStreamingPanel:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.streaming_panel import StreamingPanel
        panel = StreamingPanel(mock_session_state, mock_signal_hub)
        assert panel is not None

class TestConfigPanel:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.config_panel import ConfigPanel
        panel = ConfigPanel(mock_session_state, mock_signal_hub)
        assert panel is not None

class TestResultsPanel:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.results_panel import ResultsPanel
        panel = ResultsPanel(mock_session_state, mock_signal_hub)
        assert panel is not None
```

### 5.5 Testes de Diálogos (test_dialogs.py)

```python
"""Testes de integração para diálogos."""

import pytest
from PyQt6.QtWidgets import QDialog

class TestFilterDialog:
    def test_creates(self, qapp):
        from platform_base.desktop.dialogs.filter_dialog import FilterDialog
        dialog = FilterDialog()
        assert dialog is not None
        assert isinstance(dialog, QDialog)

class TestSmoothingDialog:
    def test_creates(self, qapp):
        from platform_base.desktop.dialogs.smoothing_dialog import SmoothingDialog
        dialog = SmoothingDialog()
        assert dialog is not None

class TestSettingsDialog:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.desktop.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(mock_session_state, mock_signal_hub)
        assert dialog is not None

class TestUploadDialog:
    def test_creates(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.desktop.dialogs.upload_dialog import UploadDialog
        dialog = UploadDialog(mock_session_state, mock_signal_hub)
        assert dialog is not None

class TestAboutDialog:
    def test_creates(self, qapp):
        from platform_base.desktop.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog()
        assert dialog is not None
```

### 5.6 Testes End-to-End (test_full_integration.py)

```python
"""Testes de integração completa."""

import pytest
from PyQt6.QtWidgets import QMainWindow

class TestMainWindowIntegration:
    def test_main_window_creates(self, qapp):
        from platform_base.desktop.main_window import MainWindow
        window = MainWindow()
        assert window is not None
        assert isinstance(window, QMainWindow)
    
    def test_main_window_loads_ui(self, qapp):
        from platform_base.desktop.main_window import MainWindow
        window = MainWindow()
        assert window._ui_loaded
    
    def test_main_window_has_all_docks(self, qapp):
        from platform_base.desktop.main_window import MainWindow
        window = MainWindow()
        docks = ["dataDock", "vizDock", "configDock", "resultsDock", "operationsDock"]
        for dock_name in docks:
            dock = window._find_widget(dock_name)
            assert dock is not None, f"Dock {dock_name} não encontrado"

class TestFullWorkflow:
    def test_app_starts_without_errors(self, qapp):
        from platform_base.desktop.main_window import MainWindow
        window = MainWindow()
        window.show()
        assert window.isVisible()
        window.close()
    
    def test_all_panels_instantiate(self, qapp, mock_session_state, mock_signal_hub):
        from platform_base.ui.panels.data_panel import DataPanel
        from platform_base.ui.panels.viz_panel import VizPanel
        from platform_base.ui.panels.operations_panel import OperationsPanel
        
        panels = [
            DataPanel(mock_session_state, mock_signal_hub),
            VizPanel(mock_session_state, mock_signal_hub),
            OperationsPanel(mock_session_state, mock_signal_hub),
        ]
        
        for panel in panels:
            assert panel is not None
```

---

## Cronograma Consolidado

| Fase | Duração | Atividades | Entregáveis |
|------|---------|------------|-------------|
| Fase 0 | 1-2 dias | Limpeza e preparação | Script de validação, remoção de .ui inválidos |
| Fase 1 | 5-7 dias | Integrar 99 .ui órfãos | 55 classes migradas para UiLoaderMixin |
| Fase 2 | 3-5 dias | Casos híbridos | 10 widgets de visualização migrados |
| Fase 3 | 2-3 dias | Criar .ui faltantes | 6 novos arquivos .ui |
| Fase 4 | 1-2 dias | Limpeza final | Código limpo, sem fallbacks |
| Fase 5 | 3-4 dias | Testes de integração | Suite completa de testes automatizados |
| **Total** | **15-23 dias** | - | - |

---

## Métricas de Sucesso

| Métrica | Antes | Depois |
|---------|-------|--------|
| Arquivos .ui em uso | 9 | 108+ |
| Arquivos .ui órfãos | 99 | 0 |
| Classes programáticas | 55 | 0 |
| Linhas de código UI | ~8000+ | ~500 (híbridos) |
| Cobertura de testes UI | ~60% | 95%+ |
| Fallbacks ativos | 9 | 0 |

---

## Comandos de Execução

```bash
# Executar todos os testes de UI
pytest tests/integration/ui/ -v

# Executar apenas testes de carregamento
pytest tests/integration/ui/test_ui_loading.py -v

# Executar testes de painéis
pytest tests/integration/ui/test_panels.py -v

# Executar testes end-to-end
pytest tests/integration/ui/test_full_integration.py -v

# Executar com cobertura
pytest tests/integration/ui/ --cov=platform_base.ui --cov-report=html

# Executar testes rápidos (smoke)
pytest tests/integration/ui/ -m smoke -v
```
