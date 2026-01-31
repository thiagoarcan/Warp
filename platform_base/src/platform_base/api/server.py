from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from platform_base.core.dataset_store import DatasetStore
from platform_base.io.loader import load
from platform_base.processing.interpolation import interpolate
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from platform_base.core.models import TimeWindow


logger = get_logger(__name__)


class InterpolationRequest(BaseModel):
    method: str
    params: dict = {}


class ViewRequest(BaseModel):
    series_ids: list[str]
    window: TimeWindow


def create_app(store: DatasetStore | None = None) -> FastAPI:
    store = store or DatasetStore()
    app = FastAPI(title="Platform Base API", version="2.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/datasets/upload")
    async def upload_dataset(file: UploadFile = File(...)):
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        dataset = load(tmp_path)
        dataset_id = store.add_dataset(dataset)
        return {"dataset_id": dataset_id}

    @app.get("/datasets")
    def list_datasets():
        return [{"dataset_id": ds.dataset_id, "n_series": ds.n_series} for ds in store.list_datasets()]

    @app.get("/datasets/{dataset_id}/series")
    def list_series(dataset_id: str):
        return [{"series_id": s.series_id, "name": s.name} for s in store.list_series(dataset_id)]

    @app.post("/datasets/{dataset_id}/series/{series_id}/interpolate")
    def interpolate_series(dataset_id: str, series_id: str, request: InterpolationRequest):
        dataset = store.get_dataset(dataset_id)
        series = dataset.series[series_id]
        result = interpolate(series.values, dataset.t_seconds, request.method, request.params)
        return {"values": result.values.tolist(), "method": result.metadata.method}

    @app.post("/datasets/{dataset_id}/view")
    def create_view(dataset_id: str, request: ViewRequest):
        view = store.create_view(dataset_id, request.series_ids, request.window)
        return {"t_seconds": view.t_seconds.tolist(), "series": {k: v.tolist() for k, v in view.series.items()}}

    logger.info("api_ready")
    return app
