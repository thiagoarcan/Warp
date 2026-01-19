from __future__ import annotations

import dash
import dash_bootstrap_components as dbc

from platform_base.core.dataset_store import DatasetStore
from platform_base.ui.callbacks import register_callbacks
from platform_base.ui.layout import build_layout


def create_app(store: DatasetStore | None = None) -> dash.Dash:
    store = store or DatasetStore()
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = build_layout()
    register_callbacks(app, store)
    return app


def run():
    app = create_app()
    app.run_server(debug=False)
