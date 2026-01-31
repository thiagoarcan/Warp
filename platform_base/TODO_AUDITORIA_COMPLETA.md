# 🔴 TODO LIST - AUDITORIA COMPLETA PARA PRODUÇÃO

## Platform Base v2.0 - Varredura Linha por Linha

**Data da Auditoria:** 31 de Janeiro de 2026  
**Auditor:** Análise automatizada completa do código fonte  
**Política:** Nenhum erro pode ser ignorado, simplificado ou omitido

---

## 📊 RESUMO EXECUTIVO

| Categoria | Itens | Status |
|-----------|-------|--------|
| **Funcionalidades "Coming Soon"** | 9 | 🔴 NÃO IMPLEMENTADO |
| **Stubs (pass/NotImplementedError)** | 27 | 🔴 NÃO IMPLEMENTADO |
| **Conexões UI↔Backend faltantes** | 12 | 🔴 CRÍTICO |
| **Temas/Estilos** | 3 | 🔴 NÃO IMPLEMENTADO |
| **Undo/Redo** | 1 | 🔴 NÃO IMPLEMENTADO |
| **Exportação** | 4 | 🔴 PARCIAL |
| **3D Renderização** | 2 | 🟡 PARCIAL |
| **Streaming** | 1 | 🟡 PARCIAL |

**TOTAL DE ITENS A IMPLEMENTAR: 59+ funcionalidades**

---

## 🔴 CATEGORIA 1: FUNCIONALIDADES "COMING SOON" - CÓDIGO PROMETE MAS NÃO ENTREGA

Todos os itens abaixo mostram uma mensagem "Coming soon" para o usuário, indicando que a funcionalidade não existe.

### 1.1 Menu de Contexto do Gráfico

**Arquivo:** `desktop/menus/plot_context_menu.py`

| Linha | Funcionalidade | Status |
|-------|---------------|--------|
| 523 | FFT Analysis | `QMessageBox.information("FFT analysis feature coming soon!")` |
| 529 | Correlation Analysis | `QMessageBox.information("Correlation analysis feature coming soon!")` |
| 545 | Filtros (Low/High/Bandpass) | `QMessageBox.information(f"{filter_type} filter feature coming soon!")` |
| 551 | Detecção de Outliers | `QMessageBox.information("Outlier detection feature coming soon!")` |
| 591 | Copy to Clipboard | `QMessageBox.information("Copy to clipboard feature coming soon!")` |
| 618 | Series Properties | `QMessageBox.information("Series properties dialog coming soon!")` |

### 1.2 Main Window Desktop

**Arquivo:** `desktop/main_window.py`

| Linha | Funcionalidade | Status |
|-------|---------------|--------|
| 576 | Export Data | `self.status_label.setText("Export functionality - Coming soon")` |
| 588 | Undo | `self.status_label.setText("Undo - not yet implemented")` |
| 595 | Redo | `self.status_label.setText("Redo - not yet implemented")` |

---

## 🔴 CATEGORIA 2: STUBS (MÉTODOS COM `pass` QUE NÃO FAZEM NADA)

### 2.1 Sincronização de Plots

**Arquivo:** `ui/plot_sync.py`

| Linha | Método | O que deveria fazer |
|-------|--------|---------------------|
| 229 | `_sync_xlim()` exception handler | Sincronizar eixo X entre múltiplos gráficos |
| 253 | `_sync_ylim()` exception handler | Sincronizar eixo Y entre múltiplos gráficos |
| 275 | `_sync_crosshair()` exception handler | Sincronizar posição do crosshair |
| 298 | `_sync_region()` exception handler | Sincronizar seleção de região |
| 340 | `sync_pan()` exception handler | Sincronizar pan entre gráficos |

### 2.2 VizPanel

**Arquivo:** `ui/panels/viz_panel.py`

