"""Data profiling and file loading utilities."""

from io import BytesIO
from typing import Any

import pandas as pd
from pydantic import BaseModel

from app.utils.logger import setup_logger

logger = setup_logger("profiler")


class ColumnProfile(BaseModel):
    """Container for single-column profile metrics."""

    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    num_unique: int
    outliers_count: int | None = None
    mean: float | None = None
    min_val: Any | None = None
    max_val: Any | None = None


class DataProfile(BaseModel):
    """Container for whole-dataset profile metrics."""

    shape: tuple[int, int]
    num_rows: int
    num_cols: int
    columns: list[str]
    duplicate_rows: int
    duplicate_pct: float
    memory_usage_bytes: int
    memory_usage_str: str
    column_profiles: dict[str, ColumnProfile]


def load_file(file_source: str | bytes | BytesIO, filename: str) -> pd.DataFrame:
    """Loads a supported file format into a Pandas DataFrame.

    Args:
        file_source: Path to file or bytes/buffer of the file.
        filename: Name of the file, used to determine the format extension.

    Returns:
        Loaded Pandas DataFrame.

    Raises:
        ValueError: If file format is not supported or parsing fails.
    """
    logger.info(f"Attempting to load file: {filename}")
    ext = filename.split(".")[-1].lower()

    try:
        if ext == "csv":
            return pd.read_csv(file_source)
        elif ext in ("xlsx", "xls"):
            return pd.read_excel(file_source, engine="openpyxl")
        elif ext == "parquet":
            return pd.read_parquet(file_source, engine="pyarrow")
        else:
            raise ValueError(
                f"Unsupported file format '.{ext}'. "
                "Supported formats are CSV, XLSX, XLS, and Parquet."
            )
    except Exception as e:
        err_msg = f"Failed to load file '{filename}': {e}"
        logger.error(err_msg)
        raise ValueError(err_msg) from e


def format_memory_usage(bytes_count: int) -> str:
    """Formats bytes into human-readable memory usage format.

    Args:
        bytes_count: Memory size in bytes.

    Returns:
        Formatted memory string (e.g. '12.4 MB').
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count //= 1024
    return f"{bytes_count:.2f} TB"


def get_outliers_count(series: pd.Series) -> int:
    """Calculates the count of outlier values using the IQR method.

    Args:
        series: Pandas numerical Series.

    Returns:
        Number of outliers.
    """
    # Drop NaNs before calculation
    clean_series = series.dropna()
    if clean_series.empty:
        return 0

    q1 = clean_series.quantile(0.25)
    q3 = clean_series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = clean_series[(clean_series < lower_bound) | (clean_series > upper_bound)]
    return int(len(outliers))


def profile_dataframe(df: pd.DataFrame) -> DataProfile:
    """Analyzes a Pandas DataFrame and generates structured profile metrics.

    Args:
        df: Pandas DataFrame to profile.

    Returns:
        DataProfile containing metrics.
    """
    logger.info("Profiling DataFrame...")

    num_rows, num_cols = df.shape
    columns = list(df.columns)

    # Calculate duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = (duplicate_rows / num_rows * 100) if num_rows > 0 else 0.0

    # Calculate memory usage
    memory_usage_bytes = int(df.memory_usage(deep=True).sum())
    memory_usage_str = format_memory_usage(memory_usage_bytes)

    column_profiles = {}
    for col in df.columns:
        series = df[col]
        dtype_str = str(series.dtype)

        # Basic missing stats
        missing_count = int(series.isna().sum())
        missing_pct = (missing_count / num_rows * 100) if num_rows > 0 else 0.0
        num_unique = int(series.nunique(dropna=True))

        # Check if numeric for outlier calculations
        outliers_count = None
        mean_val = None
        min_val: Any = None
        max_val: Any = None

        if pd.api.types.is_numeric_dtype(series.dtype):
            outliers_count = get_outliers_count(series)
            mean_val = float(series.mean()) if not series.empty else None

            # Handle NaN / Inf check for min/max
            if not series.dropna().empty:
                min_val = float(series.min())
                max_val = float(series.max())
        else:
            # For non-numeric columns, clean strings/objects
            clean_series = series.dropna()
            if not clean_series.empty:
                min_val = str(clean_series.min())
                max_val = str(clean_series.max())

        column_profiles[str(col)] = ColumnProfile(
            name=str(col),
            dtype=dtype_str,
            missing_count=missing_count,
            missing_pct=round(missing_pct, 2),
            num_unique=num_unique,
            outliers_count=outliers_count,
            mean=round(mean_val, 2) if mean_val is not None else None,
            min_val=min_val,
            max_val=max_val,
        )

    return DataProfile(
        shape=(num_rows, num_cols),
        num_rows=num_rows,
        num_cols=num_cols,
        columns=[str(c) for c in columns],
        duplicate_rows=duplicate_rows,
        duplicate_pct=round(duplicate_pct, 2),
        memory_usage_bytes=memory_usage_bytes,
        memory_usage_str=memory_usage_str,
        column_profiles=column_profiles,
    )
