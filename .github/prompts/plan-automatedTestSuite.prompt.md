## Plan: Suíte de Testes Automatizados Completa (pytest)

**TL;DR:** Substituir os ~143 arquivos de teste existentes por uma suíte organizada em `tests/automated/`, cobrindo os 10 eixos solicitados. A nova estrutura usa um `conftest.py` raiz unificado (resolvendo o conflito atual de 4 definições diferentes de `qapp`), adiciona `pytest-memray` e `pytest-html` às dependências, e gera relatórios HTML + JUnit XML. Todos os 73 arquivos `.ui` serão testados, bem como os ~17 dialogs, ~20 painéis/widgets, 25+ signals do `SignalHub`, e 5 temas. A cobertura alvo permanece 70% conforme o `pyproject.toml` existente.

---

**Steps**

### Fase 0 — Preparação de Infraestrutura

1. **Adicionar dependências** em [pyproject.toml](platform_base/pyproject.toml): incluir `pytest-memray >= 1.5.0` e `pytest-html >= 4.0.0` na seção `[project.optional-dependencies]` dev/test. Manter todas as dependências existentes (`pytest-qt`, `pytest-cov`, `pytest-xdist`, `pytest-benchmark`, `hypothesis`).

2. **Atualizar configuração pytest** em [pyproject.toml](platform_base/pyproject.toml): alterar `testpaths` de `["tests"]` para `["tests/automated"]`, adicionar `--html=docs/reports/test_report.html --self-contained-html --junitxml=docs/reports/junit.xml` ao `addopts`, registrar marker `automated` na lista de markers.

3. **Remover/arquivar testes antigos**: mover toda a pasta `tests/` atual para `tests/_legacy/` (preservar histórico, não deletar). Manter `tests/fixtures/` (dados CSV/XLSX/parquet de exemplo são reutilizáveis).

4. **Criar estrutura de diretórios**:
   ```
   tests/
   ├── _legacy/            ← testes antigos movidos aqui
   ├── fixtures/            ← mantido (dados de exemplo)
   ├── automated/
   │   ├── __init__.py
   │   ├── conftest.py      ← conftest unificado
   │   ├── test_01_ui_loading.py
   │   ├── test_02_mandatory_widgets.py
   │   ├── test_03_navigation.py
   │   ├── test_04_signals_slots.py
   │   ├── test_05_initialization.py
   │   ├── test_06_resources.py
   │   ├── test_07_state_visibility.py
   │   ├── test_08_memory_leaks.py
   │   ├── test_09_exceptions_errors.py
   │   └── test_10_coverage.py
   ```

### Fase 1 — `conftest.py` Unificado

5. **Criar** [tests/automated/conftest.py](tests/automated/conftest.py) com:
   - **Fixture `qapp` (session)**: `QApplication` única com `QT_QPA_PLATFORM=offscreen` + `--platform offscreen` (resolve conflito das 4 definições atuais)
   - **Fixture `ui_files_dir` (session)**: caminho para `src/platform_base/desktop/ui_files/`
   - **Fixture `all_ui_files` (session)**: lista de todos os 73 `.ui` via `glob("*.ui")`
   - **Fixture `ui_file_contents` (session)**: dicionário `{nome: ElementTree}` com parse XML de cada `.ui`
   - **Fixture `dataset_store` (module)**: instância real de `DatasetStore`
   - **Fixture `session_state` (module)**: instância real de `SessionState(dataset_store)`
   - **Fixture `signal_hub` (module)**: instância real de `SignalHub()`
   - **Fixture `mock_session_state` (function)**: `MagicMock` com todos os signals mockados (reutilizando padrão de [tests/conftest.py](platform_base/tests/conftest.py))
   - **Fixture `mock_signal_hub` (function)**: `MagicMock` com todos os 25+ signals do `SignalHub`
   - **Fixture `widget_factory` (function)**: factory function que rastreia widgets criados, faz `close()` + `deleteLater()` + `gc.collect()` + `processEvents()` no teardown
   - **Fixture `sample_dataframe` (function)**: DataFrame com 1000 pontos (time + 3 séries)
   - **Fixture `temp_dir` (function)**: `tmp_path` wrapper
   - **Helper `get_all_widgets()`**: busca recursiva de children via `findChildren(QWidget)`
   - **Helper `validate_ui_xml()`**: valida estrutura do XML `.ui`
   - **Hook `pytest_configure()`**: registra markers `automated`, `gui`, `slow`, `smoke`
   - **Hook `cleanup_qt_objects` (autouse, function)**: `processEvents()` após cada teste

