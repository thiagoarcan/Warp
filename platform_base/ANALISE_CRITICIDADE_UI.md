# 🔴 ANÁLISE DE CRITICIDADE - Arquivos .ui Incompletos

## Resumo Executivo

De 51 arquivos `.ui` incompletos (contêm apenas `contentLayout"/>`), identifiquei quais são **CRÍTICOS** para o funcionamento da aplicação baseado em:

1. **Referência por classe Python com `UI_FILE`**
2. **Ausência de fallback** (levanta `RuntimeError` se falhar)
3. **Uso no fluxo de inicialização principal** (MainWindow → Painéis)

---

## 📊 STATUS GERAL

| Categoria | Quantidade |
|-----------|------------|
| Arquivos `.ui` COMPLETOS | 16 |
| Arquivos `.ui` INCOMPLETOS | 51 |
| Arquivos `.ui` FALTANTES (não existem) | 6 |

---

## 🚨 TOP 10 ARQUIVOS .ui MAIS CRÍTICOS (Prioridade de Correção)

### 1. 🔴 **streamingControlWidget.ui** - CRITICIDADE: CRÍTICA
- **Classe Python**: `StreamingControlWidget`
- **Arquivo**: `src/platform_base/ui/streaming_controls.py` (linha 52)
- **UI_FILE**: `streamingControlWidget.ui`
- **Impacto**: **RAISE RuntimeError** - Widget de controle de streaming.
- **Fallback**: **NENHUM** - Aplicação FALHA ao instanciar.

### 2. 🔴 **streamingControls.ui** - CRITICIDADE: CRÍTICA  
- **Classe Python**: `StreamingControls`
- **Arquivo**: `src/platform_base/ui/streaming_controls.py` (linha 450)
- **UI_FILE**: `streamingControls.ui`
- **Impacto**: **RAISE RuntimeError** - Controles de playback/streaming.
- **Fallback**: **NENHUM** - Bloqueia funcionalidade de streaming.

### 3. 🔴 **baseOperationDialog.ui** - CRITICIDADE: CRÍTICA
- **Classe Python**: `BaseOperationDialog`
- **Arquivo**: `src/platform_base/ui/operation_dialogs.py` (linha 302)
- **UI_FILE**: `baseOperationDialog.ui`
- **Impacto**: **RAISE RuntimeError** - Base para TODOS os diálogos de operação.
- **Fallback**: **NENHUM** - Bloqueia cálculos/operações matemáticas.

### 4. 🔴 **previewWidget.ui** - CRITICIDADE: CRÍTICA
- **Classe Python**: `PreviewWidget`
- **Arquivo**: `src/platform_base/ui/operation_dialogs.py` (linha 236)
- **UI_FILE**: `previewWidget.ui`
- **Impacto**: **RAISE RuntimeError** - Preview de operações.
- **Fallback**: **NENHUM** - Sem preview nas operações.

### 5. 🔴 **operationPreviewDialog.ui** - CRITICIDADE: ALTA
- **Classe Python**: `OperationPreviewDialog`
- **Arquivo**: `src/platform_base/ui/preview_dialog.py` (linha 134)
- **UI_FILE**: `operationPreviewDialog.ui`
- **Impacto**: **RAISE RuntimeError** - Diálogo de preview de operações.
- **Fallback**: **NENHUM**.

### 6. 🔴 **shortcutsDialog.ui** - CRITICIDADE: ALTA
- **Classe Python**: `ShortcutsDialog`
- **Arquivo**: `src/platform_base/ui/shortcuts.py` (linha 581)
- **UI_FILE**: `shortcutsDialog.ui`
- **Impacto**: **RAISE RuntimeError** - Diálogo de atalhos de teclado.
- **Fallback**: **NENHUM** - Menu Ajuda → Atalhos falha.

### 7. 🟠 **annotationDialog.ui** - CRITICIDADE: MÉDIA-ALTA
- **Classe Python**: `AnnotationDialog`
- **Arquivo**: `src/platform_base/ui/context_menu.py` (linha 154)
- **UI_FILE**: `annotationDialog.ui`
- **Impacto**: **RAISE RuntimeError** - Adicionar anotações no gráfico.
- **Fallback**: **NENHUM** - Menu de contexto falha.

