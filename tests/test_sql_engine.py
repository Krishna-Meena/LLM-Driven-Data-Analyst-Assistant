"""Unit tests for the DuckDB SQLEngine."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.analytics.profiler import ColumnProfile, DataProfile
from app.analytics.sql_engine import SQLEngine
from app.services.ollama_service import OllamaService


@pytest.fixture
def mock_ollama() -> OllamaService:
    """Fixture to mock OllamaService."""
    return MagicMock(spec=OllamaService)


@pytest.fixture
def sql_engine(mock_ollama: OllamaService) -> SQLEngine:
    """Fixture to instantiate SQLEngine with mock Ollama."""
    return SQLEngine(ollama_service=mock_ollama, model_name="qwen2.5-coder:7b")


@pytest.fixture
def mock_df() -> pd.DataFrame:
    """Fixture for a simple DataFrame."""
    return pd.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30], "cat": ["A", "B", "C"]})


@pytest.fixture
def mock_profile() -> DataProfile:
    """Fixture for DataProfile metadata matching mock_df."""
    return DataProfile(
        shape=(3, 3),
        num_rows=3,
        num_cols=3,
        columns=["id", "val", "cat"],
        duplicate_rows=0,
        duplicate_pct=0.0,
        memory_usage_bytes=300,
        memory_usage_str="300 B",
        column_profiles={
            "id": ColumnProfile(
                name="id",
                dtype="int64",
                missing_count=0,
                missing_pct=0.0,
                num_unique=3,
            ),
            "val": ColumnProfile(
                name="val",
                dtype="int64",
                missing_count=0,
                missing_pct=0.0,
                num_unique=3,
            ),
            "cat": ColumnProfile(
                name="cat",
                dtype="object",
                missing_count=0,
                missing_pct=0.0,
                num_unique=3,
            ),
        },
    )


def test_register_dataframe(sql_engine: SQLEngine, mock_df: pd.DataFrame) -> None:
    """Test registering a DataFrame in DuckDB."""
    sql_engine.register_dataframe(mock_df, "data_table")
    assert sql_engine.table_registered is True

    # Test we can run standard query directly on the connection
    res = sql_engine.conn.execute("SELECT COUNT(*) FROM data_table").fetchone()
    assert res is not None
    assert res[0] == 3


def test_generate_sql(
    sql_engine: SQLEngine, mock_profile: DataProfile, mock_ollama: MagicMock
) -> None:
    """Test generating SQL from natural language."""
    mock_ollama.generate_completion.return_value = (
        "```sql\nSELECT * FROM data_table;\n```"
    )

    sql = sql_engine.generate_sql("Get all rows", mock_profile)

    assert sql == "SELECT * FROM data_table"
    mock_ollama.generate_completion.assert_called_once()


def test_execute_query(sql_engine: SQLEngine, mock_df: pd.DataFrame) -> None:
    """Test executing a valid SQL query on DuckDB."""
    sql_engine.register_dataframe(mock_df, "data_table")

    res_df = sql_engine.execute_query("SELECT val FROM data_table WHERE val > 15")

    assert len(res_df) == 2
    assert list(res_df["val"]) == [20, 30]


def test_execute_query_failure(sql_engine: SQLEngine) -> None:
    """Test that executing invalid query raises ValueError."""
    sql_engine.table_registered = True
    with pytest.raises(ValueError, match="SQL Execution failed"):
        sql_engine.execute_query("SELECT * FROM non_existent_table")


def test_clean_sql(sql_engine: SQLEngine) -> None:
    """Test cleaning of various LLM generated SQL formats."""
    # Test markdown stripping
    assert (
        sql_engine._clean_sql("```sql\nSELECT * FROM tbl;\n```") == "SELECT * FROM tbl"
    )
    assert sql_engine._clean_sql("```\nSELECT * FROM tbl\n```") == "SELECT * FROM tbl"

    # Test trailing semicolon removal
    assert sql_engine._clean_sql("SELECT * FROM tbl;") == "SELECT * FROM tbl"

    # Test surrounding quotes removal
    assert sql_engine._clean_sql('"SELECT * FROM tbl"') == "SELECT * FROM tbl"
    assert sql_engine._clean_sql("'SELECT * FROM tbl;'") == "SELECT * FROM tbl"
