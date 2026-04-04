import numpy as np
import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st

from platform_base.processing.calculus import derivative, integral


@given(st.lists(st.floats(min_value=-10, max_value=10), min_size=20, max_size=50))
def test_derivative_integral_relation(samples):
    t = np.linspace(0, 1, len(samples))
    values = np.array(samples, dtype=float)
    integ = integral(values, t)
    deriv = derivative(values, t, 1, "finite_diff", {})
    assert len(deriv.values) == len(values)
    assert np.isfinite(integ.values[0])
