from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from platform_base.core.models import (
    Dataset,
    DatasetMetadata,
    InterpolationInfo,
    Lineage,
    Series,
    SeriesMetadata,
    SourceInfo,
)
from platform_base.io.schema_detector import SchemaRules, detect_schema
from platform_base.io.validator import validate_time, validate_values
from platform_base.processing.timebase import to_seconds
from platform_base.processing.units import infer_unit_from_name, parse_unit
from platform_base.utils.errors import DataLoadError
from platform_base.utils.ids import new_id
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class LoadConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    timestamp_column: Optional[str] = None
    unit_overrides: dict[str, str] = Field(default_factory=dict)
    timezone: str = "UTC"
    sheet_name: Optional[str | int] = 0
    max_rows: Optional[int] = None
    max_missing_ratio: float = 0.95
    schema_rules: SchemaRules = Field(default_factory=SchemaRules)


def _detect_format(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".csv", ".txt"}:
        return "csv"
    if ext in {".xlsx", ".xls"}:
        return "excel"
    if ext in {".parquet", ".pq"}:
        return "parquet"
    if ext in {".h5", ".hdf5"}:
        return "hdf5"
    raise DataLoadError("Unsupported file format", {"path": str(path)})


def _read_file(path: Path, fmt: str, config: LoadConfig) -> pd.DataFrame:
    if fmt == "csv":
        return pd.read_csv(path, nrows=config.max_rows)
    if fmt == "excel":
        return pd.read_excel(path, sheet_name=config.sheet_name, nrows=config.max_rows)
    if fmt == "parquet":
        return pd.read_parquet(path)
    if fmt == "hdf5":
        return pd.read_hdf(path)
    raise DataLoadError("Unsupported file format", {"format": fmt})


def load(path: str, config: dict | LoadConfig | None = None) -> Dataset:
    cfg = config if isinstance(config, LoadConfig) else LoadConfig(**(config or {}))
    path_obj = Path(path)
    fmt = _detect_format(path_obj)
    df = _read_file(path_obj, fmt, cfg)

    schema = detect_schema(df, cfg.schema_rules)
    timestamp_column = cfg.timestamp_column or schema.timestamp_column

    time_report = validate_time(df, timestamp_column)
    candidate_names = [c.name for c in schema.candidate_series]
    values_report = validate_values(df, candidate_names, max_missing_ratio=cfg.max_missing_ratio)

    if timestamp_column == "__index__":
        timestamps = pd.to_datetime(df.index, errors="coerce")
    else:
        timestamps = pd.to_datetime(df[timestamp_column], errors="coerce")

    t_datetime = timestamps.to_numpy()
    t_seconds = to_seconds(t_datetime)

    series_dict: dict[str, Series] = {}
    for candidate in schema.candidate_series:
        values = pd.to_numeric(df[candidate.name], errors="coerce").to_numpy(dtype=float)
        unit_str = cfg.unit_overrides.get(candidate.name)
        if unit_str is None:
            unit_str = infer_unit_from_name(candidate.name)
        unit = parse_unit(unit_str)
        method_used = np.where(np.isnan(values), "missing", "original")
        interpolation_info = InterpolationInfo(
            is_interpolated_mask=np.zeros(len(values), dtype=bool),
            method_used=method_used.astype("<U32"),
        )
        metadata = SeriesMetadata(source_column=candidate.name, original_unit=unit_str)
        lineage = Lineage(
            origin_series=[],
            operation="load",
            parameters={"path": str(path_obj)},
            timestamp=datetime.utcnow(),
            version="2.0.0",
        )
        series_dict[candidate.name] = Series(
            series_id=candidate.name,
            name=candidate.name,
            unit=unit,
            values=values,
            interpolation_info=interpolation_info,
            metadata=metadata,
            lineage=lineage,
        )

    metadata = DatasetMetadata(
        schema_confidence=schema.confidence,
        validation_warnings=[w.message for w in time_report.warnings + values_report.warnings],
        validation_errors=[e.message for e in time_report.errors + values_report.errors],
        timezone=cfg.timezone,
    )

    dataset = Dataset(
        dataset_id=new_id("dataset"),
        version=1,
        parent_id=None,
        source=SourceInfo(path=str(path_obj), format=fmt, loaded_at=datetime.utcnow()),
        t_seconds=t_seconds,
        t_datetime=t_datetime,
        series=series_dict,
        metadata=metadata,
        created_at=datetime.utcnow(),
    )

    logger.info(
        "dataset_loaded",
        dataset_id=dataset.dataset_id,
        n_series=len(dataset.series),
        n_points=len(dataset.t_seconds),
    )
    return dataset