### 8. 🟠 **compareSeriesDialog.ui** - CRITICIDADE: MÉDIA-ALTA
- **Classe Python**: `CompareSeriesDialog`
- **Arquivo**: `src/platform_base/ui/context_menu.py` (linha 45)
- **UI_FILE**: `compareSeriesDialog.ui`
- **Impacto**: **RAISE RuntimeError** - Comparar séries temporais.
- **Fallback**: **NENHUM**.

### 9. 🟠 **selectionManagerWidget.ui** - CRITICIDADE: MÉDIA
- **Classe Python**: `SelectionManagerWidget`
- **Arquivo**: `src/platform_base/ui/selection_widgets.py` (linha 553)
- **UI_FILE**: `selectionManagerWidget.ui`
- **Impacto**: **RAISE RuntimeError** - Gerenciamento de seleções.
- **Fallback**: **NENHUM**.

### 10. 🟠 **modernMainWindow.ui** - CRITICIDADE: MÉDIA
- **Classe Python**: `ModernMainWindow`
- **Arquivo**: `src/platform_base/ui/main_window.py` (linha 48)
- **UI_FILE**: `desktop/ui_files/modernMainWindow.ui`
- **Impacto**: É a janela principal alternativa.
- **Fallback**: **TEM** fallback programático, então não bloqueia totalmente.

---

## 🚫 ARQUIVOS .ui FALTANTES (NÃO EXISTEM)

Estes arquivos são referenciados por classes Python mas **NÃO EXISTEM** no diretório `ui_files`:

| Arquivo Faltante | Classe Python | Arquivo Python |
|-----------------|---------------|----------------|
| `smoothingConfigDialog.ui` | `SmoothingDialog` | `src/platform_base/ui/context_menu.py` (linha 113) |
| `conditionalSelectionDialog.ui` | `ConditionalSelectionDialog` | `src/platform_base/desktop/selection/selection_widgets.py` (linha 196) |
| `selectionStatsWidget.ui` | `SelectionStatsWidget` | `src/platform_base/desktop/selection/selection_widgets.py` (linha 297) |
| `selectionPanel.ui` | `SelectionPanel` | `src/platform_base/desktop/selection/selection_widgets.py` (linha 384) |
| `mathAnalysisDialog.ui` | `MathAnalysisDialog` | `src/platform_base/desktop/menus/plot_context_menu.py` (linha 54) |
| `compactDataPanel.ui` | `DataPanel` (alternativo) | `src/platform_base/ui/panels/data_panel.py` (linha 147) |

---

## ✅ ARQUIVOS .ui COMPLETOS (Funcionais)

Estes 16 arquivos estão **completos** e funcionais:

| # | Arquivo | Classe |
|---|---------|--------|
| 1 | `aboutDialog.ui` | `AboutDialog` |
| 2 | `axesConfigDialog.ui` | `AxesConfigDialog` |
| 3 | `configPanel.ui` | `ConfigPanel` |
| 4 | `dataPanel.ui` | `DataPanel` |
| 5 | `exportDialog.ui` | `ExportDialog` |
| 6 | `filterDialog.ui` | `FilterDialog` |
| 7 | `mainWindow.ui` | `MainWindow` |
| 8 | `operationsPanel.ui` | `OperationsPanel` |
| 9 | `resultsPanel.ui` | `ResultsPanel` |
| 10 | `settingsDialog.ui` | `SettingsDialog` |
| 11 | `smoothingDialog.ui` | `SmoothingDialog` |
| 12 | `streamingPanel.ui` | `StreamingPanel` |
| 13 | `syncSettingsWidget.ui` | `SyncSettingsWidget` |
| 14 | `uploadDialog.ui` | `UploadDialog` |
| 15 | `videoExportDialog.ui` | `VideoExportDialog` |
| 16 | `vizPanel.ui` | `VizPanel` |

---

## 📋 LISTA COMPLETA DE DEPENDÊNCIAS COM RuntimeError

