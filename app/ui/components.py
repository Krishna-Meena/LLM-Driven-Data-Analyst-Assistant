"""Reusable premium UI components for the Streamlit dashboard.

Provides glassmorphic KPI cards, status indicators, section headers,
and feature grid items using the project's design system tokens.
"""

import streamlit as st


def kpi_card(label: str, value: str, icon: str = "📊") -> None:
    """Renders a premium glassmorphism KPI card with gradient accent.

    Args:
        label: Text label of the KPI.
        value: Numeric or text value to display prominently.
        icon: Emoji icon to display above the value.
    """
    st.markdown(
        f"""
        <div class="glass-card kpi-container">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-val">{value}</div>
            <div class="kpi-lbl">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_indicator(is_healthy: bool, label: str) -> None:
    """Renders a pulsing status indicator dot with text.

    Args:
        is_healthy: True for green success state, False for red failure state.
        label: Descriptive label adjacent to the indicator.
    """
    status_class = "online" if is_healthy else "offline"
    status_text = "Connected" if is_healthy else "Disconnected"
    text_color = "#10B981" if is_healthy else "#EF4444"

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        ">
            <div class="status-dot {status_class}"></div>
            <div style="flex: 1;">
                <div style="
                    font-size: 0.78rem;
                    font-weight: 500;
                    color: #E2E8F0;
                ">{label}</div>
                <div style="
                    font-size: 0.68rem;
                    font-weight: 600;
                    color: {text_color};
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">{status_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str | None = None) -> None:
    """Renders a styled section header with optional subtitle.

    Args:
        title: Title of the section.
        subtitle: Optional detailed subtext.
    """
    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<p class="section-subtitle">{subtitle}</p>'

    st.markdown(
        f"""
        <div class="section-header">
            <h2>{title}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_banner(text: str) -> None:
    """Renders a glassmorphic purple-bordered information callout card.

    Args:
        text: Notification message.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="
            border-left: 3px solid #7C3AED !important;
            padding: 16px 20px !important;
            margin-bottom: 16px !important;
        ">
            <div style="
                color: #E2E8F0;
                font-size: 0.9rem;
                line-height: 1.6;
            ">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(icon: str, title: str, description: str) -> str:
    """Returns an HTML string for a single feature card in the welcome grid.

    Args:
        icon: Emoji icon for the feature.
        title: Feature title.
        description: Short description text.

    Returns:
        HTML string for the feature card.
    """
    return f"""
    <div class="feature-item">
        <span class="icon">{icon}</span>
        <div class="title">{title}</div>
        <div class="desc">{description}</div>
    </div>
    """


def welcome_feature_grid() -> None:
    """Renders the welcome page feature grid with all core capabilities."""
    features = [
        feature_card(
            "📂",
            "Smart Data Ingestion",
            "Upload CSV, Excel, or Parquet files with automatic schema "
            "detection and profiling.",
        ),
        feature_card(
            "🔍",
            "Natural Language SQL",
            "Ask questions in plain English — the AI translates them to "
            "optimized DuckDB queries.",
        ),
        feature_card(
            "📈",
            "Interactive Visualizations",
            "Auto-generated Plotly charts with dark-mode styling and "
            "intelligent chart type selection.",
        ),
        feature_card(
            "💡",
            "Executive Insights",
            "AI-powered trend detection, anomaly flagging, and strategic "
            "recommendations.",
        ),
        feature_card(
            "💬",
            "Conversational AI Chat",
            "Discuss your data with context-aware AI that understands "
            "your dataset schema.",
        ),
        feature_card(
            "🔒",
            "100% Local & Private",
            "All processing runs on your machine via Ollama — no data "
            "ever leaves your device.",
        ),
    ]

    grid_html = '<div class="feature-grid">' + "".join(features) + "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)
