import pytest

pd = pytest.importorskip("pandas")

from platform_base.io.schema_detector import SchemaRules, detect_schema


def test_detect_schema_timestamp_column():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="s"),
            "a": [1, 2, 3, 4, 5],
            "b": [10, 11, 12, 13, 14],
        }
    )
    schema = detect_schema(df, SchemaRules())
    assert schema.timestamp_column == "timestamp"
    assert {c.name for c in schema.candidate_series} == {"a", "b"}
