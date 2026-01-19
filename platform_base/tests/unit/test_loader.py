from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

from platform_base.io.loader import load


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _sample_xlsx() -> Path | None:
    root = _repo_root()
    files = sorted(root.glob("*.xlsx"))
    return files[0] if files else None


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
    sample = _sample_xlsx()
    if sample is None:
        pytest.skip("No SCADA sample file found")
    dataset = load(str(sample), config={"max_rows": 2000})
    assert len(dataset.series) >= 1
