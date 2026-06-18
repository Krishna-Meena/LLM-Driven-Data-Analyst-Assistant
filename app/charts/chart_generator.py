"""Module for generating interactive Plotly charts based on data profiles.

Includes auto-fallbacks and LLM-driven configuration recommendations.
"""

import json
import re
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pydantic import BaseModel

from app.analytics.profiler import DataProfile
from app.services.ollama_service import OllamaService
from app.utils.logger import setup_logger

logger = setup_logger("chart_generator")


class ChartConfig(BaseModel):
    """Pydantic model representing chart configuration options."""

    chart_type: str  # bar, line, scatter, histogram, heatmap, pie
    x_axis: str | None = None
    y_axis: str | None = None
    color: str | None = None
    title: str | None = None
    nbins: int | None = None


class ChartGenerator:
    """Generates premium interactive Plotly charts from data profiles."""

    def __init__(self, ollama_service: OllamaService, model_name: str):
        """Initializes the chart generator.

        Args:
            ollama_service: Configured Ollama service client.
            model_name: The name of the LLM model to use for chart decisions.
        """
        self.ollama_service = ollama_service
        self.model_name = model_name

    def create_chart(self, df: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Creates a Plotly figure based on the provided configuration.

        Args:
            df: The DataFrame to plot.
            config: Config details (type, axes, colors, title).

        Returns:
            Plotly Figure object.
        """
        chart_type = config.chart_type.lower()
        title = config.title or f"{chart_type.capitalize()} Chart"
        x = config.x_axis
        y = config.y_axis
        color = config.color

        # Validate columns exist in DataFrame, fall back if missing
        if x and x not in df.columns:
            logger.warning(f"X column '{x}' not found. Defaulting to first column.")
            x = df.columns[0]
        if y and y not in df.columns:
            logger.warning(f"Y column '{y}' not found. Defaulting to None.")
            y = None
        if color and color not in df.columns:
            logger.warning(
                f"Color column '{color}' not found. Disabling color grouping."
            )
            color = None

        fig: go.Figure

        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y, color=color, title=title, template="plotly_dark")
        elif chart_type == "line":
            fig = px.line(
                df, x=x, y=y, color=color, title=title, template="plotly_dark"
            )
        elif chart_type == "scatter":
            fig = px.scatter(
                df, x=x, y=y, color=color, title=title, template="plotly_dark"
            )
        elif chart_type == "histogram":
            fig = px.histogram(
                df, x=x, nbins=config.nbins, title=title, template="plotly_dark"
            )
        elif chart_type == "heatmap":
            # For correlation matrices or pivot tables
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr()
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    aspect="auto",
                    title=title,
                    template="plotly_dark",
                    color_continuous_scale="Viridis",
                )
            else:
                # Fallback to general heatmap of first 50 rows if
                # correlation isn't possible
                fig = px.imshow(
                    df.head(50).select_dtypes(include=["number"]),
                    title=title,
                    template="plotly_dark",
                )
        elif chart_type == "pie":
            # Pie charts require name (x) and value (y)
            fig = px.pie(df, names=x, values=y, title=title, template="plotly_dark")
        else:
            logger.warning(
                f"Unknown chart type '{chart_type}'. Falling back to Bar Chart."
            )
            fig = px.bar(df, x=x, y=y, title=title, template="plotly_dark")

        # Custom Premium SaaS visual styling
        fig.update_layout(
            paper_bgcolor="rgba(10, 10, 10, 0.4)",
            plot_bgcolor="rgba(10, 10, 10, 0.4)",
            font={"family": "Outfit, Inter, sans-serif", "color": "#E2E8F0"},
            title_font={
                "size": 18,
                "family": "Outfit, sans-serif",
                "color": "#F8FAFC",
            },
            margin={"l": 40, "r": 40, "t": 50, "b": 40},
            hovermode="x unified",
        )
        if hasattr(fig.layout, "xaxis") and fig.layout.xaxis:
            fig.update_xaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        if hasattr(fig.layout, "yaxis") and fig.layout.yaxis:
            fig.update_yaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")

        return fig

    def auto_generate_chart(self, df: pd.DataFrame) -> go.Figure | None:
        """Examines the data types and constructs a logical default chart.

        Args:
            df: DataFrame to plot.

        Returns:
            A Plotly Figure, or None if the DataFrame is empty.
        """
        if df.empty:
            return None

        numeric_cols = list(df.select_dtypes(include=["number"]).columns)
        categorical_cols = list(df.select_dtypes(exclude=["number"]).columns)

        # 1. Heatmap correlation if there are multiple numeric columns
        if len(numeric_cols) >= 3:
            config = ChartConfig(chart_type="heatmap", title="Correlation Heatmap")
            return self.create_chart(df, config)

        # 2. Line chart if there's a date/time column + numeric column
        datetime_cols = [
            c
            for c in df.columns
            if "date" in str(c).lower() or "time" in str(c).lower()
        ]
        if datetime_cols and numeric_cols:
            config = ChartConfig(
                chart_type="line",
                x_axis=datetime_cols[0],
                y_axis=numeric_cols[0],
                title=f"{numeric_cols[0]} Trend Over Time",
            )
            return self.create_chart(df, config)

        # 3. Bar chart of Category vs Numerical Column
        if categorical_cols and numeric_cols:
            config = ChartConfig(
                chart_type="bar",
                x_axis=categorical_cols[0],
                y_axis=numeric_cols[0],
                title=f"{numeric_cols[0]} by {categorical_cols[0]}",
            )
            return self.create_chart(df, config)

        # 4. Scatter plot of first two numeric columns
        if len(numeric_cols) >= 2:
            config = ChartConfig(
                chart_type="scatter",
                x_axis=numeric_cols[0],
                y_axis=numeric_cols[1],
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
            )
            return self.create_chart(df, config)

        # 5. Histogram fallback of first numeric column
        if numeric_cols:
            config = ChartConfig(
                chart_type="histogram",
                x_axis=numeric_cols[0],
                title=f"Distribution of {numeric_cols[0]}",
            )
            return self.create_chart(df, config)

        # 6. Basic counts bar chart for categorical data
        if categorical_cols:
            counts = df[categorical_cols[0]].value_counts().reset_index()
            counts.columns = [categorical_cols[0], "count"]
            config = ChartConfig(
                chart_type="bar",
                x_axis=categorical_cols[0],
                y_axis="count",
                title=f"Count of {categorical_cols[0]}",
            )
            return self.create_chart(counts, config)

        return None

    def recommend_chart_config(
        self, user_query: str, profile: DataProfile
    ) -> ChartConfig:
        """Queries the local LLM to get recommended chart configuration parameters.

        Args:
            user_query: The user's query or conversational intent.
            profile: Dataset structure metadata.

        Returns:
            ChartConfig object containing selected parameters.
        """
        schema_lines = []
        for col, col_prof in profile.column_profiles.items():
            schema_lines.append(f"- Name: {col}, Type: {col_prof.dtype}")
        schema_desc = "\n".join(schema_lines)

        system_prompt = (
            "You are a visualization expert. Recommend the best chart configuration "
            "to answer the user's query. You must respond ONLY with a raw JSON "
            "object matching this schema. Do not include markdown wraps unless "
            "necessary. If you use markdown, format it as a code block. JSON format:\n"
            "{\n"
            '  "chart_type": "bar|line|scatter|histogram|heatmap|pie",\n'
            '  "x_axis": "column_name_for_x",\n'
            '  "y_axis": "column_name_for_y_or_null",\n'
            '  "color": "column_name_for_color_grouping_or_null",\n'
            '  "title": "A descriptive chart title"\n'
            "}\n"
            "Strictly follow:\n"
            "1. Output ONLY the JSON block, no conversational text.\n"
            "2. Make sure column names exist EXACTLY in the schema.\n"
            "3. Choose the chart type logically: line for trends over time, bar for "
            "comparing groups, scatter for correlations, histogram for distributions, "
            "pie for shares of a whole, heatmap for correlations matrix."
        )

        prompt = (
            f"Table Columns:\n{schema_desc}\n\n"
            f'User Question: "{user_query}"\n\n'
            f"JSON Recommendation:"
        )

        try:
            raw = self.ollama_service.generate_completion(
                model=self.model_name,
                prompt=prompt,
                system_prompt=system_prompt,
                options={"temperature": 0.0},
            )
            logger.info(f"Raw chart recommendation response: {raw}")
            config_dict = self._parse_json_recommendation(raw)
            return ChartConfig(**config_dict)
        except Exception as e:
            logger.error(f"Failed to get chart recommendation: {e}")
            # Safe default fallback
            numeric_cols = [
                c
                for c, p in profile.column_profiles.items()
                if "int" in p.dtype or "float" in p.dtype
            ]
            x_col = list(profile.column_profiles.keys())[0]
            y_col = numeric_cols[0] if numeric_cols else None
            return ChartConfig(
                chart_type="bar" if y_col else "histogram",
                x_axis=x_col,
                y_axis=y_col,
                title=f"Analysis plot for: {user_query}",
            )

    def _parse_json_recommendation(self, raw: str) -> dict[str, Any]:
        """Cleans and extracts JSON dict from the raw LLM recommendation response."""
        cleaned = raw.strip()
        if "```" in cleaned:
            match = re.search(
                r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE
            )
            if match:
                cleaned = match.group(1).strip()
            else:
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        try:
            res = json.loads(cleaned)
            if not isinstance(res, dict):
                raise ValueError("LLM response did not parse as a JSON object.")
            return res
        except Exception as e:
            logger.error(f"JSON Parsing failed for string: {cleaned}. Error: {e}")
            raise ValueError(f"Failed to parse LLM chart config: {e}") from e
