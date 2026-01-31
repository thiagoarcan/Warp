"""
Unit tests for processing/calculus.py

Tests cover:
- Derivative calculations (finite_diff, savitzky_golay, spline_derivative)
- Integral calculations (trapezoid, simpson, cumulative)
- Area between curves calculations
- Edge cases (NaN, empty, single point)
- Quality metrics generation
"""

from __future__ import annotations

import numpy as np
import pytest

from platform_base.processing.calculus import (
    area_between,
    area_between_with_crossings,
    derivative,
    integral,
)
from platform_base.utils.errors import CalculusError

# ============================================
# FIXTURES
# ============================================


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


@pytest.fixture
def large_dataset() -> dict[str, np.ndarray]:
    """Create a large dataset for performance tests."""
    n_points = 1_000_000
    return {
        "time": np.linspace(0, 1000, n_points),
        "value": np.sin(np.linspace(0, 100 * np.pi, n_points)),
    }


# ============================================
# DERIVATIVE TESTS - FINITE DIFFERENCE
# ============================================


class TestDerivativeFiniteDiff:
    """Tests for finite difference derivative method."""

    def test_derivative_finite_diff_first_order_linear(self) -> None:
        """First derivative of linear function should be constant."""
        t = np.linspace(0, 10, 1001)
        y = 2 * t + 3  # y = 2x + 3, dy/dx = 2

        result = derivative(y, t, order=1, method="finite_diff")

        # First derivative should be approximately 2 everywhere
        assert result.values is not None
        assert len(result.values) == len(t)
        np.testing.assert_allclose(result.values[1:-1], 2.0, atol=1e-10)
        assert result.operation == "derivative"
        assert result.order == 1

    def test_derivative_finite_diff_first_order_quadratic(
        self,
        quadratic_data: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """First derivative of x^2 should be 2x."""
        t, y = quadratic_data  # y = x^2

        result = derivative(y, t, order=1, method="finite_diff")

        # dy/dx = 2x
        expected = 2 * t
        # Use larger tolerance at endpoints due to finite diff approximation
        np.testing.assert_allclose(result.values[10:-10], expected[10:-10], rtol=0.01)

    def test_derivative_finite_diff_second_order_quadratic(
        self,
        quadratic_data: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Second derivative of x^2 should be 2."""
        t, y = quadratic_data  # y = x^2

        result = derivative(y, t, order=2, method="finite_diff")

        # d²y/dx² = 2
        # Interior points should be close to 2
        assert result.order == 2
        np.testing.assert_allclose(result.values[20:-20], 2.0, rtol=0.1)

    def test_derivative_finite_diff_third_order_cubic(self) -> None:
        """Third derivative of x^3 should be 6."""
        t = np.linspace(0, 5, 501)
        y = t ** 3  # y = x^3

        result = derivative(y, t, order=3, method="finite_diff")

        # d³y/dx³ = 6
        assert result.order == 3
        # Third order has more numerical noise, use larger tolerance
        np.testing.assert_allclose(result.values[50:-50], 6.0, rtol=0.5)

    def test_derivative_finite_diff_sine(
        self,
        sine_data: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """First derivative of sin(x) should be cos(x)."""
        t, y = sine_data  # y = sin(t)

        result = derivative(y, t, order=1, method="finite_diff")

        expected = np.cos(t)
        np.testing.assert_allclose(result.values[10:-10], expected[10:-10], atol=0.01)


# ============================================
# DERIVATIVE TESTS - SAVITZKY-GOLAY
# ============================================


class TestDerivativeSavitzkyGolay:
    """Tests for Savitzky-Golay derivative method."""

    def test_derivative_savitzky_golay_first_order(self) -> None:
        """Savitzky-Golay derivative of linear function."""
        t = np.linspace(0, 10, 101)
        y = 3 * t + 1

        result = derivative(
            y, t, order=1, method="savitzky_golay",
            params={"window_length": 7, "polyorder": 3},
        )

        # Should be approximately 3
        np.testing.assert_allclose(result.values[10:-10], 3.0, rtol=0.01)

    def test_derivative_savitzky_golay_second_order(self) -> None:
        """Savitzky-Golay second derivative of quadratic."""
        t = np.linspace(0, 10, 201)
        y = t ** 2

        result = derivative(
            y, t, order=2, method="savitzky_golay",
            params={"window_length": 11, "polyorder": 4},
        )

        # d²(x²)/dx² = 2
        np.testing.assert_allclose(result.values[20:-20], 2.0, rtol=0.2)


# ============================================
# DERIVATIVE TESTS - SPLINE
# ============================================


class TestDerivativeSpline:
    """Tests for spline derivative method."""

    def test_derivative_spline_first_order(self) -> None:
        """Spline derivative of smooth function."""
        t = np.linspace(0, 2 * np.pi, 201)
        y = np.sin(t)

        result = derivative(y, t, order=1, method="spline_derivative", params={"s": 0})

        expected = np.cos(t)
        np.testing.assert_allclose(result.values[5:-5], expected[5:-5], atol=0.05)


# ============================================
# DERIVATIVE TESTS - EDGE CASES
# ============================================


class TestDerivativeEdgeCases:
    """Tests for derivative edge cases."""

    def test_derivative_with_nan_values(self) -> None:
        """Derivative with NaN values in input."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        y[40:45] = np.nan

        result = derivative(y, t, order=1, method="finite_diff")

        # Result should contain NaN values around the gap
        assert np.any(np.isnan(result.values))
        assert result.quality_metrics.n_nan > 0

    def test_derivative_empty_array_raises(self) -> None:
        """Derivative with empty array should raise error."""
        t = np.array([])
        y = np.array([])

        with pytest.raises(CalculusError, match="Insufficient points"):
            derivative(y, t, order=1, method="finite_diff")

    def test_derivative_single_point_raises(self) -> None:
        """Derivative with single point should raise error."""
        t = np.array([0.0])
        y = np.array([1.0])

        with pytest.raises(CalculusError, match="Insufficient points"):
            derivative(y, t, order=1, method="finite_diff")

    def test_derivative_two_points(self) -> None:
        """Derivative with exactly two points should work."""
        t = np.array([0.0, 1.0])
        y = np.array([0.0, 2.0])  # slope = 2

        result = derivative(y, t, order=1, method="finite_diff")

        assert len(result.values) == 2
        np.testing.assert_allclose(result.values, [2.0, 2.0], rtol=1e-10)

    def test_derivative_invalid_order_raises(self) -> None:
        """Derivative with invalid order should raise error."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        with pytest.raises(CalculusError, match="Order must be between"):
            derivative(y, t, order=0, method="finite_diff")

        with pytest.raises(CalculusError, match="Order must be between"):
            derivative(y, t, order=4, method="finite_diff")

    def test_derivative_invalid_method_raises(self) -> None:
        """Derivative with invalid method should raise error."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        with pytest.raises(CalculusError, match="method not available"):
            derivative(y, t, order=1, method="invalid_method")  # type: ignore[arg-type]


# ============================================
# DERIVATIVE TESTS - METADATA
# ============================================


class TestDerivativeMetadata:
    """Tests for derivative metadata generation."""

    def test_derivative_generates_metadata(self) -> None:
        """Derivative should generate proper metadata."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        result = derivative(y, t, order=1, method="finite_diff")

        assert result.metadata is not None
        assert result.metadata.operation == "finite_diff"
        assert result.metadata.duration_ms >= 0

    def test_derivative_quality_metrics(self) -> None:
        """Derivative should generate quality metrics."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        result = derivative(y, t, order=1, method="finite_diff")

        assert result.quality_metrics is not None
        assert result.quality_metrics.n_valid == len(t)
        assert result.quality_metrics.n_nan == 0
        assert result.quality_metrics.n_interpolated == 0


# ============================================
# INTEGRAL TESTS - TRAPEZOID
# ============================================


class TestIntegralTrapezoid:
    """Tests for trapezoidal integration."""

    def test_integral_trapezoid_constant(
        self,
        constant_data: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Integral of constant 5 over [0,10] should be 50."""
        t, y = constant_data

        result = integral(y, t, method="trapezoid")

        expected_area = 5.0 * (t[-1] - t[0])
        np.testing.assert_allclose(result.values[0], expected_area, rtol=0.01)

    def test_integral_trapezoid_linear(
        self,
        linear_data: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Integral of 2x+1 over [0,10] should be x^2+x = 110."""
        t, y = linear_data

        result = integral(y, t, method="trapezoid")

        # ∫(2x+1)dx from 0 to 10 = [x²+x] from 0 to 10 = 100+10 = 110
        expected_area = 110.0
        np.testing.assert_allclose(result.values[0], expected_area, rtol=0.01)

    def test_integral_trapezoid_sine_full_period(self) -> None:
        """Integral of sin(x) over full period should be 0."""
        t = np.linspace(0, 2 * np.pi, 10001)
        y = np.sin(t)

        result = integral(y, t, method="trapezoid")

        np.testing.assert_allclose(result.values[0], 0.0, atol=1e-5)


# ============================================
# INTEGRAL TESTS - SIMPSON
# ============================================


class TestIntegralSimpson:
    """Tests for Simpson integration."""

    def test_integral_simpson_quadratic(self) -> None:
        """Simpson's rule should be exact for quadratics."""
        t = np.linspace(0, 5, 101)  # Odd number of points
        y = t ** 2

        result = integral(y, t, method="simpson")

        # ∫x²dx from 0 to 5 = [x³/3] = 125/3 ≈ 41.667
        expected_area = 125.0 / 3.0
        np.testing.assert_allclose(result.values[0], expected_area, rtol=0.01)


# ============================================
# INTEGRAL TESTS - CUMULATIVE
# ============================================


class TestIntegralCumulative:
    """Tests for cumulative integration."""

    def test_integral_cumulative_linear(self) -> None:
        """Cumulative integral of constant should be linear."""
        t = np.linspace(0, 10, 101)
        y = np.ones_like(t) * 2  # constant 2

        result = integral(y, t, method="cumulative")

        # Cumulative integral should be 2*t
        expected = 2 * t
        assert len(result.values) == len(t)
        np.testing.assert_allclose(result.values, expected, rtol=0.01)

    def test_integral_cumulative_starts_at_zero(self) -> None:
        """Cumulative integral should start at zero."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        result = integral(y, t, method="cumulative")

        assert result.values[0] == 0.0


# ============================================
# INTEGRAL TESTS - EDGE CASES
# ============================================


class TestIntegralEdgeCases:
    """Tests for integral edge cases."""

    def test_integral_with_nan_values(self) -> None:
        """Integral with NaN values in input."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        y[40:45] = np.nan

        result = integral(y, t, method="trapezoid")

        # Result should be NaN due to NaN in input
        assert np.isnan(result.values[0])

    def test_integral_empty_array_raises(self) -> None:
        """Integral with empty array should raise error."""
        t = np.array([])
        y = np.array([])

        with pytest.raises(CalculusError, match="Insufficient points"):
            integral(y, t, method="trapezoid")

    def test_integral_single_point_raises(self) -> None:
        """Integral with single point should raise error."""
        t = np.array([0.0])
        y = np.array([1.0])

        with pytest.raises(CalculusError, match="Insufficient points"):
            integral(y, t, method="trapezoid")

    def test_integral_invalid_method_raises(self) -> None:
        """Integral with invalid method should raise error."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        with pytest.raises(CalculusError, match="method not available"):
            integral(y, t, method="invalid_method")  # type: ignore[arg-type]


# ============================================
# AREA BETWEEN CURVES TESTS
# ============================================


class TestAreaBetweenCurves:
    """Tests for area between curves calculation."""

    def test_area_between_positive(
        self,
        two_curves_data: tuple[np.ndarray, np.ndarray, np.ndarray],
    ) -> None:
        """Area between y1=sin(x) and y2=0.5*sin(x) should be positive."""
        t, y1, y2 = two_curves_data

        result = area_between(y1, y2, t, method="trapezoid")

        # Area should be positive since y1 > y2
        assert result.values[0] > 0

    def test_area_between_negative(
        self,
        two_curves_data: tuple[np.ndarray, np.ndarray, np.ndarray],
    ) -> None:
        """Area between swapped curves should be negative."""
        t, y1, y2 = two_curves_data

        result = area_between(y2, y1, t, method="trapezoid")  # Swapped order

        # Area should be negative since y2 < y1
        assert result.values[0] < 0

    def test_area_between_symmetric(self) -> None:
        """Area between f and -f over symmetric interval should be 2*|area|."""
        t = np.linspace(-np.pi, np.pi, 1001)
        y_upper = np.abs(np.sin(t))
        y_lower = -np.abs(np.sin(t))

        result = area_between(y_upper, y_lower, t, method="trapezoid")

        # Area = 2 * ∫|sin(x)|dx from -π to π = 2 * 4 = 8
        np.testing.assert_allclose(result.values[0], 8.0, rtol=0.01)


# ============================================
# AREA BETWEEN WITH CROSSINGS TESTS
# ============================================


class TestAreaBetweenWithCrossings:
    """Tests for area between curves with crossing detection."""

    def test_area_between_crossing_curves(
        self,
        crossing_curves_data: tuple[np.ndarray, np.ndarray, np.ndarray],
    ) -> None:
        """Area calculation with curves that cross."""
        t, y1, y2 = crossing_curves_data  # sin and cos

        result = area_between_with_crossings(y1, y2, t, method="trapezoid")

        assert "total_area" in result
        assert "absolute_area" in result
        assert "positive_area" in result
        assert "negative_area" in result
        assert "crossings" in result

        # Absolute area should be larger than |total_area| when curves cross
        assert result["absolute_area"] >= abs(result["total_area"])


# ============================================
# AREA BETWEEN EDGE CASES
# ============================================


class TestAreaBetweenEdgeCases:
    """Tests for area between curves edge cases."""

    def test_area_between_mismatched_lengths_raises(self) -> None:
        """Area between with mismatched array lengths should raise error."""
        t = np.linspace(0, 10, 100)
        y1 = np.sin(t)
        y2 = np.cos(t)[:-10]  # Different length

        with pytest.raises(CalculusError, match="lengths must match"):
            area_between(y1, y2, t, method="trapezoid")

    def test_area_between_empty_raises(self) -> None:
        """Area between with empty arrays should raise error."""
        t = np.array([])
        y1 = np.array([])
        y2 = np.array([])

        with pytest.raises(CalculusError, match="Insufficient points"):
            area_between(y1, y2, t, method="trapezoid")

    def test_area_between_identical_curves(self) -> None:
        """Area between identical curves should be zero."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        result = area_between(y, y, t, method="trapezoid")

        np.testing.assert_allclose(result.values[0], 0.0, atol=1e-10)


# ============================================
# DERIVATIVE-INTEGRAL INVERSE RELATIONSHIP
# ============================================


class TestDerivativeIntegralInverse:
    """Tests for derivative-integral inverse relationship."""

    def test_integral_of_derivative_approximates_original(self) -> None:
        """Integral of derivative should approximate original minus constant."""
        t = np.linspace(0, 10, 1001)
        y = np.sin(t)

        # Calculate derivative
        deriv_result = derivative(y, t, order=1, method="finite_diff")

        # Calculate cumulative integral of derivative
        integ_result = integral(deriv_result.values, t, method="cumulative")

        # Should be approximately sin(t) - sin(0) = sin(t)
        # Need to add back the initial value
        reconstructed = integ_result.values + y[0]

        np.testing.assert_allclose(reconstructed[10:-10], y[10:-10], atol=0.1)


# ============================================
# PERFORMANCE TESTS
# ============================================


@pytest.mark.slow
class TestDerivativePerformance:
    """Performance tests for derivative calculation."""

    def test_derivative_large_dataset(self, large_dataset: dict[str, np.ndarray]) -> None:
        """Derivative should handle 1M points within time limit."""
        t = large_dataset["time"]
        y = large_dataset["value"]

        result = derivative(y, t, order=1, method="finite_diff")

        assert len(result.values) == len(t)
        assert result.metadata.duration_ms < 1000  # Should complete in < 1s


# ============================================
# SMOKE TESTS
# ============================================


@pytest.mark.smoke
class TestDerivativeSmokeTests:
    """Smoke tests for derivative functionality."""

    def test_derivative_basic_functionality(self) -> None:
        """Basic derivative calculation works."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        result = derivative(y, t, order=1, method="finite_diff")

        assert result is not None
        assert result.values is not None
        assert len(result.values) == len(t)
        assert result.metadata is not None
        assert result.quality_metrics is not None


@pytest.mark.smoke
class TestIntegralSmokeTests:
    """Smoke tests for integral functionality."""

    def test_integral_basic_functionality(self) -> None:
        """Basic integral calculation works."""
        t = np.linspace(0, 10, 100)
        y = np.sin(t)

        result = integral(y, t, method="trapezoid")

        assert result is not None
        assert result.values is not None
        assert result.metadata is not None
        assert result.quality_metrics is not None


# ============================================
# LEGACY TESTS (Existing tests preserved)
# ============================================


def test_derivative_linear():
    """Legacy test: derivative of linear function."""
    t = np.linspace(0, 10, 100)
    values = 2.0 * t + 1.0
    result = derivative(values, t, order=1, method="finite_diff", params={})
    assert np.allclose(result.values, 2.0, atol=1e-2)


def test_integral_constant():
    """Legacy test: integral of constant."""
    t = np.linspace(0, 5, 100)
    values = np.full_like(t, 3.0)
    result = integral(values, t)
    assert np.isclose(result.values[0], 15.0, atol=1e-2)


def test_area_between_legacy():
    """Legacy test: area between curves."""
    t = np.linspace(0, 5, 100)
    upper = np.full_like(t, 5.0)
    lower = np.full_like(t, 2.0)
    result = area_between(upper, lower, t)
    assert np.isclose(result.values[0], 15.0, atol=1e-2)

