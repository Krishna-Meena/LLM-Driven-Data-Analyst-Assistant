"""Unit tests for the ReportGenerator module."""

import os
import tempfile

import pytest

from app.analytics.insight_engine import InsightsReport
from app.analytics.profiler import ColumnProfile, DataProfile
from app.reports.report_generator import ReportGenerator


@pytest.fixture
def report_generator() -> ReportGenerator:
    """Fixture to instantiate ReportGenerator."""
    return ReportGenerator()


@pytest.fixture
def mock_profile() -> DataProfile:
    """Fixture for DataProfile metadata."""
    return DataProfile(
        shape=(100, 2),
        num_rows=100,
        num_cols=2,
        columns=["sales", "region"],
        duplicate_rows=2,
        duplicate_pct=2.0,
        memory_usage_bytes=1600,
        memory_usage_str="1.56 KB",
        column_profiles={
            "sales": ColumnProfile(
                name="sales",
                dtype="int64",
                missing_count=0,
                missing_pct=0.0,
                num_unique=95,
                outliers_count=3,
                mean=150.5,
                min_val=10.0,
                max_val=300.0,
            ),
            "region": ColumnProfile(
                name="region",
                dtype="object",
                missing_count=5,
                missing_pct=5.0,
                num_unique=4,
            ),
        },
    )


@pytest.fixture
def mock_insights() -> InsightsReport:
    """Fixture for InsightsReport."""
    return InsightsReport(
        executive_summary="Sleek executive summary of findings.",
        trends=["Sales are increasing."],
        patterns=["Region East dominates."],
        anomalies=["Detected missing regions."],
        recommendations=["Focus sales on Region East."],
    )


def test_generate_markdown_report(
    report_generator: ReportGenerator,
    mock_profile: DataProfile,
    mock_insights: InsightsReport,
) -> None:
    """Test generating a markdown report."""
    md = report_generator.generate_markdown_report(mock_profile, mock_insights)

    assert "Executive Data Analysis Report" in md
    assert "Sleek executive summary of findings." in md
    assert "sales" in md
    assert "1.56 KB" in md


def test_generate_html_report(
    report_generator: ReportGenerator,
    mock_profile: DataProfile,
    mock_insights: InsightsReport,
) -> None:
    """Test generating an HTML report."""
    html = report_generator.generate_html_report(mock_profile, mock_insights)

    assert "<!DOCTYPE html>" in html
    assert "Sleek executive summary of findings." in html
    assert "sales" in html
    assert "100" in html


def test_generate_pdf_report(
    report_generator: ReportGenerator,
    mock_profile: DataProfile,
    mock_insights: InsightsReport,
) -> None:
    """Test generating a binary PDF report and saving it to file."""
    # Write to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "test_report.pdf")

        report_generator.generate_pdf_report(mock_profile, mock_insights, pdf_path)

        # Assert file exists and has size
        assert os.path.exists(pdf_path) is True
        assert os.path.getsize(pdf_path) > 1000  # standard PDF should be > 1KB
