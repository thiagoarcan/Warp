# Codebase Structure

**Analysis Date:** 2026-03-31

## Directory Layout

```
platform_base/                        ← project root (Python package)
├── launch_app.py                     ← primary entry point
├── run_app.py                        ← development entry point
├── fixed_launch.py                   ← workaround launcher (spacer bugs)
├── debug_launch.py                   ← diagnostic launcher
├── test_launch.py                    ← test harness launcher
├── pyproject.toml                    ← package metadata and build config
├── README.md                         ← project documentation
├── run_test_suite.py                 ← run all tests
├── configs/
│   └── platform.yaml                ← main platform configuration
├── .platform_config/
│   ├── config_schema.json           ← JSON Schema for config validation
│   ├── system/platform.yaml         ← system-level defaults
│   └── user/default.yaml            ← user-level defaults
├── data/
│   └── samples/                     ← sample .xlsx datasets (BAR_*.xlsx, PLN_*.xlsx)
├── docs/
│   ├── API_REFERENCE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PLUGIN_DEVELOPMENT.md
│   ├── TROUBLESHOOTING.md
│   ├── UI_MIGRATION.md              ← documents desktop/ → ui/ migration
│   ├── USER_GUIDE.md
│   ├── USER_MANUAL.md
│   ├── examples/                    ← code examples (disk_cache, cache_integration)
│   ├── reports/
│   └── ux_ui_redesign/
├── examples/
│   ├── data_panel_refactored_example.py
│   └── README.md
├── plugins/
│   ├── _base.py                     ← PluginBase class + pluggy hookspec
│   ├── README.md
│   ├── dtw_plugin/                  ← Dynamic Time Warping plugin
│   │   ├── manifest.json
│   │   ├── plugin.py
│   │   ├── test_plugin.py
│   │   └── README.md
│   └── advanced_sync/               ← advanced synchronization plugin
│       ├── manifest.json
│       ├── __init__.py
│       └── dtw_plugin.py
├── scripts/
│   ├── compile_ui.py                ← compile Qt .ui files → *_ui.py
│   ├── generate_ui_files.py         ← generate UI file skeletons
│   ├── validate_all.py              ← full validation suite
│   ├── validate_performance.py
│   ├── validate_ui_files.py
│   ├── validate_ui_migration.py
│   ├── run_tests.py
│   ├── project_status.py
│   └── ...
├── src/
│   └── platform_base/               ← installable package (src-layout)
│       ├── __init__.py
│       ├── analytics/               ← telemetry
│       ├── api/                     ← FastAPI REST server
│       ├── caching/                 ← memory + disk cache
│       ├── core/                    ← application backbone
│       ├── desktop/                 ← legacy PySide6 UI layer
│       ├── io/                      ← file I/O and format detection
│       ├── processing/              ← signal processing algorithms
│       ├── profiling/               ← performance instrumentation
│       ├── streaming/               ← ZeroMQ real-time data
│       ├── ui/                      ← current PySide6 UI layer
│       ├── utils/                   ← shared utilities
│       └── viz/                     ← visualization rendering
├── tests/
│   ├── automated/                   ← numbered test suite (01-10)
│   ├── fixtures/                    ← shared test data and helpers
│   └── _legacy/                     ← archived legacy tests
├── profiling_reports/               ← saved profiling output
└── test_profiling/                  ← profiling benchmark snapshots
```

---

## Key Files

**Entry Points:**
- `platform_base/launch_app.py` — primary app launcher; start here
- `platform_base/run_app.py` — development/alternate launcher
- `platform_base/run_test_suite.py` — runs the full pytest suite

**Configuration:**
- `platform_base/configs/platform.yaml` — main platform config (runtime)
- `platform_base/.platform_config/config_schema.json` — config validation schema
- `platform_base/.platform_config/system/platform.yaml` — system defaults
- `platform_base/.platform_config/user/default.yaml` — user defaults
- `platform_base/pyproject.toml` — package metadata, dependencies, tool config

**Core Logic:**
- `src/platform_base/core/orchestrator.py` — application bootstrap and wiring
- `src/platform_base/core/registry.py` — plugin/component registry
- `src/platform_base/core/signal_hub.py` — application event bus
- `src/platform_base/core/models.py` — Pydantic data models (shared DTOs)
- `src/platform_base/core/protocols.py` — Protocol interfaces for structural subtyping
- `src/platform_base/core/dataset_store.py` — in-memory dataset catalog
- `src/platform_base/core/config_manager.py` — config load/save/merge

**Plugin System:**
- `plugins/_base.py` — `PluginBase` base class + pluggy hookspec definitions
- `plugins/<name>/manifest.json` — plugin metadata and entry point declaration
- `plugins/<name>/plugin.py` — concrete plugin implementation

