from __future__ import annotations

from typing import TYPE_CHECKING

import pint


if TYPE_CHECKING:
    import numpy as np


ureg = pint.UnitRegistry()


def parse_unit(unit_str: str | None) -> pint.Unit:
    if not unit_str:
        return ureg.dimensionless
    return ureg.parse_units(unit_str)


def infer_unit_from_name(name: str) -> str | None:
    lower = name.lower()
    if "bar" in lower:
        return "bar"
    if "psi" in lower:
        return "psi"
    if "c" in lower and "temp" in lower:
        return "degC"
    return None


def normalize_units(values: np.ndarray, from_unit: str, to_unit: str) -> np.ndarray:
    quantity = values * parse_unit(from_unit)
    return quantity.to(to_unit).magnitude
