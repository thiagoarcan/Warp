from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


@dataclass
class SyntheticDataGenerator:
    def generate_timeseries(
        self,
        n_points: int,
        n_series: int,
        irregularity: float,
        noise: float,
        gaps: list[tuple[int, int]],
        seed: int = 42,
    ) -> pd.DataFrame:
        np.random.seed(seed)
        if irregularity > 0:
            deltas = np.random.exponential(1.0 / irregularity, n_points)
            t = np.cumsum(deltas)
        else:
            t = np.linspace(0, n_points, n_points)

        timestamps = [datetime(2024, 1, 1) + timedelta(seconds=float(s)) for s in t]
        data = {}
        for i in range(n_series):
            signal = np.sin(2 * np.pi * t / (n_points / 10))
            signal += np.random.normal(0, noise, n_points)
            data[f"series_{i}"] = signal

        df = pd.DataFrame(data, index=timestamps)
        df.index.name = "timestamp"

        for start, end in gaps:
            df.iloc[start:end] = np.nan

        return df.reset_index()
