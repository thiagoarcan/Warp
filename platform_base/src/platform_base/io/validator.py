"""
File Validator - Category 10.5

Sistema de validação de integridade de arquivos carregados.

Features:
- Verificação de checksum para arquivos
- Detecção de arquivos truncados
- Validação de schema para CSV/XLSX
- Detecção de encoding incorreto
- Detecção de dados corrompidos (NaN excessivos, outliers)
- Verificação de consistência temporal
- Relatório de qualidade de dados
- Opções de reparo automático
"""

from __future__ import annotations

import gzip
import hashlib
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

import chardet
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from platform_base.processing.timebase import to_seconds
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


def _parse_timestamps_for_validation(data: pd.Series | pd.Index) -> pd.DatetimeIndex:
    """
    Parse timestamps robustly for validation, trying common formats.

    Args:
        data: Series or Index containing timestamp data

    Returns:
        DatetimeIndex with parsed timestamps
    """
    # If already datetime, just convert
    if pd.api.types.is_datetime64_any_dtype(data):
        return pd.DatetimeIndex(data)

    # Common datetime formats to try
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            parsed = pd.to_datetime(data, format=fmt, errors="raise")
            return pd.DatetimeIndex(parsed)
        except (ValueError, TypeError):
            continue

    # Fallback - try auto detection
    parsed = pd.to_datetime(data, errors="coerce")
    return pd.DatetimeIndex(parsed)


