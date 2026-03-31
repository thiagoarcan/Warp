# Testing Patterns

**Analysis Date:** 2026-03-31

## Framework

**Runner:**
- pytest 8.4.2
- Config: `platform_base/pyproject.toml` (`[tool.pytest.ini_options]` section)

**Plugin / Hook system:**
- pluggy — shared between pytest plugin system and the app's own plugin architecture

**Run Commands:**
```bash
# Run full automated suite (primary)
python run_test_suite.py

# Alternative runner (CI / scripts)
python scripts/run_tests.py

# Run specific test file
pytest tests/automated/test_01_ui_loading.py -v

# Run with coverage
pytest tests/automated/ --cov=src/platform_base --cov-report=html

# Run from workspace root (platform_base/ is the working directory)
cd platform_base/
pytest tests/automated/
```

## Test File Organization

**Active test suite location:**
```
platform_base/tests/
├── automated/                  ← PRIMARY — 10 numbered integration tests (use these)
│   ├── conftest.py             ← suite-level fixtures and configuration
│   ├── helpers.py              ← shared test helper functions
│   ├── test_01_ui_loading.py
│   ├── test_02_mandatory_widgets.py
│   ├── test_03_navigation.py
│   ├── test_04_signals_slots.py
│   ├── test_05_initialization.py
│   ├── test_06_resources.py
│   ├── test_07_state_visibility.py
│   ├── test_08_memory_leaks.py
│   ├── test_09_exceptions_errors.py
│   ├── test_10_coverage.py
│   └── __init__.py
├── fixtures/                   ← shared test data and Qt fixtures
│   ├── conftest.py             ← fixture registration (if present)
│   ├── qt_fixtures.py          ← Qt/PySide6 app + widget fixtures
│   ├── synthetic_data.py       ← programmatic test data generators
│   ├── csv/                    ← sample CSV files
│   ├── xlsx/                   ← sample Excel files
│   ├── parquet/                ← sample Parquet files
│   ├── data/                   ← other binary test data
│   └── sessions/               ← saved session state fixtures
└── _legacy/                    ← ARCHIVED — do not add tests here
    ├── unit/                   ← 80+ old unit tests (one per module)
    ├── integration/
    ├── functional/
    ├── e2e/
    ├── smoke/
    ├── performance/
    ├── stress/
    ├── property/
    ├── gui/
    ├── ui/
    └── ui_validation/
```

**Plugin tests (co-located):**
```
platform_base/plugins/
└── dtw_plugin/
    └── test_plugin.py          ← plugin-specific tests next to the plugin
```

**Naming:**
- Current suite: `test_NN_descriptive_name.py` — two-digit prefix enforces execution order
- Legacy unit tests: `test_<module_name>.py` and `test_<module_name>_complete.py`

## Test Types

**UI / Integration tests (primary suite `tests/automated/`):**
- `test_01_ui_loading.py` — all UI panels and dialogs load without errors
- `test_02_mandatory_widgets.py` — mandatory widget presence and accessibility
- `test_03_navigation.py` — navigation flows between panels/modes
- `test_04_signals_slots.py` — Qt signal/slot connections work as expected
- `test_05_initialization.py` — component initialization order and state
- `test_06_resources.py` — resource loading (icons, stylesheets, data)
- `test_07_state_visibility.py` — widget visibility and enabled/disabled state
- `test_08_memory_leaks.py` — no dangling widget or dataset references after close
- `test_09_exceptions_errors.py` — error handling and `crash_handler.py` paths
- `test_10_coverage.py` — coverage summary assertions

**Legacy unit tests (`tests/_legacy/unit/` — do not extend, reference only):**
- One test file per module (e.g., `test_signal_hub_complete.py`, `test_loader.py`, `test_calculus.py`)
- Covers core, processing, caching, streaming, viz, ui, utils, io modules individually
- ~80+ unit test files testing module-level functions and classes in isolation

**Other legacy types (archived):**
- `_legacy/integration/` — pipeline integration tests
- `_legacy/e2e/` — end-to-end user scenario tests
- `_legacy/functional/` — feature-level behavioral tests
- `_legacy/performance/` — benchmark tests (`test_benchmarks.py`)
- `_legacy/stress/` — large dataset stress tests
- `_legacy/property/` — property-based tests (calculus invariants)
- `_legacy/smoke/` — minimal smoke tests
- `_legacy/gui/` — Qt widget direct tests

## Test Structure