| Linha | Método | O que deveria fazer |
|-------|--------|---------------------|
| 567 | Algum handler | Sem contexto suficiente para determinar |
| 1313 | Handler | Sem contexto suficiente |
| 1322 | Handler | Sem contexto suficiente |

### 2.3 Video Export

**Arquivo:** `ui/video_export.py`

| Linha | Método | O que deveria fazer |
|-------|--------|---------------------|
| 252 | `_finalize_export()` | Finalizar exportação de vídeo |

### 2.4 Menu de Contexto - Ações Vazias

**Arquivo:** `desktop/menus/plot_context_menu.py`

| Linha | Método | O que deveria fazer |
|-------|--------|---------------------|
| 553-554 | `_toggle_grid()` | Alternar grid no gráfico - MÉTODO VAZIO |
| 557-558 | `_toggle_legend()` | Alternar legenda no gráfico - MÉTODO VAZIO |
| 569-570 | `_clear_selection()` | Limpar seleção atual - MÉTODO VAZIO |
| 573-574 | `_select_all()` | Selecionar todos os pontos - MÉTODO VAZIO |
| 577-578 | `_invert_selection()` | Inverter seleção - MÉTODO VAZIO |
| 601-602 | `_hide_series()` | Ocultar série - MÉTODO VAZIO |

### 2.5 Classes Base Abstratas

**Arquivo:** `viz/base.py`

| Linha | Método | Descrição |
|-------|--------|-----------|
| 324 | método abstrato | `raise NotImplementedError` |
| 329 | método abstrato | `raise NotImplementedError` |
| 334 | método abstrato | `raise NotImplementedError` |

**Arquivo:** `ui/selection_sync.py`

| Linha | Método | Descrição |
|-------|--------|-----------|
| 355 | `apply_synced_selection()` | `raise NotImplementedError("Subclasses must implement")` |

---

## 🔴 CATEGORIA 3: CONEXÕES UI↔BACKEND CRÍTICAS FALTANTES

### 3.1 OperationsPanel NÃO ESTÁ CONECTADO

**Problema Central:** O `OperationsPanel` emite signals (`operation_requested`) mas **NINGUÉM ESCUTA** no desktop app.

**Arquivo:** `ui/panels/operations_panel.py`

- Linha 69: `operation_requested = pyqtSignal(str, dict)`
- Este signal é emitido quando usuário clica "Aplicar" em qualquer operação
- **MAS** no `desktop/main_window.py` NÃO HÁ conexão com este signal

**TODO:**

```python
# Em desktop/main_window.py, adicionar:
# 1. Importar OperationsPanel
# 2. Criar instância: self.operations_panel = OperationsPanel(session_state)
# 3. Conectar: self.operations_panel.operation_requested.connect(self._handle_operation)
# 4. Implementar _handle_operation(operation, params)
```

### 3.2 MathAnalysisDialog NÃO EXECUTA OPERAÇÕES

**Arquivo:** `desktop/menus/plot_context_menu.py`

- `MathAnalysisDialog` coleta parâmetros e emite `operation_requested`
- Mas quem escuta esse signal? Somente se conectado corretamente
- O `PlotContextMenu.math_operation_requested` precisa ser conectado ao worker

**TODO:**

```python
# O signal math_operation_requested (linha 234) precisa:
# 1. Ser conectado no VizPanel ou MainWindow
# 2. Criar worker apropriado (CalculusWorker, InterpolationWorker)
# 3. Executar operação
# 4. Adicionar resultado ao gráfico
```

### 3.3 Workers Existem Mas Não São Chamados Corretamente

**Arquivo:** `desktop/workers/processing_worker.py`

Os workers `InterpolationWorker` e `CalculusWorker` existem e funcionam, **MAS**:

- Não há código que os instancia a partir da UI
- O fluxo UI → Worker → Resultado → UI não está completo

### 3.4 ResultsPanel Não Recebe Resultados

**Arquivo:** `desktop/widgets/results_panel.py`

- O painel existe mas não está conectado para receber resultados de operações
- `operation_completed` signal não chega aqui

