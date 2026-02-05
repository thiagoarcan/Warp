## Plano de Migração - Abordagem "Complexos Primeiro"

### TL;DR
Migração invertida começando pelos componentes mais complexos (MainWindow, painéis principais, widgets de visualização), garantindo que a arquitetura esteja sólida antes de migrar componentes simples. Reduz retrabalho e garante integração correta desde o início.

---

### Fase 1: Preparação e Arquitetura Base (3-5 dias)

1. **Consolidar caminhos de arquivos .ui** - Usar apenas `desktop/ui_files/` como diretório padrão

2. **Eliminar duplicatas de código** - Escolher implementação canônica para `AboutDialog`, `PlotContextMenu`, `Plot2DWidget`, `Plot3DWidget`, `ConfigPanel`, `ResultsPanel`, `DataPanel`

3. **Criar infraestrutura de promoted widgets** - Configurar QtDesigner para reconhecer widgets customizados do projeto

4. **Definir estratégia para widgets dinâmicos** - Placeholders no .ui com inserção programática para matplotlib/pyqtgraph/pyvista

### Considerações Fase 1
- Criar arquivo `.pth` ou plugin QtDesigner para promoted widgets?
- Definir convenção de nomenclatura: `{nome}Placeholder` para widgets dinâmicos

---

### Fase 2: MainWindow e Painéis Principais (10-14 dias)

1. **Migrar MainWindow** - Criar/atualizar .ui completo para `main_window.py` incluindo:
   - Menu bar completo com todas as ações
   - Toolbar principal
   - Status bar com indicadores
   - Dock widgets para todos os painéis
   - Layout de splitters

2. **Migrar VizPanel (mais complexo):**
   - Atualizar `vizPanel.ui` com:
     - Toolbar de ações de plot
     - QTabWidget para abas de plots (conteúdo dinâmico)
     - Splitter com controles laterais
     - Placeholders para `Plot2DWidget`, `Plot3DWidget`
   - Configurar promoted widgets para widgets de visualização

3. **Migrar OperationsPanel (100% programático → .ui):**
   - Criar operationsPanel.ui com:
     - Seletor de operação (StableComboBox)
     - Área de parâmetros dinâmicos (QStackedWidget)
     - Botões de execução/preview
     - Preview canvas placeholder

4. **Migrar StreamingPanel (100% programático → .ui):**
   - Criar streamingPanel.ui com:
     - Timeline/slider de posição
     - Controles de playback (play, pause, stop)
     - Minimap de navegação
     - Indicadores de posição/tempo

5. **Atualizar painéis existentes:**
   - `DataPanel` → eliminar fallback, usar 100% `dataPanel.ui`
   - `ConfigPanel` → atualizar `configPanel.ui` com promoted widgets
   - `ResultsPanel` → atualizar `resultsPanel.ui`

### Considerações Fase 2
- MainWindow usa QDockWidget - testar persistência de layout com .ui
- Widgets de visualização matplotlib/pyvista devem usar placeholder + inserção programática

---

### Fase 3: Widgets de Visualização e Seleção (10-14 dias)

1. **Widgets de Visualização (6 widgets - críticos):**
   - `Plot2DWidget` (pyqtgraph) → `plot2DWidget.ui`
   - `Plot3DWidget` (pyvista) → `plot3DWidget.ui`
   - `HeatmapWidget` → heatmapWidget.ui
   - `MatplotlibWidget` → matplotlibWidget.ui
   - `PreviewCanvas` → `previewCanvas.ui`
   - `PreviewWidget` → `previewWidget.ui`

2. **Widgets de Seleção (10 widgets):**
   - `SelectionPanel` → selectionPanel.ui
   - `SelectionManagerWidget` → `selectionManagerWidget.ui`
   - `RangePickerWidget` → `rangePickerWidget.ui`
   - `BrushSelectionWidget` → `brushSelectionWidget.ui`
   - `QueryBuilderWidget` → `queryBuilderWidget.ui`
   - `SelectionHistoryWidget` → `selectionHistoryWidget.ui`
   - `SelectionToolbar` → `selectionToolbar.ui`
   - `SelectionInfo` → `selectionInfo.ui`
   - `StatisticsWidget` → statisticsWidget.ui
   - `SelectionSynchronizer` → `selectionSynchronizer.ui`

3. **Widgets de Streaming/Filtros (7 widgets):**
   - `StreamingControlWidget` → `streamingControlWidget.ui`
   - `StreamingControls` → `streamingControls.ui`
   - `MinimapWidget` → minimapWidget.ui
   - `TimeIntervalWidget` → `timeIntervalWidget.ui`
   - `ValuePredicateWidget` → `valuePredicateWidget.ui`
   - `StreamFiltersWidget` → `streamFiltersWidget.ui`
   - `TimelineSlider` → timelineSlider.ui

### Considerações Fase 3
- Widgets pyqtgraph/matplotlib: usar QWidget placeholder no .ui, inserir widget real em `__init__`
- Testar integração com painéis principais migrados na Fase 2

---

### Fase 4: Widgets de Configuração e Parâmetros (7-10 dias)

