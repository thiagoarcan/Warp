from pathlib import Path

import pytest

pytest.importorskip("pandas")

from platform_base.io.loader import load
from platform_base.processing.calculus import derivative
from platform_base.processing.interpolation import interpolate
from platform_base.processing.synchronization import synchronize


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _sample_xlsx() -> Path | None:
    root = _repo_root()
    files = sorted(root.glob("*.xlsx"))
    return files[0] if files else None


def test_pipeline_scada_sample():
    sample = _sample_xlsx()
    if sample is None:
        pytest.skip("No SCADA sample file found")

    dataset = load(str(sample), config={"max_rows": 2000})
    series_ids = list(dataset.series.keys())[:2]
    if not series_ids:
        pytest.skip("No series detected")

    series = dataset.series[series_ids[0]]
    interp = interpolate(series.values, dataset.t_seconds, "linear", {})
    assert len(interp.values) == len(series.values)

    if len(series_ids) > 1:
        s1 = dataset.series[series_ids[0]].values
        s2 = dataset.series[series_ids[1]].values
        t = dataset.t_seconds
        sync = synchronize(
            {"s1": s1, "s2": s2},
            {"s1": t, "s2": t},
            "common_grid_interpolate",
            {},
        )
        assert len(sync.t_common) > 0

    deriv = derivative(series.values, dataset.t_seconds, 1, "finite_diff", {})
    assert len(deriv.values) == len(series.values)
