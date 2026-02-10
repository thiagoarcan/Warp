"""
Pytest configuration and shared fixtures for Platform Base tests.

This file contains fixtures that are available to all tests in the test suite.
Fixtures are organized by scope and purpose.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication

# Add src to path for imports
SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# ============================================
# SESSION-SCOPED FIXTURES (Created once per test session)
# ============================================


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """
    Create a QApplication instance for GUI tests.

    This fixture is session-scoped to avoid creating multiple QApplication
    instances, which would cause Qt errors.
    """
    # Check if running in CI without display
    if os.environ.get("CI") and not os.environ.get("DISPLAY"):
        pytest.skip("Skipping GUI tests in CI without display")

    from PyQt6.QtWidgets import QApplication

    # Use existing app if available
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app

    # Don't quit the app as other tests may need it


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_csv_path(test_data_dir: Path) -> Path:
    """Return path to sample CSV file, creating it if needed."""
    csv_path = test_data_dir / "csv" / "simple.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        # Create sample CSV data
        df = pd.DataFrame({
            "time": np.linspace(0, 10, 1000),
            "value1": np.sin(np.linspace(0, 10, 1000)),
            "value2": np.cos(np.linspace(0, 10, 1000)),
            "value3": np.random.randn(1000),
        })
        df.to_csv(csv_path, index=False)

    return csv_path


@pytest.fixture(scope="session")
def sample_xlsx_path(test_data_dir: Path) -> Path:
    """Return path to sample XLSX file, creating it if needed."""
    xlsx_path = test_data_dir / "xlsx" / "simple.xlsx"
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    if not xlsx_path.exists():
        # Create sample XLSX data
        df = pd.DataFrame({
            "time": np.linspace(0, 10, 500),
            "sensor_a": np.sin(np.linspace(0, 10, 500)) * 100,
            "sensor_b": np.cos(np.linspace(0, 10, 500)) * 100,
        })
        df.to_excel(xlsx_path, index=False, engine="openpyxl")

    return xlsx_path


# ============================================
# MODULE-SCOPED FIXTURES
# ============================================


@pytest.fixture(scope="module")
def large_dataset() -> pd.DataFrame:
    """Create a large dataset for performance tests."""
    n_points = 1_000_000
    return pd.DataFrame({
        "time": np.linspace(0, 1000, n_points),
        "value": np.sin(np.linspace(0, 100 * np.pi, n_points)),
    })


# ============================================
# FUNCTION-SCOPED FIXTURES (Created for each test)
# ============================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_time_array() -> np.ndarray:
    """Generate a sample time array."""
    return np.linspace(0, 10, 1000)


@pytest.fixture
def sample_value_array() -> np.ndarray:
    """Generate a sample value array (sine wave)."""
    t = np.linspace(0, 10, 1000)
    return np.sin(t)


@pytest.fixture
def sample_value_array_with_noise() -> np.ndarray:
    """Generate a sample value array with added noise."""
    t = np.linspace(0, 10, 1000)
    return np.sin(t) + 0.1 * np.random.randn(1000)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    n = 1000
    return pd.DataFrame({
        "time": np.linspace(0, 10, n),
        "value1": np.sin(np.linspace(0, 10, n)),
        "value2": np.cos(np.linspace(0, 10, n)),
        "value3": np.random.randn(n),
    })


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """Create an empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def dataframe_with_nan() -> pd.DataFrame:
    """Create a DataFrame with NaN values."""
    n = 100
    values = np.sin(np.linspace(0, 10, n))
    values[10:15] = np.nan
    values[50:55] = np.nan
    return pd.DataFrame({
        "time": np.linspace(0, 10, n),
        "value": values,
    })


