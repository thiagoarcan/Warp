from __future__ import annotations

from datetime import datetime
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field
from pint import Unit

DatasetID = str
SeriesID = str
ViewID = str
SessionID = str


class SourceInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: str
    format: str
    loaded_at: datetime
    notes: Optional[str] = None


class DatasetMetadata(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    schema_confidence: float
    validation_warnings: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    timezone: str = "UTC"


class SeriesMetadata(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_column: str
    original_unit: Optional[str] = None
    tags: dict[str, str] = Field(default_factory=dict)


class InterpolationInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_interpolated_mask: NDArray[np.bool_]
    method_used: NDArray[np.str_]


class ResultMetadata(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str
    params: dict
    version: str
    timestamp: datetime
    seed: Optional[int] = None


class QualityMetrics(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    rmse: Optional[float] = None
    mae: Optional[float] = None


class Lineage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    origin_series: list[SeriesID]
    operation: str
    parameters: dict
    timestamp: datetime
    version: str


class Series(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    series_id: SeriesID
    name: str
    unit: Unit
    values: NDArray[np.float64]
    interpolation_info: Optional[InterpolationInfo]
    metadata: SeriesMetadata
    lineage: Lineage


class Dataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_id: DatasetID
    version: int
    parent_id: Optional[DatasetID]
    source: SourceInfo
    t_seconds: NDArray[np.float64]
    t_datetime: NDArray[np.datetime64]
    series: dict[SeriesID, Series]
    metadata: DatasetMetadata
    created_at: datetime


class TimeWindow(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    start_seconds: float
    end_seconds: float


class ViewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_id: DatasetID
    series: dict[SeriesID, NDArray[np.float64]]
    t_seconds: NDArray[np.float64]
    t_datetime: NDArray[np.datetime64]
    window: TimeWindow


class DerivedResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    values: NDArray[np.float64]
    metadata: ResultMetadata
    quality_metrics: Optional[QualityMetrics] = None


class InterpResult(DerivedResult):
    interpolation_info: InterpolationInfo


class CalcResult(DerivedResult):
    operation: str
    order: Optional[int] = None


class SyncResult(DerivedResult):
    t_common: NDArray[np.float64]
    synced_series: dict[SeriesID, NDArray[np.float64]]
    alignment_error: float
    confidence: float