**UI (Current):**
- `src/platform_base/ui/app.py` — Qt application setup for current UI
- `src/platform_base/ui/main_window.py` — main application window (current)
- `src/platform_base/ui/main_window_unified.py` — unified main window variant
- `src/platform_base/ui/signal_hub.py` — UI-specific event bus
- `src/platform_base/ui/state.py` — transient UI state
- `src/platform_base/ui/themes.py` — theme definitions
- `src/platform_base/ui/undo_redo.py` — command-pattern undo/redo
- `src/platform_base/ui/ui_loader_mixin.py` — dynamic `.ui` file loader mixin

**UI Panels (Current):**
- `src/platform_base/ui/panels/viz_panel.py` — visualization panel
- `src/platform_base/ui/panels/data_panel.py` — dataset list and table view
- `src/platform_base/ui/panels/operations_panel.py` — operation list and triggering
- `src/platform_base/ui/panels/streaming_panel.py` — live streaming display
- `src/platform_base/ui/panels/results_panel.py` — operation results
- `src/platform_base/ui/panels/activity_log_panel.py` — structured log viewer
- `src/platform_base/ui/panels/resource_monitor_panel.py` — memory/CPU monitor

**UI (Legacy — `desktop/`):**
- `src/platform_base/desktop/app.py` — Qt application setup for legacy UI
- `src/platform_base/desktop/main_window.py` — legacy main window
- `src/platform_base/desktop/widgets/` — legacy panel/widget implementations
- `src/platform_base/desktop/ui_files/` — compiled Qt UI files (70+ `*_ui.py`)

**Visualization:**
- `src/platform_base/viz/figures_2d.py` — 2D line/scatter/bar charts (matplotlib)
- `src/platform_base/viz/figures_3d.py` — 3D mesh and volumetric visualization (PyVista)
- `src/platform_base/viz/heatmaps.py` — heatmap rendering
- `src/platform_base/viz/multipanel.py` — synchronized multi-panel layouts
- `src/platform_base/viz/streaming.py` — real-time streaming visualization
- `src/platform_base/viz/computation_engine.py` — heavy computation off main thread

**Processing:**
- `src/platform_base/processing/filters.py` — band-pass, high-pass, low-pass, notch filters
- `src/platform_base/processing/smoothing.py` — moving average and other smoothing
- `src/platform_base/processing/calculus.py` — derivatives and integrals
- `src/platform_base/processing/synchronization.py` — multi-signal time alignment
- `src/platform_base/processing/downsampling.py` — dataset downsampling
- `src/platform_base/processing/interpolation.py` — resampling and gap filling
- `src/platform_base/processing/units.py` — physical unit conversion (pint)

**I/O:**
- `src/platform_base/io/loader.py` — main file loader (xlsx, csv, parquet, etc.)
- `src/platform_base/io/schema_detector.py` — automatic column schema inference
- `src/platform_base/io/encoding_detector.py` — text encoding detection
- `src/platform_base/io/validator.py` — dataset rule validation
- `src/platform_base/io/integrity_checker.py` — file/data integrity checks

**Background Workers:**
- `src/platform_base/desktop/workers/base_worker.py` — QThread base worker
- `src/platform_base/desktop/workers/processing_worker.py` — data processing
- `src/platform_base/desktop/workers/export_worker.py` — file/video export
- `src/platform_base/ui/workers/operation_workers.py` — current UI operation workers
- `src/platform_base/ui/workers/file_worker.py` — async file loading

**Utils:**
- `src/platform_base/utils/errors.py` — custom exception hierarchy
- `src/platform_base/utils/safe_eval.py` — sandboxed expression evaluation
- `src/platform_base/utils/serialization.py` — JSON/pickle helpers
- `src/platform_base/utils/validation.py` — reusable validation helpers
- `src/platform_base/utils/i18n.py` — internationalization (Babel)

**Build / Dev Scripts:**
- `scripts/compile_ui.py` — compiles Qt `.ui` files to `*_ui.py` modules
- `scripts/generate_ui_files.py` — scaffolds new UI file pairs
- `scripts/validate_all.py` — runs all validation checks
- `scripts/run_tests.py` — convenient test runner wrapper

---

## Naming Conventions

**Files:**
- `snake_case.py` — all Python modules
- `*_ui.py` — generated Qt UI files (compiled from `.ui` → placed in `desktop/ui_files/` or `ui/ui_files/`)
- `*_worker.py` — background worker modules
- `*_panel.py` — UI panel modules
- `*_dialog.py` — dialog modules
- `*_widget.py` — reusable widget modules
- `test_*.py` — pytest test files
- `conftest.py` — pytest fixtures

