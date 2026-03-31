# Architecture

**Analysis Date:** 2026-03-31

## Pattern Overview

**Overall:** Plugin-based, layered desktop application with a signal-driven event bus

**Key Characteristics:**
- Strict layer separation: core → data/processing → visualization → UI → API
- Signal-hub pattern for decoupled inter-component communication (not Qt signals alone)
- Plugin discovery via `pluggy` + a central `registry.py`
- Dual UI stacks: legacy `desktop/` and current `ui/` (migration in progress)
- Background workers for all long-running operations (keeps GUI responsive)
- Local REST API (`fastapi`) running alongside the desktop application

---

## Layers

**Core (`platform_base/src/platform_base/core/`):**
- Purpose: Application backbone — orchestration, configuration, state, event routing
- Contains: `orchestrator.py`, `registry.py`, `signal_hub.py`, `models.py`, `protocols.py`, `dataset_store.py`, `session_state.py`, `config.py`, `config_manager.py`, `memory_manager.py`, `auto_save.py`, `crash_handler.py`, `structured_logger.py`
- Depends on: nothing above itself (foundation layer)
- Used by: all other layers

**I/O (`platform_base/src/platform_base/io/`):**
- Purpose: File ingestion with format detection, schema inference and validation
- Contains: `loader.py`, `encoding_detector.py`, `schema_detector.py`, `validator.py`, `integrity_checker.py`
- Depends on: `core/`
- Used by: `desktop/workers/`, `ui/workers/`

**Processing (`platform_base/src/platform_base/processing/`):**
- Purpose: Signal processing algorithms
- Contains: `filters.py`, `smoothing.py`, `calculus.py`, `downsampling.py`, `interpolation.py`, `synchronization.py`, `timebase.py`, `units.py`, `analysis.py`, `lazy_loading.py`
- Depends on: `core/`, `caching/`
- Used by: `desktop/workers/processing_worker.py`, `ui/workers/operation_workers.py`, plugins

**Caching (`platform_base/src/platform_base/caching/`):**
- Purpose: Two-tier caching (in-memory + disk) for computed results
- Contains: `memory.py`, `disk.py`
- Depends on: `core/`
- Used by: `processing/`, `viz/`

**Streaming (`platform_base/src/platform_base/streaming/`):**
- Purpose: Real-time data ingestion via ZeroMQ messaging
- Contains: `filters.py`, `temporal_sync.py`
- Depends on: `core/`, `processing/`
- Used by: `ui/panels/streaming_panel.py`, `viz/streaming.py`

**Visualization (`platform_base/src/platform_base/viz/`):**
- Purpose: Rendering layer — 2D charts, 3D meshes, heatmaps, multi-panel views
- Contains: `base.py`, `figures_2d.py`, `figures_3d.py`, `heatmaps.py`, `multipanel.py`, `multi_canvas_plot.py`, `multi_y_axis.py`, `computation_engine.py`, `streaming.py`, `state_cube.py`, `hue_coordinator.py`, `datetime_axis.py`, `config.py`, `comprehensive_context_menu.py`
- Depends on: `core/`, `processing/`, `caching/`
- Used by: `ui/panels/viz_panel.py`, `desktop/widgets/viz_panel.py`

**Desktop UI — Legacy (`platform_base/src/platform_base/desktop/`):**
- Purpose: Original PySide6 UI layer — fully functional but superseded by `ui/`
- Contains: `app.py`, `main_window.py`, `session_state.py`, `signal_hub.py`, sub-packages: `dialogs/`, `menus/`, `models/`, `selection/`, `widgets/`, `workers/`, `ui_files/`
- Depends on: `core/`, `viz/`, `processing/`, `io/`, `caching/`
- Status: Legacy — `UI_MIGRATION.md` documents active migration to `ui/`

**UI — Current (`platform_base/src/platform_base/ui/`):**
- Purpose: Rebuilt PySide6 UI layer with automated `.ui` file loading, themes, accessibility, undo/redo
- Contains: `app.py`, `main_window.py`, `main_window_unified.py`, `state.py`, `signal_hub.py`, `themes.py`, `shortcuts.py`, `accessibility.py`, `callbacks.py`, `mixins.py`, `layout.py`, `undo_redo.py`, `ui_loader_mixin.py`, sub-packages: `panels/`, `dialogs/`, `workers/`
- Depends on: `core/`, `viz/`, `processing/`, `io/`, `caching/`, `streaming/`
- Used by: entry point scripts

