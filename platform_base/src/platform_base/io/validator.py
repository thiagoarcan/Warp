from __future__ import annotations

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


class ValidationReport(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_valid: bool
    warnings: list[ValidationWarning]
    errors: list[ValidationError]
    gaps: GapReport


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