### 3.5 StreamingPanel Não Está Integrado no Desktop App

**Arquivo:** `ui/panels/streaming_panel.py`

- Existe implementação completa de playback
- **MAS** não está incluído no `desktop/main_window.py`
- Usuário não tem acesso a essa funcionalidade

---

## 🔴 CATEGORIA 4: PROBLEMAS FUNCIONAIS ESPECÍFICOS

### 4.1 Sistema de Cores das Séries

**Arquivo:** `desktop/widgets/viz_panel.py`

**Problema:** O índice de cor é passado corretamente (`series_index = len(plot_info["series"])`), mas há inconsistência entre diferentes partes do código.

**Linhas afetadas:** 647-651

```python
# Código atual (linha 647):
series_index = len(plot_info["series"])  # Index for color selection
widget.add_series(
    series_id=series_id,
    x_data=dataset.t_seconds,
    y_data=series.values,
    series_index=series_index,  # ← Este valor está correto
)
```

**Verificar:** Se as cores estão funcionando, o problema pode estar no `Plot2DWidget.add_series()` não usando `series_index` corretamente.

### 4.2 Legenda Mostra ID em vez de Nome

**Arquivo:** `desktop/widgets/viz_panel.py` linha 647-652

**Problema:** O parâmetro `name` não é passado para `add_series()`, então a legenda mostra `series_id` em vez de `series.name`.

**TODO:**

```python
widget.add_series(
    series_id=series_id,
    x_data=dataset.t_seconds,
    y_data=series.values,
    series_index=series_index,
    name=series.name,  # ← ADICIONAR ESTA LINHA
)
```

### 4.3 Checkboxes de Séries Não Funcionam

**Arquivo:** `desktop/widgets/data_panel.py`

**Problema:** O modelo `DatasetTreeModel` suporta checkboxes, mas marcar/desmarcar não afeta o gráfico.

**TODO:**

- Conectar `model.dataChanged` ao `VizPanel`
- Quando checkbox mudar, chamar `viz_panel.toggle_series_visibility()`

### 4.4 Gráficos 3D

**Arquivo:** `desktop/widgets/viz_panel.py`

**Problema:** PyVista está instalado mas a lógica de renderização 3D precisa de pelo menos 3 séries selecionadas.

**Linhas afetadas:** 262-287 (`Plot3DWidget.plot_trajectory_3d`)

---

## 🔴 CATEGORIA 5: SISTEMA DE TEMAS

**Arquivo:** `desktop/main_window.py`

| Linha | Funcionalidade | Status |
|-------|---------------|--------|
| 247-259 | Theme selection menu | Menu existe mas `_set_theme()` não faz nada real |
| 496-498 | `_apply_theme()` | Apenas loga, não aplica tema |

**TODO:**

```python
def _apply_theme(self, theme: str):
    # 1. Definir QSS para tema claro
    # 2. Definir QSS para tema escuro
    # 3. Detectar tema do sistema para "auto"
    # 4. Aplicar stylesheet em toda a aplicação
```

---

## 🔴 CATEGORIA 6: SISTEMA DE UNDO/REDO

**Arquivos:** `desktop/main_window.py`, `ui/undo_redo.py`

**Status:** COMPLETAMENTE NÃO IMPLEMENTADO

**TODO:**

1. Criar classe `Command` base com `execute()` e `undo()`
2. Criar `CommandStack` para gerenciar histórico
3. Implementar commands para cada operação:
   - `AddSeriesCommand`
   - `RemoveSeriesCommand`
   - `CalculationCommand`
   - `InterpolationCommand`
4. Conectar `Ctrl+Z` e `Ctrl+Y` aos métodos do stack

---

## 🔴 CATEGORIA 7: EXPORTAÇÃO

**Arquivos:** `desktop/main_window.py`, `desktop/workers/export_worker.py`

