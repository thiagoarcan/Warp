# Technology Stack

**Analysis Date:** 2026-03-31

## Languages

**Primary:**
- Python 3.12 — All application code (confirmed via `.mypy_cache/3.12/` and `cpython-312` pyc files)

**Secondary:**
- YAML — Configuration files (`configs/platform.yaml`, `.platform_config/system/platform.yaml`, `.platform_config/user/default.yaml`)
- TOML — Project packaging (`platform_base/pyproject.toml`)
- JSON — Plugin manifests (`plugins/*/manifest.json`, `.platform_config/config_schema.json`)

## Runtime

**Environment:**
- CPython 3.12 (Anaconda distribution — `base` conda environment active)

**Package Manager:**
- Conda (base environment)
- Lockfile: Not detected (pixi/conda-lock not used)

## Frameworks

**Core:**
- PySide6 + shiboken6 — Primary desktop GUI framework (Qt6 Python bindings)
- FastAPI — Local REST API server (`platform_base/src/platform_base/api/server.py`)
- Starlette — FastAPI's ASGI foundation
- Pydantic v2 (pydantic + pydantic_core) — Data model validation and serialization (`platform_base/src/platform_base/core/models.py`)

**Testing:**
- pytest 8.4.2 — Test runner (confirmed from `cpython-312-pytest-8.4.2.pyc` pyc files)
- pluggy — Plugin hook system for pytest and app plugin architecture

**Build/Dev:**
- pyproject.toml — Build and dependency manifest (`platform_base/pyproject.toml`, 13 709 bytes)
- mypy — Static type checking (`.mypy_cache/3.12/` present, extensive)
- ruff — Fast Python linter (`.ruff_cache/` present)
- compile_ui.py / generate_ui_files.py — Scripts to compile Qt `.ui` files → `*_ui.py` (`platform_base/scripts/`)

## Key Dependencies

**GUI:**
- PySide6 — Qt6 desktop application framework (80+ generated UI files in `platform_base/src/platform_base/desktop/ui_files/`)
- shiboken6 — C++ binding layer for PySide6

**Visualization:**
- matplotlib — 2D charts and plots (`platform_base/src/platform_base/viz/figures_2d.py`, `heatmaps.py`)
- PyVista + vtkmodules — 3D mesh and volumetric visualization (`platform_base/src/platform_base/viz/figures_3d.py`)
- trimesh — 3D mesh geometry operations
- rtree — Spatial indexing for 3D support
- Bokeh — Potentially alternative/embedded web visualizations
- Dash — Potentially embedded interactive dashboards

**Data Processing:**
- numpy — Numerical arrays and math
- scipy (inferred) — Signal filters, interpolation, calculus (`platform_base/src/platform_base/processing/filters.py`, `calculus.py`, `interpolation.py`)
- pint — Physical unit handling (`platform_base/src/platform_base/processing/units.py`)
- python-dateutil — Datetime parsing and timezone handling
- dask — Parallel/lazy computation for large datasets

**Data I/O:**
- openpyxl (inferred from `utils/xlsx_to_csv.py`) — Excel `.xlsx` read/write
- pandas (inferred) — DataFrame operations on time-series data
- Sample data is `.xlsx` files (`platform_base/data/samples/*.xlsx`)

**Image/Video:**
- Pillow (PIL) — Image processing
- OpenCV (cv2) — Video frame capture/export (`platform_base/src/platform_base/ui/video_export.py`)
- imageio — Image sequence I/O

**Messaging & Streaming:**
- ZeroMQ (zmq) — High-performance messaging for real-time data streaming (`platform_base/src/platform_base/streaming/`)
- websocket — WebSocket client/server

**API & HTTP:**
- FastAPI + Uvicorn (inferred) — Local REST API (`platform_base/src/platform_base/api/`)
- Flask — Secondary/alternative web interface (present in mypy cache)
- requests — HTTP client calls
- httpx — Async HTTP client
- h11 / httpcore — Low-level HTTP protocol

**Logging:**
- structlog — Structured logging (`platform_base/src/platform_base/core/structured_logger.py`)
- python-json-logger (pythonjsonlogger) — JSON log formatting
- rich — Rich terminal output for logs and CLI

**Caching:**
- Custom disk cache (`platform_base/src/platform_base/caching/disk.py`)
- Custom memory cache (`platform_base/src/platform_base/caching/memory.py`)
- flexcache — Serialization cache
- diskcache or joblib (inferred behind caching layer)

**Serialization:**
- orjson — Fast JSON serialization
- tomli / tomli_w — TOML read/write
- ruamel.yaml — Round-trip YAML with comment preservation
- PyYAML (yaml) — Standard YAML
- pickle (stdlib) — Python object serialization

**Internationalization:**
- Babel — i18n/l10n support (`platform_base/src/platform_base/utils/i18n.py`)

**Metrics & Observability:**
- prometheus_client — Prometheus metrics exposition

**Utilities:**
- cryptography / bcrypt — Secure credential handling
- overrides — Decorator to enforce method override contracts
- packaging — Version parsing
- importlib_metadata — Package metadata

## Configuration

**User Configuration:**
- `.platform_config/user/default.yaml` — User-level defaults
- `.platform_config/system/platform.yaml` — System-level platform settings
- `.platform_config/config_schema.json` — JSON Schema for config validation
- `configs/platform.yaml` — Main platform configuration
- Managed by `platform_base/src/platform_base/core/config.py` and `core/config_manager.py`

**Build:**
- `platform_base/pyproject.toml` — Package metadata and build config (13 709 bytes)

**Linting/Typing:**
- `.ruff_cache/` — Ruff linter cache
- `.mypy_cache/3.12/` — mypy type check cache

## Build & Packaging

**Package Layout:**
- Source layout: `platform_base/src/platform_base/` (`src`-layout pattern)
- Entry points: `platform_base/run_app.py`, `platform_base/launch_app.py`
- UI compilation: Qt `.ui` → `*_ui.py` via `platform_base/scripts/compile_ui.py`
- Test runner: `platform_base/run_test_suite.py` and `platform_base/scripts/run_tests.py`
- Plugin packaging: individual directories under `platform_base/plugins/` with `manifest.json`

**Platform Requirements:**
- Development: Windows (Anaconda base, VS Code)
- Runtime dependencies require Qt6 (PySide6), Python 3.12

---

*Stack analysis: 2026-03-31*
