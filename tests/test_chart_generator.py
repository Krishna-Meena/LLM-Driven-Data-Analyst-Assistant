"""Unit tests for the ChartGenerator."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.analytics.profiler import ColumnProfile, DataProfile
from app.charts.chart_generator import ChartConfig, ChartGenerator
from app.services.ollama_service import OllamaService


@pytest.fixture
def mock_ollama() -> OllamaService:
    """Fixture to mock OllamaService."""
    return MagicMock(spec=OllamaService)


@pytest.fixture
def chart_generator(mock_ollama: OllamaService) -> ChartGenerator:
    """Fixture to instantiate ChartGenerator with mock Ollama."""
    return ChartGenerator(ollama_service=mock_ollama, model_name="qwen2.5-coder:7b")


@pytest.fixture
def mock_df() -> pd.DataFrame:
    """Fixture for a simple DataFrame."""
    return pd.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30], "cat": ["A", "B", "C"]})


def test_create_chart_bar(
    chart_generator: ChartGenerator, mock_df: pd.DataFrame
) -> None:
    """Test generating a bar chart."""
    config = ChartConfig(chart_type="bar", x_axis="cat", y_axis="val", title="Test Bar")
    fig = chart_generator.create_chart(mock_df, config)
    assert fig is not None
    assert fig.layout.title.text == "Test Bar"


def test_create_chart_heatmap(
    chart_generator: ChartGenerator, mock_df: pd.DataFrame
) -> None:
    """Test generating a correlation heatmap."""
    config = ChartConfig(chart_type="heatmap", title="Correlation")
    fig = chart_generator.create_chart(mock_df, config)
    assert fig is not None
    assert fig.layout.title.text == "Correlation"


def test_auto_generate_chart_bar(
    chart_generator: ChartGenerator, mock_df: pd.DataFrame
) -> None:
    """Test auto-chart picker selects bar chart for categorical + numeric."""
    fig = chart_generator.auto_generate_chart(mock_df)
    assert fig is not None
    # Auto-generation for mock_df (has numeric 'id' and categorical 'cat')
    # should yield a bar plot 'id by cat'
    assert "id by cat" in fig.layout.title.text.lower()


def test_parse_json_recommendation(chart_generator: ChartGenerator) -> None:
    """Test JSON parser extracts clean dict from code blocks or raw text."""
    raw_json = (
        '```json\n{\n  "chart_type": "line",\n  "x_axis": "x",\n  "y_axis": "y"\n}\n```'
    )
    res = chart_generator._parse_json_recommendation(raw_json)
    assert res["chart_type"] == "line"
    assert res["x_axis"] == "x"


def test_recommend_chart_config(
    chart_generator: ChartGenerator, mock_ollama: MagicMock
) -> None:
    """Test recommend_chart_config returns correct Pydantic configuration."""
    profile = DataProfile(
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

    mock_ollama.generate_completion.return_value = (
        '{\n  "chart_type": "pie",\n  "x_axis": "cat",\n  "y_axis": "val"\n}'
    )

    config = chart_generator.recommend_chart_config("Show share of groups", profile)

    assert config.chart_type == "pie"
    assert config.x_axis == "cat"
    assert config.y_axis == "val"
