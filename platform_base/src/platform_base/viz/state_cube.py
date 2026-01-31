from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.graph_objects as go

from platform_base.viz.base import BaseFigure


if TYPE_CHECKING:
    import numpy as np


class StateCube3D(BaseFigure):
    def render(self, states: np.ndarray) -> go.Figure:
        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=states[:, 0],
                    y=states[:, 1],
                    z=states[:, 2],
                    mode="markers",
                ),
            ],
        )
        fig.update_layout(title=self.config.title)
        return fig
