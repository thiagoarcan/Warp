import numpy as np

from platform_base.processing.units import normalize_units, parse_unit


def test_unit_parse_dimensionless():
    unit = parse_unit(None)
    assert str(unit) == "dimensionless"


def test_normalize_units_bar_to_bar():
    values = np.array([1.0, 2.0])
    result = normalize_units(values, "bar", "bar")
    assert np.allclose(result, values)
