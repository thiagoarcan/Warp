# TODO LIST COMPLETA PARA PRODUÇÃO - Platform Base v2.0

> **AVISO**: Esta lista representa TUDO que precisa ser implementado para colocar a aplicação em produção real.
> Nenhum workaround, nenhuma simplificação, nenhum jeitinho.
>
> **Estado Atual Estimado**: ~20% funcional
> **TODOs/Stubs identificados no código**: 176+
> **Componentes UI a migrar para .ui**: 60 classes → ~45 arquivos .ui
> **Data da Auditoria**: 30/01/2026

---

## 📊 SUMÁRIO EXECUTIVO

| Módulo | Status | Funcional | A Implementar |
|--------|--------|-----------|---------------|
| **Visualização 2D** | 🟡 Parcial | 40% | Cores, Legenda, Multi-eixo, Seleção |
| **Visualização 3D** | 🔴 Crítico | 10% | Toda implementação de renderização |
| **Cálculos** | 🟡 Parcial | 60% | Conexão UI↔Backend |
| **Streaming** | 🔴 Crítico | 5% | Implementação completa |
| **Exportação** | 🔴 Crítico | 20% | Todas as funcionalidades |
| **Menu de Contexto** | 🔴 Crítico | 5% | Todas as ações |
| **Undo/Redo** | 🔴 Crítico | 0% | Sistema completo |
| **Seleção de Dados** | 🟡 Parcial | 30% | Sincronização, Multi-seleção |
| **Configurações** | 🟡 Parcial | 50% | Persistência, Temas |
| **Results Panel** | 🔴 Crítico | 10% | Exibição de resultados |
| **Testes** | 🔴 Crítico | 15% | Cobertura e integração |
| **Migração .ui** | 🔴 Crítico | 3% | 60 classes → 45 arquivos .ui |

---

## 🔴 CATEGORIA 1: BUGS CRÍTICOS (ALTA PRIORIDADE)

### BUG-001: Sistema de Cores no Gráfico 2D

**Arquivo**: `desktop/widgets/viz_panel.py`
**Status**: PARCIALMENTE IMPLEMENTADO - QUEBRADO
**Problema**:

- O índice de série para seleção de cor não incrementa corretamente
- Apenas 2 cores funcionam (primeira e segunda série)
- O método `add_series()` usa `series_index` mas quem chama passa sempre o mesmo valor

**TODO**:

```
[ ] Corrigir incremento de series_index em _add_series_to_plot()
[ ] Garantir que cada série receba índice único baseado na ordem de adição
[ ] Testar com 10+ séries para verificar ciclo de cores
[ ] Adicionar cor à legenda corretamente
```

### BUG-002: Legenda Mostrando "valor" em vez do Nome do Arquivo

**Arquivo**: `desktop/widgets/viz_panel.py`
**Status**: NÃO IMPLEMENTADO
**Problema**:

- A legenda mostra texto genérico em vez do nome real da série/arquivo
- O parâmetro `name` no `add_series()` recebe `series_id` quando deveria receber `series.name`

**TODO**:

```
[ ] Passar series.name (nome original do arquivo) para add_series()
[ ] Atualizar legenda quando nome mudar
[ ] Adicionar tooltip com path completo do arquivo
```

### BUG-003: Menu de Contexto (Click Direito) - Ações Não Funcionam

**Arquivo**: `desktop/menus/plot_context_menu.py`
**Status**: STUBS - NÃO IMPLEMENTADO
**Problema**: 6 métodos são apenas `pass`:

**TODO**:

```
[ ] Implementar _toggle_grid() - conectar com plot.showGrid()
[ ] Implementar _toggle_legend() - conectar com plot.legend
[ ] Implementar _clear_selection() - limpar seleção visual
[ ] Implementar _select_all() - selecionar todos os pontos
[ ] Implementar _invert_selection() - inverter seleção atual
[ ] Implementar _hide_series() - ocultar série específica
[ ] Implementar _apply_lowpass_filter() - não é apenas "coming soon"
[ ] Implementar _apply_highpass_filter() - não é apenas "coming soon"
[ ] Implementar _apply_bandpass_filter() - não é apenas "coming soon"
[ ] Implementar _detect_outliers() - não é apenas "coming soon"
[ ] Implementar _copy_to_clipboard() - copiar dados/imagem
```

### BUG-004: Cálculos (Derivada, Integral, Área) Não Conectados à UI

**Arquivos**: `ui/panels/operations_panel.py`, `desktop/workers/processing_worker.py`
**Status**: BACKEND EXISTE - UI NÃO CONECTADA
**Problema**:

- Os cálculos estão implementados em `processing/calculus.py`
- A UI emite signals (`operation_requested`)
- NINGUÉM ESCUTA esses signals no desktop app

**TODO**:

```
[ ] Criar conexão entre OperationsPanel.operation_requested e ProcessingWorker
[ ] No MainWindow, conectar signals do operations_panel
[ ] Implementar handler para receber resultado do worker
[ ] Exibir resultado no ResultsPanel
[ ] Adicionar série calculada ao gráfico
[ ] Implementar validação de dados antes do cálculo
```

### BUG-005: Checkboxes de Séries Não Funcionam

**Arquivo**: `desktop/widgets/data_panel.py`
**Status**: UI EXISTE - LÓGICA NÃO IMPLEMENTADA
**Problema**:

- Checkboxes existem na árvore de dados
- Marcar/desmarcar não afeta o gráfico

**TODO**:

```
[ ] Conectar checkbox state change com viz_panel
[ ] Implementar show/hide série baseado em checkbox
[ ] Persistir estado dos checkboxes na sessão
[ ] Implementar "Select All" / "Deselect All"
```

### BUG-006: Gráficos 3D Não Renderizam

**Arquivo**: `desktop/widgets/viz_panel.py`, `viz/figures_3d.py`
**Status**: ESTRUTURA EXISTE - RENDERIZAÇÃO QUEBRADA
**Problema**:

- PyVista é importado mas plots não aparecem
- Falta conversão correta de dados para formato 3D

**TODO**:

```
[ ] Implementar plot_trajectory_3d() completamente
[ ] Adicionar tratamento de erro quando < 3 séries selecionadas
[ ] Implementar controles de câmera 3D
[ ] Adicionar colormap selection
[ ] Implementar exportação de modelo 3D
[ ] Testar com diferentes tamanhos de dados
```

### BUG-007: Nomes de Arquivo Exibidos Incorretamente

**Arquivo**: `desktop/widgets/data_panel.py`
**Status**: PARCIALMENTE IMPLEMENTADO
**Problema**:

- Path completo em vez de apenas filename
- Encoding issues em nomes com caracteres especiais

**TODO**:

```
[ ] Usar Path(file).name para exibição
[ ] Adicionar tooltip com path completo
[ ] Tratar encoding de nomes de arquivo
[ ] Permitir renomear séries
```

---

## 🔴 CATEGORIA 2: FUNCIONALIDADES NÃO IMPLEMENTADAS

### 2.1 Sistema de Streaming/Playback

**Arquivos**: `ui/panels/streaming_panel.py`, `streaming/`
**Status**: UI EXISTE - 95% NÃO IMPLEMENTADO

**TODO**:

```
[ ] Implementar _connect_signals() no StreamingPanel
[ ] Criar engine de playback com timer QTimer
[ ] Implementar _play(), _pause(), _stop(), _seek()
[ ] Sincronizar posição com gráfico (janela deslizante)
[ ] Implementar controle de velocidade (0.5x, 1x, 2x, etc.)
[ ] Implementar loop e modo reverso
[ ] Adicionar timeline interativa com drag
[ ] Implementar minimap com overview dos dados
[ ] Conectar filtros de streaming
[ ] Implementar buffer de dados para performance
```

### 2.2 Results Panel - Exibição de Resultados

**Arquivo**: `desktop/widgets/results_panel.py`
**Status**: UI EXISTE - NÃO FUNCIONA

**TODO**:

```
[ ] Implementar _poll_logs() para mostrar logs em tempo real
[ ] Implementar _export_results() - não é apenas log
[ ] Conectar ResultsPanel com operações completadas
[ ] Exibir estatísticas de qualidade dos dados
[ ] Mostrar métricas de cálculos (área, integral, etc.)
[ ] Implementar tabela de resultados com sorting
[ ] Adicionar gráficos de qualidade
[ ] Permitir copiar resultados para clipboard
```

### 2.3 Sistema de Undo/Redo

**Arquivo**: `ui/undo_redo.py`
**Status**: ESTRUTURA - 0% IMPLEMENTADO

**TODO**:

```
[ ] Implementar classe Command base funcional (não apenas pass)
[ ] Implementar execute() e undo() para cada tipo de operação
[ ] Implementar CommandStack com limite de memória
[ ] Conectar todas as operações com sistema de commands
[ ] Adicionar shortcuts Ctrl+Z / Ctrl+Y
[ ] Implementar redo queue
[ ] Persistir history entre sessões (opcional)
[ ] Mostrar histórico visual de operações
```

### 2.4 Exportação de Dados

**Arquivo**: `ui/export_dialog.py`, `desktop/workers/export_worker.py`
**Status**: PARCIAL - MUITAS FEATURES FALTANDO

**TODO**:

```
[ ] Implementar exportação de sessão completa
[ ] Implementar exportação de gráfico como imagem (PNG, SVG, PDF)
[ ] Implementar exportação de animação/vídeo
[ ] Adicionar opções de compressão
[ ] Implementar exportação seletiva (só séries marcadas)
[ ] Adicionar metadados nos arquivos exportados
[ ] Implementar batch export (múltiplos arquivos)
[ ] Suportar exportação para formatos científicos (MAT, NetCDF)
```

### 2.5 Sistema de Seleção Multi-View

**Arquivos**: `ui/selection_sync.py`, `ui/multi_view_sync.py`
**Status**: ESTRUTURA - MAIORIA NÃO IMPLEMENTADA

**TODO**:

```
[ ] Implementar apply_synced_selection() - raise NotImplementedError atual
[ ] Implementar sincronização de seleção entre gráficos
[ ] Implementar brush selection (arrastar para selecionar)
[ ] Implementar lasso selection
[ ] Implementar box selection
[ ] Sincronizar zoom entre gráficos
[ ] Sincronizar crosshair entre gráficos
[ ] Implementar linked views (X-axis sync)
```

### 2.6 Plot Sync - Sincronização de Gráficos

**Arquivo**: `ui/plot_sync.py`
**Status**: ESTRUTURA - 5 MÉTODOS COM `pass`

**TODO**:

```
[ ] Implementar _on_y_range_changed() (linha 228)
[ ] Implementar _on_x_range_changed() (linha 252)
[ ] Implementar _on_crosshair_moved() (linha 274)
[ ] Implementar _on_selection_changed() (linha 297)
[ ] Implementar _sync_widget() completamente (linha 339)
[ ] Adicionar opção de desativar sincronização
[ ] Implementar sincronização de apenas X ou apenas Y
```

### 2.7 Video Export

**Arquivo**: `ui/video_export.py`
**Status**: ESTRUTURA - TODO EXPLÍCITO NO CÓDIGO

**TODO**:

```
[ ] Implementar _frame_to_numpy() corretamente (linha 229)
[ ] Implementar _finalize_export() (linha 239 - apenas pass)
[ ] Integrar com moviepy para geração de vídeo
[ ] Suportar GIF animado
[ ] Adicionar opções de qualidade/fps
[ ] Implementar progress tracking
```

### 2.8 Eixo Datetime

**Status**: NÃO IMPLEMENTADO
**Problema**: Eixo X sempre mostra segundos, não timestamps

**TODO**:

```
[ ] Criar DateTimeAxis customizado para pyqtgraph
[ ] Implementar formatação de datetime no eixo
[ ] Suportar diferentes formatos (ISO, locale, etc.)
[ ] Implementar zoom com datetime awareness
[ ] Sincronizar seleção temporal com datetime
```

### 2.9 Multi-Y Axis

**Arquivo**: `desktop/widgets/viz_panel.py`
**Status**: ESTRUTURA EXISTE - NÃO FUNCIONA

**TODO**:

```
[ ] Corrigir add_secondary_y_axis() para funcionar
[ ] Implementar _move_selected_to_y2() (linha 617 - apenas comentário)
[ ] Permitir até 4 eixos Y
[ ] Colorir eixos conforme séries
[ ] Implementar auto-range para cada eixo
[ ] Adicionar indicador visual de qual eixo cada série usa
```

---

## 🟡 CATEGORIA 3: MELHORIAS DE UI/UX

### 3.1 Temas

**Status**: NÃO IMPLEMENTADO

**TODO**:

```
[ ] Implementar tema claro (atual)
[ ] Implementar tema escuro
[ ] Adicionar seletor de tema nas configurações
[ ] Persistir tema selecionado
[ ] Aplicar tema em todos os componentes
[ ] Suportar tema do sistema operacional
```

### 3.2 Internacionalização (i18n)

**Arquivo**: `utils/i18n.py`
**Status**: ESTRUTURA - 1 TODO + muitas traduções faltando

**TODO**:

```
[ ] Completar traduções PT-BR
[ ] Adicionar suporte a EN
[ ] Implementar seletor de idioma
[ ] Traduzir mensagens de erro
[ ] Traduzir tooltips
[ ] Adicionar suporte a ES (opcional)
```

### 3.3 Tooltips e Help

**Status**: PARCIAL

**TODO**:

```
[ ] Adicionar tooltips em todos os botões
[ ] Implementar help contextual (F1)
[ ] Criar documentação inline
[ ] Adicionar "What's This?" mode
```

### 3.4 Keyboard Shortcuts

**Status**: PARCIAL

**TODO**:

```
[ ] Documentar todos os shortcuts existentes
[ ] Adicionar shortcuts faltantes (ver lista abaixo)
[ ] Permitir customização de shortcuts
[ ] Mostrar shortcuts em tooltips

Shortcuts a implementar:
[ ] Ctrl+D - Duplicar série
[ ] Delete - Remover série selecionada
[ ] Ctrl+A - Selecionar tudo
[ ] Ctrl+Shift+A - Desselecionar tudo
[ ] F5 - Atualizar dados
[ ] F11 - Fullscreen
[ ] Space - Play/Pause streaming
```

---

## 🟡 CATEGORIA 4: CONEXÕES UI↔BACKEND FALTANTES

### 4.1 Operations Panel → Processing

**Problema**: UI emite signals que ninguém escuta

**TODO**:

```
[ ] Em MainWindow.__init__, adicionar:
    - self.operations_panel = OperationsPanel(...)
    - self.operations_panel.operation_requested.connect(self._handle_operation)
    
[ ] Implementar _handle_operation(operation, params):
    - Validar dados selecionados
    - Criar worker apropriado
    - Conectar worker.finished → ResultsPanel
    - Conectar worker.error → StatusBar
    
[ ] Conectar OperationsPanel ao desktop app (não apenas ui app)
```

### 4.2 Data Panel → Viz Panel

**Problema**: Selecionar série não plota automaticamente

**TODO**:

```
[ ] Conectar data_panel.series_double_clicked → viz_panel.add_series
[ ] Conectar data_panel.checkbox_changed → viz_panel.toggle_series
[ ] Implementar drag & drop de série para gráfico
```

### 4.3 Config Panel → Todos os Componentes

**Problema**: Mudanças de config não afetam componentes

**TODO**:

```
[ ] Conectar config changes com viz_panel (cores, grid, etc.)
[ ] Conectar config changes com streaming panel
[ ] Conectar config changes com performance settings
[ ] Implementar "Apply" e "Reset" buttons
```

---

## 🔴 CATEGORIA 5: COMPONENTES DO DESKTOP APP FALTANTES

### 5.1 Operations Panel no Desktop App

**Problema**: Existe em `ui/panels/operations_panel.py` mas não está no desktop app

**TODO**:

```
[ ] Adicionar OperationsPanel ao desktop/main_window.py
[ ] Criar dock widget para operations
[ ] Conectar com session_state
[ ] Conectar com signal_hub
```

### 5.2 Streaming Panel no Desktop App

**Problema**: Existe em `ui/panels/streaming_panel.py` mas não está no desktop app

**TODO**:

```
[ ] Adicionar StreamingPanel ao desktop app
[ ] Integrar controles na toolbar ou dock
[ ] Conectar com viz_panel para atualização de janela
```

### 5.3 Preview Dialog para Operações

**Arquivo**: `ui/operation_preview.py`
**Status**: EXISTE - NÃO CONECTADO

**TODO**:

```
[ ] Integrar OperationPreviewDialog no fluxo de operações
[ ] Mostrar preview antes de aplicar operação
[ ] Implementar comparação before/after
```

---

## 🔴 CATEGORIA 6: TESTES E QUALIDADE (PIRÂMIDE COMPLETA)

> **POLÍTICA DE TESTES**: Nenhum teste pode ser ignorado, simplificado ou omitido.
> Se um teste falhar, DEVE ser corrigido antes de prosseguir.
> Cobertura mínima exigida: **90%** para produção.

### 📊 SUMÁRIO DE TESTES

| Nível | Tipo | Status | Cobertura | Ferramentas |
|-------|------|--------|-----------|-------------|
| 1º | Linting/Static | 🔴 0% | N/A | ruff, mypy, bandit |
| 2º | Unit Tests | 🔴 ~15% | 15% | pytest |
| 3º | Doctests | 🔴 0% | 0% | pytest --doctest |
| 4º | Integration | 🔴 0% | 0% | pytest |
| 5º | Property-based | 🔴 0% | 0% | hypothesis |
| 6º | GUI/Functional | 🔴 0% | 0% | pytest-qt |
| 7º | Performance | 🔴 0% | N/A | pytest-benchmark |
| 8º | E2E | 🔴 0% | 0% | pytest-qt + selenium |
| 9º | Load/Stress | 🔴 0% | N/A | locust, pytest |
| 10º | Smoke Tests | 🔴 0% | N/A | pytest -m smoke |

---

### 6.1 NÍVEL 1: LINTING E ANÁLISE ESTÁTICA

**Prioridade**: 🔴 CRÍTICA - Executar PRIMEIRO
**Ferramentas**: ruff, mypy, bandit, pylint, black, isort

#### 6.1.1 Configuração do Linting

**TODO**:

```
[ ] Criar/atualizar pyproject.toml com configurações de linting
[ ] Configurar ruff para PEP8 + regras extras
[ ] Configurar mypy para type checking strict
[ ] Configurar bandit para segurança
[ ] Configurar pre-commit hooks
[ ] Adicionar CI/CD para lint automático
```