### Fase 2 — 10 Módulos de Teste

6. **`test_01_ui_loading.py`** — Carregamento de todos os arquivos `.ui`
   - `test_ui_files_exist`: verifica que todos os 73 `.ui` existem no diretório
   - `test_ui_xml_valid[{file}]`: parametrizado sobre `all_ui_files`, valida XML bem-formado
   - `test_ui_has_root_widget[{file}]`: cada `.ui` tem `<widget>` raiz com `class` e `name`
   - `test_ui_loadable_with_uic[{file}]`: parametrizado, usa `PyQt6.uic.loadUi()` para carregar cada `.ui` em `QWidget` offscreen
   - `test_ui_compiled_files_exist`: verifica que cada `.ui` tem `_ui.py` correspondente
   - `test_ui_compiled_matches_source`: compara timestamp `.ui` vs `_ui.py` (warning se desatualizado)
   - Total estimado: **~220 testes** (73×3 parametrizados + extras)

7. **`test_02_mandatory_widgets.py`** — Validação de widgets obrigatórios em cada tela
   - Definir dicionário `MANDATORY_WIDGETS` mapeando cada tela para seus widgets esperados, extraído dos `.ui` e do código-fonte (ex: `ModernMainWindow` deve ter `centralWidget`, `statusBar`, `menuBar`; `DataPanel` deve ter `treeView`/`tableView`; `UploadDialog` deve ter `QDialogButtonBox`; etc.)
   - `test_mandatory_widgets_present[{ui_file}]`: parametrizado, carrega `.ui` e verifica que widgets obrigatórios existem via `findChild()`
   - `test_widget_types_correct[{ui_file}]`: verifica que cada widget obrigatório é da classe Qt correta
   - `test_widget_names_unique[{ui_file}]`: verifica que não há nomes de `objectName` duplicados
   - `test_layouts_not_empty[{ui_file}]`: verifica que layouts principais contêm pelo menos um widget
   - Mapear widgets obrigatórios para os principais painéis: `DataPanel` (`dataPanel.ui`), `VizPanel` (`vizPanel.ui`), `OperationsPanel` (`operationsPanel.ui`), `ConfigPanel` (`configPanel.ui`), `ResultsPanel` (`resultsPanel.ui`), `StreamingPanel` (`streamingControls.ui`)
   - Total estimado: **~150 testes**

8. **`test_03_navigation.py`** — Testes de navegação entre todas as telas
   - `test_main_window_dock_panels`: instancia `ModernMainWindow` (com mocks), verifica que todos os dock widgets (Data, Config, Operations, Streaming, Results) são criados e acessíveis
   - `test_menu_actions_exist`: verifica menus (File, Edit, View, Tools, Help) e suas actions
   - `test_dialog_open_close[{dialog}]`: parametrizado sobre todos os ~17 dialogs (`UploadDialog`, `SettingsDialog`, `AboutDialog`, `ExportDialog`, `FilterDialog`, `SmoothingDialog`, `ShortcutsDialog`, `VideoExportDialog`, etc.) — instancia, mostra, fecha
   - `test_panel_show_hide[{panel}]`: parametrizado sobre painéis — toggle visibility
   - `test_tab_navigation`: se `QTabWidget` existe, navega entre tabs
   - `test_stacked_widget_pages`: se `QStackedWidget` existe, navega entre páginas
   - `test_theme_switch[{theme}]`: parametrizado sobre 5 temas (Light, Dark, Ocean, Forest, Sunset)
   - Total estimado: **~50 testes**

9. **`test_04_signals_slots.py`** — Verificação de sinais e slots
   - `test_signal_hub_signals_exist`: verifica que `SignalHub` tem os 25+ signals declarados como atributos
   - `test_signal_hub_emit_receive[{signal}]`: parametrizado, conecta slot mock, emite signal, verifica recepção via `qtbot.waitSignal()` ou `QSignalSpy`
   - `test_session_state_signals`: verifica que `SessionState` emite `selection_changed`, `view_state_changed`, etc. quando estado muda
   - `test_worker_signals`: instancia `BaseWorker`, verifica `progress`, `status_updated`, `error`, `finished`
   - `test_ui_connections_from_xml[{file}]`: parametrizado, extrai `<connection>` dos `.ui` XML, verifica que signal e slot existem
   - `test_cross_component_signals`: testa fluxo `dataset_loaded → DataPanel.refresh() → VizPanel.update()`
   - `test_signal_disconnect`: conecta e desconecta, verifica que slot não é chamado após disconnect
   - Total estimado: **~80 testes**

