from __future__ import annotations

from typing import Literal

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import BaseModel, ConfigDict, Field


class PanelConfig(BaseModel):
    """Configuração de painel conforme PRD seção 12.1"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    position: Literal["left", "center", "right", "bottom"] = "center"
    width: float = 0.33  # fração da largura total
    collapsible: bool = True
    default_collapsed: bool = False


class LayoutConfig(BaseModel):
    """Layout responsivo e configurável conforme PRD seção 12.1"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    areas: list[PanelConfig] = Field(
        default_factory=lambda: [
            PanelConfig(name="data", position="left", width=0.25),
            PanelConfig(name="viz", position="center", width=0.50),
            PanelConfig(name="config", position="right", width=0.25),
        ],
    )
    responsive: bool = True
    breakpoints: dict[str, int] = Field(default_factory=lambda: {
        "mobile": 768,
        "tablet": 1024,
        "desktop": 1440,
    })


def _create_data_panel() -> dbc.Card:
    """Cria painel de dados e upload"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("📊 Data", className="mb-0"),
        ]),
        dbc.CardBody([
            # Upload Section
            html.H6("Upload Dataset", className="mb-2"),
            dcc.Upload(
                id="upload-data",
                children=html.Div([
                    "Drag and Drop or ",
                    html.A("Select File", href="#"),
                ]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,
            ),

            html.Hr(),

            # Dataset Selection
            html.H6("Select Dataset", className="mb-2"),
            dcc.Dropdown(
                id="dataset-dropdown",
                options=[],
                placeholder="Choose dataset...",
                className="mb-3",
            ),

            # Series Selection
            html.H6("Select Series", className="mb-2"),
            dcc.Dropdown(
                id="series-dropdown",
                options=[],
                multi=True,
                placeholder="Choose series...",
                className="mb-3",
            ),

            # Time Range Selection
            html.H6("Time Range", className="mb-2"),
            dcc.RangeSlider(
                id="time-range-slider",
                marks={},
                step=1,
                className="mb-3",
            ),
        ]),
    ], className="h-100")


def _create_viz_panel() -> dbc.Card:
    """Cria painel de visualização"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("📈 Visualization", className="mb-0"),
            dbc.ButtonGroup([
                dbc.Button("2D", id="btn-2d", size="sm", outline=True),
                dbc.Button("3D", id="btn-3d", size="sm", outline=True),
                dbc.Button("Stream", id="btn-stream", size="sm", outline=True),
            ], className="ms-auto"),
        ], className="d-flex align-items-center"),
        dbc.CardBody([
            # Main Plot
            dcc.Graph(
                id="main-plot",
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": "platform_base_plot",
                        "height": 600,
                        "width": 1000,
                        "scale": 1,
                    },
                },
                style={"height": "400px"},
            ),

            # Streaming Controls
            dbc.Collapse([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🎬 Streaming Controls", className="mb-2"),
                        dbc.ButtonGroup([
                            dbc.Button("⏮", id="btn-first", size="sm", color="secondary"),
                            dbc.Button("⏪", id="btn-backward", size="sm", color="secondary"),
                            dbc.Button("⏸", id="btn-pause", size="sm", color="warning"),
                            dbc.Button("▶", id="btn-play", size="sm", color="success"),
                            dbc.Button("⏩", id="btn-forward", size="sm", color="secondary"),
                            dbc.Button("⏭", id="btn-last", size="sm", color="secondary"),
                        ], className="w-100 mb-2"),

                        html.Label("Speed:"),
                        dcc.Slider(
                            id="speed-slider",
                            min=0.1,
                            max=5.0,
                            step=0.1,
                            value=1.0,
                            marks={0.1: "0.1x", 1.0: "1x", 2.0: "2x", 5.0: "5x"},
                            className="mb-2",
                        ),

                        html.Label("Window Size (seconds):"),
                        dcc.Input(
                            id="window-size",
                            type="number",
                            value=60,
                            min=1,
                            max=3600,
                            className="form-control mb-2",
                        ),

                        dbc.Checklist(
                            options=[
                                {"label": "Loop", "value": "loop"},
                                {"label": "Hide interpolated", "value": "hide_interp"},
                                {"label": "Export video", "value": "export_video"},
                            ],
                            value=[],
                            id="streaming-options",
                            inline=True,
                        ),
                    ]),
                ], color="light", outline=True),
            ], id="streaming-controls", is_open=False),

        ]),
    ], className="h-100")


