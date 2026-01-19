from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from platform_base.viz.base import BaseFigure


class StateHeatmap(BaseFigure):
    def render(self, matrix: np.ndarray, axes: tuple[np.ndarray, np.ndarray]) -> go.Figure:
        fig = go.Figure(data=[go.Heatmap(z=matrix, x=axes[0], y=axes[1])])
        fig.update_layout(title=self.config.title)
        return fig