@pytest.fixture
def dataframe_with_gaps() -> pd.DataFrame:
    """Create a DataFrame with irregular time gaps."""
    # Create non-uniform time series
    t1 = np.linspace(0, 3, 30)
    t2 = np.linspace(5, 8, 30)  # Gap from 3 to 5
    t3 = np.linspace(9, 10, 10)  # Gap from 8 to 9
    time = np.concatenate([t1, t2, t3])

    return pd.DataFrame({
        "time": time,
        "value": np.sin(time),
    })


# ============================================
# MOCK FIXTURES
# ============================================


@pytest.fixture
def mock_session_state() -> MagicMock:
    """Create a mock SessionState for testing."""
    mock = MagicMock()
    mock.datasets = {}
    mock.selected_series = []
    mock.time_window = None
    return mock


@pytest.fixture
def mock_signal_hub() -> MagicMock:
    """Create a mock SignalHub for testing."""
    mock = MagicMock()
    mock.dataset_changed = MagicMock()
    mock.selection_changed = MagicMock()
    mock.plot_created = MagicMock()
    mock.operation_finished = MagicMock()
    return mock


# ============================================
# DATASET FIXTURES
# ============================================


@pytest.fixture
def sample_series_data() -> dict[str, Any]:
    """Create sample series data dictionary."""
    return {
        "id": "test_series_001",
        "name": "Test Series",
        "time": np.linspace(0, 10, 100),
        "values": np.sin(np.linspace(0, 10, 100)),
        "unit": "m/s",
        "source_file": "test.csv",
    }


@pytest.fixture
def quadratic_data() -> tuple[np.ndarray, np.ndarray]:
    """Create quadratic test data (y = x^2) for derivative tests."""
    t = np.linspace(0, 10, 1001)
    y = t ** 2
    return t, y


@pytest.fixture
def linear_data() -> tuple[np.ndarray, np.ndarray]:
    """Create linear test data (y = 2x + 1) for integral tests."""
    t = np.linspace(0, 10, 1001)
    y = 2 * t + 1
    return t, y


@pytest.fixture
def constant_data() -> tuple[np.ndarray, np.ndarray]:
    """Create constant test data (y = 5) for edge case tests."""
    t = np.linspace(0, 10, 100)
    y = np.full_like(t, 5.0)
    return t, y


@pytest.fixture
def sine_data() -> tuple[np.ndarray, np.ndarray]:
    """Create sine wave test data."""
    t = np.linspace(0, 4 * np.pi, 1000)
    y = np.sin(t)
    return t, y


@pytest.fixture
def two_curves_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create two curves for area between curves tests."""
    t = np.linspace(0, 10, 1000)
    y1 = np.sin(t)
    y2 = 0.5 * np.sin(t)
    return t, y1, y2


@pytest.fixture
def crossing_curves_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create two crossing curves for area tests."""
    t = np.linspace(0, 2 * np.pi, 1000)
    y1 = np.sin(t)
    y2 = np.cos(t)
    return t, y1, y2


# ============================================
# HELPER FUNCTIONS
# ============================================


def assert_arrays_close(
    actual: np.ndarray,
    expected: np.ndarray,
    rtol: float = 1e-5,
    atol: float = 1e-8,
) -> None:
    """Assert that two arrays are element-wise equal within a tolerance."""
    np.testing.assert_allclose(actual, expected, rtol=rtol, atol=atol)


def create_test_csv(path: Path, rows: int = 1000) -> Path:
    """Create a test CSV file with sample data."""
    df = pd.DataFrame({
        "time": np.linspace(0, rows / 100, rows),
        "value": np.sin(np.linspace(0, 10 * np.pi, rows)),
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


# ============================================
# PYTEST HOOKS
# ============================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "smoke: smoke tests (critical path tests)"
    )
    config.addinivalue_line(
        "markers", "gui: GUI tests requiring Qt"
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to add markers."""
    for item in items:
        # Mark GUI tests
        if "gui" in str(item.fspath):
            item.add_marker(pytest.mark.gui)

        # Mark performance tests as slow
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

        # Mark stress tests as slow
        if "stress" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
