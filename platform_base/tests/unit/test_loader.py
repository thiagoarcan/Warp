from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

from platform_base.io.loader import load


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sample_scada_xlsx() -> Path | None:
    """Find a SCADA sample file (XXX_YY-ZZZ.xlsx pattern - any 3-char prefix)."""
    root = _repo_root()
    # Look for SCADA files with pattern: XXX_*-*.xlsx (any 3-char prefix)
    # Examples: BAR_FT-OP10.xlsx, PLN_PT-001.xlsx, LOS_DT-ABC.xlsx
    scada_pattern = "???_*-*.xlsx"
    files = sorted(root.glob(scada_pattern))
    if files:
        return files[0]
    return None


def test_load_csv(tmp_path):
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="s"),
            "a": [1, 2, 3, 4, 5],
            "b": [10, 11, 12, 13, 14],
        }
    )
    path = tmp_path / "data.csv"
    df.to_csv(path, index=False)
    dataset = load(str(path))
    assert len(dataset.series) == 2


def test_load_scada_sample():
    """Test loading real SCADA xlsx files with 'tempo' and 'valor' columns."""
    sample = _sample_scada_xlsx()
    if sample is None:
        pytest.skip("No SCADA sample file found (XXX_*-*.xlsx pattern)")
    
    # Load the SCADA file
    dataset = load(str(sample), config={"max_rows": 2000})
    
    # Verify dataset was created with series
    assert dataset is not None
    assert len(dataset.series) >= 1, f"Expected at least 1 series, got {len(dataset.series)}"
    
    # Verify time series has valid data
    assert len(dataset.t_seconds) > 0
    assert "valor" in dataset.series, "Expected 'valor' column as series"


def test_load_scada_csv_fixture():
    """Test loading SCADA data from CSV fixture file."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "BAR_FT-OP10_sample.csv"
    if not fixture_path.exists():
        pytest.skip("SCADA CSV fixture not found")
    
    dataset = load(str(fixture_path))
    
    # Verify dataset was loaded correctly
    assert dataset is not None
    assert len(dataset.series) == 1
    assert "valor" in dataset.series
    assert len(dataset.t_seconds) == 1536  # Known size from original file
    
    # Verify timestamps are properly parsed
    assert not pd.isna(dataset.t_datetime).all(), "All timestamps are NaT"
