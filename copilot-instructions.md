<!-- GSD:project-start source:PROJECT.md -->
## Project

**Warp**

Warp e uma plataforma desktop para engenharia, operacao e analise de dados de sinais com arquitetura em camadas e extensibilidade por plugins. O produto oferece ingestao, processamento e visualizacao (2D/3D) em ambiente PySide6, com API local para automacao. Nesta iniciativa, o foco e consolidar a camada de UI e reduzir risco tecnico para aumentar estabilidade e velocidade de evolucao.

**Core Value:** Manter um fluxo estavel de ingestao -> processamento -> visualizacao para usuarios tecnicos sem regressao operacional.

### Constraints

- **Tech stack**: Manter Python + PySide6 + arquitetura plugin-based — preservar investimento tecnico e compatibilidade do ecossistema
- **Compatibilidade**: Nivel medio com comportamento legado — permitir melhorias com ajustes pontuais controlados
- **Entrega**: Migracao em ondas pequenas — reduzir risco operacional e facilitar rollback
- **Performance**: Evitar degradacao de tempo de resposta e memoria — risco mais critico definido para a fase
- **Operacao**: Sem interrupcao dos fluxos principais de engenharia/operacao/analise — proteger uso diario
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12 — All application code (confirmed via `.mypy_cache/3.12/` and `cpython-312` pyc files)
- YAML — Configuration files (`configs/platform.yaml`, `.platform_config/system/platform.yaml`, `.platform_config/user/default.yaml`)
- TOML — Project packaging (`platform_base/pyproject.toml`)
- JSON — Plugin manifests (`plugins/*/manifest.json`, `.platform_config/config_schema.json`)
## Runtime
- CPython 3.12 (Anaconda distribution — `base` conda environment active)
- Conda (base environment)
- Lockfile: Not detected (pixi/conda-lock not used)
## Frameworks
- PySide6 + shiboken6 — Primary desktop GUI framework (Qt6 Python bindings)
- FastAPI — Local REST API server (`platform_base/src/platform_base/api/server.py`)
- Starlette — FastAPI's ASGI foundation
- Pydantic v2 (pydantic + pydantic_core) — Data model validation and serialization (`platform_base/src/platform_base/core/models.py`)
- pytest 8.4.2 — Test runner (confirmed from `cpython-312-pytest-8.4.2.pyc` pyc files)
- pluggy — Plugin hook system for pytest and app plugin architecture
- pyproject.toml — Build and dependency manifest (`platform_base/pyproject.toml`, 13 709 bytes)
- mypy — Static type checking (`.mypy_cache/3.12/` present, extensive)
- ruff — Fast Python linter (`.ruff_cache/` present)
- compile_ui.py / generate_ui_files.py — Scripts to compile Qt `.ui` files → `*_ui.py` (`platform_base/scripts/`)
## Key Dependencies
- PySide6 — Qt6 desktop application framework (80+ generated UI files in `platform_base/src/platform_base/desktop/ui_files/`)
- shiboken6 — C++ binding layer for PySide6
- matplotlib — 2D charts and plots (`platform_base/src/platform_base/viz/figures_2d.py`, `heatmaps.py`)
- PyVista + vtkmodules — 3D mesh and volumetric visualization (`platform_base/src/platform_base/viz/figures_3d.py`)
- trimesh — 3D mesh geometry operations
- rtree — Spatial indexing for 3D support
- Bokeh — Potentially alternative/embedded web visualizations
- Dash — Potentially embedded interactive dashboards
- numpy — Numerical arrays and math
- scipy (inferred) — Signal filters, interpolation, calculus (`platform_base/src/platform_base/processing/filters.py`, `calculus.py`, `interpolation.py`)
- pint — Physical unit handling (`platform_base/src/platform_base/processing/units.py`)
- python-dateutil — Datetime parsing and timezone handling
- dask — Parallel/lazy computation for large datasets
- openpyxl (inferred from `utils/xlsx_to_csv.py`) — Excel `.xlsx` read/write
- pandas (inferred) — DataFrame operations on time-series data
- Sample data is `.xlsx` files (`platform_base/data/samples/*.xlsx`)
- Pillow (PIL) — Image processing
- OpenCV (cv2) — Video frame capture/export (`platform_base/src/platform_base/ui/video_export.py`)
- imageio — Image sequence I/O
- ZeroMQ (zmq) — High-performance messaging for real-time data streaming (`platform_base/src/platform_base/streaming/`)
- websocket — WebSocket client/server
- FastAPI + Uvicorn (inferred) — Local REST API (`platform_base/src/platform_base/api/`)
- Flask — Secondary/alternative web interface (present in mypy cache)
- requests — HTTP client calls
- httpx — Async HTTP client
- h11 / httpcore — Low-level HTTP protocol
- structlog — Structured logging (`platform_base/src/platform_base/core/structured_logger.py`)
- python-json-logger (pythonjsonlogger) — JSON log formatting
- rich — Rich terminal output for logs and CLI
- Custom disk cache (`platform_base/src/platform_base/caching/disk.py`)
- Custom memory cache (`platform_base/src/platform_base/caching/memory.py`)
- flexcache — Serialization cache
- diskcache or joblib (inferred behind caching layer)
- orjson — Fast JSON serialization
- tomli / tomli_w — TOML read/write
- ruamel.yaml — Round-trip YAML with comment preservation
- PyYAML (yaml) — Standard YAML
- pickle (stdlib) — Python object serialization
- Babel — i18n/l10n support (`platform_base/src/platform_base/utils/i18n.py`)
- prometheus_client — Prometheus metrics exposition
- cryptography / bcrypt — Secure credential handling
- overrides — Decorator to enforce method override contracts
- packaging — Version parsing
- importlib_metadata — Package metadata
## Configuration
- `.platform_config/user/default.yaml` — User-level defaults
- `.platform_config/system/platform.yaml` — System-level platform settings
- `.platform_config/config_schema.json` — JSON Schema for config validation
- `configs/platform.yaml` — Main platform configuration
- Managed by `platform_base/src/platform_base/core/config.py` and `core/config_manager.py`
- `platform_base/pyproject.toml` — Package metadata and build config (13 709 bytes)
- `.ruff_cache/` — Ruff linter cache
- `.mypy_cache/3.12/` — mypy type check cache
## Build & Packaging
- Source layout: `platform_base/src/platform_base/` (`src`-layout pattern)
- Entry points: `platform_base/run_app.py`, `platform_base/launch_app.py`
- UI compilation: Qt `.ui` → `*_ui.py` via `platform_base/scripts/compile_ui.py`
- Test runner: `platform_base/run_test_suite.py` and `platform_base/scripts/run_tests.py`
- Plugin packaging: individual directories under `platform_base/plugins/` with `manifest.json`
- Development: Windows (Anaconda base, VS Code)
- Runtime dependencies require Qt6 (PySide6), Python 3.12
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Code Style
- ruff 0.12.5 — fast linter (`.ruff_cache/0.12.5/` present); config in `platform_base/pyproject.toml`
- Applied to all `src/platform_base/` and test files
- mypy with extensive cache in `.mypy_cache/3.12/` — all source modules are type-checked
- `typing.Protocol` used for structural interfaces (not ABC); see `platform_base/src/platform_base/core/protocols.py`
- Pydantic v2 for runtime-validated data models; see `platform_base/src/platform_base/core/models.py`
- `overrides` package used to enforce `@override` contract on subclass methods
- Type hints required throughout (enforced by mypy)
- Use `Protocol` definitions (`core/protocols.py`) as function parameter types instead of concrete classes
- Pydantic `BaseModel` subclasses for all cross-boundary data structures (API, configs, operation parameters)
## Naming Conventions
- All source files: `snake_case.py` — universal throughout 160+ modules
- Generated Qt UI files: `<WidgetName>_ui.py` suffix (e.g., `aboutDialog_ui.py`, `dataPanel_ui.py`)
- Compiled from Qt Designer `.ui` files by `platform_base/scripts/compile_ui.py`
- All lowercase `snake_case/` (e.g., `signal_hub`, `crash_handler`, `dataset_store`)
- `PascalCase` — e.g., `SignalHub`, `Registry`, `Orchestrator`, `DatasetStore`, `PluginBase`, `BaseFigure`, `BaseWorker`, `DatasetModel`
- `snake_case` — standard Python convention
- `UPPER_SNAKE_CASE` — standard Python convention
- Named after what they describe with `Protocol` suffix or the class-like noun (e.g., `DatasetProtocol`, `WorkerProtocol`, `ProcessorProtocol`)
- `_single_leading_underscore` for internal/protected attributes and methods
- Current suite: `test_NN_descriptive_name.py` (two-digit number prefix, e.g., `test_01_ui_loading.py`)
- Legacy unit tests: `test_<module_name>.py` (e.g., `test_signal_hub_complete.py`)
- Plugin tests: `test_plugin.py` co-located in `plugins/<name>/`
## Patterns
- `core/signal_hub.py` — application-wide pub/sub; decouples producers from consumers
- `ui/signal_hub.py` — UI-scoped variant
- Components subscribe at init, publish domain events (e.g., `dataset_added`, `result_ready`)
- Prefer `SignalHub` over direct Qt signal wiring for cross-layer communication
- `core/protocols.py` defines `typing.Protocol` interfaces for all major subsystems
- Use protocols as type hints to enable duck-typing and testability without hard inheritance chains
- Examples: `DatasetProtocol`, `PluginProtocol`, `ProcessorProtocol`, `WorkerProtocol`
- `desktop/workers/base_worker.py` — `BaseWorker(QThread)` base class
- All long-running operations run in a worker, never on the main GUI thread
- Workers emit Qt signals for `progress`, `result_ready`, and `error` back to the UI thread
- Subclass `BaseWorker` and implement `run()` for new operations
- All cross-layer DTOs and config structures use Pydantic v2 `BaseModel`
- Defined in `core/models.py`; shared across all layers
- Provides serialization, validation, and schema generation for free
- `ui/mixins.py` and `ui/ui_loader_mixin.py` for composable UI behaviors
- Mixins provide reusable capabilities (dynamic `.ui` file loading, common callbacks) without deep inheritance
- `plugins/_base.py` — `PluginBase` + `pluggy` hookspec
- Each plugin: `plugins/<name>/manifest.json` + `plugins/<name>/plugin.py`
- Lifecycle: `load()`, `unload()`, `get_operations()`, `get_ui_components()`
- Discovery via `core/registry.py` at startup
- `core/registry.py` — central catalog of all registered plugins and components
- Enables listing and instantiation by name without hard imports
- `ui/undo_redo.py` — command pattern for reversible user operations
- `profiling/decorators.py` — function-level timing decorators
- Applied selectively to hot-path processing functions
- Two-tier: `caching/memory.py` (in-memory LRU) + `caching/disk.py` (persistent)
- Processing results are cached by `processing/` modules after first computation
- `processing/lazy_loading.py` — defers data materialization until first access for large datasets
## Error Handling
- Raise specific subclasses (`DataError`, `ProcessingError`) at the source; never re-raise bare `Exception`
- Catch at the boundary (worker, API endpoint, dialog) and convert to user-facing messages
- Workers emit an `error` signal instead of propagating exceptions across thread boundaries
- `core/crash_handler.py` installs a top-level `sys.excepthook`
- Uncaught exceptions are logged, a crash report is written, and a user dialog is shown
- `utils/safe_eval.py` wraps user-supplied math expressions to prevent arbitrary code execution
## Logging
- Always use keyword arguments (structured fields), never positional string formatting
- Log at module level (`get_logger(__name__)`) — one logger per module
- Use `rich` terminal output for developer-facing CLI / debug runs
## Comments & Documentation
- Required on public classes and public methods
- Style: not explicitly confirmed (mypy + ruff present; Google or NumPy style expected)
- Use for non-obvious logic only (algorithm choices, workaround explanations)
- Portuguese or English both appear in this codebase; prefer English for code-level comments
- Preferred over docstring parameter descriptions; enforced by mypy
## Import Organization
## Module Design
- `__init__.py` files expose the public API of each package
- Internal modules use `_` prefix on private helpers
- Do not re-export everything from `__init__.py` — only key public symbols
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Strict layer separation: core → data/processing → visualization → UI → API
- Signal-hub pattern for decoupled inter-component communication (not Qt signals alone)
- Plugin discovery via `pluggy` + a central `registry.py`
- Dual UI stacks: legacy `desktop/` and current `ui/` (migration in progress)
- Background workers for all long-running operations (keeps GUI responsive)
- Local REST API (`fastapi`) running alongside the desktop application
## Layers
- Purpose: Application backbone — orchestration, configuration, state, event routing
- Contains: `orchestrator.py`, `registry.py`, `signal_hub.py`, `models.py`, `protocols.py`, `dataset_store.py`, `session_state.py`, `config.py`, `config_manager.py`, `memory_manager.py`, `auto_save.py`, `crash_handler.py`, `structured_logger.py`
- Depends on: nothing above itself (foundation layer)
- Used by: all other layers
- Purpose: File ingestion with format detection, schema inference and validation
- Contains: `loader.py`, `encoding_detector.py`, `schema_detector.py`, `validator.py`, `integrity_checker.py`
- Depends on: `core/`
- Used by: `desktop/workers/`, `ui/workers/`
- Purpose: Signal processing algorithms
- Contains: `filters.py`, `smoothing.py`, `calculus.py`, `downsampling.py`, `interpolation.py`, `synchronization.py`, `timebase.py`, `units.py`, `analysis.py`, `lazy_loading.py`
- Depends on: `core/`, `caching/`
- Used by: `desktop/workers/processing_worker.py`, `ui/workers/operation_workers.py`, plugins
- Purpose: Two-tier caching (in-memory + disk) for computed results
- Contains: `memory.py`, `disk.py`
- Depends on: `core/`
- Used by: `processing/`, `viz/`
- Purpose: Real-time data ingestion via ZeroMQ messaging
- Contains: `filters.py`, `temporal_sync.py`
- Depends on: `core/`, `processing/`
- Used by: `ui/panels/streaming_panel.py`, `viz/streaming.py`
- Purpose: Rendering layer — 2D charts, 3D meshes, heatmaps, multi-panel views
- Contains: `base.py`, `figures_2d.py`, `figures_3d.py`, `heatmaps.py`, `multipanel.py`, `multi_canvas_plot.py`, `multi_y_axis.py`, `computation_engine.py`, `streaming.py`, `state_cube.py`, `hue_coordinator.py`, `datetime_axis.py`, `config.py`, `comprehensive_context_menu.py`
- Depends on: `core/`, `processing/`, `caching/`
- Used by: `ui/panels/viz_panel.py`, `desktop/widgets/viz_panel.py`
- Purpose: Original PySide6 UI layer — fully functional but superseded by `ui/`
- Contains: `app.py`, `main_window.py`, `session_state.py`, `signal_hub.py`, sub-packages: `dialogs/`, `menus/`, `models/`, `selection/`, `widgets/`, `workers/`, `ui_files/`
- Depends on: `core/`, `viz/`, `processing/`, `io/`, `caching/`
- Status: Legacy — `UI_MIGRATION.md` documents active migration to `ui/`
- Purpose: Rebuilt PySide6 UI layer with automated `.ui` file loading, themes, accessibility, undo/redo
- Contains: `app.py`, `main_window.py`, `main_window_unified.py`, `state.py`, `signal_hub.py`, `themes.py`, `shortcuts.py`, `accessibility.py`, `callbacks.py`, `mixins.py`, `layout.py`, `undo_redo.py`, `ui_loader_mixin.py`, sub-packages: `panels/`, `dialogs/`, `workers/`
- Depends on: `core/`, `viz/`, `processing/`, `io/`, `caching/`, `streaming/`
- Used by: entry point scripts
- Purpose: Local FastAPI REST server running in-process alongside the desktop app
- Contains: `server.py`, `endpoints.py`
- Depends on: `core/`, `processing/`
- Used by: external scripts or plugins that need programmatic access
- Purpose: Usage telemetry and metrics
- Contains: `telemetry.py`
- Depends on: `core/`
- Purpose: Performance instrumentation via decorators
- Contains: `decorators.py`, `profiler.py`, `reports.py`, `setup.py`
- Used by: any module needing perf measurement; integrates with `test_profiling/` reports
- Purpose: Cross-cutting helpers
- Contains: `errors.py`, `logging.py`, `validation.py`, `serialization.py`, `ids.py`, `i18n.py`, `a11y_helpers.py`, `memory_monitor.py`, `resource_manager.py`, `safe_eval.py`, `xlsx_to_csv.py`
- Depends on: nothing (leaf utilities)
## Entry Points
- Triggers: direct Python execution (`python launch_app.py`)
- Responsibilities: bootstrap Qt application, instantiate `core/orchestrator.py`, start `api/server.py`, show main window from `ui/app.py`
- Triggers: alternative launcher (simpler path for development)
- Responsibilities: similar to `launch_app.py`, used in development / CI
- Triggers: workaround launcher when spacer/layout bugs prevent normal start
- Responsibilities: initializes app with known-good widget spacers (`fix_spacers.py`, `check_spacers.py`)
- Triggers: diagnostic / test execution
- Responsibilities: bring up application with debug instrumentation
## Core Abstractions
- Purpose: Central controller that wires all subsystems together at startup
- Initializes: registry, signal hub, dataset store, config, session state, workers
- There is one Orchestrator instance per application session
- Purpose: Python `typing.Protocol` interfaces for structural subtyping
- Examples: `DatasetProtocol`, `PluginProtocol`, `ProcessorProtocol`, `WorkerProtocol`
- Enables type-safe dependency injection without inheritance
- Purpose: Validated, serializable data structures shared across all layers
- Examples: dataset descriptors, operation parameters, configuration schemas
- Uses Pydantic v2
- Purpose: Application-wide event bus; decouples producers from consumers
- Pattern: subscribe/publish; replicated in `ui/signal_hub.py` for UI-specific events
- All inter-layer communication goes through the hub rather than direct method calls
- Purpose: Central catalog of plugins and components
- Discovers plugins in `plugins/` directory via `pluggy` hooks
- Provides lookup by name/type for the orchestrator and UI
- Purpose: In-memory store for all open datasets; single source of truth
- Emits events via `SignalHub` when datasets are added, updated, or removed
- Purpose: Base class (and `pluggy` hookspec) for all plugins
- Defines plugin lifecycle: `load()`, `unload()`, `get_operations()`, `get_ui_components()`
- Each concrete plugin subclasses `PluginBase` and registers hooks
- Purpose: Abstract visualization component; all chart types inherit from here
- Provides common interface: `render()`, `update()`, `reset()`, `get_config()`
- Purpose: Qt `QThread`-based worker base class for non-blocking operations
- Pattern: emit progress/result signals back to UI thread; all heavy work runs in subclass `run()`
## Data Flow
## Plugin System
```
```
- `core/registry.py` scans `plugins/` directory for `manifest.json` files
- Instantiates the class specified in `manifest.json`'s `entry_point` field
- Hooks registered via `pluggy` hookspec from `plugins/_base.py`
- `plugin_loaded(plugin)` — fired after successful registration
- Operations returned by `plugin.get_operations()` appear in the UI
- UI components returned by `plugin.get_ui_components()` are injected into panels
- `dtw_plugin` — Dynamic Time Warping for signal synchronization
- `advanced_sync` — Advanced multi-signal synchronization strategies
## Error Handling
- `core/crash_handler.py` — top-level `sys.excepthook` replacement; logs crash + shows user-facing dialog; writes crash report
- `utils/errors.py` — custom exception hierarchy (`PlatformError`, `DataError`, `ProcessingError`, etc.)
- Workers catch exceptions internally and emit an `error` signal to the UI thread (never crash the main thread)
- `utils/safe_eval.py` — sandboxed expression evaluation to prevent injection from user-entered filter expressions
## State Management
- `core/session_state.py` — persistent session data (open files, view settings, last operation) serialized to `.platform_config/user/`
- `desktop/session_state.py` / `ui/state.py` — transient UI state (panel layout, selection, zoom level)
- `ui/undo_redo.py` — command-pattern undo/redo stack; each operation creates a reversible command object
- `core/config.py` — typed config object (Pydantic model)
- `core/config_manager.py` — loads/saves/merges system + user YAML configs
- Schema validated against `.platform_config/config_schema.json`
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