**Suite organization (automated suite):**
```python
# tests/automated/test_NN_something.py
import pytest
from tests.fixtures.qt_fixtures import app_fixture, main_window  # Qt fixtures
from tests.automated.helpers import some_helper

class TestSomeThing:
    """Tests for some aspect."""
    
    def test_specific_behavior(self, app_fixture, main_window):
        # Arrange
        # Act
        # Assert
        assert something is True

    def test_error_case(self, app_fixture):
        with pytest.raises(SomePlatformError):
            ...
```

**conftest.py role:**
- `tests/automated/conftest.py` — registers Qt app fixture, sets up logging for tests
- `tests/fixtures/qt_fixtures.py` — provides `QApplication` instance and common widget fixtures

## Mocking

**Qt application mocking:**
- `tests/fixtures/qt_fixtures.py` provides a shared `QApplication` fixture
- Qt widgets are instantiated directly in tests (not mocked) to verify real behavior

**Signal mocking:**
- Qt signals are connected to lambda or `Mock()` callables to capture emissions
- `assert signal_spy.call_count == 1` pattern used for signal emission checks

**Dependency mocking:**
- `unittest.mock.MagicMock` or `pytest-mock` (if present — not confirmed) for non-Qt deps
- `core/protocols.py` Protocol interfaces make it easy to pass mock objects that satisfy structural typing
- Production code is designed around Protocol interfaces so tests substitute lightweight fakes

**Worker mocking:**
- `BaseWorker` subclasses are tested by calling `run()` directly (bypassing thread launch)
- Signals emitted by workers are captured with `QSignalSpy` or connected to MagicMock

## Fixtures and Factories

**Qt application fixture (shared across all UI tests):**
```python
# tests/fixtures/qt_fixtures.py
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app_fixture():
    app = QApplication.instance() or QApplication([])
    yield app
```

**Synthetic data fixture:**
```python
# tests/fixtures/synthetic_data.py
# Provides programmatic DataFrame / time-series generation for processing tests
```

**File fixtures:**
- `tests/fixtures/csv/`, `tests/fixtures/xlsx/`, `tests/fixtures/parquet/` — real-format files for I/O tests
- `tests/fixtures/BAR_FT-OP10_sample.csv` — representative industrial dataset sample

**Session fixtures:**
- `tests/fixtures/sessions/` — pre-built session state files for state restoration tests

## Fixture Locations

- Suite fixtures: `tests/automated/conftest.py`
- Qt-specific fixtures: `tests/fixtures/qt_fixtures.py`
- Data generators: `tests/fixtures/synthetic_data.py`
- Shared helper functions: `tests/automated/helpers.py`

## Coverage

**Requirements:**
- `test_10_coverage.py` is the final test in the suite and performs coverage assertions
- No explicit percentage threshold confirmed — threshold defined inside `test_10_coverage.py`

**View coverage:**
```bash
pytest tests/automated/ --cov=src/platform_base --cov-report=html
# opens htmlcov/index.html
```

**Benchmarks:**
- Stored in `platform_base/.benchmarks/` (pytest-benchmark or manual)
- Profiling reports in `platform_base/profiling_reports/`
- Performance tests live in legacy `tests/_legacy/performance/test_benchmarks.py`

## Common Patterns

**Async / Qt thread testing:**
```python
from PySide6.QtTest import QTest

def test_worker_result(app_fixture):
    worker = MyWorker(params)
    results = []
    worker.result_ready.connect(results.append)
    worker.run()           # call run() directly, not start()
    assert len(results) == 1
```

**Error / exception testing:**
```python
def test_invalid_file_raises():
    with pytest.raises(DataError, match="unsupported format"):
        loader.load("file.xyz")
```

**Signal emission testing:**
```python
def test_signal_emitted(app_fixture, signal_hub):
    received = []
    signal_hub.dataset_added.connect(lambda d: received.append(d))
    dataset_store.add(mock_dataset)
    assert len(received) == 1
```

**Parametrized tests:**
```python
@pytest.mark.parametrize("file_path,expected_rows", [
    ("fixtures/csv/sample.csv", 100),
    ("fixtures/xlsx/sample.xlsx", 200),
])
def test_loader(file_path, expected_rows, tmp_path):
    ...
```

## Where to Add New Tests

**New feature tests:**
- If the feature touches UI or integration: add to `tests/automated/` (extend or add a new numbered `test_NN_*.py` at the end)
- If testing a pure Python module in isolation: add a unit test in `tests/automated/helpers.py` or create a focused test within the automated suite

**New plugin tests:**
- Place `test_plugin.py` co-located inside `plugins/<plugin_name>/`

**Do NOT add to `tests/_legacy/`** — that directory is archived

---

*Testing analysis: 2026-03-31*
