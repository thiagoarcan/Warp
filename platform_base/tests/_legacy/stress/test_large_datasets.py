import os

import numpy as np
import pytest

from platform_base.processing.calculus import derivative


def test_large_dataset_derivative():
    if os.getenv("RUN_STRESS") != "1":
        pytest.skip("Stress tests disabled")
    n = 1_000_000
    t = np.linspace(0, 1000, n)
    values = np.sin(t)
    result = derivative(values, t, 1, "finite_diff", {})
    assert len(result.values) == n