| Funcionalidade | Status |
|----------------|--------|
| Export CSV | 🟡 Worker existe, UI não conectada |
| Export Excel | 🟡 Worker existe, UI não conectada |
| Export Parquet | 🟡 Worker existe, UI não conectada |
| Export Plot Image | 🔴 Não implementado |
| Export Session | 🟡 Parcial |
| Export Animation/Video | 🔴 Stub em video_export.py |

---

## 📋 CATEGORIA 8: TESTES OBRIGATÓRIOS

> **POLÍTICA:** Cada erro identificado DEVE ter um teste que falha antes da correção e passa depois.

### 8.1 Testes que DEVEM FALHAR agora (e passar após correção)

```python
# tests/integration/test_ui_backend_connection.py

def test_operations_panel_signal_is_connected():
    """O signal operation_requested do OperationsPanel deve estar conectado"""
    # Este teste DEVE FALHAR atualmente
    main_window = create_main_window()
    assert hasattr(main_window, 'operations_panel')
    assert main_window.operations_panel.operation_requested.receivers() > 0

def test_derivative_from_context_menu_executes():
    """Derivada do menu de contexto deve executar e retornar resultado"""
    # Este teste DEVE FALHAR atualmente
    viz_panel = create_viz_panel_with_data()
    viz_panel.context_menu._show_analysis_dialog("derivative")
    # Simular "Apply"
    # Verificar que resultado foi adicionado ao gráfico

def test_legend_shows_series_name_not_id():
    """Legenda deve mostrar nome do arquivo, não ID interno"""
    # Este teste DEVE FALHAR atualmente
    plot = create_plot_with_series(name="Temperatura Sensor 1")
    legend_text = get_legend_text(plot)
    assert "Temperatura Sensor 1" in legend_text
    assert "series_" not in legend_text

def test_theme_dark_is_applied():
    """Tema escuro deve mudar cores da aplicação"""
    # Este teste DEVE FALHAR atualmente
    main_window = create_main_window()
    main_window._set_theme("dark")
    bg_color = main_window.palette().color(QPalette.Window)
    assert bg_color.lightness() < 50  # Deve ser escuro

def test_undo_reverts_operation():
    """Ctrl+Z deve reverter última operação"""
    # Este teste DEVE FALHAR atualmente
    main_window = create_main_window()
    add_series_to_plot(main_window)
    series_count_before = get_series_count(main_window)
    main_window._undo_operation()
    series_count_after = get_series_count(main_window)
    assert series_count_after == series_count_before - 1

def test_checkbox_hides_series():
    """Desmarcar checkbox deve ocultar série do gráfico"""
    # Este teste DEVE FALHAR atualmente
    data_panel = create_data_panel_with_data()
    viz_panel = create_viz_panel_with_data()
    uncheck_series(data_panel, "series_1")
    assert not is_series_visible(viz_panel, "series_1")

def test_fft_analysis_works():
    """FFT Analysis deve funcionar, não mostrar 'coming soon'"""
    # Este teste DEVE FALHAR atualmente
    context_menu = create_context_menu()
    result = context_menu._show_fft_analysis()
    assert result is not None
    assert "coming soon" not in str(result).lower()

def test_export_csv_creates_file():
    """Export CSV deve criar arquivo"""
    # Este teste DEVE FALHAR atualmente
    main_window = create_main_window_with_data()
    main_window._export_data()
    # Deve criar arquivo, não mostrar "Coming soon"

def test_streaming_panel_exists_in_desktop():
    """StreamingPanel deve existir no desktop app"""
    # Este teste DEVE FALHAR atualmente
    main_window = create_main_window()
    assert hasattr(main_window, 'streaming_panel')
```

### 8.2 Estrutura de Testes Obrigatória