def _create_config_panel() -> dbc.Card:
    """Cria painel de configuração"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("⚙️ Processing", className="mb-0"),
        ]),
        dbc.CardBody([
            # Interpolation Section
            html.H6("Interpolation", className="mb-2"),
            dcc.Dropdown(
                id="interp-method",
                options=[
                    {"label": "Linear", "value": "linear"},
                    {"label": "Cubic Spline", "value": "spline_cubic"},
                    {"label": "Smoothing Spline", "value": "smoothing_spline"},
                    {"label": "Resample Grid", "value": "resample_grid"},
                    {"label": "Moving Least Squares (MLS)", "value": "mls"},
                    {"label": "Gaussian Process (GPR)", "value": "gpr"},
                    {"label": "Lomb-Scargle Spectral", "value": "lomb_scargle_spectral"},
                ],
                value="linear",
                className="mb-2",
            ),

            html.Hr(),

            # Calculus Section
            html.H6("Calculus", className="mb-2"),
            dcc.Dropdown(
                id="calc-operation",
                options=[
                    {"label": "None", "value": "none"},
                    {"label": "1st Derivative", "value": "derivative_1"},
                    {"label": "2nd Derivative", "value": "derivative_2"},
                    {"label": "3rd Derivative", "value": "derivative_3"},
                    {"label": "Integral", "value": "integral"},
                ],
                value="none",
                className="mb-2",
            ),

            dcc.Dropdown(
                id="calc-method",
                options=[
                    {"label": "Finite Difference", "value": "finite_diff"},
                    {"label": "Savitzky-Golay", "value": "savitzky_golay"},
                    {"label": "Spline", "value": "spline_derivative"},
                ],
                value="finite_diff",
                className="mb-2",
            ),

            html.Hr(),

            # Synchronization Section
            html.H6("Synchronization", className="mb-2"),
            dcc.Dropdown(
                id="sync-method",
                options=[
                    {"label": "None", "value": "none"},
                    {"label": "Common Grid", "value": "common_grid_interpolate"},
                    {"label": "Kalman Align", "value": "kalman_align"},
                ],
                value="none",
                className="mb-2",
            ),

            html.Hr(),

            # Export Section
            html.H6("Export", className="mb-2"),
            dbc.ButtonGroup([
                dbc.Button("CSV", id="btn-export-csv", size="sm", color="primary", outline=True),
                dbc.Button("Excel", id="btn-export-xlsx", size="sm", color="primary", outline=True),
                dbc.Button("Parquet", id="btn-export-parquet", size="sm", color="primary", outline=True),
            ], className="w-100 mb-2"),

            dbc.Button(
                "💾 Export Session",
                id="btn-export-session",
                size="sm",
                color="secondary",
                className="w-100",
            ),
        ]),
    ], className="h-100")


def build_layout(config: LayoutConfig | None = None) -> html.Div:
    """
    Constrói layout responsivo conforme PRD seção 12.1

    Áreas configuráveis:
    - DataPanel (upload + datasets + series)
    - VizPanel (2D/3D/heatmap/cube)
    - ConfigPanel (métodos + streaming + perf)
    - ResultsPanel (tabelas + logs + export)

    Suporta mobile/diferentes resoluções via dash-bootstrap-components.
    """
    config or LayoutConfig()

    return dbc.Container([
        # Global stores for app state
        dcc.Store(id="app-state", data={}),
        dcc.Store(id="dataset-store", data={}),
        dcc.Store(id="streaming-state", data={}),
        dcc.Store(id="selection-store", data={}),

        # Interval for streaming updates
        dcc.Interval(id="streaming-interval", interval=100, disabled=True),

        # Progress bar for async operations
        dbc.Progress(
            id="progress-bar",
            style={"display": "none", "margin": "10px 0"},
        ),

        # Toast notifications
        html.Div(id="notifications"),

        # Main Layout - Responsive Grid
        dbc.Row([
            # Left Panel - Data
            dbc.Col(
                _create_data_panel(),
                width={"size": 3, "order": 1},
                lg=3,
                md=4,
                sm=12,
                xs=12,
            ),

            # Center Panel - Visualization
            dbc.Col(
                _create_viz_panel(),
                width={"size": 6, "order": 2},
                lg=6,
                md=8,
                sm=12,
                xs=12,
            ),

            # Right Panel - Config
            dbc.Col(
                _create_config_panel(),
                width={"size": 3, "order": 3},
                lg=3,
                md=12,
                sm=12,
                xs=12,
            ),
        ], className="g-3"),

        # Bottom area for results/logs (collapsible)
        dbc.Row([
            dbc.Col([
                dbc.Collapse([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📊 Results & Logs", className="mb-0"),
                            dbc.Button(
                                "×",
                                id="btn-close-results",
                                size="sm",
                                color="light",
                                className="ms-auto",
                            ),
                        ], className="d-flex align-items-center"),
                        dbc.CardBody([
                            dbc.Tabs([
                                dbc.Tab(label="Statistics", tab_id="stats"),
                                dbc.Tab(label="Logs", tab_id="logs"),
                                dbc.Tab(label="Performance", tab_id="perf"),
                            ], id="results-tabs", active_tab="stats"),
                            html.Div(id="results-content"),
                        ]),
                    ]),
                ], id="results-collapse", is_open=False),
            ], width=12),
        ], className="mt-3"),

    ], fluid=True, className="p-3")
