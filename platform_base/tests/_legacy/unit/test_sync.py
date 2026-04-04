import numpy as np

from platform_base.processing.synchronization import synchronize


def test_common_grid_sync():
    t1 = np.array([0.0, 1.0, 2.0, 3.0])
    t2 = np.array([0.5, 1.5, 2.5, 3.5])
    s1 = np.array([1.0, 2.0, 3.0, 4.0])
    s2 = np.array([10.0, 11.0, 12.0, 13.0])
    result = synchronize({"s1": s1, "s2": s2}, {"s1": t1, "s2": t2}, "common_grid_interpolate", {})
    assert len(result.t_common) > 0
    assert set(result.synced_series.keys()) == {"s1", "s2"}