10. **`test_05_initialization.py`** — Testes de inicialização da aplicação
    - `test_qapplication_creation`: verifica `QApplication` cria sem erros
    - `test_platform_application_init`: instancia `PlatformApplication` (de [desktop/app.py](platform_base/src/platform_base/desktop/app.py)), verifica atributos
    - `test_dataset_store_init`: `DatasetStore()` cria vazio
    - `test_session_state_init`: `SessionState(dataset_store)` inicializa com estado default
    - `test_signal_hub_init`: `SignalHub()` inicializa com todos os signals
    - `test_main_window_init`: `ModernMainWindow(session_state, signal_hub)` inicializa (com mocks)
    - `test_panels_init[{panel}]`: parametrizado, cada painel inicializa com session_state e signal_hub mockados
    - `test_dialogs_init[{dialog}]`: parametrizado, cada dialog instancia sem erros
    - `test_theme_manager_init`: `ThemeManager` inicializa com tema default
    - `test_config_manager_init`: `ConfigManager` carrega config ou cria default
    - `test_undo_manager_init`: `UndoManager` inicializa com stack vazio
    - `test_init_with_missing_ui_fallback`: testa que widgets criam fallback UI quando `.ui` não encontrado
    - Total estimado: **~40 testes**

11. **`test_06_resources.py`** — Validação de recursos (ícones, imagens)
    - `test_ui_files_dir_exists`: diretório `desktop/ui_files/` existe
    - `test_resources_dir_exists`: diretório `desktop/resources/` existe
    - `test_icons_dir_exists`: `desktop/resources/icons/` existe
    - `test_styles_dir_exists`: `desktop/resources/styles/` existe  
    - `test_config_file_exists`: [configs/platform.yaml](platform_base/configs/platform.yaml) existe e é YAML válido
    - `test_sample_data_files_exist`: arquivos em `data/samples/` existem
    - `test_ui_file_references_valid[{file}]`: parametrizado, extrai referências a recursos dos `.ui` (`<iconset>`, `<pixmap>`) e verifica que arquivos existem
    - `test_theme_stylesheets_loadable[{theme}]`: parametrizado sobre 5 temas, `ThemeManager.apply_theme()` não lança exceção
    - `test_emoji_icons_render`: verifica que os ícones baseados em Unicode/emoji são strings válidas
    - Total estimado: **~90 testes**

12. **`test_07_state_visibility.py`** — Testes de estado e visibilidade de widgets
    - `test_widget_initial_visibility[{widget}]`: parametrizado, verifica estado inicial de visibilidade
    - `test_widget_enable_disable[{widget}]`: testa `setEnabled(True/False)` e confirma `isEnabled()`
    - `test_widget_show_hide[{widget}]`: testa `show()/hide()` e confirma `isVisible()`
    - `test_session_state_persistence`: altera estado na `SessionState`, verifica que widgets refletem mudança
    - `test_theme_changes_widget_style[{theme}]`: aplica tema, verifica que `palette()` ou `styleSheet()` muda
    - `test_widget_resize`: redimensiona widgets, verifica que layout ajusta sem overflow
    - `test_dock_widget_float_dock`: `QDockWidget` pode ser flutuante e re-dockado
    - `test_menu_actions_checkable`: menus com estados toggle funcionam
    - `test_statusbar_messages`: `status_updated` signal atualiza `statusBar().showMessage()`
    - Total estimado: **~60 testes**

13. **`test_08_memory_leaks.py`** — Detecção de memory leaks (pytest-memray)
    - `@pytest.mark.limit_memory("100 MB")` nos testes mais pesados
    - `test_widget_creation_destruction_leak`: cria/destrói 100 instâncias de cada widget, verifica que memória retorna ao baseline (`weakref.ref` + `gc.collect`)
    - `test_dialog_open_close_leak[{dialog}]`: parametrizado, abre/fecha 50 vezes cada dialog
    - `test_signal_connection_leak`: conecta/desconecta 1000 slots, verifica sem crescimento
    - `test_large_dataset_load_unload`: carrega DataFrame 100k linhas, remove, verifica memória liberada
    - `test_plot_widget_memory`: cria/destrói `Plot2DWidget` repetidamente
    - `test_theme_switch_memory`: alterna entre 5 temas 20 vezes
    - `test_timer_cleanup_no_leak`: verifica que `autosave_timer` e `memory_timer` de `ModernMainWindow` são parados no `closeEvent`
    - Usar `pytest-memray` decorators (`@pytest.mark.limit_memory`, `@pytest.mark.limit_leaks`) + `tracemalloc` para snapshots granulares onde necessário
    - Total estimado: **~30 testes**

