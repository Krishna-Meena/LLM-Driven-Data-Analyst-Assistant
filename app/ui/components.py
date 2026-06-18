"""Reusable premium UI components for the Streamlit dashboard."""

import streamlit as st


def kpi_card(label: str, value: str) -> None:
    """Renders a custom glassmorphism KPI card.

    Args:
        label: Text label of the KPI.
        value: Numeric or text value to display prominently.
    """
    st.markdown(
        f"""
        <div class="glass-card kpi-container">
            <div class="kpi-lbl">{label}</div>
            <div class="kpi-val">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_indicator(is_healthy: bool, label: str) -> None:
    """Renders a glowing status indicator dot with text.

    Args:
        is_healthy: True for green success state, False for red failure state.
        label: Descriptive label adjacent to the indicator.
    """
    color = "#10B981" if is_healthy else "#EF4444"
    glow = "rgba(16, 185, 129, 0.4)" if is_healthy else "rgba(239, 68, 68, 0.4)"
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0;">
            <div style="
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: {color};
                box-shadow: 0 0 10px {glow};
                transition: all 0.3s ease;
            "></div>
            <span style="font-size: 0.9rem; font-weight: 500; color: #E2E8F0;">
                {label}
            </span>
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
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(
            f'<p style="color: #94A3B8; margin-top: -15px; margin-bottom: 20px;">'
            f"{subtitle}</p>",
            unsafe_allow_html=True,
        )


def info_banner(text: str) -> None:
    """Renders a glassmorphic blue information callout card.

    Args:
        text: Notification message.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="
            border-left: 4px solid #3B82F6 !important;
            padding: 15px 20px !important;
            margin-bottom: 15px !important;
        ">
            <div style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.5;">
                {text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
