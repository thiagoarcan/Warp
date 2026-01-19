from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from platform_base.viz.base import BaseFigure


class Trajectory3D(BaseFigure):
    def render(self, points_3d: np.ndarray) -> go.Figure:
        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=points_3d[:, 0],
                    y=points_3d[:, 1],
                    z=points_3d[:, 2],
                    mode="lines",
                )
            ]
        )
        fig.update_layout(title=self.config.title)
        return fig
