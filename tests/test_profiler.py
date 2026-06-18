"""Unit tests for the Data Profiler module."""

from io import BytesIO
from typing import Any
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from app.analytics.profiler import (
    format_memory_usage,
    get_outliers_count,
    load_file,
    profile_dataframe,
)


def test_format_memory_usage() -> None:
    """Test memory formatting for various byte sizes."""
    assert format_memory_usage(500) == "500.00 B"
    assert format_memory_usage(1500) == "1.00 KB"
    assert format_memory_usage(1024 * 1024 * 3) == "3.00 MB"


def test_get_outliers_count() -> None:
    """Test outlier detection count using IQR method."""
    # Data with no outliers
    data = pd.Series([10, 12, 11, 13, 12, 11, 10, 12, 11, 12])
    assert get_outliers_count(data) == 0

    # Data with outliers (100 and -50 are extreme outliers)
    data_outliers = pd.Series([10, 12, 11, 13, 12, 11, 10, 12, 100, -50])
    assert get_outliers_count(data_outliers) == 2


def test_profile_dataframe() -> None:
    """Test profile_dataframe on a simple mock DataFrame."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 3, 3],  # 3 is duplicated
            "val": [10.5, 20.0, np.nan, 20.0, 20.0],  # One missing value
            "cat": ["A", "B", "C", "C", "C"],
        }
    )

    profile = profile_dataframe(df)

    assert profile.shape == (5, 3)
    assert profile.num_rows == 5
    assert profile.num_cols == 3
    assert profile.columns == ["id", "val", "cat"]
    # The duplicate rows count is 1 (row 4 is identical to row 3)
    assert profile.duplicate_rows == 1
    assert profile.column_profiles["id"].missing_count == 0
    assert profile.column_profiles["val"].missing_count == 1
    # Mean calculation: (10.5 + 20.0 + 20.0 + 20.0) / 4 = 17.625
    assert profile.column_profiles["val"].mean == 17.62
    assert profile.column_profiles["cat"].num_unique == 3


@patch("pandas.read_csv")
def test_load_file_csv(mock_read_csv: Any) -> None:
    """Test load_file for CSV extensions."""
    mock_df = pd.DataFrame({"a": [1, 2]})
    mock_read_csv.return_value = mock_df

    buf = BytesIO(b"a\n1\n2")
    res = load_file(buf, "test.csv")
    assert res.equals(mock_df)
    mock_read_csv.assert_called_once_with(buf)


def test_load_file_unsupported() -> None:
    """Test load_file raises ValueError for unsupported extensions."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_file(BytesIO(b""), "test.txt")
