from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import plotly.graph_objects as go

from platform_base.viz.base import BaseFigure


if TYPE_CHECKING:
    import numpy as np

    from platform_base.ui.state import Selection


class StateCube3D(BaseFigure):
    """3D State Cube visualization for state-space analysis."""

    def render(self, states: np.ndarray) -> go.Figure:
        """Render 3D scatter plot of states.
        
        Args:
            states: Nx3 array of 3D coordinates
            
        Returns:
            Plotly Figure with 3D scatter
        """
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

    def export(self, path: Path, format: str = "png") -> None:
        """Export the figure to file.
        
        Args:
            path: Output file path
            format: Export format (png, html, svg, etc.)
        """
        # Create a placeholder figure for export
        fig = go.Figure()
        fig.update_layout(title=self.config.title)

        if format == "html":
            fig.write_html(str(path))
        else:
            fig.write_image(str(path), format=format)

    def update_selection(self, selection: Selection) -> None:
        """Update visualization based on selection.
        
        Args:
            selection: Current selection state
        """
        # StateCube3D doesn't support selection updates in basic form
