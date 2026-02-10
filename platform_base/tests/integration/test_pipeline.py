from pathlib import Path

import pytest

pytest.importorskip("pandas")

from platform_base.io.loader import load
from platform_base.processing.calculus import derivative
from platform_base.processing.interpolation import interpolate
from platform_base.processing.synchronization import synchronize


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


def test_pipeline_scada_sample():
    sample = _sample_scada_xlsx()
    if sample is None:
        pytest.skip("No SCADA sample file found (XXX_*-*.xlsx pattern)")

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