**API (`platform_base/src/platform_base/api/`):**
- Purpose: Local FastAPI REST server running in-process alongside the desktop app
- Contains: `server.py`, `endpoints.py`
- Depends on: `core/`, `processing/`
- Used by: external scripts or plugins that need programmatic access

**Analytics (`platform_base/src/platform_base/analytics/`):**
- Purpose: Usage telemetry and metrics
- Contains: `telemetry.py`
- Depends on: `core/`

**Profiling (`platform_base/src/platform_base/profiling/`):**
- Purpose: Performance instrumentation via decorators
- Contains: `decorators.py`, `profiler.py`, `reports.py`, `setup.py`
- Used by: any module needing perf measurement; integrates with `test_profiling/` reports

**Utils (`platform_base/src/platform_base/utils/`):**
- Purpose: Cross-cutting helpers
- Contains: `errors.py`, `logging.py`, `validation.py`, `serialization.py`, `ids.py`, `i18n.py`, `a11y_helpers.py`, `memory_monitor.py`, `resource_manager.py`, `safe_eval.py`, `xlsx_to_csv.py`
- Depends on: nothing (leaf utilities)

---

## Entry Points

**`platform_base/launch_app.py`:**
- Triggers: direct Python execution (`python launch_app.py`)
- Responsibilities: bootstrap Qt application, instantiate `core/orchestrator.py`, start `api/server.py`, show main window from `ui/app.py`

**`platform_base/run_app.py`:**
- Triggers: alternative launcher (simpler path for development)
- Responsibilities: similar to `launch_app.py`, used in development / CI

**`platform_base/fixed_launch.py`:**
- Triggers: workaround launcher when spacer/layout bugs prevent normal start
- Responsibilities: initializes app with known-good widget spacers (`fix_spacers.py`, `check_spacers.py`)

**`platform_base/debug_launch.py` / `platform_base/test_launch.py`:**
- Triggers: diagnostic / test execution
- Responsibilities: bring up application with debug instrumentation

---

## Core Abstractions

**`core/orchestrator.py` — `Orchestrator`:**
- Purpose: Central controller that wires all subsystems together at startup
- Initializes: registry, signal hub, dataset store, config, session state, workers
- There is one Orchestrator instance per application session

**`core/protocols.py` — Protocol definitions:**
- Purpose: Python `typing.Protocol` interfaces for structural subtyping
- Examples: `DatasetProtocol`, `PluginProtocol`, `ProcessorProtocol`, `WorkerProtocol`
- Enables type-safe dependency injection without inheritance

**`core/models.py` — Pydantic models:**
- Purpose: Validated, serializable data structures shared across all layers
- Examples: dataset descriptors, operation parameters, configuration schemas
- Uses Pydantic v2

**`core/signal_hub.py` — `SignalHub`:**
- Purpose: Application-wide event bus; decouples producers from consumers
- Pattern: subscribe/publish; replicated in `ui/signal_hub.py` for UI-specific events
- All inter-layer communication goes through the hub rather than direct method calls

**`core/registry.py` — `Registry`:**
- Purpose: Central catalog of plugins and components
- Discovers plugins in `plugins/` directory via `pluggy` hooks
- Provides lookup by name/type for the orchestrator and UI

**`core/dataset_store.py` — `DatasetStore`:**
- Purpose: In-memory store for all open datasets; single source of truth
- Emits events via `SignalHub` when datasets are added, updated, or removed

**`plugins/_base.py` — `PluginBase`:**
- Purpose: Base class (and `pluggy` hookspec) for all plugins
- Defines plugin lifecycle: `load()`, `unload()`, `get_operations()`, `get_ui_components()`
- Each concrete plugin subclasses `PluginBase` and registers hooks

**`viz/base.py` — `BaseFigure` / `BaseRenderer`:**
- Purpose: Abstract visualization component; all chart types inherit from here
- Provides common interface: `render()`, `update()`, `reset()`, `get_config()`

**`desktop/workers/base_worker.py` / `ui/workers/` — `BaseWorker`:**
- Purpose: Qt `QThread`-based worker base class for non-blocking operations
- Pattern: emit progress/result signals back to UI thread; all heavy work runs in subclass `run()`

---

## Data Flow

