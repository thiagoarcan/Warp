from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator

from platform_base.core.models import (
    Dataset,
    DatasetMetadata,
    InterpolationInfo,
    Lineage,
    Series,
    SeriesMetadata,
    SourceInfo,
)
from platform_base.io.encoding_detector import detect_encoding
from platform_base.io.schema_detector import SchemaRules, detect_schema
from platform_base.io.validator import validate_time, validate_values
from platform_base.processing.timebase import to_seconds
from platform_base.processing.units import infer_unit_from_name, parse_unit
from platform_base.utils.errors import DataLoadError
from platform_base.utils.ids import new_id
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class FileFormat(Enum):
    """Formatos de arquivo suportados"""
    CSV = "csv"
    EXCEL = "xlsx"
    PARQUET = "parquet"
    HDF5 = "hdf5"

    @classmethod
    def from_extension(cls, ext: str) -> FileFormat:
        """Detecta formato a partir da extensão"""
        ext_lower = ext.lower().lstrip(".")
        mapping = {
            "csv": cls.CSV,
            "txt": cls.CSV,
            "xlsx": cls.EXCEL,
            "xls": cls.EXCEL,
            "parquet": cls.PARQUET,
            "pq": cls.PARQUET,
            "h5": cls.HDF5,
            "hdf5": cls.HDF5,
        }
        if ext_lower not in mapping:
            raise DataLoadError(f"Unsupported file extension: {ext}", {"extension": ext})
        return mapping[ext_lower]


