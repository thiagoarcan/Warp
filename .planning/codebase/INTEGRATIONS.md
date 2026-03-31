# External Integrations

**Analysis Date:** 2026-03-31

## GUI/Frontend

**Framework: PySide6 (Qt6)**
- All desktop UI is built with PySide6 + Qt6
- 80+ generated UI Python files in `platform_base/src/platform_base/desktop/ui_files/*_ui.py`
- UI definition files compiled from `.ui` XML via `platform_base/scripts/compile_ui.py`
- Main window: `platform_base/src/platform_base/desktop/main_window.py` and `platform_base/src/platform_base/ui/main_window.py`
- Application class: `platform_base/src/platform_base/desktop/app.py` and `platform_base/src/platform_base/ui/app.py`
- Theme system: `platform_base/src/platform_base/ui/themes.py`
- Accessibility: `platform_base/src/platform_base/ui/accessibility.py` and `platform_base/src/platform_base/utils/a11y_helpers.py`
- Multi-view synchronization: `platform_base/src/platform_base/ui/multi_view_sync.py`
- Undo/Redo: `platform_base/src/platform_base/ui/undo_redo.py`
- Keyboard shortcuts: `platform_base/src/platform_base/ui/shortcuts.py`
- Tooltips: `platform_base/src/platform_base/ui/tooltips.py`, `platform_base/src/platform_base/ui/tooltip_manager.py`

**Qt Workers (background threads):**
- `platform_base/src/platform_base/desktop/workers/base_worker.py`
- `platform_base/src/platform_base/desktop/workers/processing_worker.py`
- `platform_base/src/platform_base/desktop/workers/export_worker.py`
- `platform_base/src/platform_base/ui/workers/`

## Data Processing

**Numerical & Scientific Computing:**
- numpy — Core numerical arrays used across all processing modules
- scipy (inferred) — Signal processing (`platform_base/src/platform_base/processing/filters.py`), calculus (`calculus.py`), interpolation (`interpolation.py`), smoothing (`smoothing.py`)
- pint — Physical units for sensor data (`platform_base/src/platform_base/processing/units.py`)
- dask — Distributed/out-of-core computation for large time-series

**Time Series:**
- python-dateutil — Datetime handling in `platform_base/src/platform_base/processing/timebase.py`
- Custom synchronization: `platform_base/src/platform_base/processing/synchronization.py`
- Custom DTW (Dynamic Time Warping): `platform_base/plugins/dtw_plugin/plugin.py`
- Downsampling: `platform_base/src/platform_base/processing/downsampling.py`

**Data I/O:**
- openpyxl (inferred) — Excel `.xlsx` loading; sample industrial data in `platform_base/data/samples/*.xlsx` (BAR/PLN instrument tags: DT, FT, PT, TT)
- `platform_base/src/platform_base/utils/xlsx_to_csv.py` — Converts xlsx to CSV
- `platform_base/src/platform_base/io/loader.py` — Generic file loader
- `platform_base/src/platform_base/io/encoding_detector.py` — Auto-detects file encoding
- `platform_base/src/platform_base/io/schema_detector.py` — Detects CSV/tabular schemas
- `platform_base/src/platform_base/io/validator.py` — Data validation on load

## Visualization

**2D Plotting:**
- matplotlib — 2D line charts and heatmaps (`platform_base/src/platform_base/viz/figures_2d.py`, `heatmaps.py`)
- Custom multi-panel layout: `platform_base/src/platform_base/viz/multipanel.py`
- Multiple Y-axes: `platform_base/src/platform_base/viz/multi_y_axis.py`
- Datetime axis: `platform_base/src/platform_base/viz/datetime_axis.py`
- Streaming viz: `platform_base/src/platform_base/viz/streaming.py`
- Hue coordinator (color management): `platform_base/src/platform_base/viz/hue_coordinator.py`
- Computation engine (lazy render): `platform_base/src/platform_base/viz/computation_engine.py`
- State cube (3D state view): `platform_base/src/platform_base/viz/state_cube.py`

**3D Visualization:**
- PyVista + vtkmodules — 3D mesh/volumetric rendering (`platform_base/src/platform_base/viz/figures_3d.py`)
- trimesh — 3D geometry manipulation
- rtree — Spatial indexing

**Web-based (optional/embedded):**
- Bokeh — Interactive browser-based charts
- Dash — React-based Python dashboards
- cv2 (OpenCV) — Video frame rendering for export (`platform_base/src/platform_base/ui/video_export.py`)
- imageio — Image and video I/O

## API Server (Local)

