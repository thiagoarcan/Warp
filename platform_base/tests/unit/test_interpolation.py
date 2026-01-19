import numpy as np

from platform_base.processing.interpolation import interpolate


def test_linear_interpolation_fills_nans():
    t = np.array([0.0, 1.0, 2.0, 3.0])
    values = np.array([1.0, np.nan, 3.0, np.nan])
    result = interpolate(values, t, method="linear", params={})
    assert np.isfinite(result.values).all()
    assert result.interpolation_info.is_interpolated_mask.sum() == 2
