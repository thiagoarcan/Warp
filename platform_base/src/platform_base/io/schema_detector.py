from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class SeriesCandidate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    dtype: str
    unit_hint: str | None = None


class SchemaMap(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    timestamp_column: str
    candidate_series: list[SeriesCandidate]
    confidence: float


class SchemaRules(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    timestamp_candidates: list[str] = Field(
        default_factory=lambda: ["timestamp", "time", "datetime", "date", "datahora"],
    )
    min_series_columns: int = 1


def _match_timestamp_column(columns: list[str], rules: SchemaRules) -> str | None:
    candidates = {c.lower(): c for c in columns}
    for name in rules.timestamp_candidates:
        if name.lower() in candidates:
            return candidates[name.lower()]
    return None


def detect_schema(df: pd.DataFrame, rules: SchemaRules) -> SchemaMap:
    """Detect schema using pandas dtypes and simple heuristics."""
    timestamp_col = None
    confidence = 0.5

    datetime_cols = [
        col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])
    ]
    if datetime_cols:
        timestamp_col = datetime_cols[0]
        confidence = 0.95
    else:
        timestamp_col = _match_timestamp_column(list(df.columns), rules)
        if timestamp_col:
            confidence = 0.9

    if timestamp_col is None and isinstance(df.index, pd.DatetimeIndex):
        timestamp_col = "__index__"
        confidence = 0.9

    if timestamp_col is None:
        timestamp_col = df.columns[0]
        confidence = 0.5

    candidates = []
    for col in df.columns:
        if col == timestamp_col:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            candidates.append(SeriesCandidate(name=col, dtype=str(df[col].dtype)))

    return SchemaMap(
        timestamp_column=timestamp_col,
        candidate_series=candidates,
        confidence=confidence,
    )