| # | Arquivo .ui | Classe Python | Arquivo Python | Prioridade |
|---|------------|---------------|----------------|------------|
| 1 | streamingControlWidget.ui | StreamingControlWidget | ui/streaming_controls.py:52 | 🔴 CRÍTICA |
| 2 | streamingControls.ui | StreamingControls | ui/streaming_controls.py:450 | 🔴 CRÍTICA |
| 3 | baseOperationDialog.ui | BaseOperationDialog | ui/operation_dialogs.py:302 | 🔴 CRÍTICA |
| 4 | previewWidget.ui | PreviewWidget | ui/operation_dialogs.py:236 | 🔴 CRÍTICA |
| 5 | operationPreviewDialog.ui | OperationPreviewDialog | ui/preview_dialog.py:134 | 🔴 ALTA |
| 6 | shortcutsDialog.ui | ShortcutsDialog | ui/shortcuts.py:581 | 🔴 ALTA |
| 7 | annotationDialog.ui | AnnotationDialog | ui/context_menu.py:154 | 🟠 MÉDIA-ALTA |
| 8 | compareSeriesDialog.ui | CompareSeriesDialog | ui/context_menu.py:45 | 🟠 MÉDIA-ALTA |
| 9 | rangePickerWidget.ui | RangePickerWidget | ui/selection_widgets.py:71 | 🟠 MÉDIA |
| 10 | brushSelectionWidget.ui | BrushSelectionWidget | ui/selection_widgets.py:200 | 🟠 MÉDIA |
| 11 | queryBuilderWidget.ui | QueryBuilderWidget | ui/selection_widgets.py:340 | 🟠 MÉDIA |
| 12 | selectionHistoryWidget.ui | SelectionHistoryWidget | ui/selection_widgets.py:457 | 🟠 MÉDIA |
| 13 | selectionManagerWidget.ui | SelectionManagerWidget | ui/selection_widgets.py:553 | 🟠 MÉDIA |
| 14 | selectionSync.ui | SelectionSyncWidget | ui/selection_widgets.py:740 | 🟠 MÉDIA |
| 15 | selectionToolbar.ui | SelectionToolbar | ui/selection_widgets.py:857 | 🟠 MÉDIA |
| 16 | selectionInfo.ui | SelectionInfoWidget | ui/selection_widgets.py:956 | 🟠 MÉDIA |

---

## 🎯 PLANO DE AÇÃO RECOMENDADO

### Fase 1 - CRÍTICO (Bloqueia aplicação) - **4 arquivos**
```
1. streamingControlWidget.ui
2. streamingControls.ui
3. baseOperationDialog.ui
4. previewWidget.ui
```

### Fase 2 - ALTO (Funcionalidade importante) - **4 arquivos**
```
5. operationPreviewDialog.ui
6. shortcutsDialog.ui
7. CRIAR: smoothingConfigDialog.ui (FALTANTE)
8. CRIAR: mathAnalysisDialog.ui (FALTANTE)
```

### Fase 3 - MÉDIO-ALTO (Context Menu) - **2 arquivos**
```
9. annotationDialog.ui
10. compareSeriesDialog.ui
```

### Fase 4 - MÉDIO (Widgets de seleção) - **8 arquivos**
```
11-18. rangePickerWidget, brushSelectionWidget, queryBuilderWidget,
       selectionHistoryWidget, selectionManagerWidget, selectionSync,
       selectionToolbar, selectionInfo
```

### Fase 5 - CRIAR arquivos faltantes
```
- conditionalSelectionDialog.ui
- selectionStatsWidget.ui
- selectionPanel.ui
- compactDataPanel.ui
```

### Fase 6 - BAIXO (Utilitários/Especializados) - **37 arquivos restantes**
```
- Filtros (bandpass, highpass, lowpass, notch, movingAverage)
- Widgets de parâmetros (boolean, choice, numeric, parameter)
- Indicadores (autoSave, memory, log)
- Diálogos de cálculo (calculus, derivative, integral, interpolation)
- Widgets de preview (previewCanvas, previewVisualization)
- Outros (plot2D, plot3D, plotContextMenu, resultsTable, etc.)
```

---

## 📈 MÉTRICAS

- **Total de classes Python com UI_FILE**: 45+
- **Arquivos .ui que causam RuntimeError se incompletos**: 30+
- **Estimativa de esforço para Fase 1**: 4-8 horas
- **Estimativa de esforço para Fases 1-3**: 16-24 horas
- **Estimativa de esforço total**: 40-60 horas

---

*Gerado em: 2026-02-05*
