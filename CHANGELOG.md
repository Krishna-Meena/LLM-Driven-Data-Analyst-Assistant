# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-18

### Added

- **Data Ingestion & Profiling**: Upload CSV, Excel, and Parquet files with automatic schema detection, missing value analysis, duplicate detection, and IQR outlier counting.
- **Natural Language to SQL**: Ask questions in plain English and translate them to optimized DuckDB SQL queries, with automatic execution and result explanation.
- **Interactive Visualizations**: Auto-generated Plotly charts (bar, line, scatter, histogram, heatmap, pie) with premium dark-mode glassmorphic styling.
- **Analytical AI Chat**: Conversational chat with local LLMs featuring sliding-window turn-level memory and dataset-aware context injection.
- **Executive Insights Engine**: LLM-driven trend detection, anomaly flagging, pattern analysis, and strategic recommendations generation.
- **Report Exporter**: Generate executive briefing reports in Markdown, styled HTML, and print-ready PDF formats.
- **Premium UI/UX**: Custom Vercel/Linear-inspired dark theme with glassmorphism, animated gradients, pulsing status indicators, and responsive layouts.
- **Ollama Integration**: Auto-detection, auto-start, health checks, model listing, and retry logic with exponential backoff.
- **Testing**: 29 pytest unit tests covering all functional layers with mocked LLM services.
- **CI/CD**: GitHub Actions pipeline running Ruff, MyPy, and Pytest on every push.
- **Documentation**: Architecture guide, setup instructions, deployment guide, and contributing guidelines.
