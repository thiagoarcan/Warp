from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import json
import pandas as pd

from platform_base.ui.selection import Selection
from platform_base.utils.errors import ExportError
from platform_base.utils.serialization import to_jsonable


@dataclass
class ExportResult:
    path: Path


@dataclass
class ExportProgress:
    percent: float


def _selection_to_df(selection: Selection) -> pd.DataFrame:
    data = {"t_seconds": selection.t_seconds}
    data.update(selection.series)
    return pd.DataFrame(data)


def export_selection(selection: Selection, format: str, output_path: Path) -> ExportResult:
    df = _selection_to_df(selection)
    if format == "csv":
        df.to_csv(output_path, index=False)
    elif format == "xlsx":
        df.to_excel(output_path, index=False)
    elif format == "parquet":
        df.to_parquet(output_path, index=False)
    elif format == "hdf5":
        df.to_hdf(output_path, key="data", mode="w")
    else:
        raise ExportError("Unsupported export format", {"format": format})
    return ExportResult(path=output_path)


def export_session(output_path: Path, session_data: dict) -> ExportResult:
    payload = json.dumps(to_jsonable(session_data), indent=2)
    output_path.write_text(payload, encoding="utf-8")
    return ExportResult(path=output_path)


def export_large_dataset(dataset_id, output_path: Path, chunk_size_mb: int = 50) -> Iterator[ExportProgress]:
    _ = (dataset_id, output_path, chunk_size_mb)
    yield ExportProgress(percent=100.0)