class LoadStrategy(BaseModel):
    """Estratégia de carregamento por formato"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    format: FileFormat
    reader_params: dict[str, Any] = Field(default_factory=dict)
    preprocessing: Callable[[pd.DataFrame], pd.DataFrame] | None = None

    def read_file(self, path: Path, config: LoadConfig) -> pd.DataFrame:
        """Le arquivo usando estratégia específica"""
        if self.format == FileFormat.CSV:
            # Auto-detect encoding se configurado
            encoding = config.encoding
            if encoding == "auto":
                encoding = detect_encoding(path)
                logger.info(f"auto_detected_encoding: {encoding}")

            params = {
                "delimiter": config.delimiter,
                "encoding": encoding,
                "nrows": config.max_rows,
                **self.reader_params,
            }
            df = pd.read_csv(path, **params)

        elif self.format == FileFormat.EXCEL:
            # Ensure sheet_name defaults to 0 (first sheet) to avoid returning dict
            sheet = config.sheet_name if config.sheet_name is not None else 0
            params = {
                "sheet_name": sheet,
                "nrows": config.max_rows,
                **self.reader_params,
            }
            df = pd.read_excel(path, **params)

            # Handle case where dict is returned (shouldn't happen with sheet_name set)
            if isinstance(df, dict):
                # Get first sheet
                df = next(iter(df.values()))

        elif self.format == FileFormat.PARQUET:
            df = pd.read_parquet(path, **self.reader_params)
            if config.max_rows:
                df = df.head(config.max_rows)

        elif self.format == FileFormat.HDF5:
            # Para HDF5, permite especificar key
            key = config.hdf5_key or "/data"
            df = pd.read_hdf(path, key=key, **self.reader_params)
            if config.max_rows:
                df = df.head(config.max_rows)
        else:
            raise DataLoadError(f"Unsupported format: {self.format}", {"format": self.format.value})

        # Aplica pré-processamento se definido
        if self.preprocessing:
            df = self.preprocessing(df)

        return df


def _parse_timestamps(data: pd.Series | pd.Index) -> pd.DatetimeIndex:
    """
    Parse timestamps robustly, trying common formats to avoid pandas warnings.

    Args:
        data: Series or Index containing timestamp data

    Returns:
        DatetimeIndex with parsed timestamps
    """
    # If already datetime, just convert
    if pd.api.types.is_datetime64_any_dtype(data):
        return pd.DatetimeIndex(data)

    # Common datetime formats to try (most specific first)
    formats = [
        "%Y-%m-%d %H:%M:%S",      # 2025-08-10 00:00:00
        "%Y-%m-%d %H:%M:%S.%f",   # 2025-08-10 00:00:00.123456
        "%Y-%m-%dT%H:%M:%S",      # ISO format
        "%Y-%m-%dT%H:%M:%S.%f",   # ISO with microseconds
        "%Y-%m-%d",               # Date only
        "%d/%m/%Y %H:%M:%S",      # Brazilian format
        "%d/%m/%Y",               # Brazilian date only
        "%m/%d/%Y %H:%M:%S",      # US format
        "%m/%d/%Y",               # US date only
    ]

    # Try each format
    for fmt in formats:
        try:
            result = pd.to_datetime(data, format=fmt, errors="raise")
            logger.debug("timestamp_format_detected", format=fmt)
            return result
        except (ValueError, TypeError):
            continue

    # Fallback: let pandas infer (will generate warning for mixed formats)
    logger.debug("timestamp_format_fallback", message="Using pandas inference")
    return pd.to_datetime(data, errors="coerce")


class LoadConfig(BaseModel):
    """Configuração de carregamento conforme especificação seção 6.1"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Configurações básicas
    timestamp_column: str | None = None  # auto-detect se None
    delimiter: str = ","
    encoding: str = "auto"  # "auto" para detecção automática
    sheet_name: str | int | None = 0  # para Excel
    hdf5_key: str | None = "/data"  # para HDF5

    # Configurações de performance
    max_rows: int | None = None
    chunk_size: int | None = None

    # Configurações de validação
    max_missing_ratio: float = 0.95
    min_valid_points: int = 10

    # Configurações de unidades e timezone
    unit_overrides: dict[str, str] = Field(default_factory=dict)
    timezone: str = "UTC"

    # Configurações de schema
    schema_rules: SchemaRules = Field(default_factory=SchemaRules)

    # Configurações de estratégia
    custom_strategy: LoadStrategy | None = None

    @field_validator("max_missing_ratio")
    @classmethod
    def validate_missing_ratio(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("max_missing_ratio deve estar entre 0 e 1")
        return v

    @field_validator("min_valid_points")
    @classmethod
    def validate_min_points(cls, v: int) -> int:
        if v < 1:
            raise ValueError("min_valid_points deve ser >= 1")
        return v


def _get_default_strategy(fmt: FileFormat) -> LoadStrategy:
    """Obtém estratégia padrão para formato"""
    return LoadStrategy(format=fmt)


def _create_source_info(path: Path, fmt: FileFormat) -> SourceInfo:
    """Cria SourceInfo com checksum conforme especificação"""
    # Calcula checksum SHA256
    with open(path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    return SourceInfo(
        filepath=str(path.absolute()),
        filename=path.name,
        format=fmt.value,
        size_bytes=path.stat().st_size,
        checksum=file_hash,
    )


def _validate_dataframe(df: pd.DataFrame, config: LoadConfig) -> None:
    """Validações básicas do DataFrame carregado"""
    if df.empty:
        raise DataLoadError("File loaded as empty DataFrame", {})

    if len(df) < config.min_valid_points:
        raise DataLoadError(
            f"Dataset has only {len(df)} points, minimum required: {config.min_valid_points}",
            {"n_points": len(df), "min_required": config.min_valid_points},
        )

    # Verifica se há pelo menos uma coluna numérica
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        raise DataLoadError("No numeric columns found in dataset", {"columns": list(df.columns)})

    logger.debug("dataframe_validated", shape=df.shape, numeric_cols=len(numeric_cols))


def load(path: str, config: dict | LoadConfig | None = None) -> Dataset:
    """Carrega dataset de arquivo conforme especificação seção 6"""
    cfg = config if isinstance(config, LoadConfig) else LoadConfig(**(config or {}))
    path_obj = Path(path)

    if not path_obj.exists():
        raise DataLoadError(f"File not found: {path}", {"path": path})

    # Detecta formato e cria estratégia
    try:
        fmt = FileFormat.from_extension(path_obj.suffix)
    except DataLoadError:
        raise DataLoadError(f"Unsupported file format: {path_obj.suffix}", {"path": path})

    strategy = cfg.custom_strategy or _get_default_strategy(fmt)

    logger.info("loading_file", path=str(path_obj), format=fmt.value, size_mb=path_obj.stat().st_size / 1024 / 1024)

    try:
        df = strategy.read_file(path_obj, cfg)
        _validate_dataframe(df, cfg)
    except Exception as e:
        logger.exception("file_load_failed", path=str(path_obj), error=str(e))
        raise DataLoadError(f"Failed to load file: {e}", {"path": path, "original_error": str(e)})

    schema = detect_schema(df, cfg.schema_rules)
    timestamp_column = cfg.timestamp_column or schema.timestamp_column

    time_report = validate_time(df, timestamp_column)
    candidate_names = [c.name for c in schema.candidate_series]
    values_report = validate_values(df, candidate_names, max_missing_ratio=cfg.max_missing_ratio)

    if timestamp_column == "__index__":
        timestamps = _parse_timestamps(df.index)
    else:
        timestamps = _parse_timestamps(df[timestamp_column])

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
            is_interpolated=np.zeros(len(values), dtype=bool),
            method_used=method_used.astype("<U32"),
        )
        metadata = SeriesMetadata(
            original_name=candidate.name,
            source_column=candidate.name,
            original_unit=unit_str,
        )
        lineage = Lineage(
            origin_series=[],
            operation="load",
            parameters={
                "path": str(path_obj),
                "format": fmt.value,
                "config": cfg.model_dump(exclude={"custom_strategy"}),
            },
            timestamp=datetime.now(UTC),
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
        source=_create_source_info(path_obj, fmt),
        t_seconds=t_seconds,
        t_datetime=t_datetime,
        series=series_dict,
        metadata=metadata,
        created_at=datetime.now(UTC),
    )

    logger.info(
        "dataset_loaded",
        dataset_id=dataset.dataset_id,
        n_series=len(dataset.series),
        n_points=len(dataset.t_seconds),
        file_format=fmt.value,
        file_size_mb=path_obj.stat().st_size / 1024 / 1024,
        schema_confidence=schema.confidence,
    )
    return dataset


def load_async(path: str, config: dict | LoadConfig | None = None,
               progress_callback: Callable[[float, str], None] | None = None) -> Dataset:
    """Versão assíncrona do loader com callback de progresso"""
    if progress_callback:
        progress_callback(0.0, "Starting load...")

    try:
        if progress_callback:
            progress_callback(20.0, "Reading file...")

        dataset = load(path, config)

        if progress_callback:
            progress_callback(100.0, "Load complete")

        return dataset

    except Exception as e:
        if progress_callback:
            progress_callback(0.0, f"Load failed: {e}")
        raise


def get_file_info(path: str) -> dict[str, Any]:
    """Obtém informações do arquivo sem carregar completamente"""
    path_obj = Path(path)

    if not path_obj.exists():
        raise DataLoadError(f"File not found: {path}", {"path": path})

    fmt = FileFormat.from_extension(path_obj.suffix)

    # Cria preview com poucas linhas
    preview_config = LoadConfig(max_rows=5)
    strategy = _get_default_strategy(fmt)

    try:
        preview_df = strategy.read_file(path_obj, preview_config)

        return {
            "path": str(path_obj.absolute()),
            "filename": path_obj.name,
            "format": fmt.value,
            "size_bytes": path_obj.stat().st_size,
            "size_mb": round(path_obj.stat().st_size / 1024 / 1024, 2),
            "preview_shape": preview_df.shape,
            "columns": list(preview_df.columns),
            "column_types": {col: str(dtype) for col, dtype in preview_df.dtypes.items()},
            "numeric_columns": list(preview_df.select_dtypes(include=[np.number]).columns),
        }

    except Exception as e:
        logger.warning("file_info_preview_failed", path=str(path_obj), error=str(e))
        return {
            "path": str(path_obj.absolute()),
            "filename": path_obj.name,
            "format": fmt.value,
            "size_bytes": path_obj.stat().st_size,
            "size_mb": round(path_obj.stat().st_size / 1024 / 1024, 2),
            "preview_error": str(e),
        }


class DataLoaderService:
    """
    Serviço de carregamento de dados com gerenciamento de cache e validação.
    
    Fornece interface de alto nível para carregar arquivos de dados
    com suporte a múltiplos formatos e validação automática.
    """
    
    def __init__(self, default_config: LoadConfig | None = None):
        """
        Inicializa o serviço.
        
        Args:
            default_config: Configuração padrão para carregamentos
        """
        self._default_config = default_config or LoadConfig()
        self._cache: dict[str, pd.DataFrame] = {}
        self._loaded_files: list[str] = []
        
    def load_file(
        self,
        path: str | Path,
        config: LoadConfig | None = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Carrega arquivo como DataFrame.
        
        Args:
            path: Caminho do arquivo
            config: Configuração de carregamento (opcional)
            use_cache: Se deve usar cache
            
        Returns:
            DataFrame com os dados carregados
        """
        path_obj = Path(path)
        path_str = str(path_obj.absolute())
        
        # Verifica cache
        if use_cache and path_str in self._cache:
            logger.debug("data_loader_cache_hit", path=path_str)
            return self._cache[path_str]
        
        # Usa configuração fornecida ou padrão
        load_config = config or self._default_config
        
        # Detecta formato
        fmt = FileFormat.from_extension(path_obj.suffix)
        strategy = _get_default_strategy(fmt)
        
        # Carrega dados
        df = strategy.read_file(path_obj, load_config)
        
        # Armazena em cache
        if use_cache:
            self._cache[path_str] = df
            self._loaded_files.append(path_str)
        
        logger.info("data_loader_file_loaded", 
                   path=path_str, 
                   shape=df.shape)
        
        return df
    
    def load_dataset(
        self,
        path: str | Path,
        config: LoadConfig | None = None
    ) -> Dataset:
        """
        Carrega arquivo como Dataset completo.
        
        Args:
            path: Caminho do arquivo
            config: Configuração de carregamento
            
        Returns:
            Dataset com séries de dados
        """
        load_config = config or self._default_config
        return load(path, load_config)
    
    def clear_cache(self) -> None:
        """Limpa o cache de dados."""
        self._cache.clear()
        logger.debug("data_loader_cache_cleared")
    
    def get_loaded_files(self) -> list[str]:
        """Retorna lista de arquivos carregados."""
        return self._loaded_files.copy()
    
    def get_file_info(self, path: str | Path) -> dict[str, Any]:
        """
        Obtém informações sobre um arquivo.
        
        Args:
            path: Caminho do arquivo
            
        Returns:
            Dicionário com informações do arquivo
        """
        return get_file_info(path)
