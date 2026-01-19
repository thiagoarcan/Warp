import numpy as np

from platform_base.processing.calculus import area_between, derivative, integral


def test_derivative_linear():
    t = np.linspace(0, 10, 100)
    values = 2.0 * t + 1.0
    result = derivative(values, t, order=1, method="finite_diff", params={})
    assert np.allclose(result.values, 2.0, atol=1e-2)


def test_integral_constant():
    t = np.linspace(0, 5, 100)
    values = np.full_like(t, 3.0)
    result = integral(values, t)
    assert np.isclose(result.values[0], 15.0, atol=1e-2)


def test_area_between():
    t = np.linspace(0, 5, 100)
    upper = np.full_like(t, 5.0)
    lower = np.full_like(t, 2.0)
    result = area_between(upper, lower, t)
    assert np.isclose(result.values[0], 15.0, atol=1e-2)
