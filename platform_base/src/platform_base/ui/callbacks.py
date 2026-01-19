from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from dash import Input, Output, State, callback

from platform_base.io.loader import load
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def register_callbacks(app, store):
    @callback(
        Output("dataset-dropdown", "options"),
        Output("dataset-store", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def _on_upload(contents, filename):
        if contents is None:
            return [], None
        _, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(decoded)
            tmp_path = tmp.name
        dataset = load(tmp_path, config={"max_rows": 10000})
        dataset_id = store.add_dataset(dataset)
        logger.info("upload_loaded", dataset_id=dataset_id, filename=filename)
        return [{"label": dataset_id, "value": dataset_id}], dataset_id

    @callback(
        Output("series-dropdown", "options"),
        Input("dataset-store", "data"),
        prevent_initial_call=True,
    )
    def _update_series(dataset_id):
        if not dataset_id:
            return []
        dataset = store.get_dataset(dataset_id)
        return [{"label": name, "value": name} for name in dataset.series.keys()]