**File Load Flow:**
1. User triggers upload dialog (`ui/panels/data_panel.py` or `desktop/dialogs/upload_dialog.py`)
2. `io/loader.py` detects encoding (`encoding_detector.py`), infers schema (`schema_detector.py`), validates (`validator.py`), checks integrity (`integrity_checker.py`)
3. Validated DataFrame → `core/dataset_store.py` emits `dataset_added` signal via `core/signal_hub.py`
4. `ui/panels/viz_panel.py` receives signal → delegates to `viz/figures_2d.py` to render
5. `ui/panels/data_panel.py` / `desktop/widgets/data_panel.py` updates table view via `desktop/models/dataset_model.py`

**Operation / Processing Flow:**
1. User selects operation in `ui/panels/operations_panel.py`, fills dialog (`ui/operation_dialogs.py`)
2. Dialog dispatches work to `desktop/workers/processing_worker.py` (or `ui/workers/operation_workers.py`)
3. Worker calls appropriate `processing/` module (`filters.py`, `smoothing.py`, `calculus.py`, etc.)
4. Results cached by `caching/disk.py` + `caching/memory.py`
5. Worker emits `result_ready` signal → `dataset_store` updated → viz/panels re-render

**Streaming Flow:**
1. External source sends data via ZeroMQ
2. `streaming/` layer receives, applies `streaming/filters.py`, synchronizes with `streaming/temporal_sync.py`
3. Buffered data published via `core/signal_hub.py`
4. `ui/panels/streaming_panel.py` + `viz/streaming.py` display in near-real-time

**Plugin Operation Flow:**
1. `core/registry.py` discovers plugin in `plugins/<name>/` on startup
2. Plugin registers its operations and UI components via `pluggy` hooks
3. `ui/panels/operations_panel.py` lists plugin operations alongside built-in ones
4. On invocation, plugin `run()` receives dataset from `dataset_store`, returns result dataset

---

## Plugin System

**Location:** `platform_base/plugins/<plugin_name>/`

**Structure per plugin:**
```
plugins/
  dtw_plugin/
    manifest.json   ← metadata: name, version, description, entry_point
    plugin.py       ← subclass of plugins/_base.py PluginBase
    README.md
    test_plugin.py
  advanced_sync/
    manifest.json
    __init__.py
    dtw_plugin.py   ← implementation
```

**Discovery mechanism:**
- `core/registry.py` scans `plugins/` directory for `manifest.json` files
- Instantiates the class specified in `manifest.json`'s `entry_point` field
- Hooks registered via `pluggy` hookspec from `plugins/_base.py`

**Hook lifecycle:**
- `plugin_loaded(plugin)` — fired after successful registration
- Operations returned by `plugin.get_operations()` appear in the UI
- UI components returned by `plugin.get_ui_components()` are injected into panels

**Built-in plugins:**
- `dtw_plugin` — Dynamic Time Warping for signal synchronization
- `advanced_sync` — Advanced multi-signal synchronization strategies

---

## Error Handling

**Strategy:** Structured exception hierarchy with centralized crash handling

**Patterns:**
- `core/crash_handler.py` — top-level `sys.excepthook` replacement; logs crash + shows user-facing dialog; writes crash report
- `utils/errors.py` — custom exception hierarchy (`PlatformError`, `DataError`, `ProcessingError`, etc.)
- Workers catch exceptions internally and emit an `error` signal to the UI thread (never crash the main thread)
- `utils/safe_eval.py` — sandboxed expression evaluation to prevent injection from user-entered filter expressions

---

## State Management

**Session State:**
- `core/session_state.py` — persistent session data (open files, view settings, last operation) serialized to `.platform_config/user/`
- `desktop/session_state.py` / `ui/state.py` — transient UI state (panel layout, selection, zoom level)

**Undo/Redo:**
- `ui/undo_redo.py` — command-pattern undo/redo stack; each operation creates a reversible command object

**Configuration:**
- `core/config.py` — typed config object (Pydantic model)
- `core/config_manager.py` — loads/saves/merges system + user YAML configs
- Schema validated against `.platform_config/config_schema.json`

---

## Cross-Cutting Concerns

**Logging:** `core/structured_logger.py` wraps `structlog`; all modules obtain a logger from this; JSON output compatible with `pythonjsonlogger`

**Validation:** `utils/validation.py` + Pydantic models at I/O boundaries; `io/validator.py` for dataset-level rules

**Internationalization:** `utils/i18n.py` wraps `Babel`; all user-facing strings routed through translation

**Accessibility:** `ui/accessibility.py` + `utils/a11y_helpers.py` for keyboard nav and screen reader support

**Metrics:** `analytics/telemetry.py` + `prometheus_client` for usage metrics

---

*Architecture analysis: 2026-03-31*