```
tests/
├── integration/
│   ├── test_ui_backend_connection.py      # Conexões UI↔Backend
│   ├── test_operation_flow.py             # Fluxo completo de operações
│   └── test_export_flow.py                # Fluxo de exportação
├── functional/
│   ├── test_context_menu_actions.py       # Todas as ações do menu
│   ├── test_theme_application.py          # Aplicação de temas
│   ├── test_undo_redo.py                  # Sistema de undo/redo
│   └── test_streaming_playback.py         # Funcionalidades de streaming
├── gui/
│   ├── test_legend_display.py             # Legenda correta
│   ├── test_series_colors.py              # Cores das séries
│   ├── test_checkbox_visibility.py        # Checkboxes funcionando
│   └── test_3d_rendering.py               # Gráficos 3D
└── e2e/
    ├── test_complete_analysis_workflow.py # Fluxo completo
    └── test_user_scenarios.py             # Cenários de usuário
```

---

## 📝 PLANO DE EXECUÇÃO ORDENADO

### Fase 1: Conexões Críticas (BLOQUEIA TUDO)

1. [ ] Conectar `OperationsPanel.operation_requested` ao handler
2. [ ] Conectar `PlotContextMenu.math_operation_requested` ao worker
3. [ ] Conectar `ResultsPanel` para receber resultados
4. [ ] Adicionar `StreamingPanel` ao desktop app
5. [ ] Passar `name=series.name` para `add_series()`

### Fase 2: Implementar Stubs

1. [ ] Implementar `_toggle_grid()` no menu de contexto
2. [ ] Implementar `_toggle_legend()` no menu de contexto
3. [ ] Implementar `_clear_selection()`
4. [ ] Implementar `_select_all()`
5. [ ] Implementar `_invert_selection()`
6. [ ] Implementar `_hide_series()`

### Fase 3: Funcionalidades "Coming Soon"

1. [ ] Implementar FFT Analysis
2. [ ] Implementar Correlation Analysis
3. [ ] Implementar Filtros (Lowpass, Highpass, Bandpass)
4. [ ] Implementar Detecção de Outliers
5. [ ] Implementar Copy to Clipboard
6. [ ] Implementar Series Properties Dialog
7. [ ] Implementar Export Data

### Fase 4: Sistema de Undo/Redo

1. [ ] Criar classe Command base
2. [ ] Criar CommandStack
3. [ ] Implementar AddSeriesCommand
4. [ ] Implementar RemoveSeriesCommand
5. [ ] Implementar CalculationCommand
6. [ ] Conectar Ctrl+Z / Ctrl+Y

### Fase 5: Temas

1. [ ] Definir QSS tema claro
2. [ ] Definir QSS tema escuro
3. [ ] Implementar detecção de tema do sistema
4. [ ] Implementar `_apply_theme()` completo

### Fase 6: Exportação

1. [ ] Conectar UI ao ExportWorker
2. [ ] Implementar export de imagem do gráfico
3. [ ] Implementar export de vídeo/animação
4. [ ] Testar todos os formatos

### Fase 7: Testes

1. [ ] Criar todos os testes listados em 8.1
2. [ ] Verificar que todos FALHAM antes das correções
3. [ ] Após cada correção, verificar que teste passa
4. [ ] Cobertura > 80% das funcionalidades corrigidas

---

## ⚠️ CRITÉRIOS DE ACEITAÇÃO PARA PRODUÇÃO

A aplicação só pode ser considerada PRONTA PARA PRODUÇÃO quando:

1. [ ] **ZERO** mensagens "Coming soon" na aplicação
2. [ ] **ZERO** métodos com `pass` que deveriam fazer algo
3. [ ] **TODAS** as conexões UI↔Backend funcionando
4. [ ] **TODOS** os testes de integração passando
5. [ ] **TODAS** as ações do menu de contexto funcionando
6. [ ] Sistema de Undo/Redo funcional
7. [ ] Exportação em todos os formatos funcional
8. [ ] Temas claro/escuro funcionando
9. [ ] Streaming/Playback funcional
10. [ ] 3D funcional quando 3+ séries selecionadas

---

*Documento gerado em 31/01/2026*
*Auditoria completa linha por linha do código fonte*
