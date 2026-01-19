from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from platform_base.core.models import ViewData
from platform_base.viz.base import BaseFigure


def _downsample(t: np.ndarray, y: np.ndarray, max_points: int) -> tuple[np.ndarray, np.ndarray]:
    if len(t) <= max_points:
        return t, y
    idx = np.linspace(0, len(t) - 1, max_points).astype(int)
    return t[idx], y[idx]


class TimeseriesPlot(BaseFigure):
    def render(self, view_data: ViewData) -> go.Figure:
        fig = go.Figure()
        for i, (series_id, values) in enumerate(view_data.series.items()):
            t = view_data.t_seconds
            t_plot, v_plot = _downsample(t, values, self.config.downsample.max_points)
            color = self.config.colors.palette[i % len(self.config.colors.palette)]
            fig.add_trace(
                go.Scatter(
                    x=t_plot,
                    y=v_plot,
                    name=series_id,
                    mode="lines",
                    line=dict(color=color),
                )
            )
        fig.update_layout(
            title=self.config.title,
            showlegend=self.config.interactive.show_legend,
            hovermode=self.config.interactive.hover_mode,
            xaxis_title=self.config.axes.title,
        )
        return fig


class MultipanelPlot(BaseFigure):
    def render(self, panels: list[ViewData]) -> go.Figure:
        from plotly.subplots import make_subplots

        fig = make_subplots(rows=len(panels), cols=1, shared_xaxes=True)
        for row, panel in enumerate(panels, start=1):
            for i, (series_id, values) in enumerate(panel.series.items()):
                t_plot, v_plot = _downsample(
                    panel.t_seconds,
                    values,
                    self.config.downsample.max_points,
                )
                color = self.config.colors.palette[i % len(self.config.colors.palette)]
                fig.add_trace(
                    go.Scatter(x=t_plot, y=v_plot, name=series_id, mode="lines", line=dict(color=color)),
                    row=row,
                    col=1,
                )
        fig.update_layout(title=self.config.title, showlegend=self.config.interactive.show_legend)
        return fig
