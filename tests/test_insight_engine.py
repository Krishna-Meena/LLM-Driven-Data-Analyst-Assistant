"""Unit tests for the InsightEngine."""

from unittest.mock import MagicMock

import pytest

from app.analytics.insight_engine import InsightEngine, InsightsReport
from app.analytics.profiler import ColumnProfile, DataProfile
from app.services.ollama_service import OllamaService


@pytest.fixture
def mock_ollama() -> OllamaService:
    """Fixture to mock OllamaService."""
    return MagicMock(spec=OllamaService)


@pytest.fixture
def insight_engine(mock_ollama: OllamaService) -> InsightEngine:
    """Fixture to instantiate InsightEngine with mock Ollama."""
    return InsightEngine(ollama_service=mock_ollama, model_name="qwen2.5-coder:7b")


@pytest.fixture
def mock_profile() -> DataProfile:
    """Fixture for DataProfile metadata."""
    return DataProfile(
        shape=(10, 2),
        num_rows=10,
        num_cols=2,
        columns=["a", "b"],
        duplicate_rows=0,
        duplicate_pct=0.0,
        memory_usage_bytes=160,
        memory_usage_str="160 B",
        column_profiles={
            "a": ColumnProfile(
                name="a",
                dtype="int64",
                missing_count=0,
                missing_pct=0.0,
                num_unique=10,
            ),
            "b": ColumnProfile(
                name="b",
                dtype="int64",
                missing_count=0,
                missing_pct=0.0,
                num_unique=10,
            ),
        },
    )


def test_generate_insights_success(
    insight_engine: InsightEngine,
    mock_profile: DataProfile,
    mock_ollama: MagicMock,
) -> None:
    """Test generating insights successfully with valid JSON returned."""
    mock_ollama.generate_completion.return_value = (
        "{\n"
        '  "executive_summary": "Sleek overview.",\n'
        '  "trends": ["Trend A"],\n'
        '  "patterns": ["Pattern B"],\n'
        '  "anomalies": ["Anomaly C"],\n'
        '  "recommendations": ["Rec D"]\n'
        "}"
    )

    report = insight_engine.generate_insights(mock_profile)

    assert isinstance(report, InsightsReport)
    assert report.executive_summary == "Sleek overview."
    assert report.trends == ["Trend A"]
    assert report.patterns == ["Pattern B"]
    assert report.anomalies == ["Anomaly C"]
    assert report.recommendations == ["Rec D"]
    mock_ollama.generate_completion.assert_called_once()


def test_generate_insights_fallback(
    insight_engine: InsightEngine,
    mock_profile: DataProfile,
    mock_ollama: MagicMock,
) -> None:
    """Test generate_insights graceful fallback on invalid LLM output."""
    # Configure mock side effect on mock_ollama
    mock_ollama.generate_completion.side_effect = RuntimeError("Connection timeout")

    report = insight_engine.generate_insights(mock_profile)

    assert isinstance(report, InsightsReport)
    assert (
        "data profiling was completed successfully" in report.executive_summary.lower()
    )
    assert len(report.trends) == 1
    assert len(report.recommendations) == 1