**Arquivo pyproject.toml a criar/atualizar**:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "ARG",  # flake8-unused-arguments
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "PTH",  # flake8-use-pathlib
    "ERA",  # eradicate (commented code)
    "PL",   # pylint
    "RUF",  # Ruff-specific
]
ignore = ["E501"]  # line too long (handled by formatter)

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # assert used
```

#### 6.1.2 Arquivos a Corrigir (Linting)

**TODO - Ruff (PEP8 + Style)**:

```
[ ] Corrigir todos os erros em processing/*.py
[ ] Corrigir todos os erros em viz/*.py
[ ] Corrigir todos os erros em desktop/*.py
[ ] Corrigir todos os erros em ui/*.py
[ ] Corrigir todos os erros em core/*.py
[ ] Corrigir todos os erros em io/*.py
[ ] Corrigir todos os erros em streaming/*.py
[ ] Corrigir todos os erros em caching/*.py
[ ] Corrigir todos os erros em utils/*.py
[ ] Corrigir todos os erros em profiling/*.py
[ ] Remover código comentado (ERA001)
[ ] Remover imports não usados (F401)
[ ] Corrigir variáveis não usadas (F841)
```

**TODO - MyPy (Type Checking)**:

```
[ ] Adicionar type hints em processing/calculus.py
[ ] Adicionar type hints em processing/interpolation.py
[ ] Adicionar type hints em processing/smoothing.py
[ ] Adicionar type hints em processing/downsampling.py
[ ] Adicionar type hints em viz/figures_2d.py
[ ] Adicionar type hints em viz/figures_3d.py
[ ] Adicionar type hints em viz/heatmaps.py
[ ] Adicionar type hints em desktop/main_window.py
[ ] Adicionar type hints em desktop/widgets/*.py
[ ] Adicionar type hints em desktop/dialogs/*.py
[ ] Adicionar type hints em ui/panels/*.py
[ ] Adicionar type hints em core/models.py
[ ] Adicionar type hints em io/loader.py
[ ] Corrigir todos os erros "Any" implícitos
[ ] Corrigir todos os Optional sem None check
```

**TODO - Bandit (Segurança)**:

```
[ ] Verificar uso de pickle (B301)
[ ] Verificar hardcoded passwords (B105, B106)
[ ] Verificar SQL injection (B608)
[ ] Verificar uso de eval/exec (B307)
[ ] Verificar paths inseguros (B108)
[ ] Verificar uso de random (B311) - usar secrets para crypto
[ ] Verificar SSL/TLS (B501-B504)
```

---

### 6.2 NÍVEL 2: TESTES UNITÁRIOS

**Prioridade**: 🔴 CRÍTICA
**Cobertura Atual**: ~15%
**Cobertura Alvo**: 90%
**Ferramenta**: pytest, pytest-cov

#### 6.2.1 Configuração

**TODO**:

```
[ ] Criar pytest.ini ou configurar em pyproject.toml
[ ] Configurar pytest-cov para cobertura
[ ] Criar fixtures compartilhadas em conftest.py
[ ] Criar factories para objetos de teste
[ ] Configurar markers para categorizar testes
```

**Configuração pytest (pyproject.toml)**:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=platform_base",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=90",
]
markers = [
    "slow: marks tests as slow",
    "smoke: smoke tests",
    "unit: unit tests",
    "integration: integration tests",
    "gui: GUI tests",
    "e2e: end-to-end tests",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]
```

#### 6.2.2 Testes Unitários - processing/

**Arquivo**: `tests/unit/test_calculus.py`

```
[ ] test_derivative_finite_diff_first_order
[ ] test_derivative_finite_diff_second_order
[ ] test_derivative_finite_diff_third_order
[ ] test_derivative_savitzky_golay_first_order
[ ] test_derivative_savitzky_golay_second_order
[ ] test_derivative_spline_derivative
[ ] test_derivative_with_nan_values
[ ] test_derivative_empty_array
[ ] test_derivative_single_point
[ ] test_derivative_two_points
[ ] test_derivative_large_dataset_performance
[ ] test_integral_trapezoid
[ ] test_integral_simpson
[ ] test_integral_cumulative
[ ] test_integral_with_nan_values
[ ] test_integral_empty_array
[ ] test_integral_single_point
[ ] test_area_between_curves_positive
[ ] test_area_between_curves_negative
[ ] test_area_between_curves_crossing
[ ] test_area_between_curves_with_crossings
[ ] test_area_under_curve
[ ] test_metadata_generation
[ ] test_quality_metrics_calculation
```

**Arquivo**: `tests/unit/test_interpolation.py`

```
[ ] test_linear_interpolation
[ ] test_cubic_interpolation
[ ] test_akima_interpolation
[ ] test_pchip_interpolation
[ ] test_spline_interpolation
[ ] test_nearest_interpolation
[ ] test_polynomial_interpolation
[ ] test_rbf_interpolation
[ ] test_kriging_interpolation
[ ] test_gpr_interpolation
[ ] test_interpolation_with_gaps
[ ] test_interpolation_extrapolation
[ ] test_interpolation_no_extrapolation
[ ] test_interpolation_empty_array
[ ] test_interpolation_single_point
[ ] test_interpolation_preserves_endpoints
[ ] test_interpolation_metadata
```

**Arquivo**: `tests/unit/test_smoothing.py`

```
[ ] test_moving_average
[ ] test_gaussian_smoothing
[ ] test_savitzky_golay_smoothing
[ ] test_exponential_smoothing
[ ] test_lowess_smoothing
[ ] test_median_filter
[ ] test_smoothing_window_sizes
[ ] test_smoothing_edge_handling
[ ] test_smoothing_preserves_length
[ ] test_smoothing_with_nan
```

**Arquivo**: `tests/unit/test_downsampling.py`

```
[ ] test_minmax_downsampling
[ ] test_lttb_downsampling
[ ] test_nth_point_downsampling
[ ] test_average_downsampling
[ ] test_adaptive_downsampling
[ ] test_downsampling_preserves_extrema
[ ] test_downsampling_target_points
```

#### 6.2.3 Testes Unitários - io/

**Arquivo**: `tests/unit/test_loader.py`

```
[ ] test_load_csv_simple
[ ] test_load_csv_with_headers
[ ] test_load_csv_without_headers
[ ] test_load_csv_custom_delimiter
[ ] test_load_csv_custom_decimal
[ ] test_load_csv_encoding_utf8
[ ] test_load_csv_encoding_latin1
[ ] test_load_csv_encoding_cp1252
[ ] test_load_csv_auto_detect_encoding
[ ] test_load_xlsx_single_sheet
[ ] test_load_xlsx_multiple_sheets
[ ] test_load_xlsx_specific_sheet
[ ] test_load_xlsx_with_formulas
[ ] test_load_xlsx_with_dates
[ ] test_load_parquet
[ ] test_load_parquet_partitioned
[ ] test_load_hdf5
[ ] test_load_hdf5_with_groups
[ ] test_load_file_not_found
[ ] test_load_file_permission_denied
[ ] test_load_file_corrupted
[ ] test_load_file_empty
[ ] test_load_large_file_memory
[ ] test_load_with_dtype_inference
[ ] test_load_with_explicit_dtypes
```

**Arquivo**: `tests/unit/test_encoding_detector.py`

```
[ ] test_detect_utf8
[ ] test_detect_utf8_bom
[ ] test_detect_utf16
[ ] test_detect_latin1
[ ] test_detect_cp1252
[ ] test_detect_ascii
[ ] test_detect_binary_file
[ ] test_detect_empty_file
```

#### 6.2.4 Testes Unitários - viz/

**Arquivo**: `tests/unit/test_figures_2d.py`

```
[ ] test_plot2d_widget_creation
[ ] test_plot2d_add_series
[ ] test_plot2d_add_multiple_series
[ ] test_plot2d_color_assignment_sequential
[ ] test_plot2d_color_cycling
[ ] test_plot2d_legend_creation
[ ] test_plot2d_legend_names
[ ] test_plot2d_remove_series
[ ] test_plot2d_clear_all
[ ] test_plot2d_axis_labels
[ ] test_plot2d_grid_toggle
[ ] test_plot2d_auto_range
[ ] test_plot2d_manual_range
[ ] test_plot2d_secondary_y_axis
[ ] test_plot2d_plot_on_y2
[ ] test_plot2d_selection_region
[ ] test_plot2d_time_selection_signal
[ ] test_plot2d_with_nan_data
[ ] test_plot2d_with_inf_data
[ ] test_plot2d_empty_data
[ ] test_plot2d_single_point
[ ] test_plot2d_large_dataset
```

**Arquivo**: `tests/unit/test_figures_3d.py`

```
[ ] test_plot3d_widget_creation
[ ] test_plot3d_trajectory
[ ] test_plot3d_surface
[ ] test_plot3d_scatter
[ ] test_plot3d_point_cloud
[ ] test_plot3d_colormap
[ ] test_plot3d_camera_position
[ ] test_plot3d_clear
[ ] test_plot3d_export_image
[ ] test_plot3d_pyvista_not_available
```

**Arquivo**: `tests/unit/test_heatmaps.py`

```
[ ] test_heatmap_creation
[ ] test_heatmap_correlation_pearson
[ ] test_heatmap_correlation_spearman
[ ] test_heatmap_correlation_kendall
[ ] test_heatmap_colormap
[ ] test_heatmap_annotations
[ ] test_heatmap_axis_labels
```

#### 6.2.5 Testes Unitários - desktop/widgets/

**Arquivo**: `tests/unit/test_viz_panel.py`

```
[ ] test_viz_panel_creation
[ ] test_viz_panel_create_2d_plot
[ ] test_viz_panel_create_3d_plot
[ ] test_viz_panel_close_tab
[ ] test_viz_panel_clear_plot
[ ] test_viz_panel_add_series_to_plot
[ ] test_viz_panel_series_color_increment
[ ] test_viz_panel_series_name_in_legend
[ ] test_viz_panel_export_plot
[ ] test_viz_panel_toggle_grid
[ ] test_viz_panel_toggle_legend
[ ] test_viz_panel_line_width_change
[ ] test_viz_panel_secondary_y_axis
[ ] test_viz_panel_move_to_y2
[ ] test_viz_panel_time_selection
[ ] test_viz_panel_welcome_tab
```

**Arquivo**: `tests/unit/test_data_panel.py`

```
[ ] test_data_panel_creation
[ ] test_data_panel_add_dataset
[ ] test_data_panel_remove_dataset
[ ] test_data_panel_tree_structure
[ ] test_data_panel_checkbox_toggle
[ ] test_data_panel_series_selection
[ ] test_data_panel_double_click_plot
[ ] test_data_panel_filename_display
[ ] test_data_panel_tooltip_path
[ ] test_data_panel_context_menu
[ ] test_data_panel_drag_drop
```

**Arquivo**: `tests/unit/test_config_panel.py`

```
[ ] test_config_panel_creation
[ ] test_config_panel_interpolation_config
[ ] test_config_panel_calculus_config
[ ] test_config_panel_emit_config_changed
[ ] test_config_panel_load_settings
[ ] test_config_panel_save_settings
```

**Arquivo**: `tests/unit/test_results_panel.py`

```
[ ] test_results_panel_creation
[ ] test_results_panel_add_result
[ ] test_results_panel_clear_results
[ ] test_results_panel_export_results
[ ] test_results_panel_quality_metrics
[ ] test_results_panel_log_display
```

#### 6.2.6 Testes Unitários - desktop/dialogs/

**Arquivo**: `tests/unit/test_upload_dialog.py`

```
[ ] test_upload_dialog_creation
[ ] test_upload_dialog_file_selection
[ ] test_upload_dialog_preview
[ ] test_upload_dialog_column_mapping
[ ] test_upload_dialog_validation
[ ] test_upload_dialog_accept
[ ] test_upload_dialog_cancel
```

**Arquivo**: `tests/unit/test_settings_dialog.py`

```
[ ] test_settings_dialog_creation
[ ] test_settings_dialog_general_tab
[ ] test_settings_dialog_performance_tab
[ ] test_settings_dialog_logging_tab
[ ] test_settings_dialog_save
[ ] test_settings_dialog_reset
[ ] test_settings_dialog_cancel
```

**Arquivo**: `tests/unit/test_export_dialog.py`

```
[ ] test_export_dialog_creation
[ ] test_export_dialog_format_selection
[ ] test_export_dialog_series_selection
[ ] test_export_dialog_options
[ ] test_export_dialog_preview
[ ] test_export_dialog_execute
```

#### 6.2.7 Testes Unitários - core/

**Arquivo**: `tests/unit/test_models.py`

```
[ ] test_dataset_creation
[ ] test_dataset_add_series
[ ] test_dataset_remove_series
[ ] test_series_creation
[ ] test_series_metadata
[ ] test_lineage_tracking
[ ] test_time_window_creation
[ ] test_time_window_contains
[ ] test_calc_result_creation
[ ] test_quality_metrics
[ ] test_result_metadata
```

**Arquivo**: `tests/unit/test_session_state.py`

```
[ ] test_session_state_creation
[ ] test_session_state_add_dataset
[ ] test_session_state_selection
[ ] test_session_state_time_window
[ ] test_session_state_signals
[ ] test_session_state_serialization
[ ] test_session_state_deserialization
```

**Arquivo**: `tests/unit/test_dataset_store.py`

```
[ ] test_dataset_store_add
[ ] test_dataset_store_get
[ ] test_dataset_store_remove
[ ] test_dataset_store_list
[ ] test_dataset_store_clear
```

#### 6.2.8 Testes Unitários - utils/

**Arquivo**: `tests/unit/test_i18n.py`

```
[ ] test_translation_pt_br
[ ] test_translation_en
[ ] test_translation_missing_key
[ ] test_translation_fallback
[ ] test_locale_detection
```

**Arquivo**: `tests/unit/test_logging.py`

```
[ ] test_logger_creation
[ ] test_logger_levels
[ ] test_logger_format
[ ] test_logger_file_output
[ ] test_logger_rotation
```

**Arquivo**: `tests/unit/test_errors.py`

```
[ ] test_platform_error
[ ] test_calculus_error
[ ] test_io_error
[ ] test_validation_error
[ ] test_error_messages
```

---

### 6.3 NÍVEL 3: DOCTESTS

**Prioridade**: 🟡 MÉDIA
**Ferramentas**: pytest --doctest-modules

**TODO - Adicionar doctests em**:

```
[ ] processing/calculus.py - derivative(), integral(), area_between()
[ ] processing/interpolation.py - interpolate(), all methods
[ ] processing/smoothing.py - smooth(), all methods
[ ] processing/downsampling.py - downsample()
[ ] core/models.py - Dataset, Series, TimeWindow
[ ] io/loader.py - load_file()
[ ] utils/validation.py - validate functions
[ ] viz/figures_2d.py - Plot2DWidget methods
```

**Exemplo de doctest a adicionar**:

```python
def derivative(values, t, order=1, method="finite_diff"):
    """
    Calculate derivative of time series.
    
    Parameters
    ----------
    values : np.ndarray
        Y values
    t : np.ndarray
        Time values
    order : int
        Derivative order (1, 2, or 3)
    method : str
        Method: 'finite_diff', 'savitzky_golay', 'spline_derivative'
    
    Returns
    -------
    CalcResult
        Result with derivative values and metadata
    
    Examples
    --------
    >>> import numpy as np
    >>> t = np.array([0, 1, 2, 3, 4])
    >>> y = np.array([0, 1, 4, 9, 16])  # y = x^2
    >>> result = derivative(y, t, order=1)
    >>> np.allclose(result.values, [1, 2, 4, 6, 7], atol=0.5)
    True
    
    >>> result = derivative(y, t, order=2)
    >>> np.allclose(result.values[1:-1], [2, 2, 2], atol=0.5)
    True
    """
```

---

### 6.4 NÍVEL 4: TESTES DE INTEGRAÇÃO

**Prioridade**: 🔴 ALTA
**Ferramentas**: pytest

#### 6.4.1 Integração: Load → Store → Display

**Arquivo**: `tests/integration/test_data_flow.py`

```
[ ] test_load_csv_to_dataset_store
[ ] test_load_xlsx_to_dataset_store
[ ] test_load_parquet_to_dataset_store
[ ] test_dataset_store_to_data_panel
[ ] test_data_panel_to_viz_panel
[ ] test_series_selection_to_plot
[ ] test_multiple_files_load
[ ] test_large_file_flow
```

#### 6.4.2 Integração: UI → Calculation → Result

**Arquivo**: `tests/integration/test_calculation_flow.py`

```
[ ] test_operations_panel_to_worker
[ ] test_worker_to_calculus
[ ] test_calculus_to_results_panel
[ ] test_derivative_end_to_end
[ ] test_integral_end_to_end
[ ] test_smoothing_end_to_end
[ ] test_interpolation_end_to_end
[ ] test_calculation_adds_series
[ ] test_calculation_preserves_original
```

#### 6.4.3 Integração: Export Flow

**Arquivo**: `tests/integration/test_export_flow.py`

```
[ ] test_export_csv_complete
[ ] test_export_xlsx_complete
[ ] test_export_parquet_complete
[ ] test_export_with_metadata
[ ] test_export_selected_series
[ ] test_export_session
[ ] test_export_plot_image
```

#### 6.4.4 Integração: Session Flow

**Arquivo**: `tests/integration/test_session_flow.py`

```
[ ] test_session_save
[ ] test_session_load
[ ] test_session_restore_state
[ ] test_session_restore_plots
[ ] test_session_restore_calculations
[ ] test_session_auto_save
```

#### 6.4.5 Integração: Signal Flow

**Arquivo**: `tests/integration/test_signal_flow.py`

```
[ ] test_signal_hub_dataset_changed
[ ] test_signal_hub_selection_changed
[ ] test_signal_hub_plot_created
[ ] test_signal_hub_operation_finished
[ ] test_signal_propagation_data_to_viz
[ ] test_signal_propagation_config_to_all
```

---

### 6.5 NÍVEL 5: TESTES BASEADOS EM PROPRIEDADES (Property-Based)

**Prioridade**: 🟡 MÉDIA
**Ferramentas**: hypothesis

**TODO - Configuração**:

```
[ ] Instalar hypothesis
[ ] Configurar hypothesis em conftest.py
[ ] Criar estratégias customizadas para dados
```

**Arquivo**: `tests/property/test_calculus_properties.py`

```
[ ] test_derivative_integral_inverse
[ ] test_derivative_linearity
[ ] test_integral_bounds
[ ] test_derivative_order_composition
[ ] test_smoothing_idempotence
[ ] test_interpolation_endpoint_preservation
```

**Arquivo**: `tests/property/test_data_properties.py`

```
[ ] test_load_save_roundtrip
[ ] test_downsampling_preserves_range
[ ] test_downsampling_reduces_points
[ ] test_encoding_decode_roundtrip
```

**Exemplo com Hypothesis**:

```python
from hypothesis import given, strategies as st
import numpy as np

@given(
    st.lists(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False), 
             min_size=10, max_size=1000)
)
def test_derivative_integral_inverse(values):
    """Integral of derivative should approximate original (minus constant)."""
    y = np.array(values)
    t = np.linspace(0, 1, len(y))
    
    deriv = derivative(y, t, order=1)
    integ = integral(deriv.values, t, method='cumulative')
    
    # Should be close to original minus the constant
    reconstructed = integ.values + y[0]
    assert np.allclose(reconstructed, y, atol=0.1 * np.std(y))
```

---

### 6.6 NÍVEL 6: TESTES GUI/FUNCIONAIS

**Prioridade**: 🔴 ALTA
**Ferramentas**: pytest-qt

**TODO - Configuração**:

```
[ ] Instalar pytest-qt
[ ] Configurar QApplication fixture
[ ] Criar helpers para GUI testing
[ ] Configurar screenshots on failure
```

**conftest.py para GUI tests**:

```python
import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    
@pytest.fixture
def qtbot(qapp, qtbot):
    return qtbot
```

#### 6.6.1 Testes Funcionais - MainWindow

**Arquivo**: `tests/gui/test_main_window.py`

```
[ ] test_main_window_opens
[ ] test_main_window_close
[ ] test_main_window_menu_file
[ ] test_main_window_menu_edit
[ ] test_main_window_menu_view
[ ] test_main_window_menu_tools
[ ] test_main_window_menu_help
[ ] test_main_window_toolbar_visible
[ ] test_main_window_statusbar_visible
[ ] test_main_window_dock_panels
[ ] test_main_window_resize
[ ] test_main_window_minimize_maximize
[ ] test_main_window_keyboard_shortcuts
```

#### 6.6.2 Testes Funcionais - Dialogs

**Arquivo**: `tests/gui/test_dialogs.py`

```
[ ] test_upload_dialog_opens
[ ] test_upload_dialog_file_browse
[ ] test_upload_dialog_preview_updates
[ ] test_upload_dialog_ok_button
[ ] test_upload_dialog_cancel_button
[ ] test_settings_dialog_opens
[ ] test_settings_dialog_tabs
[ ] test_settings_dialog_save
[ ] test_export_dialog_opens
[ ] test_export_dialog_format_change
[ ] test_about_dialog_opens
[ ] test_about_dialog_close
```

#### 6.6.3 Testes Funcionais - Panels

**Arquivo**: `tests/gui/test_panels.py`

```
[ ] test_data_panel_tree_click
[ ] test_data_panel_checkbox_click
[ ] test_data_panel_double_click
[ ] test_data_panel_right_click_menu
[ ] test_viz_panel_tab_create
[ ] test_viz_panel_tab_close
[ ] test_viz_panel_plot_interaction
[ ] test_viz_panel_zoom
[ ] test_viz_panel_pan
[ ] test_config_panel_value_change
[ ] test_config_panel_apply_button
[ ] test_results_panel_table_display
[ ] test_results_panel_export_button
```

#### 6.6.4 Testes Funcionais - Context Menu

**Arquivo**: `tests/gui/test_context_menu.py`

```
[ ] test_plot_context_menu_opens
[ ] test_context_menu_derivative
[ ] test_context_menu_integral
[ ] test_context_menu_smoothing
[ ] test_context_menu_filter
[ ] test_context_menu_export
[ ] test_context_menu_zoom
[ ] test_context_menu_selection
```

---

### 6.7 NÍVEL 7: TESTES DE PERFORMANCE

**Prioridade**: 🟡 MÉDIA
**Ferramentas**: pytest-benchmark, memory_profiler

**TODO - Configuração**:

```
[ ] Instalar pytest-benchmark
[ ] Instalar memory_profiler
[ ] Criar fixtures com dados de diferentes tamanhos
[ ] Definir baselines de performance
```

**Baselines de Performance**:

| Operação | Tamanho | Tempo Máximo | Memória Máxima |
|----------|---------|--------------|----------------|
| Load CSV | 1M rows | 5s | 500MB |
| Load XLSX | 100K rows | 10s | 300MB |
| Plot 2D | 1M points | 1s | 200MB |
| Derivative | 1M points | 500ms | 100MB |
| Integral | 1M points | 300ms | 100MB |
| Interpolation | 100K points | 2s | 150MB |
| Downsampling | 10M → 10K | 1s | 50MB |

**Arquivo**: `tests/performance/test_load_performance.py`

```
[ ] test_load_csv_10k_benchmark
[ ] test_load_csv_100k_benchmark
[ ] test_load_csv_1m_benchmark
[ ] test_load_xlsx_10k_benchmark
[ ] test_load_xlsx_100k_benchmark
[ ] test_load_parquet_1m_benchmark
[ ] test_load_memory_usage_1m
```

**Arquivo**: `tests/performance/test_calc_performance.py`

```
[ ] test_derivative_10k_benchmark
[ ] test_derivative_100k_benchmark
[ ] test_derivative_1m_benchmark
[ ] test_integral_10k_benchmark
[ ] test_integral_100k_benchmark
[ ] test_integral_1m_benchmark
[ ] test_smoothing_100k_benchmark
[ ] test_interpolation_10k_benchmark
[ ] test_interpolation_100k_benchmark
```

**Arquivo**: `tests/performance/test_viz_performance.py`

```
[ ] test_plot_10k_points_benchmark
[ ] test_plot_100k_points_benchmark
[ ] test_plot_1m_points_benchmark
[ ] test_plot_10_series_benchmark
[ ] test_plot_update_benchmark
[ ] test_zoom_performance
[ ] test_pan_performance
```

**Arquivo**: `tests/performance/test_memory.py`

```
[ ] test_load_memory_leak
[ ] test_plot_memory_leak
[ ] test_calculation_memory_leak
[ ] test_session_memory_growth
[ ] test_repeated_operations_memory
```

---

### 6.8 NÍVEL 8: TESTES END-TO-END (E2E)

**Prioridade**: 🔴 ALTA
**Ferramentas**: pytest-qt, pytest-xvfb (Linux)

**TODO - Configuração**:

```
[ ] Configurar ambiente E2E
[ ] Criar test data fixtures
[ ] Configurar video recording on failure
[ ] Criar helpers para E2E
```

**Arquivo**: `tests/e2e/test_complete_workflow.py`

```
[ ] test_e2e_load_analyze_export_csv
[ ] test_e2e_load_analyze_export_xlsx
[ ] test_e2e_multiple_files_workflow
[ ] test_e2e_calculation_workflow
[ ] test_e2e_comparison_workflow
[ ] test_e2e_session_save_load
```

**Arquivo**: `tests/e2e/test_user_scenarios.py`

```
[ ] test_scenario_new_user_first_file
[ ] test_scenario_compare_two_series
[ ] test_scenario_calculate_derivative_integral
[ ] test_scenario_export_results
[ ] test_scenario_change_settings
[ ] test_scenario_multiple_plots
[ ] test_scenario_3d_visualization
```

**Arquivo**: `tests/e2e/test_error_recovery.py`

```
[ ] test_e2e_corrupted_file_recovery
[ ] test_e2e_calculation_error_recovery
[ ] test_e2e_export_error_recovery
[ ] test_e2e_crash_recovery
[ ] test_e2e_session_corruption_recovery
```

---

### 6.9 NÍVEL 9: TESTES DE CARGA E STRESS

**Prioridade**: 🟡 MÉDIA
**Ferramentas**: locust, pytest

**TODO - Configuração**:

```
[ ] Instalar locust (se API)
[ ] Criar stress test fixtures
[ ] Definir limites de stress
```

**Arquivo**: `tests/stress/test_load_stress.py`

```
[ ] test_load_100_files_sequential
[ ] test_load_100_files_parallel
[ ] test_load_10m_rows
[ ] test_load_1000_columns
[ ] test_load_repeated_1000_times
```

**Arquivo**: `tests/stress/test_ui_stress.py`

```
[ ] test_create_100_plots
[ ] test_add_1000_series_to_plot
[ ] test_rapid_tab_creation_deletion
[ ] test_rapid_zoom_pan
[ ] test_rapid_selection_changes
[ ] test_concurrent_calculations
```

**Arquivo**: `tests/stress/test_memory_stress.py`

```
[ ] test_load_until_memory_limit
[ ] test_plot_until_memory_limit
[ ] test_calculate_until_memory_limit
[ ] test_memory_recovery_after_clear
```

---

### 6.10 NÍVEL 10: SMOKE TESTS

**Prioridade**: 🔴 CRÍTICA (Executar em cada build)
**Ferramentas**: pytest -m smoke

**Arquivo**: `tests/smoke/test_smoke.py`

```
[ ] test_smoke_app_starts
[ ] test_smoke_main_window_opens
[ ] test_smoke_can_load_csv
[ ] test_smoke_can_plot
[ ] test_smoke_can_calculate
[ ] test_smoke_can_export
[ ] test_smoke_can_save_session
[ ] test_smoke_can_load_session
[ ] test_smoke_all_panels_visible
[ ] test_smoke_no_critical_errors
```

---

### 6.11 ESTRUTURA DE DIRETÓRIOS DE TESTES

```
tests/
├── conftest.py                    # Fixtures globais
├── fixtures/                      # Dados de teste
│   ├── csv/
│   │   ├── simple.csv
│   │   ├── large_1m.csv
│   │   ├── with_nan.csv
│   │   ├── different_encodings/
│   │   └── malformed/
│   ├── xlsx/
│   ├── parquet/
│   └── sessions/
├── unit/                          # Testes unitários
│   ├── test_calculus.py
│   ├── test_interpolation.py
│   ├── test_smoothing.py
│   ├── test_downsampling.py
│   ├── test_loader.py
│   ├── test_figures_2d.py
│   ├── test_figures_3d.py
│   ├── test_viz_panel.py
│   ├── test_data_panel.py
│   ├── test_config_panel.py
│   ├── test_results_panel.py
│   ├── test_dialogs.py
│   ├── test_models.py
│   ├── test_session_state.py
│   └── test_utils.py
├── integration/                   # Testes de integração
│   ├── test_data_flow.py
│   ├── test_calculation_flow.py
│   ├── test_export_flow.py
│   ├── test_session_flow.py
│   └── test_signal_flow.py
├── property/                      # Testes baseados em propriedades
│   ├── test_calculus_properties.py
│   └── test_data_properties.py
├── gui/                           # Testes de GUI
│   ├── test_main_window.py
│   ├── test_dialogs.py
│   ├── test_panels.py
│   └── test_context_menu.py
├── performance/                   # Testes de performance
│   ├── test_load_performance.py
│   ├── test_calc_performance.py
│   ├── test_viz_performance.py
│   └── test_memory.py
├── e2e/                          # Testes end-to-end
│   ├── test_complete_workflow.py
│   ├── test_user_scenarios.py
│   └── test_error_recovery.py
├── stress/                       # Testes de stress
│   ├── test_load_stress.py
│   ├── test_ui_stress.py
│   └── test_memory_stress.py
└── smoke/                        # Smoke tests
    └── test_smoke.py
```

---

### 6.12 CI/CD PIPELINE PARA TESTES

**GitHub Actions Workflow**: `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff mypy bandit
      - run: ruff check .
      - run: mypy src/
      - run: bandit -r src/

  unit-tests:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[test]"
      - run: pytest tests/unit -v --cov

  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[test]"
      - run: pytest tests/integration -v

  gui-tests:
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: sudo apt-get install -y xvfb
      - run: pip install -e ".[test]"
      - run: xvfb-run pytest tests/gui -v

  smoke-tests:
    needs: [unit-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[test]"
      - run: pytest tests/smoke -v -m smoke
```

---

### 6.13 CHECKLIST DE EXECUÇÃO DE TESTES

**Ordem obrigatória de execução**:

```
1º [ ] ruff check . --fix
   [ ] Todos os erros corrigidos? ___

2º [ ] mypy src/ --strict
   [ ] Todos os erros corrigidos? ___

3º [ ] bandit -r src/
   [ ] Todos os erros corrigidos? ___

4º [ ] pytest tests/unit -v --cov --cov-fail-under=90
   [ ] Cobertura >= 90%? ___
   [ ] Todos os testes passam? ___

5º [ ] pytest --doctest-modules src/
   [ ] Todos os doctests passam? ___

6º [ ] pytest tests/integration -v
   [ ] Todos os testes passam? ___

7º [ ] pytest tests/property -v
   [ ] Todos os testes passam? ___

8º [ ] pytest tests/gui -v
   [ ] Todos os testes passam? ___

9º [ ] pytest tests/performance -v --benchmark-only
   [ ] Todos os benchmarks dentro do limite? ___

10º [ ] pytest tests/e2e -v
    [ ] Todos os testes passam? ___

11º [ ] pytest tests/stress -v
    [ ] Sistema estável sob stress? ___

12º [ ] pytest tests/smoke -v -m smoke
    [ ] Smoke tests passam? ___
```

---

### 6.14 RESUMO DE TESTES A CRIAR

| Categoria | Arquivos | Testes | Status |
|-----------|----------|--------|--------|
| Linting Config | 3 | N/A | 🔴 TODO |
| Unit Tests | 25 | ~250 | 🔴 TODO |
| Doctests | 8 | ~50 | 🔴 TODO |
| Integration | 5 | ~40 | 🔴 TODO |
| Property-based | 2 | ~15 | 🔴 TODO |
| GUI/Functional | 4 | ~60 | 🔴 TODO |
| Performance | 4 | ~30 | 🔴 TODO |
| E2E | 3 | ~20 | 🔴 TODO |
| Stress | 3 | ~15 | 🔴 TODO |
| Smoke | 1 | ~10 | 🔴 TODO |
| **TOTAL** | **58** | **~490** | 🔴 |

---

### ⚠️ TESTES MANUAIS (APÓS AUTOMATIZADOS)

> **IMPORTANTE**: Os testes abaixo SÓ devem ser iniciados APÓS todos os 490+ testes automatizados passarem sem intervenção.

**Testes Manuais Pendentes**:

- 🔲 **Exploratório** - Teste livre pela aplicação
- 🔲 **Usabilidade** - Teste com usuários reais
- 🔲 **Aceitação (UAT)** - Validação com stakeholders

**Aguardando aprovação para iniciar testes manuais.**

---

## 🟡 CATEGORIA 7: PERFORMANCE E OTIMIZAÇÃO

### 7.1 Decimação de Dados para Visualização

**Arquivo**: `processing/downsampling.py`, `ui/panels/performance.py`
**Status**: IMPLEMENTADO NO BACKEND - NÃO CONECTADO

**TODO**:

```
[ ] Conectar adaptive decimation com viz_panel
[ ] Implementar LOD (Level of Detail) baseado em zoom
[ ] Adicionar indicador de decimação no gráfico
[ ] Permitir desativar decimação
```

### 7.2 Caching

**Arquivo**: `caching/disk.py`, `caching/memory.py`
**Status**: ESTRUTURA - PARCIALMENTE IMPLEMENTADO

**TODO**:

```
[ ] Implementar cache de arquivos carregados
[ ] Implementar cache de cálculos
[ ] Adicionar invalidação de cache
[ ] Implementar limite de memória
```

### 7.3 Lazy Loading

**TODO**:

```
[ ] Implementar carregamento sob demanda para arquivos grandes
[ ] Carregar apenas janela visível do gráfico
[ ] Implementar virtual scrolling para listas grandes
```

---

## 📝 CATEGORIA 8: DOCUMENTAÇÃO

### 8.1 Documentação de Usuário

**TODO**:

```
[ ] Manual de uso completo
[ ] Tutoriais em vídeo
[ ] FAQ
[ ] Troubleshooting guide
```

### 8.2 Documentação de Desenvolvedor

**TODO**:

```
[ ] API reference completa
[ ] Architecture overview
[ ] Contributing guide
[ ] Plugin development guide
```

---

## 📋 LISTA DE ARQUIVOS COM MAIS STUBS/TODOS

| Arquivo | Stubs/TODOs | Prioridade |
|---------|-------------|------------|
| `desktop/menus/plot_context_menu.py` | 6 pass | 🔴 ALTA |
| `ui/panels/operations_panel.py` | 16+ TODOs | 🔴 ALTA |
| `ui/panels/streaming_panel.py` | Estrutura só | 🔴 ALTA |
| `ui/panels/results_panel.py` | 3 pass | 🔴 ALTA |
| `ui/plot_sync.py` | 5 pass | 🟡 MÉDIA |
| `ui/selection_sync.py` | NotImplementedError | 🟡 MÉDIA |
| `ui/undo_redo.py` | 3 pass | 🟡 MÉDIA |
| `ui/video_export.py` | 1 TODO + 1 pass | 🟡 MÉDIA |
| `viz/figures_3d.py` | 3 pass | 🔴 ALTA |
| `viz/heatmaps.py` | 3 pass | 🟢 BAIXA |

---

---

## 🎨 CATEGORIA 9: MIGRAÇÃO COMPLETA PARA Qt Designer (.ui)

> **IMPORTANTE**: Atualmente a aplicação tem 2 arquivos .ui criados mas **NÃO SÃO USADOS**.
> O código Python cria toda a UI programaticamente. Esta seção documenta a migração completa.

### 9.0 Estado Atual dos Arquivos .ui

**Arquivos .ui existentes (NÃO CONECTADOS):**

- `ui/designer/main_window.ui` (534 linhas) - NÃO USADO
- `ui/designer/panels/data_panel.ui` (480 linhas) - NÃO USADO

**Total de componentes UI em código Python**: 60+ classes
**Total de arquivos .ui necessários**: ~45 arquivos

---

### 9.1 JANELAS PRINCIPAIS (QMainWindow)

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `MainWindow` | `desktop/main_window.py:38` | `designer/windows/main_window.ui` | 🔴 ALTA |
| `ModernMainWindow` | `ui/main_window.py:45` | `designer/windows/modern_main_window.ui` | 🔴 ALTA |

**TODO MainWindow:**

```
[ ] Criar main_window.ui com:
    - Menu bar completo (File, Edit, View, Tools, Help)
    - Tool bar com todas as ações
    - Status bar com progress e labels
    - Dock areas para painéis
    - Central widget para visualização
[ ] Criar UiLoaderMixin para carregar .ui
[ ] Migrar _create_menu_bar() para .ui
[ ] Migrar _create_tool_bar() para .ui
[ ] Migrar _create_status_bar() para .ui
[ ] Conectar signals em Python (não na UI)
```

---

### 9.2 DIÁLOGOS (QDialog) - 15 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `AboutDialog` | `desktop/dialogs/about_dialog.py:23` | `designer/dialogs/about_dialog.ui` | 🟢 BAIXA |
| `SettingsDialog` | `desktop/dialogs/settings_dialog.py:384` | `designer/dialogs/settings_dialog.ui` | 🟡 MÉDIA |
| `UploadDialog` | `desktop/dialogs/upload_dialog.py:184` | `designer/dialogs/upload_dialog.ui` | 🔴 ALTA |
| `MathAnalysisDialog` | `desktop/menus/plot_context_menu.py:32` | `designer/dialogs/math_analysis_dialog.ui` | 🟡 MÉDIA |
| `ConditionalSelectionDialog` | `desktop/selection/selection_widgets.py:178` | `designer/dialogs/conditional_selection_dialog.ui` | 🟡 MÉDIA |
| `CompareSeriesDialog` | `ui/context_menu.py:34` | `designer/dialogs/compare_series_dialog.ui` | 🟡 MÉDIA |
| `SmoothingDialog` (ui) | `ui/context_menu.py:119` | `designer/dialogs/smoothing_dialog_simple.ui` | 🟡 MÉDIA |
| `AnnotationDialog` | `ui/context_menu.py:169` | `designer/dialogs/annotation_dialog.ui` | 🟢 BAIXA |
| `ExportDialog` | `ui/export_dialog.py:110` | `designer/dialogs/export_dialog.ui` | 🔴 ALTA |
| `BaseOperationDialog` | `ui/operation_dialogs.py:292` | `designer/dialogs/base_operation_dialog.ui` | 🟡 MÉDIA |
| `OperationPreviewDialog` | `ui/preview_dialog.py:116` | `designer/dialogs/operation_preview_dialog.ui` | 🟡 MÉDIA |
| `VideoExportDialog` | `ui/video_export.py:304` | `designer/dialogs/video_export_dialog.ui` | 🟡 MÉDIA |
| `FilterDialog` | `ui/dialogs/filter_dialog.py:38` | `designer/dialogs/filter_dialog.ui` | 🔴 ALTA |
| `SettingsDialog` (ui) | `ui/dialogs/settings_dialog.py:128` | `designer/dialogs/settings_dialog_modern.ui` | 🟡 MÉDIA |
| `SmoothingDialog` | `ui/dialogs/smoothing_dialog.py:40` | `designer/dialogs/smoothing_dialog.ui` | 🔴 ALTA |
| `AxesConfigDialog` | `ui/panels/viz_panel.py:1326` | `designer/dialogs/axes_config_dialog.ui` | 🟡 MÉDIA |

**TODO Diálogos:**

```
[ ] Criar estrutura: designer/dialogs/
[ ] Para cada diálogo:
    - Criar arquivo .ui no Qt Designer
    - Layout com QFormLayout ou QVBoxLayout
    - QDialogButtonBox para OK/Cancel
    - Campos de entrada apropriados
    - Usar QStackedWidget para abas se necessário
[ ] Criar DialogLoaderMixin base
[ ] Migrar validações para Python
[ ] Manter signals/slots em Python
```

---

### 9.3 PAINÉIS PRINCIPAIS (QWidget) - 14 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `DataPanel` | `desktop/widgets/data_panel.py:40` | `designer/panels/data_panel.ui` | 🔴 ALTA |
| `ConfigPanel` (desktop) | `desktop/widgets/config_panel.py:229` | `designer/panels/config_panel.ui` | 🔴 ALTA |
| `ResultsPanel` (desktop) | `desktop/widgets/results_panel.py:197` | `designer/panels/results_panel.ui` | 🔴 ALTA |
| `VizPanel` | `desktop/widgets/viz_panel.py:305` | `designer/panels/viz_panel.ui` | 🔴 ALTA |
| `SelectionPanel` | `desktop/selection/selection_widgets.py:473` | `designer/panels/selection_panel.ui` | 🟡 MÉDIA |
| `ConfigPanel` (ui) | `ui/panels/config_panel.py:90` | `designer/panels/config_panel_modern.ui` | 🟡 MÉDIA |
| `CompactDataPanel` | `ui/panels/data_panel.py:66` | `designer/panels/compact_data_panel.ui` | 🟡 MÉDIA |
| `OperationsPanel` | `ui/panels/operations_panel.py:56` | `designer/panels/operations_panel.ui` | 🔴 ALTA |
| `ResultsPanel` (ui) | `ui/panels/results_panel.py:211` | `designer/panels/results_panel_modern.ui` | 🟡 MÉDIA |
| `StreamingPanel` | `ui/panels/streaming_panel.py:196` | `designer/panels/streaming_panel.ui` | 🔴 ALTA |
| `ModernVizPanel` | `ui/panels/viz_panel.py:1649` | `designer/panels/modern_viz_panel.ui` | 🟡 MÉDIA |

**TODO Painéis:**

```
[ ] Criar estrutura: designer/panels/
[ ] Para cada painel:
    - Criar arquivo .ui no Qt Designer
    - Definir layout principal
    - Adicionar GroupBoxes para seções
    - Definir splitters onde necessário
    - Placeholders para widgets dinâmicos
[ ] Usar promoted widgets para gráficos
[ ] Conectar com session_state em Python
```

---

### 9.4 WIDGETS DE CONFIGURAÇÃO (QWidget) - 10 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `GeneralSettingsTab` | `desktop/dialogs/settings_dialog.py:27` | `designer/widgets/general_settings_tab.ui` | 🟡 MÉDIA |
| `PerformanceSettingsTab` | `desktop/dialogs/settings_dialog.py:125` | `designer/widgets/performance_settings_tab.ui` | 🟡 MÉDIA |
| `LoggingSettingsTab` | `desktop/dialogs/settings_dialog.py:267` | `designer/widgets/logging_settings_tab.ui` | 🟢 BAIXA |
| `InterpolationConfigWidget` | `desktop/widgets/config_panel.py:37` | `designer/widgets/interpolation_config.ui` | 🟡 MÉDIA |
| `CalculusConfigWidget` | `desktop/widgets/config_panel.py:156` | `designer/widgets/calculus_config.ui` | 🟡 MÉDIA |
| `SelectionStatsWidget` | `desktop/selection/selection_widgets.py:339` | `designer/widgets/selection_stats.ui` | 🟢 BAIXA |
| `ParameterWidget` | `ui/operation_dialogs.py:63` | `designer/widgets/parameter_widget.ui` | 🟡 MÉDIA |
| `PreviewWidget` | `ui/operation_dialogs.py:239` | `designer/widgets/preview_widget.ui` | 🟡 MÉDIA |
| `PreviewVisualizationWidget` | `ui/operation_preview.py:287` | `designer/widgets/preview_visualization.ui` | 🟡 MÉDIA |
| `MinimapWidget` | `ui/panels/streaming_panel.py:93` | `designer/widgets/minimap.ui` | 🟢 BAIXA |

---

### 9.5 WIDGETS DE SELEÇÃO (QWidget) - 6 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `RangePickerWidget` | `ui/selection_widgets.py:45` | `designer/widgets/range_picker.ui` | 🟡 MÉDIA |
| `BrushSelectionWidget` | `ui/selection_widgets.py:188` | `designer/widgets/brush_selection.ui` | 🟡 MÉDIA |
| `QueryBuilderWidget` | `ui/selection_widgets.py:346` | `designer/widgets/query_builder.ui` | 🟡 MÉDIA |
| `SelectionHistoryWidget` | `ui/selection_widgets.py:518` | `designer/widgets/selection_history.ui` | 🟢 BAIXA |
| `SelectionManagerWidget` | `ui/selection_widgets.py:626` | `designer/widgets/selection_manager.ui` | 🟡 MÉDIA |

---

### 9.6 WIDGETS DE STREAMING/FILTROS (QWidget) - 4 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `StreamingControlWidget` | `ui/streaming_controls.py:33` | `designer/widgets/streaming_control.ui` | 🔴 ALTA |
| `TimeIntervalWidget` | `ui/stream_filters.py:35` | `designer/widgets/time_interval.ui` | 🟡 MÉDIA |
| `ValuePredicateWidget` | `ui/stream_filters.py:102` | `designer/widgets/value_predicate.ui` | 🟡 MÉDIA |
| `StreamFiltersWidget` | `ui/stream_filters.py:171` | `designer/widgets/stream_filters.ui` | 🔴 ALTA |

---

### 9.7 WIDGETS DE VISUALIZAÇÃO (QWidget) - 6 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `Plot2DWidget` | `viz/figures_2d.py:64` | (Código Python - promoted widget) | 🟡 MÉDIA |
| `Plot3DWidget` | `viz/figures_3d.py:64` | (Código Python - promoted widget) | 🟡 MÉDIA |
| `Plot3DWidget` (desktop) | `desktop/widgets/viz_panel.py:239` | (Código Python - promoted widget) | 🟡 MÉDIA |
| `MatplotlibWidget` | `ui/panels/viz_panel.py:63` | (Código Python - promoted widget) | 🟢 BAIXA |
| `HeatmapWidget` | `viz/heatmaps.py:86` | (Código Python - promoted widget) | 🟢 BAIXA |
| `PreviewCanvas` | `ui/preview_dialog.py:37` | (Código Python - promoted widget) | 🟢 BAIXA |

**Nota**: Widgets de visualização não podem ser migrados 100% para .ui porque contêm lógica de renderização.
Usar "promoted widgets" no Qt Designer.

---

### 9.8 MENUS E TOOLBARS - 3 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `PlotContextMenu` (desktop) | `desktop/menus/plot_context_menu.py:214` | `designer/menus/plot_context_menu.ui` | 🔴 ALTA |
| `SelectionToolbar` | `desktop/selection/selection_widgets.py:30` | `designer/toolbars/selection_toolbar.ui` | 🟡 MÉDIA |
| `PlotContextMenu` (ui) | `ui/context_menu.py:247` | `designer/menus/plot_context_menu_modern.ui` | 🟡 MÉDIA |

---

### 9.9 FRAMES E CONTAINERS - 3 classes

| Classe | Arquivo Atual | Arquivo .ui a Criar | Prioridade |
|--------|---------------|---------------------|------------|
| `StatCard` | `ui/panels/results_panel.py:57` | `designer/widgets/stat_card.ui` | 🟢 BAIXA |
| `StatisticsTable` | `ui/panels/results_panel.py:137` | `designer/widgets/statistics_table.ui` | 🟢 BAIXA |
| `DropZone` | `ui/panels/viz_panel.py:1547` | `designer/widgets/drop_zone.ui` | 🟢 BAIXA |

---

### 9.10 ESTRUTURA DE DIRETÓRIOS PARA .ui

```
ui/designer/
├── windows/
│   ├── main_window.ui
│   └── modern_main_window.ui
├── dialogs/
│   ├── about_dialog.ui
│   ├── settings_dialog.ui
│   ├── upload_dialog.ui
│   ├── export_dialog.ui
│   ├── filter_dialog.ui
│   ├── smoothing_dialog.ui
│   ├── math_analysis_dialog.ui
│   ├── annotation_dialog.ui
│   ├── compare_series_dialog.ui
│   ├── conditional_selection_dialog.ui
│   ├── operation_preview_dialog.ui
│   ├── video_export_dialog.ui
│   └── axes_config_dialog.ui
├── panels/
│   ├── data_panel.ui
│   ├── config_panel.ui
│   ├── results_panel.ui
│   ├── viz_panel.ui
│   ├── operations_panel.ui
│   ├── streaming_panel.ui
│   └── selection_panel.ui
├── widgets/
│   ├── general_settings_tab.ui
│   ├── performance_settings_tab.ui
│   ├── logging_settings_tab.ui
│   ├── interpolation_config.ui
│   ├── calculus_config.ui
│   ├── selection_stats.ui
│   ├── parameter_widget.ui
│   ├── preview_widget.ui
│   ├── range_picker.ui
│   ├── brush_selection.ui
│   ├── query_builder.ui
│   ├── selection_history.ui
│   ├── selection_manager.ui
│   ├── streaming_control.ui
│   ├── time_interval.ui
│   ├── value_predicate.ui
│   ├── stream_filters.ui
│   ├── stat_card.ui
│   ├── statistics_table.ui
│   ├── drop_zone.ui
│   └── minimap.ui
├── menus/
│   └── plot_context_menu.ui
└── toolbars/
    └── selection_toolbar.ui
```

---

### 9.11 INFRAESTRUTURA NECESSÁRIA

**TODO Infraestrutura:**

```
[ ] Criar classe UiLoader base em ui/loader.py (usar a existente ou melhorar)
[ ] Criar UiLoaderMixin para widgets
[ ] Criar DialogLoaderMixin para diálogos
[ ] Criar script para compilar .ui para .py (pyuic6)
[ ] Adicionar ao build process
[ ] Documentar promoted widgets
```

**Código de exemplo para UiLoaderMixin:**

```python
from PyQt6 import uic
from pathlib import Path

class UiLoaderMixin:
    def load_ui(self, ui_file: str):
        ui_path = Path(__file__).parent / "designer" / ui_file
        uic.loadUi(ui_path, self)
```

---

### 9.12 MESSAGE BOXES A PADRONIZAR (89 total)

| Arquivo | Quantidade | TODO |
|---------|------------|------|
| `ui/context_menu.py` | 23 | Criar classe MessageHelper |
| `desktop/main_window.py` | 14 | Usar MessageHelper |
| `desktop/menus/plot_context_menu.py` | 9 | Usar MessageHelper |
| `ui/main_window.py` | 7 | Usar MessageHelper |
| `ui/export_dialog.py` | 5 | Usar MessageHelper |
| `ui/selection_widgets.py` | 5 | Usar MessageHelper |
| `ui/panels/operations_panel.py` | 5 | Usar MessageHelper |
| Outros | 21 | Usar MessageHelper |

**TODO MessageBoxes:**

```
[ ] Criar utils/messages.py com classe MessageHelper
[ ] Padronizar textos de mensagens
[ ] Adicionar suporte a i18n nas mensagens
[ ] Criar constantes para mensagens comuns
```

---

### 9.13 PLANO DE MIGRAÇÃO PARA .ui

**Fase A: Preparação (1 semana)**

```
[ ] Criar estrutura de diretórios
[ ] Implementar UiLoaderMixin
[ ] Implementar DialogLoaderMixin
[ ] Criar script de build para .ui → .py
[ ] Testar com um widget simples
```

**Fase B: Diálogos Críticos (2 semanas)**

```
[ ] Migrar UploadDialog
[ ] Migrar ExportDialog
[ ] Migrar FilterDialog
[ ] Migrar SmoothingDialog
[ ] Migrar SettingsDialog
```

**Fase C: Painéis Principais (2 semanas)**

```
[ ] Migrar DataPanel
[ ] Migrar ConfigPanel
[ ] Migrar ResultsPanel
[ ] Migrar OperationsPanel
[ ] Migrar StreamingPanel
```

**Fase D: MainWindow (1 semana)**

```
[ ] Migrar menu bar para .ui
[ ] Migrar tool bar para .ui
[ ] Migrar status bar para .ui
[ ] Configurar dock widgets
```

**Fase E: Widgets Restantes (2 semanas)**

```
[ ] Migrar widgets de configuração
[ ] Migrar widgets de seleção
[ ] Migrar widgets de streaming
[ ] Promoted widgets para visualização
```

**Fase F: Padronização (1 semana)**

```
[ ] Criar MessageHelper
[ ] Padronizar estilos via QSS
[ ] Documentar todos os .ui
[ ] Testes de regressão
```

---

### 9.14 RESUMO DA MIGRAÇÃO

| Categoria | Quantidade | .ui Existentes | A Criar |
|-----------|------------|----------------|---------|
| MainWindows | 2 | 1 (não usado) | 2 |
| Diálogos | 16 | 0 | 16 |
| Painéis | 11 | 1 (não usado) | 11 |
| Widgets Config | 10 | 0 | 10 |
| Widgets Seleção | 5 | 0 | 5 |
| Widgets Streaming | 4 | 0 | 4 |
| Widgets Viz | 6 | 0 | (promoted) |
| Menus/Toolbars | 3 | 0 | 3 |
| Frames | 3 | 0 | 3 |
| **TOTAL** | **60** | **2** | **~45** |

**Esforço estimado**: 8-10 semanas adicionais
**Benefícios**:

- Manutenção visual mais fácil
- Designers podem ajudar
- Separação clara UI/Lógica
- Temas mais fáceis de implementar

---

## 🚀 PLANO DE IMPLEMENTAÇÃO SUGERIDO

### Fase 1: Correções Críticas (2-3 semanas)

1. ✅ Corrigir cores das séries
2. ✅ Corrigir legenda com nomes corretos
3. Conectar cálculos UI↔Backend
4. Implementar menu de contexto
5. Corrigir gráficos 3D

### Fase 2: Funcionalidades Essenciais (3-4 semanas)

1. Results Panel funcional
2. Streaming/Playback básico
3. Exportação completa
4. Checkboxes de séries
5. Multi-Y axis

### Fase 3: UX e Polimento (2-3 semanas)

1. Undo/Redo
2. Temas dark/light
3. Eixo datetime
4. Seleção avançada
5. Sincronização de views

### Fase 4: Testes e Documentação (2 semanas)

1. Cobertura de testes > 80%
2. Documentação de usuário
3. Documentação de API
4. Testes E2E

---

## ⚠️ DEPENDÊNCIAS CRÍTICAS

1. **pyqtgraph** - 2D plotting (OK)
2. **pyvista** - 3D plotting (Precisa teste mais profundo)
3. **pandas** - Data handling (OK)
4. **scipy** - Cálculos (OK)
5. **numba** - Otimização (Opcional mas recomendado)
6. **moviepy** - Video export (Não instalado/testado)

---

## 📊 MÉTRICAS DE CONCLUSÃO

Para considerar a aplicação PRONTA PARA PRODUÇÃO:

- [ ] 0 crashes em uso normal (teste de 8h)
- [ ] Todas as 7 features core funcionando (load, plot, calculate, export, streaming, selection, 3D)
- [ ] Cobertura de testes > 70%
- [ ] Documentação de usuário completa
- [ ] Performance: load 1M pontos < 5s, plot < 1s
- [ ] Todos os 176+ stubs implementados
- [ ] 0 "coming soon" messages
- [ ] 0 "pass" statements em handlers de UI

---

**Total de Itens TODO**: ~300+ (incluindo migração .ui)
**Estimativa de Esforço**: 16-22 semanas de trabalho focado
**Prioridade Absoluta**: Categorias 1, 2.4, 4.1 (conexões UI↔Backend), 9 (migração .ui)

---

*Documento gerado em: 30/01/2026*
*Última auditoria do código: 30/01/2026*
