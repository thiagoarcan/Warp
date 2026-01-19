import numpy as np

from platform_base.processing.smoothing import smooth


def test_smooth_returns_same_length():
    values = np.random.randn(100)
    result = smooth(values, "gaussian", {"sigma": 1.0})
    assert len(result) == len(values)