**Internal REST API:**
- FastAPI — HTTP API server (`platform_base/src/platform_base/api/server.py`)
- Endpoints: `platform_base/src/platform_base/api/endpoints.py`
- Pydantic — Request/response models
- Starlette — Middleware and routing
- uvicorn (inferred as ASGI server)
- httpx — Async HTTP client for API calls

**WebSocket & Messaging:**
- ZeroMQ (zmq) — High-performance pub/sub messaging for real-time data (`platform_base/src/platform_base/streaming/`)
- websocket — WebSocket protocol support
- Temporal sync: `platform_base/src/platform_base/streaming/temporal_sync.py`
- Stream filters: `platform_base/src/platform_base/streaming/filters.py`

## Plugin System

**Architecture: pluggy-based hook system**
- Base plugin interface: `platform_base/plugins/_base.py`
- Plugin discovery and registry: `platform_base/src/platform_base/core/registry.py`
- Plugin manifests: JSON files at `platform_base/plugins/*/manifest.json`
- Built-in plugins: `platform_base/plugins/dtw_plugin/` (Dynamic Time Warping), `platform_base/plugins/advanced_sync/`
- Plugin dev guide: `platform_base/docs/PLUGIN_DEVELOPMENT.md`
- Each plugin: self-contained directory with `plugin.py`, `manifest.json`, optional tests

## Configuration & Settings

**Config Files:**
- `platform_base/configs/platform.yaml` — Main platform configuration
- `platform_base/.platform_config/system/platform.yaml` — System-level settings  
- `platform_base/.platform_config/user/default.yaml` — User preference defaults
- `platform_base/.platform_config/config_schema.json` — JSON Schema for validation
- Config manager: `platform_base/src/platform_base/core/config.py` and `platform_base/src/platform_base/core/config_manager.py`

**Config Libraries:**
- ruamel.yaml — Round-trip YAML with comment preservation
- PyYAML — Standard YAML parsing
- tomli / tomli_w — TOML read and write

## Data Storage

**Databases:**
- No external database detected (SQLite via sqlite3 stdlib is in mypy cache — may be used for local storage)
- Session state: `platform_base/src/platform_base/core/session_state.py`
- Dataset store: `platform_base/src/platform_base/core/dataset_store.py`

**File Storage:**
- Local filesystem only
- Sample data: `platform_base/data/samples/` (`.xlsx` and `.json`)
- Caching: `platform_base/src/platform_base/caching/disk.py` (disk-based), `platform_base/src/platform_base/caching/memory.py` (in-memory)
- flexcache — Serialization-aware cache abstraction

**Export Formats:**
- Excel (.xlsx), CSV, video (via OpenCV), selected via `platform_base/src/platform_base/ui/export.py` and `export_dialog.py`

## Authentication & Security

**No external auth provider detected.**
- bcrypt — Password hashing (if credentials are stored locally)
- cryptography — General cryptography primitives
- `platform_base/src/platform_base/utils/safe_eval.py` — Sandboxed expression evaluation (prevents arbitrary code execution in user-supplied math expressions)

## Monitoring & Observability

**Metrics:**
- prometheus_client — Prometheus metrics endpoint (local; may be scraped by monitoring stack)
- `platform_base/src/platform_base/analytics/telemetry.py` — Internal telemetry

**Logging:**
- structlog — Structured logging throughout app (`platform_base/src/platform_base/core/structured_logger.py`)
- python-json-logger — JSON-formatted log output
- rich — Terminal-friendly log display
- Log widget: `platform_base/src/platform_base/desktop/ui_files/logWidget_ui.py`
- Memory & performance monitoring: `platform_base/src/platform_base/utils/memory_monitor.py`, `platform_base/src/platform_base/ui/panels/performance.py`

**Error Handling:**
- Crash handler: `platform_base/src/platform_base/core/crash_handler.py`
- Error utilities: `platform_base/src/platform_base/utils/errors.py`

## CI/CD & Deployment

**Testing:**
- pytest 8.4.2 — Test runner
- Test suites: `platform_base/tests/automated/` (10 numbered test files covering UI loading, widgets, navigation, signals, memory leaks, exceptions)
- Benchmarks: `platform_base/.benchmarks/`
- Profiling: `platform_base/src/platform_base/profiling/` and `platform_base/profiling_reports/`

**CI Pipeline:**
- `.github/` directory present (GitHub Actions workflows)
- No local CI tools detected (no Makefile, Dockerfile, tox.ini)

**Hosting:**
- Desktop application — no cloud deployment detected

## Internationalization

- Babel — i18n/l10n framework (`platform_base/src/platform_base/utils/i18n.py`)
- Application appears to be Portuguese-language primary (TRANSPETRO/Brazilian government context; doc files use Portuguese names)

---

*Integration audit: 2026-03-31*