14. **`test_09_exceptions_errors.py`** — Testes de exceções e tratamento de erros
    - `test_load_invalid_csv`: `Loader.load()` com CSV malformado lança exceção apropriada
    - `test_load_nonexistent_file`: lança `FileNotFoundError` ou equivalente
    - `test_load_empty_file`: trata arquivo vazio sem crash
    - `test_load_corrupt_xlsx`: arquivo XLSX corrompido é tratado
    - `test_division_by_zero_in_calculus`: operações de cálculo com divisão por zero
    - `test_nan_handling_in_processing`: NaN em dados não causa crash
    - `test_invalid_interpolation_params`: parâmetros inválidos lançam `ValueError`
    - `test_ui_load_missing_ui_file`: widget com `UI_FILE` inexistente usa fallback
    - `test_global_exception_handler`: `PlatformApplication` global exception handler captura exceções não tratadas
    - `test_worker_error_signal`: `BaseWorker` emite `error` signal em caso de falha
    - `test_crash_handler_recovery`: `CrashHandler` salva estado antes de crash
    - `test_invalid_theme_name`: tema inexistente não causa crash
    - `test_schema_validation_errors`: `Validator` rejeita dados fora do schema
    - `test_concurrent_access_safety`: acesso simultâneo a `DatasetStore` não corrompe dados
    - Total estimado: **~40 testes**

15. **`test_10_coverage.py`** — Validação meta de cobertura
    - `test_all_source_modules_imported`: importa todos os módulos de `src/platform_base/` (garante que parsing funciona)
    - `test_all_public_classes_tested`: verifica que todas as classes públicas têm pelo menos 1 teste nos 9 módulos anteriores
    - `test_all_ui_files_covered`: garante que cada um dos 73 `.ui` é referenciado em pelo menos 1 teste
    - `test_all_signals_covered`: verifica que cada signal do `SignalHub` é testado
    - `test_coverage_threshold`: meta-teste que verifica cobertura >= 70% via `coverage.py` API
    - Total estimado: **~10 testes**

### Fase 3 — Configuração de Relatórios

16. **Criar script de execução** `scripts/run_tests.py` (ou adicionar ao `Makefile`/`pyproject.toml`):
    ```
    pytest tests/automated/ 
      --html=docs/reports/test_report.html --self-contained-html 
      --junitxml=docs/reports/junit.xml 
      --cov=src/platform_base --cov-report=html:docs/reports/coverage_html 
      --cov-report=term-missing 
      --memray
      -v -ra --tb=short
    ```

17. **Criar** `docs/reports/.gitkeep` para garantir que o diretório de relatórios existe no repositório.

---

**Verificação**

- Executar `pytest tests/automated/ -v --tb=short` — todos os testes devem passar (0 falhas, 0 skips)
- Executar com `--cov` — cobertura >= 70%
- Executar com `--html` — relatório HTML gerado em `docs/reports/test_report.html`
- Executar com `--junitxml` — XML gerado em `docs/reports/junit.xml`
- Executar com `--memray` — sem leaks detectados acima dos limites configurados
- Verificar que `tests/_legacy/` NÃO é executado (removido do `testpaths`)

---

**Decisões**

- **Substituição total**: testes antigos movidos para `tests/_legacy/`, não deletados — permitindo referência futura
- **Conftest unificado**: um único `conftest.py` em `tests/automated/` resolve o conflito atual de 4 `qapp` fixtures diferentes
- **Numeração sequencial**: `test_01` a `test_10` garante ordem lógica e facilita referência
- **Parametrização massiva**: usa `@pytest.mark.parametrize` sobre `all_ui_files` para cobertura automática dos 73 `.ui` sem código repetitivo
- **pytest-memray** sobre `tracemalloc`: conforme escolha do usuário — necessita instalação (`pip install pytest-memray`)
- **Offscreen obrigatório**: `QT_QPA_PLATFORM=offscreen` em todos os testes — sem necessidade de display
- **Fixtures reais + mocks**: `SessionState` e `SignalHub` instanciados de verdade para testes de integração, `MagicMock` para testes unitários de widgets isolados
- **Total estimado: ~770 testes** cobrindo os 10 eixos solicitados