1. **Widgets de Configuração de Operações (9 widgets):**
   - `InterpolationConfigWidget` → `interpolationConfigWidget.ui`
   - `CalculusConfigWidget` → `calculusConfigWidget.ui`
   - `ParameterWidget` (base) → `parameterWidget.ui`
   - `NumericParameterWidget` → `numericParameterWidget.ui`
   - `ChoiceParameterWidget` → `choiceParameterWidget.ui`
   - `BooleanParameterWidget` → `booleanParameterWidget.ui`

2. **Tabs de Settings (3 widgets):**
   - `GeneralSettingsTab` → `generalSettingsTab.ui`
   - `PerformanceSettingsTab` → `performanceSettingsTab.ui`
   - `LoggingSettingsTab` → `loggingSettingsTab.ui`

3. **Widgets Auxiliares:**
   - `LogWidget` → `logWidget.ui`
   - `ResultsTable` → `resultsTable.ui`
   - `RichTooltip` → `richTooltip.ui`
   - `MemoryIndicator` → `memoryIndicator.ui`
   - `AutoSaveIndicator` → `autoSaveIndicator.ui`

### Considerações Fase 4
- ParameterWidgets têm hierarquia de herança - base primeiro, depois derivados

---

### Fase 5: Diálogos Complexos (5-7 dias)

1. **Diálogos com Widgets Dinâmicos:**
   - `OperationPreviewDialog` → `operationPreviewDialog.ui` (usa PreviewCanvas)
   - `VideoExportDialog` → `videoExportDialog.ui` (usa VideoExportWorker)
   - `ExportDialog` → `exportDialog.ui` (usa ExportWorkerThread)
   - `UploadDialog` → atualizar `uploadDialog.ui` (usa FileLoadWorker)
   - `SettingsDialog` → atualizar `settingsDialog.ui` (usa tabs migradas)

2. **Diálogos de Operações:**
   - `FilterDialog` → `filterDialog.ui`
   - `SmoothingDialog` → `smoothingDialog.ui`
   - `DerivativeDialog` → `derivativeDialog.ui`
   - `IntegralDialog` → `integralDialog.ui`
   - `InterpolationDialog` → `interpolationDialog.ui`
   - `SynchronizationDialog` → `synchronizationDialog.ui`

3. **Diálogos Especializados:**
   - `ShortcutsDialog` → `shortcutsDialog.ui`
   - `AnnotationDialog` → `annotationDialog.ui`
   - `CompareSeriesDialog` → `compareSeriesDialog.ui`

### Considerações Fase 5
- Diálogos dependem de widgets migrados nas fases anteriores - benefício da abordagem complexos-primeiro

---

### Fase 6: Diálogos Simples e Finalização (3-5 dias)

1. **Diálogos Simples:**
   - `AboutDialog` → `aboutDialog.ui`
   - `ConfirmationDialog` → criar confirmationDialog.ui
   - `ErrorDialog` → criar errorDialog.ui

2. **Limpeza Final:**
   - Remover todos os métodos `_setup_ui_fallback()`
   - Remover código programático obsoleto
   - Atualizar `compile_ui.py`

3. **Documentação:**
   - Atualizar `UI_MIGRATION.md`
   - Documentar padrões para futuros widgets

---

### Estrutura de Testes por Fase

| Teste | Fase 1 | Fase 2 | Fase 3 | Fase 4 | Fase 5 | Fase 6 |
|-------|--------|--------|--------|--------|--------|--------|
| Arquivos .ui existem | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Promoted widgets registrados | ✅ | ✅ | ✅ | ✅ | - | - |
| MainWindow carrega | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| Painéis integrados | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| Widgets dinâmicos funcionam | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| Diálogos funcionam | - | - | - | - | ✅ | ✅ |
| Testes e2e completos | - | - | - | - | - | ✅ |

---

### Cronograma Atualizado

| Fase | Duração | Componentes | Complexidade |
|------|---------|-------------|--------------|
| Fase 1 | 3-5 dias | Preparação | Arquitetura |
| Fase 2 | 10-14 dias | MainWindow + 6 painéis | ⭐⭐⭐⭐⭐ |
| Fase 3 | 10-14 dias | 23 widgets visualização/seleção | ⭐⭐⭐⭐ |
| Fase 4 | 7-10 dias | 17 widgets configuração | ⭐⭐⭐ |
| Fase 5 | 5-7 dias | 14 diálogos complexos | ⭐⭐⭐ |
| Fase 6 | 3-5 dias | 3 diálogos simples + limpeza | ⭐ |
| **Total** | **38-55 dias** | **~65 componentes** | - |

---

### Vantagens da Abordagem Complexos-Primeiro

1. **Arquitetura sólida desde o início** - MainWindow e painéis definem a estrutura
2. **Menos retrabalho** - Widgets menores se adaptam à estrutura definida
3. **Detecção precoce de problemas** - Promoted widgets e placeholders testados cedo
4. **Integração natural** - Diálogos simples usam widgets já migrados
5. **Valor entregue mais rápido** - Aplicação funcional com .ui desde a Fase 2

---

### Considerações Finais

1. **Promoted widgets** - Configurar na Fase 1 para uso nas fases seguintes?
2. **Fallback temporário** - Manter durante migração ou eliminar imediatamente?
3. **Testes visuais** - Implementar screenshots comparativos para validação?
