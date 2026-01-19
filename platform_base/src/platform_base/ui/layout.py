from __future__ import annotations

from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import BaseModel, ConfigDict, Field


class PanelConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    title: str


class LayoutConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    areas: list[PanelConfig] = Field(
        default_factory=lambda: [
            PanelConfig(id="data-panel", title="Data"),
            PanelConfig(id="viz-panel", title="Visualization"),
            PanelConfig(id="config-panel", title="Config"),
            PanelConfig(id="results-panel", title="Results"),
        ]
    )
    responsive: bool = True
    breakpoints: dict[str, int] = Field(default_factory=lambda: {"mobile": 768, "desktop": 1024})


def build_layout(config: Optional[LayoutConfig] = None) -> html.Div:
    cfg = config or LayoutConfig()
    return dbc.Container(
        fluid=True,
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("Upload"),
                            dcc.Upload(id="upload-data", children=html.Div(["Drag and Drop or Select File"])),
                            dcc.Dropdown(id="dataset-dropdown", options=[], placeholder="Select dataset"),
                            dcc.Dropdown(id="series-dropdown", options=[], multi=True, placeholder="Select series"),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="timeseries-plot"),
                            dcc.Store(id="dataset-store"),
                        ],
                        md=9,
                    ),
                ]
            ),
        ],
    )