**Classes:**
- `PascalCase` for all classes
- `*Worker` suffix for QThread workers (e.g., `ProcessingWorker`, `ExportWorker`)
- `*Panel` suffix for dockable panel widgets (e.g., `VizPanel`, `DataPanel`)
- `*Dialog` suffix for modal dialogs (e.g., `FilterDialog`, `SettingsDialog`)
- `*Widget` suffix for reusable sub-components (e.g., `SelectionWidget`, `SyncSettingsWidget`)
- `*Model` suffix for Qt item models (e.g., `DatasetModel`)
- `*Manager` suffix for stateful service classes (e.g., `ConfigManager`, `SelectionManager`, `DetachedManager`)
- `*Hub` suffix for event bus classes (e.g., `SignalHub`)
- `*Store` suffix for in-memory stores (e.g., `DatasetStore`)
- `*Protocol` suffix for `typing.Protocol` interface types

**Directories:**
- `snake_case/` for all sub-packages
- `_legacy/` prefix for deprecated/archived directories (tests/_legacy/)
- `.platform_config/` for runtime configuration store

---

## Module Organization

**Package layout (src layout):**
```
platform_base/src/platform_base/
├── core/        ← foundation (no inward dependencies)
├── utils/       ← leaf utilities (no inward dependencies)
├── io/          ← depends on core
├── caching/     ← depends on core
├── processing/  ← depends on core, caching
├── streaming/   ← depends on core, processing
├── viz/         ← depends on core, processing, caching
├── analytics/   ← depends on core
├── profiling/   ← depends on nothing (aspect-oriented)
├── api/         ← depends on core, processing
├── desktop/     ← depends on everything above (legacy UI)
└── ui/          ← depends on everything above (current UI)
```

**Dependency rule:** Lower layers must not import from higher layers. `core/` and `utils/` have zero upward dependencies.

**Dual UI stacks:**
- `desktop/` — legacy Qt UI; maintained for compatibility; do NOT add new features here
- `ui/` — current UI; all new UI code goes here; see `docs/UI_MIGRATION.md` for migration guide

**Worker pattern:**
- Separate worker classes in `desktop/workers/` (legacy) and `ui/workers/` (current)
- Workers live alongside the UI layer that spawns them, not in `processing/`

---

## Where to Add New Code

**New signal processing algorithm:**
- Implementation: `src/platform_base/processing/<algorithm>.py`
- Tests: `tests/automated/` or new file following `test_NN_<description>.py` pattern

**New visualization type:**
- Implementation: `src/platform_base/viz/` (create new module or extend `figures_2d.py` / `figures_3d.py`)
- Register in `viz/__init__.py`

**New UI panel:**
- Implementation: `src/platform_base/ui/panels/<name>_panel.py`
- Qt UI file (if needed): design in Qt Designer → `scripts/compile_ui.py` → `desktop/ui_files/<name>_ui.py`
- Tests: `tests/automated/`

**New plugin:**
- Create: `plugins/<plugin_name>/` with `manifest.json`, `plugin.py` (subclass `plugins/_base.py:PluginBase`), `test_plugin.py`
- Follow: `docs/PLUGIN_DEVELOPMENT.md`

**New configuration key:**
- Add to Pydantic model in `src/platform_base/core/models.py` or `core/config.py`
- Update schema: `.platform_config/config_schema.json`
- Update defaults: `.platform_config/system/platform.yaml` and/or `configs/platform.yaml`

**New background operation:**
- Worker class: `src/platform_base/ui/workers/operation_workers.py` (subclass `desktop/workers/base_worker.py:BaseWorker`)
- Processing logic: `src/platform_base/processing/` (keep worker thin)

**New utility helper:**
- Shared helper: `src/platform_base/utils/` (pick appropriate existing module or create new one)
- UI-specific helper: `src/platform_base/ui/mixins.py` or new file in `ui/`

---

## Special Directories

**`platform_base/.platform_config/`:**
- Purpose: Runtime config store (system defaults + user overrides)
- Generated: Partially (user config created on first run)
- Committed: Yes (system defaults and schema)

**`platform_base/desktop/ui_files/`:**
- Purpose: Auto-generated Python modules from Qt `.ui` files (70+ files)
- Generated: Yes — run `scripts/compile_ui.py` to regenerate
- Committed: Yes (treat as generated but stable)

**`platform_base/tests/fixtures/`:**
- Purpose: Shared test data (csv, xlsx, parquet, session files) and fixture helpers
- Key files: `qt_fixtures.py` (Qt app fixtures), `synthetic_data.py` (data generators)

**`platform_base/tests/_legacy/`:**
- Purpose: Archived test suite from before the `automated/` reorganization
- Status: Not actively maintained; do not add tests here

**`platform_base/profiling_reports/` + `platform_base/test_profiling/`:**
- Purpose: Saved profiling snapshots from `profiling/` instrumentation
- Generated: Yes
- Committed: No (gitignored, large binary data)

**`platform_base/.test_cache/`:**
- Purpose: joblib / LRU test result cache for expensive fixture computation
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-03-31*
