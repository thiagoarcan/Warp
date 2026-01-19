from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, filtfilt, medfilt, savgol_filter


@dataclass
class SmoothingConfig:
    method: str
    params: dict


def smooth(values: np.ndarray, method: str, params: dict) -> np.ndarray:
    if method == "savitzky_golay":
        window_length = params.get("window_length", 7)
        polyorder = params.get("polyorder", 3)
        return savgol_filter(values, window_length=window_length, polyorder=polyorder)

    if method == "gaussian":
        sigma = params.get("sigma", 1.0)
        return gaussian_filter1d(values, sigma=sigma)

    if method == "median":
        kernel_size = params.get("kernel_size", 5)
        return medfilt(values, kernel_size=kernel_size)

    if method == "lowpass":
        cutoff = params.get("cutoff", 0.1)
        order = params.get("order", 3)
        b, a = butter(order, cutoff, btype="low")
        return filtfilt(b, a, values)

    raise ValueError(f"Unknown smoothing method: {method}")