class ValidationWarning(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    code: str
    message: str
    context: dict = Field(default_factory=dict)


class ValidationError(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    code: str
    message: str
    context: dict = Field(default_factory=dict)


class Gap(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: int
    delta_seconds: float


class GapReport(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    count: int
    gaps: list[Gap]


class DataQualityIssue(Enum):
    """Types of data quality issues."""
    HIGH_NAN_RATIO = auto()
    OUTLIERS = auto()
    DUPLICATES = auto()
    TRUNCATED = auto()
    CORRUPTED = auto()
    ENCODING_ERROR = auto()
    SCHEMA_MISMATCH = auto()
    TEMPORAL_INCONSISTENCY = auto()


@dataclass
class FileIntegrityInfo:
    """File integrity information."""
    path: Path
    size_bytes: int
    checksum_md5: str
    checksum_sha256: str | None = None
    is_truncated: bool = False
    encoding: str = "unknown"
    encoding_confidence: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'path': str(self.path),
            'size_bytes': self.size_bytes,
            'checksum_md5': self.checksum_md5,
            'checksum_sha256': self.checksum_sha256,
            'is_truncated': self.is_truncated,
            'encoding': self.encoding,
            'encoding_confidence': self.encoding_confidence,
        }


@dataclass
class DataQualityReport:
    """Comprehensive data quality report."""
    row_count: int
    column_count: int
    nan_percent: float
    duplicate_rows: int
    value_range: dict[str, tuple[float, float]]  # column -> (min, max)
    temporal_gaps: int
    outlier_count: int
    issues: list[DataQualityIssue] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'row_count': self.row_count,
            'column_count': self.column_count,
            'nan_percent': self.nan_percent,
            'duplicate_rows': self.duplicate_rows,
            'value_range': self.value_range,
            'temporal_gaps': self.temporal_gaps,
            'outlier_count': self.outlier_count,
            'issues': [issue.name for issue in self.issues],
            'suggestions': self.suggestions,
        }


class ValidationReport(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_valid: bool
    warnings: list[ValidationWarning]
    errors: list[ValidationError]
    gaps: GapReport
    file_integrity: FileIntegrityInfo | None = None
    data_quality: DataQualityReport | None = None


def detect_gaps(t_seconds: np.ndarray, gap_multiplier: float = 5.0) -> GapReport:
    if len(t_seconds) < 2:
        return GapReport(count=0, gaps=[])
    diffs = np.diff(t_seconds)
    median = float(np.median(diffs)) if len(diffs) else 0.0
    if median <= 0:
        return GapReport(count=0, gaps=[])
    threshold = median * gap_multiplier
    gaps = [
        Gap(index=i, delta_seconds=float(delta))
        for i, delta in enumerate(diffs)
        if delta > threshold
    ]
    return GapReport(count=len(gaps), gaps=gaps)


def validate_time(df: pd.DataFrame, timestamp_column: str) -> ValidationReport:
    warnings: list[ValidationWarning] = []
    errors: list[ValidationError] = []

    if timestamp_column == "__index__":
        timestamps = _parse_timestamps_for_validation(df.index)
    else:
        timestamps = _parse_timestamps_for_validation(df[timestamp_column])

    if timestamps.isna().any():
        warnings.append(
            ValidationWarning(
                code="timestamp_nan",
                message="Timestamp column has NaT values",
                context={"count": int(timestamps.isna().sum())},
            ),
        )

    if not timestamps.is_monotonic_increasing:
        warnings.append(
            ValidationWarning(
                code="timestamp_not_monotonic",
                message="Timestamp column is not monotonic",
                context={},
            ),
        )

    if timestamps.duplicated().any():
        warnings.append(
            ValidationWarning(
                code="timestamp_duplicates",
                message="Timestamp column has duplicate entries",
                context={"count": int(timestamps.duplicated().sum())},
            ),
        )

    t_seconds = to_seconds(timestamps.to_numpy())
    gaps = detect_gaps(t_seconds)
    return ValidationReport(is_valid=True, warnings=warnings, errors=errors, gaps=gaps)


def validate_values(
    df: pd.DataFrame,
    candidate_columns: list[str],
    max_missing_ratio: float = 0.95,
) -> ValidationReport:
    warnings: list[ValidationWarning] = []
    errors: list[ValidationError] = []

    for col in candidate_columns:
        series = pd.to_numeric(df[col], errors="coerce")
        missing_ratio = float(series.isna().mean())
        if missing_ratio > max_missing_ratio:
            warnings.append(
                ValidationWarning(
                    code="series_high_missing",
                    message="Series has high missing ratio",
                    context={"column": col, "missing_ratio": missing_ratio},
                ),
            )

    return ValidationReport(
        is_valid=True,
        warnings=warnings,
        errors=errors,
        gaps=GapReport(count=0, gaps=[]),
    )


def calculate_checksum(file_path: str | Path, algorithm: str = "md5") -> str:
    """
    Calculate file checksum.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha256)
    
    Returns:
        Hex digest of checksum
    """
    path = Path(file_path)
    
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Read file in chunks
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def detect_encoding(file_path: str | Path, sample_size: int = 100000) -> tuple[str, float]:
    """
    Detect file encoding.
    
    Args:
        file_path: Path to file
        sample_size: Number of bytes to sample
    
    Returns:
        Tuple of (encoding, confidence)
    """
    path = Path(file_path)
    
    with open(path, 'rb') as f:
        sample = f.read(sample_size)
    
    result = chardet.detect(sample)
    encoding = result.get('encoding', 'utf-8') or 'utf-8'
    confidence = result.get('confidence', 0.0)
    
    return encoding, confidence


def is_file_truncated(file_path: str | Path) -> bool:
    """
    Check if file appears truncated.
    
    Args:
        file_path: Path to file
    
    Returns:
        True if file appears truncated
    """
    path = Path(file_path)
    
    try:
        # Try to read the last few bytes
        with open(path, 'rb') as f:
            f.seek(-min(1000, path.stat().st_size), 2)  # Seek from end
            tail = f.read()
        
        # Check for common file endings
        if path.suffix.lower() in ['.csv', '.txt']:
            # Should end with newline or valid character
            return not tail.endswith(b'\n') and not tail.endswith(b'\r\n')
        
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            # Excel files have specific structure
            # This is a basic check - could be enhanced
            return len(tail) < 100  # Suspiciously short
        
        return False
        
    except Exception:
        return True  # If we can't read it, consider it truncated


def check_file_integrity(file_path: str | Path) -> FileIntegrityInfo:
    """
    Comprehensive file integrity check.
    
    Args:
        file_path: Path to file
    
    Returns:
        FileIntegrityInfo with all integrity checks
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    # Calculate checksums
    md5_checksum = calculate_checksum(path, "md5")
    sha256_checksum = calculate_checksum(path, "sha256")
    
    # Detect encoding
    encoding, confidence = detect_encoding(path)
    
    # Check if truncated
    is_truncated = is_file_truncated(path)
    
    return FileIntegrityInfo(
        path=path,
        size_bytes=path.stat().st_size,
        checksum_md5=md5_checksum,
        checksum_sha256=sha256_checksum,
        is_truncated=is_truncated,
        encoding=encoding,
        encoding_confidence=confidence,
    )


def analyze_data_quality(
    df: pd.DataFrame,
    timestamp_column: str | None = None,
) -> DataQualityReport:
    """
    Analyze data quality and generate comprehensive report.
    
    Args:
        df: DataFrame to analyze
        timestamp_column: Name of timestamp column if exists
    
    Returns:
        DataQualityReport with all quality metrics
    """
    issues: list[DataQualityIssue] = []
    suggestions: list[str] = []
    
    # Basic stats
    row_count = len(df)
    column_count = len(df.columns)
    
    # NaN analysis
    nan_percent = (df.isna().sum().sum() / (row_count * column_count) * 100) if row_count > 0 else 0
    
    if nan_percent > 20:
        issues.append(DataQualityIssue.HIGH_NAN_RATIO)
        suggestions.append(f"High NaN ratio ({nan_percent:.1f}%). Consider removing or interpolating missing values.")
    
    # Duplicate rows
    duplicate_rows = df.duplicated().sum()
    
    if duplicate_rows > 0:
        issues.append(DataQualityIssue.DUPLICATES)
        suggestions.append(f"Found {duplicate_rows} duplicate rows. Consider removing duplicates.")
    
    # Value ranges and outliers
    value_range = {}
    outlier_count = 0
    
    for col in df.select_dtypes(include=[np.number]).columns:
        series = df[col].dropna()
        if len(series) > 0:
            col_min = float(series.min())
            col_max = float(series.max())
            value_range[col] = (col_min, col_max)
            
            # Detect outliers using IQR method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = ((series < lower_bound) | (series > upper_bound)).sum()
            outlier_count += outliers
    
    if outlier_count > row_count * 0.01:  # > 1% outliers
        issues.append(DataQualityIssue.OUTLIERS)
        suggestions.append(f"Found {outlier_count} outliers. Review data for correctness.")
    
    # Temporal gaps
    temporal_gaps = 0
    if timestamp_column:
        try:
            timestamps = _parse_timestamps_for_validation(
                df[timestamp_column] if timestamp_column != "__index__" else df.index
            )
            t_seconds = to_seconds(timestamps.to_numpy())
            gap_report = detect_gaps(t_seconds)
            temporal_gaps = gap_report.count
            
            if temporal_gaps > 0:
                issues.append(DataQualityIssue.TEMPORAL_INCONSISTENCY)
                suggestions.append(f"Found {temporal_gaps} temporal gaps. Data may be incomplete.")
        except Exception:
            pass
    
    return DataQualityReport(
        row_count=row_count,
        column_count=column_count,
        nan_percent=nan_percent,
        duplicate_rows=duplicate_rows,
        value_range=value_range,
        temporal_gaps=temporal_gaps,
        outlier_count=outlier_count,
        issues=issues,
        suggestions=suggestions,
    )


def validate_file(
    file_path: str | Path,
    df: pd.DataFrame | None = None,
    timestamp_column: str | None = None,
    check_integrity: bool = True,
    check_quality: bool = True,
) -> ValidationReport:
    """
    Comprehensive file validation.
    
    Args:
        file_path: Path to file
        df: Optional DataFrame if already loaded
        timestamp_column: Name of timestamp column
        check_integrity: Whether to check file integrity
        check_quality: Whether to check data quality
    
    Returns:
        Complete ValidationReport
    """
    warnings: list[ValidationWarning] = []
    errors: list[ValidationError] = []
    
    file_integrity = None
    data_quality = None
    gaps = GapReport(count=0, gaps=[])
    
    # File integrity checks
    if check_integrity:
        try:
            file_integrity = check_file_integrity(file_path)
            
            if file_integrity.is_truncated:
                errors.append(ValidationError(
                    code="file_truncated",
                    message="File appears to be truncated",
                    context={'path': str(file_path)},
                ))
            
            if file_integrity.encoding_confidence < 0.7:
                warnings.append(ValidationWarning(
                    code="encoding_uncertain",
                    message=f"Encoding detection uncertain ({file_integrity.encoding}, {file_integrity.encoding_confidence:.0%} confidence)",
                    context={'encoding': file_integrity.encoding},
                ))
                
        except Exception as e:
            errors.append(ValidationError(
                code="integrity_check_failed",
                message=f"Failed to check file integrity: {e}",
                context={},
            ))
    
    # Data quality checks
    if check_quality and df is not None:
        try:
            data_quality = analyze_data_quality(df, timestamp_column)
            
            # Add quality issues as warnings
            for issue in data_quality.issues:
                warnings.append(ValidationWarning(
                    code=f"quality_{issue.name.lower()}",
                    message=f"Data quality issue: {issue.name}",
                    context={},
                ))
            
            # Check temporal consistency if timestamp column provided
            if timestamp_column:
                time_validation = validate_time(df, timestamp_column)
                warnings.extend(time_validation.warnings)
                errors.extend(time_validation.errors)
                gaps = time_validation.gaps
                
        except Exception as e:
            warnings.append(ValidationWarning(
                code="quality_check_failed",
                message=f"Failed to check data quality: {e}",
                context={},
            ))
    
    is_valid = len(errors) == 0
    
    return ValidationReport(
        is_valid=is_valid,
        warnings=warnings,
        errors=errors,
        gaps=gaps,
        file_integrity=file_integrity,
        data_quality=data_quality,
    )


def auto_repair_data(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    interpolate_small_gaps: bool = True,
    max_gap_size: int = 5,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Attempt automatic repair of common data issues.
    
    Args:
        df: DataFrame to repair
        remove_duplicates: Whether to remove duplicate rows
        interpolate_small_gaps: Whether to interpolate small gaps
        max_gap_size: Maximum gap size to interpolate
    
    Returns:
        Tuple of (repaired_df, list of actions taken)
    """
    actions = []
    repaired = df.copy()
    
    # Remove duplicates
    if remove_duplicates:
        initial_rows = len(repaired)
        repaired = repaired.drop_duplicates()
        removed = initial_rows - len(repaired)
        if removed > 0:
            actions.append(f"Removed {removed} duplicate rows")
    
    # Interpolate small gaps in numeric columns
    if interpolate_small_gaps:
        for col in repaired.select_dtypes(include=[np.number]).columns:
            # Find NaN runs
            is_nan = repaired[col].isna()
            nan_runs = is_nan.astype(int).groupby((is_nan != is_nan.shift()).cumsum()).sum()
            
            # Interpolate only small runs
            small_gaps = nan_runs[nan_runs <= max_gap_size]
            if len(small_gaps) > 0:
                repaired[col] = repaired[col].interpolate(method='linear', limit=max_gap_size)
                actions.append(f"Interpolated small gaps in column '{col}'")
    
    return repaired, actions
