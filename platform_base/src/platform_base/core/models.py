from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

import numpy as np
from numpy.typing import NDArray
from pint import Unit
from pydantic import BaseModel, ConfigDict, Field


DatasetID = str
SeriesID = str
ViewID = str
SessionID = str


class SourceInfo(BaseModel):
    """Informação de origem do arquivo"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    filepath: str
    filename: str
    format: str  # csv, xlsx, parquet, hdf5
    size_bytes: int
    checksum: str  # SHA256
    loaded_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_file(cls, filepath: str) -> SourceInfo:
        """Cria SourceInfo a partir de um arquivo"""
        from pathlib import Path
        path_obj = Path(filepath)

        # Calcular checksum
        with open(filepath, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        return cls(
            filepath=str(path_obj.absolute()),
            filename=path_obj.name,
            format=path_obj.suffix.lower().lstrip("."),
            size_bytes=path_obj.stat().st_size,
            checksum=checksum,
        )


class DatasetMetadata(BaseModel):
    """Metadata do dataset"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    custom: dict[str, Any] = Field(default_factory=dict)
    schema_confidence: float = 1.0
    validation_warnings: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    timezone: str = "UTC"


class SeriesMetadata(BaseModel):
    """Metadata da série"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_name: str
    source_column: str
    original_unit: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    custom: dict[str, Any] = Field(default_factory=dict)


class InterpolationInfo(BaseModel):
    """Informa??o de interpola??o por ponto"""
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    is_interpolated_mask: NDArray[np.bool_] = Field(alias="is_interpolated")
    method_used: NDArray[np.str_]
    confidence: NDArray[np.float64] | None = None

    @property
    def is_interpolated(self) -> NDArray[np.bool_]:
        """Compatibilidade com nome anterior."""
        return self.is_interpolated_mask


class ResultMetadata(BaseModel):
    """Metadata de resultado de opera??o"""
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    operation: str
    parameters: dict[str, Any] = Field(default_factory=dict, alias="params")
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: float = 0.0
    platform_version: str = "2.0.0"
    seed: int | None = None

    @property
    def params(self) -> dict[str, Any]:
        return self.parameters


class QualityMetrics(BaseModel):
    """Métricas de qualidade do resultado"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    n_valid: int
    n_interpolated: int
    n_nan: int
    error_estimate: float | None = None
    rmse: float | None = None
    mae: float | None = None


class Lineage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    origin_series: list[SeriesID]
    operation: str
    parameters: dict
    timestamp: datetime
    version: str


class Series(BaseModel):
    """Série temporal"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    series_id: SeriesID
    name: str
    unit: Unit
    values: NDArray[np.float64]
    interpolation_info: InterpolationInfo | None = None
    metadata: SeriesMetadata
    lineage: Lineage | None = None


class Dataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_id: DatasetID
    version: int
    parent_id: DatasetID | None
    source: SourceInfo
    t_seconds: NDArray[np.float64]
    t_datetime: NDArray[np.datetime64]
    series: dict[SeriesID, Series]
    metadata: DatasetMetadata
    created_at: datetime


class TimeWindow(BaseModel):
    """Janela temporal"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    start: float  # segundos
    end: float  # segundos

    @property
    def duration(self) -> float:
        return self.end - self.start


class ViewData(BaseModel):
    """Dados preparados para visualização"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_id: DatasetID
    series: dict[SeriesID, NDArray[np.float64]]
    t_seconds: NDArray[np.float64]
    t_datetime: NDArray[np.datetime64]
    window: TimeWindow


class DerivedResult(BaseModel):
    """Base para resultados de operações"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    values: NDArray[np.float64]
    metadata: ResultMetadata
    quality_metrics: QualityMetrics | None = None


class InterpResult(DerivedResult):
    """Resultado de interpolação"""
    interpolation_info: InterpolationInfo


class CalcResult(DerivedResult):
    """Resultado de cálculo matemático"""
    operation: str  # derivative, integral, area
    order: int | None = None  # para derivadas


class SyncResult(DerivedResult):
    """Resultado de sincronização"""
    t_common: NDArray[np.float64]
    synced_series: dict[SeriesID, NDArray[np.float64]]
    alignment_error: float
    confidence: float


class DownsampleResult(DerivedResult):
    """Resultado de downsampling"""
    t_seconds: NDArray[np.float64]
    selected_indices: NDArray[np.int64]


class SeriesSummary(BaseModel):
    """Resumo de série para UI"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    series_id: SeriesID
    name: str
    unit: str
    n_points: int
    is_derived: bool = False
