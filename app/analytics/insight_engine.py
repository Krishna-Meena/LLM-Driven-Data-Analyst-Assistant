"""Insight Engine for automatically generating data insights and summaries."""

import json
import re
from typing import Any

from pydantic import BaseModel

from app.analytics.profiler import DataProfile
from app.services.ollama_service import OllamaService
from app.utils.logger import setup_logger

logger = setup_logger("insight_engine")


class InsightsReport(BaseModel):
    """Container for automatically generated dataset insights."""

    executive_summary: str
    trends: list[str]
    patterns: list[str]
    anomalies: list[str]
    recommendations: list[str]


class InsightEngine:
    """Uses local LLM to inspect dataset profiles and generate structured insights."""

    def __init__(self, ollama_service: OllamaService, model_name: str):
        """Initializes the insight engine.

        Args:
            ollama_service: Configured Ollama service client.
            model_name: The name of the LLM model to use for generation.
        """
        self.ollama_service = ollama_service
        self.model_name = model_name

    def generate_insights(self, profile: DataProfile) -> InsightsReport:
        """Analyzes a DataProfile and generates a structured InsightsReport.

        Args:
            profile: Profile metadata of the dataset.

        Returns:
            InsightsReport with executive summary, trends, patterns,
            anomalies, and recommendations.
        """
        logger.info("Generating automated data insights...")

        # Construct schema and statistics details for the prompt
        schema_details = []
        for col, col_prof in profile.column_profiles.items():
            stat_parts = []
            if col_prof.mean is not None:
                stat_parts.append(f"Mean: {col_prof.mean}")
            if col_prof.min_val is not None:
                stat_parts.append(f"Min: {col_prof.min_val}")
            if col_prof.max_val is not None:
                stat_parts.append(f"Max: {col_prof.max_val}")
            if col_prof.outliers_count is not None and col_prof.outliers_count > 0:
                stat_parts.append(f"Outliers Count: {col_prof.outliers_count}")

            stats_str = f" ({', '.join(stat_parts)})" if stat_parts else ""
            schema_details.append(
                f"- {col}: Type={col_prof.dtype}, Unique={col_prof.num_unique}, "
                f"Missing={col_prof.missing_count}{stats_str}"
            )
        schema_desc = "\n".join(schema_details)

        system_prompt = (
            "You are a Principal Data Scientist and Executive Business Analyst. "
            "Your task is to analyze the metadata profile of a dataset and generate "
            "a structured insights report. You must respond ONLY with a raw JSON "
            "object matching this schema. Do not include conversational text.\n"
            "JSON Format:\n"
            "{\n"
            '  "executive_summary": "A high-level executive summary of the '
            'dataset, its health, and business value (3-4 sentences).",\n'
            '  "trends": [\n'
            '    "Trend 1: detail...",\n'
            '    "Trend 2: detail..."\n'
            "  ],\n"
            '  "patterns": [\n'
            '    "Pattern 1: detail...",\n'
            '    "Pattern 2: detail..."\n'
            "  ],\n"
            '  "anomalies": [\n'
            '    "Anomaly 1: detail... (e.g. missing data or outlier counts)",\n'
            '    "Anomaly 2: detail..."\n'
            "  ],\n"
            '  "recommendations": [\n'
            '    "Recommendation 1: actionable business or engineering step...",\n'
            '    "Recommendation 2: step..."\n'
            "  ]\n"
            "}\n"
            "Make your findings specific, realistic, and highly professional."
        )

        prompt = (
            f"Dataset Metadata Profile:\n"
            f"- Row Count: {profile.num_rows}\n"
            f"- Column Count: {profile.num_cols}\n"
            f"- Duplicate Rows: {profile.duplicate_rows} "
            f"({profile.duplicate_pct}%)\n"
            f"- Memory Footprint: {profile.memory_usage_str}\n\n"
            f"Columns and Statistics:\n"
            f"{schema_desc}\n\n"
            f"JSON Insights:"
        )

        try:
            raw = self.ollama_service.generate_completion(
                model=self.model_name,
                prompt=prompt,
                system_prompt=system_prompt,
                # Low temperature for analytical consistency
                options={"temperature": 0.2},
            )
            config_dict = self._parse_json_insights(raw)
            return InsightsReport(**config_dict)
        except Exception as e:
            logger.error(f"Failed to generate structured insights: {e}")
            # Fallback safe default report
            return InsightsReport(
                executive_summary=(
                    f"This dataset contains {profile.num_rows} rows and "
                    f"{profile.num_cols} columns with a memory size of "
                    f"{profile.memory_usage_str}. Data profiling was completed "
                    f"successfully."
                ),
                trends=[
                    f"The dataset is composed of {profile.num_cols} columns with "
                    "various distributions."
                ],
                patterns=["Pattern analysis not available due to LLM parsing timeout."],
                anomalies=[f"Detected {profile.duplicate_rows} duplicate rows."]
                + [
                    f"Column '{c}' has {p.missing_count} missing values."
                    for c, p in profile.column_profiles.items()
                    if p.missing_count > 0
                ],
                recommendations=[
                    "Clean duplicate rows and address missing values to prepare "
                    "the data for modeling."
                ],
            )

    def _parse_json_insights(self, raw: str) -> dict[str, Any]:
        """Cleans and extracts JSON dict from raw LLM response."""
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
                raise ValueError("Response is not a JSON object.")

            # Guarantee all fields exist with fallbacks
            for field in [
                "executive_summary",
                "trends",
                "patterns",
                "anomalies",
                "recommendations",
            ]:
                if field not in res:
                    if field == "executive_summary":
                        res[field] = "Executive summary missing."
                    else:
                        res[field] = []

            # Clean and validate array contents
            for field in ["trends", "patterns", "anomalies", "recommendations"]:
                if not isinstance(res[field], list):
                    res[field] = [str(res[field])]
                res[field] = [str(item) for item in res[field]]

            return res
        except Exception as e:
            logger.error(f"Failed to parse insights JSON: {e}. Raw content: {cleaned}")
            raise ValueError(f"Failed to parse LLM insights: {e}") from e
