# ruff: noqa: E402
"""Main Streamlit application entry point for the Local LLM Data Analyst."""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path to enable absolute imports from 'app' package
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pandas as pd
import streamlit as st

from app.analytics.insight_engine import InsightEngine
from app.analytics.profiler import load_file, profile_dataframe
from app.analytics.sql_engine import SQLEngine
from app.charts.chart_generator import ChartGenerator
from app.llm.chat_engine import ChatEngine
from app.reports.report_generator import ReportGenerator
from app.services.ollama_service import OllamaService
from app.ui.components import (
    kpi_card,
    section_header,
    status_indicator,
    welcome_feature_grid,
)
from app.ui.styles import get_custom_css

# Page Configuration
st.set_page_config(
    page_title="Local LLM Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Custom SaaS CSS Styles
st.markdown(get_custom_css(), unsafe_allow_html=True)


def initialize_engines(selected_model: str) -> None:
    """Instantiates and updates all logic engines in session state.

    Args:
        selected_model: Name of the LLM model chosen by the user.
    """
    ollama_srv = st.session_state.ollama_service
    st.session_state.chat_engine = ChatEngine(
        ollama_service=ollama_srv, model_name=selected_model
    )
    st.session_state.sql_engine = SQLEngine(
        ollama_service=ollama_srv, model_name=selected_model
    )
    st.session_state.chart_generator = ChartGenerator(
        ollama_service=ollama_srv, model_name=selected_model
    )
    st.session_state.insight_engine = InsightEngine(
        ollama_service=ollama_srv, model_name=selected_model
    )


# --- SESSION STATE INITIALIZATION ---
if "ollama_service" not in st.session_state:
    st.session_state.ollama_service = OllamaService()

if "report_generator" not in st.session_state:
    st.session_state.report_generator = ReportGenerator()

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.profile = None
    st.session_state.insights = None

# Ensure Ollama is running and healthy
ollama_active = st.session_state.ollama_service.is_healthy()
if not ollama_active:
    with st.spinner("Initializing Local Ollama Service..."):
        ollama_active = st.session_state.ollama_service.ensure_ollama_running()

# --- SIDEBAR LAYER ---
with st.sidebar:
    st.markdown(
        '<div class="app-title">📊 Local Analyst</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="version-badge">v0.1.0 • Local LLM</div>',
        unsafe_allow_html=True,
    )

    # Health Indicator
    status_indicator(ollama_active, "Ollama Server")

    # Available Models Selector
    available_models: list[str] = []
    if ollama_active:
        available_models = st.session_state.ollama_service.get_available_models()

    if not available_models:
        st.warning("No local models found. Run: 'ollama pull qwen2.5-coder:7b'")
        selected_model = "qwen2.5-coder:7b"  # Default fallback name
    else:
        # Sort so qwen or coder models appear first if possible
        available_models.sort(key=lambda m: 0 if "coder" in m or "llama" in m else 1)
        selected_model = st.selectbox(
            "Target LLM Model",
            options=available_models,
            index=0,
        )

    # Check if model has changed to reinitialize chat context
    if (
        "current_model" not in st.session_state
        or st.session_state.current_model != selected_model
    ):
        st.session_state.current_model = selected_model
        if ollama_active:
            initialize_engines(selected_model)

    st.markdown("---")

    # File Ingestion Widget
    uploaded_file = st.file_uploader(
        "Ingest Data File",
        type=["csv", "xlsx", "xls", "parquet"],
        help="Supports CSV, Excel, and Parquet data formats.",
    )

    if uploaded_file is not None:
        try:
            # Check if file has changed
            file_changed = (
                "filename" not in st.session_state
                or st.session_state.filename != uploaded_file.name
            )
            if file_changed:
                with st.spinner("Ingesting file and parsing DataFrame..."):
                    df = load_file(uploaded_file, uploaded_file.name)
                    st.session_state.df = df
                    st.session_state.filename = uploaded_file.name
                    st.session_state.profile = profile_dataframe(df)

                    # Auto-register in SQL engine
                    if "sql_engine" in st.session_state:
                        st.session_state.sql_engine.register_dataframe(df)

                    # Reset insights and chat when a new file is loaded
                    st.session_state.insights = None
                    if "chat_engine" in st.session_state:
                        st.session_state.chat_engine.clear_history()

                st.success(f"Successfully loaded '{uploaded_file.name}'!")
        except Exception as e:
            st.error(f"Ingestion failed: {e}")

    # Navigation menu
    st.markdown("### Navigation")
    nav_option = st.radio(
        "Go to",
        options=[
            "📊 Data Profile",
            "🔍 SQL Analytics Studio",
            "💬 Analytical AI Chat",
            "💡 Executive Insights",
        ],
        disabled=(st.session_state.df is None),
        label_visibility="collapsed",
    )

# --- MAIN APP VIEW ---
# Welcome view if no dataset is loaded
if st.session_state.df is None:
    st.markdown(
        '<div class="hero-title">Local LLM Data Analyst</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-subtitle">
            Your private, AI-powered data analysis workspace.
            Upload datasets, run natural language queries, generate interactive
            charts, and compile executive reports — all running 100% locally
            on your machine.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    welcome_feature_grid()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card" style="
            border-left: 3px solid #7C3AED !important;
            padding: 20px 24px !important;
        ">
            <div style="
                font-family: 'Outfit', sans-serif;
                font-weight: 600;
                font-size: 1rem;
                color: #F1F5F9;
                margin-bottom: 10px;
            ">Quick Start</div>
            <ol style="
                color: #CBD5E1;
                padding-left: 20px;
                margin: 0;
                line-height: 2;
                font-size: 0.9rem;
            ">
                <li>Ensure <strong style="color: #7C3AED;">Ollama</strong>
                    is running locally</li>
                <li>Upload a <strong style="color: #06B6D4;">CSV, Excel,
                    or Parquet</strong> file using the sidebar</li>
                <li>Navigate the analytics studio with the sidebar menu</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Active Analysis Dashboard
else:
    df = st.session_state.df
    profile = st.session_state.profile

    # --- VIEW 1: DATA PROFILE ---
    if nav_option == "📊 Data Profile":
        section_header(
            "Data Profiling & Metadata",
            f"Structural summary of '{st.session_state.filename}'",
        )

        # KPI Metrics Row
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            kpi_card("Total Rows", f"{profile.num_rows:,}", "📋")
        with col2:
            kpi_card("Total Columns", f"{profile.num_cols:,}", "📐")
        with col3:
            kpi_card("Duplicate Rows", f"{profile.duplicate_rows:,}", "🔁")
        with col4:
            kpi_card("Memory Size", profile.memory_usage_str, "💾")

        # Column profile details
        st.markdown("### Column Schema & Types")

        schema_rows = []
        for col_name, col_prof in profile.column_profiles.items():
            outliers = (
                str(col_prof.outliers_count)
                if col_prof.outliers_count is not None
                else "N/A"
            )
            mean_val = f"{col_prof.mean:,.2f}" if col_prof.mean is not None else "N/A"
            schema_rows.append(
                {
                    "Column Name": col_name,
                    "Type": col_prof.dtype,
                    "Unique Values": col_prof.num_unique,
                    "Missing Values": (
                        f"{col_prof.missing_count} ({col_prof.missing_pct}%)"
                    ),
                    "Mean": mean_val,
                    "Outliers (IQR)": outliers,
                }
            )
        st.dataframe(pd.DataFrame(schema_rows), width="stretch")

        # Preview Data
        st.markdown("### Raw Dataset Preview (Top 20 rows)")
        st.dataframe(df.head(20), width="stretch")

    # --- VIEW 2: SQL ANALYTICS STUDIO ---
    elif nav_option == "🔍 SQL Analytics Studio":
        section_header(
            "SQL Analytics Studio",
            "Ask questions in plain English — translates to SQL, executes in DuckDB",
        )

        # SQL Input
        user_sql_question = st.text_input(
            "Enter your analysis question:",
            placeholder="e.g. 'What are the top 5 rows based on values?'",
        )

        if st.button("Generate & Run SQL"):
            if user_sql_question:
                with st.spinner("Generating DuckDB SQL query..."):
                    try:
                        # Ensure engines are initialized
                        if "sql_engine" not in st.session_state:
                            initialize_engines(selected_model)

                        sql_engine = st.session_state.sql_engine
                        # Ensure DataFrame is registered
                        sql_engine.register_dataframe(df)

                        generated_sql = sql_engine.generate_sql(
                            user_sql_question, profile
                        )

                        # Render SQL Codeblock
                        st.markdown("### Generated SQL Query")
                        st.code(generated_sql, language="sql")

                        # Run Query
                        with st.spinner("Running query in DuckDB..."):
                            res_df = sql_engine.execute_query(generated_sql)

                        st.markdown("### Query Results")
                        st.dataframe(res_df, width="stretch")

                        # Explain findings
                        with st.spinner("Analyzing results..."):
                            explanation = sql_engine.explain_results(
                                user_sql_question, generated_sql, res_df
                            )

                        st.markdown("### Executive Explanation")
                        st.markdown(
                            f'<div class="glass-card">{explanation}</div>',
                            unsafe_allow_html=True,
                        )

                        # Auto-generate chart of results if
                        # numeric columns exist
                        if len(res_df) > 0 and "chart_generator" in st.session_state:
                            chart_gen = st.session_state.chart_generator
                            fig = chart_gen.auto_generate_chart(res_df)
                            if fig is not None:
                                st.markdown("### Interactive Visualizations")
                                st.plotly_chart(fig, width="stretch")

                    except Exception as e:
                        st.error(f"Execution Error: {e}")
            else:
                st.warning("Please type a question first.")

    # --- VIEW 3: ANALYTICAL AI CHAT ---
    elif nav_option == "💬 Analytical AI Chat":
        section_header(
            "Analytical AI Chat",
            "Discuss findings, columns, or formulas conversationally "
            "with the local model",
        )

        # Clear chat button
        if st.button("Clear Chat History"):
            if "chat_engine" in st.session_state:
                st.session_state.chat_engine.clear_history()

        # Display history
        if "chat_engine" in st.session_state and st.session_state.chat_engine.history:
            for msg in st.session_state.chat_engine.history:
                role = msg["role"]
                content = msg["content"]
                if role == "user":
                    user_msg_html = (
                        f'<div class="chat-msg-user"><strong>You</strong>'
                        f"<br>{content}</div>"
                    )
                    st.markdown(user_msg_html, unsafe_allow_html=True)
                elif role == "assistant":
                    asst_msg_html = (
                        '<div class="chat-msg-assistant">'
                        f"<strong>Assistant</strong><br>{content}</div>"
                    )
                    st.markdown(asst_msg_html, unsafe_allow_html=True)

        # User input
        user_chat_msg = st.text_input(
            "Ask the AI Assistant:",
            placeholder="e.g. 'What next analysis steps do you recommend?'",
        )

        if st.button("Send Message"):
            if user_chat_msg:
                # Ensure chat engine is initialized
                if "chat_engine" not in st.session_state:
                    initialize_engines(selected_model)

                with st.spinner("Assistant thinking..."):
                    try:
                        reply = st.session_state.chat_engine.generate_response(
                            user_chat_msg, df, profile
                        )
                        st.rerun()  # Refresh screen to show messages in order
                    except Exception as e:
                        st.error(f"Chat Error: {e}")
            else:
                st.warning("Please enter a message.")

        # Display execution logs in expander
        if (
            "chat_engine" in st.session_state
            and st.session_state.chat_engine.execution_logs
        ):
            with st.expander("🛠️ View Assistant System Execution Logs"):
                for log in st.session_state.chat_engine.execution_logs:
                    st.text(log)

    # --- VIEW 4: EXECUTIVE INSIGHTS ---
    elif nav_option == "💡 Executive Insights":
        section_header(
            "Executive Insights Hub",
            "Generate business-specific patterns, anomalies, "
            "and strategic recommendations",
        )

        # Generate Button
        if st.button("Generate Executive Insights Briefing"):
            with st.spinner("Analyzing statistics and generating briefing..."):
                try:
                    if "insight_engine" not in st.session_state:
                        initialize_engines(selected_model)

                    st.session_state.insights = (
                        st.session_state.insight_engine.generate_insights(profile)
                    )
                except Exception as e:
                    st.error(f"Failed to generate briefing: {e}")

        # If insights exist, render them
        if st.session_state.insights is not None:
            insights = st.session_state.insights

            # Executive Summary card
            st.markdown("### Executive Summary")
            summary_html = (
                '<div class="glass-card" style="font-size: 1.05rem; '
                f'line-height: 1.75;">{insights.executive_summary}</div>'
            )
            st.markdown(summary_html, unsafe_allow_html=True)

            # Columns layout for lists
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.markdown("### 📈 Key Trends")
                trends_html = "".join(f"<li>{t}</li>" for t in insights.trends)
                st.markdown(
                    f'<div class="glass-card"><ul>{trends_html}</ul></div>',
                    unsafe_allow_html=True,
                )

                st.markdown("### ⚠️ Data Health & Anomalies")
                anom_html = "".join(f"<li>{a}</li>" for a in insights.anomalies)
                st.markdown(
                    f'<div class="glass-card"><ul>{anom_html}</ul></div>',
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown("### 🔍 Observed Patterns")
                patt_html = "".join(f"<li>{p}</li>" for p in insights.patterns)
                st.markdown(
                    f'<div class="glass-card"><ul>{patt_html}</ul></div>',
                    unsafe_allow_html=True,
                )

                st.markdown("### 🎯 Strategic Recommendations")
                recs_html = "".join(f"<li>{r}</li>" for r in insights.recommendations)
                card_style = (
                    '<div class="glass-card" style="border-left: '
                    '3px solid #10B981 !important;">'
                )
                st.markdown(
                    f"{card_style}<ul>{recs_html}</ul></div>",
                    unsafe_allow_html=True,
                )

            # Report Exporters Section
            st.markdown("---")
            st.markdown("### Export Executive Briefing Report")

            # Generate export outputs
            report_gen = st.session_state.report_generator
            md_content = report_gen.generate_markdown_report(profile, insights)
            html_content = report_gen.generate_html_report(profile, insights)

            # PDF needs file writing, use a temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                pdf_path = os.path.join(tmp_dir, "briefing_report.pdf")
                report_gen.generate_pdf_report(profile, insights, pdf_path)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

            # Renders Download Buttons in row
            down_col1, down_col2, down_col3 = st.columns(3, gap="medium")
            with down_col1:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="executive_report.pdf",
                    mime="application/pdf",
                    width="stretch",
                )
            with down_col2:
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_content,
                    file_name="executive_report.html",
                    mime="text/html",
                    width="stretch",
                )
            with down_col3:
                st.download_button(
                    label="📥 Download Markdown Report",
                    data=md_content,
                    file_name="executive_report.md",
                    mime="text/markdown",
                    width="stretch",
                )
