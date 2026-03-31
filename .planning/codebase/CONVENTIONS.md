# Coding Conventions

**Analysis Date:** 2026-03-31

## Code Style

**Language version:** Python 3.12 (CPython, Anaconda `base` environment)

**Linting:**
- ruff 0.12.5 — fast linter (`.ruff_cache/0.12.5/` present); config in `platform_base/pyproject.toml`
- Applied to all `src/platform_base/` and test files

**Type checking:**
- mypy with extensive cache in `.mypy_cache/3.12/` — all source modules are type-checked
- `typing.Protocol` used for structural interfaces (not ABC); see `platform_base/src/platform_base/core/protocols.py`
- Pydantic v2 for runtime-validated data models; see `platform_base/src/platform_base/core/models.py`
- `overrides` package used to enforce `@override` contract on subclass methods

**Type hint usage:**
- Type hints required throughout (enforced by mypy)
- Use `Protocol` definitions (`core/protocols.py`) as function parameter types instead of concrete classes
- Pydantic `BaseModel` subclasses for all cross-boundary data structures (API, configs, operation parameters)

## Naming Conventions

**Files:**
- All source files: `snake_case.py` — universal throughout 160+ modules
- Generated Qt UI files: `<WidgetName>_ui.py` suffix (e.g., `aboutDialog_ui.py`, `dataPanel_ui.py`)
- Compiled from Qt Designer `.ui` files by `platform_base/scripts/compile_ui.py`

**Directories:**
- All lowercase `snake_case/` (e.g., `signal_hub`, `crash_handler`, `dataset_store`)

**Classes:**
- `PascalCase` — e.g., `SignalHub`, `Registry`, `Orchestrator`, `DatasetStore`, `PluginBase`, `BaseFigure`, `BaseWorker`, `DatasetModel`

**Functions and methods:**
- `snake_case` — standard Python convention

**Constants:**
- `UPPER_SNAKE_CASE` — standard Python convention

**Module-level protocols/interfaces:**
- Named after what they describe with `Protocol` suffix or the class-like noun (e.g., `DatasetProtocol`, `WorkerProtocol`, `ProcessorProtocol`)

**Private members:**
- `_single_leading_underscore` for internal/protected attributes and methods

**Test files:**
- Current suite: `test_NN_descriptive_name.py` (two-digit number prefix, e.g., `test_01_ui_loading.py`)
- Legacy unit tests: `test_<module_name>.py` (e.g., `test_signal_hub_complete.py`)
- Plugin tests: `test_plugin.py` co-located in `plugins/<name>/`

## Patterns

**Signal / Event Bus (Observer):**
- `core/signal_hub.py` — application-wide pub/sub; decouples producers from consumers
- `ui/signal_hub.py` — UI-scoped variant
- Components subscribe at init, publish domain events (e.g., `dataset_added`, `result_ready`)
- Prefer `SignalHub` over direct Qt signal wiring for cross-layer communication

**Protocol-based interfaces:**
- `core/protocols.py` defines `typing.Protocol` interfaces for all major subsystems
- Use protocols as type hints to enable duck-typing and testability without hard inheritance chains
- Examples: `DatasetProtocol`, `PluginProtocol`, `ProcessorProtocol`, `WorkerProtocol`

**Worker / Background Thread:**
- `desktop/workers/base_worker.py` — `BaseWorker(QThread)` base class
- All long-running operations run in a worker, never on the main GUI thread
- Workers emit Qt signals for `progress`, `result_ready`, and `error` back to the UI thread
- Subclass `BaseWorker` and implement `run()` for new operations

**Pydantic Data Models:**
- All cross-layer DTOs and config structures use Pydantic v2 `BaseModel`
- Defined in `core/models.py`; shared across all layers
- Provides serialization, validation, and schema generation for free

**Mixin pattern:**
- `ui/mixins.py` and `ui/ui_loader_mixin.py` for composable UI behaviors
- Mixins provide reusable capabilities (dynamic `.ui` file loading, common callbacks) without deep inheritance

**Plugin system (pluggy):**
- `plugins/_base.py` — `PluginBase` + `pluggy` hookspec
- Each plugin: `plugins/<name>/manifest.json` + `plugins/<name>/plugin.py`
- Lifecycle: `load()`, `unload()`, `get_operations()`, `get_ui_components()`
- Discovery via `core/registry.py` at startup

**Registry / Catalog:**
- `core/registry.py` — central catalog of all registered plugins and components
- Enables listing and instantiation by name without hard imports

**Command / Undo-Redo:**
- `ui/undo_redo.py` — command pattern for reversible user operations

**Decorator / Profiling:**
- `profiling/decorators.py` — function-level timing decorators
- Applied selectively to hot-path processing functions

**Caching:**
- Two-tier: `caching/memory.py` (in-memory LRU) + `caching/disk.py` (persistent)
- Processing results are cached by `processing/` modules after first computation

**Lazy loading:**
- `processing/lazy_loading.py` — defers data materialization until first access for large datasets

## Error Handling

**Custom exception hierarchy** (defined in `platform_base/src/platform_base/utils/errors.py`):
```python
PlatformError               # base for all application errors
├── DataError               # file I/O, schema, validation failures
└── ProcessingError         # signal processing algorithm failures
```

**Rules:**
- Raise specific subclasses (`DataError`, `ProcessingError`) at the source; never re-raise bare `Exception`
- Catch at the boundary (worker, API endpoint, dialog) and convert to user-facing messages
- Workers emit an `error` signal instead of propagating exceptions across thread boundaries

**Crash handler:**
- `core/crash_handler.py` installs a top-level `sys.excepthook`
- Uncaught exceptions are logged, a crash report is written, and a user dialog is shown

**Sandboxed evaluation:**
- `utils/safe_eval.py` wraps user-supplied math expressions to prevent arbitrary code execution

## Logging

**Framework:** structlog + `python-json-logger` — outputs structured JSON logs

**Entry point:** `core/structured_logger.py` wraps `structlog` with project-level defaults

**Usage pattern:**
```python
from platform_base.core.structured_logger import get_logger

logger = get_logger(__name__)
logger.info("dataset_loaded", filename=path, rows=n_rows)
logger.warning("cache_miss", key=cache_key)
logger.error("processing_failed", error=str(exc), operation=op_name)
```

**Rules:**
- Always use keyword arguments (structured fields), never positional string formatting
- Log at module level (`get_logger(__name__)`) — one logger per module
- Use `rich` terminal output for developer-facing CLI / debug runs

## Comments & Documentation

**Docstrings:**
- Required on public classes and public methods
- Style: not explicitly confirmed (mypy + ruff present; Google or NumPy style expected)

**Inline comments:**
- Use for non-obvious logic only (algorithm choices, workaround explanations)
- Portuguese or English both appear in this codebase; prefer English for code-level comments

**Type annotations:**
- Preferred over docstring parameter descriptions; enforced by mypy

## Import Organization

**Ordering (ruff-enforced):**
1. Standard library (`import os`, `from typing import ...`)
2. Third-party (`import numpy as np`, `from PySide6 import ...`)
3. Local package (`from platform_base.core import ...`)

**Absolute imports only** — no relative imports except within the same module package

## Module Design

**Exports:**
- `__init__.py` files expose the public API of each package
- Internal modules use `_` prefix on private helpers

**No barrel anti-patterns:**
- Do not re-export everything from `__init__.py` — only key public symbols

---

*Convention analysis: 2026-03-31*
