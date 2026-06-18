"""Module for generating Markdown, HTML, and PDF analysis reports."""

import datetime

from fpdf import FPDF

from app.analytics.insight_engine import InsightsReport
from app.analytics.profiler import DataProfile
from app.utils.logger import setup_logger

logger = setup_logger("report_generator")


class PDFReport(FPDF):
    """Custom FPDF subclass for styling PDF reports."""

    def header(self) -> None:
        """Draws report header on every page."""
        self.set_text_color(248, 250, 252)  # slate-50
        self.set_fill_color(15, 23, 42)  # slate-900 background for top banner
        self.rect(0, 0, 210, 25, "F")

        self.set_y(8)
        self.set_font("helvetica", "B", 14)
        self.cell(
            w=0,
            h=10,
            text="LOCAL LLM DATA ANALYST REPORT",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )
        self.ln(10)

    def footer(self) -> None:
        """Draws footer with page number on every page."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)  # slate-400
        # Page number
        self.cell(
            w=0,
            h=10,
            text=f"Page {self.page_no()}/{{nb}}",
            new_x="RIGHT",
            new_y="LAST",
            align="C",
        )


class ReportGenerator:
    """Generates analytical reports in Markdown, HTML, and PDF formats."""

    def generate_markdown_report(
        self, profile: DataProfile, insights: InsightsReport
    ) -> str:
        """Generates report content formatted as Markdown.

        Args:
            profile: Metadata profiling of the dataset.
            insights: Generated LLM insights.

        Returns:
            A Markdown string representing the report.
        """
        logger.info("Generating Markdown report...")
        date_str = datetime.date.today().strftime("%B %d, %Y")

        md = f"""# Executive Data Analysis Report
*Generated on {date_str} by Local LLM Data Analyst*

---

## 1. Executive Summary
{insights.executive_summary}

---

## 2. Dataset Metadata
| Metric | Value |
| :--- | :--- |
| **Row Count** | {profile.num_rows:,} |
| **Column Count** | {profile.num_cols:,} |
| **Duplicate Rows** | {profile.duplicate_rows:,} ({profile.duplicate_pct}%) |
| **Memory Size** | {profile.memory_usage_str} |

### Column Schema and Profiles
| Column Name | Data Type | Unique Values | Missing Values (Pct) | Outliers Count |
| :--- | :--- | :--- | :--- | :--- |
"""

        for col, col_prof in profile.column_profiles.items():
            outliers = (
                str(col_prof.outliers_count)
                if col_prof.outliers_count is not None
                else "N/A"
            )
            md += (
                f"| {col} | {col_prof.dtype} | {col_prof.num_unique:,} | "
                f"{col_prof.missing_count:,} ({col_prof.missing_pct}%) | {outliers} |\n"
            )

        md += "\n---\n\n## 3. Deep Analytical Insights\n"

        md += "### Key Trends\n"
        for trend in insights.trends:
            md += f"- {trend}\n"

        md += "\n### Observed Patterns\n"
        for pattern in insights.patterns:
            md += f"- {pattern}\n"

        md += "\n### Anomalies & Data Health Issues\n"
        for anomaly in insights.anomalies:
            md += f"- {anomaly}\n"

        md += "\n---\n\n## 4. Strategic Recommendations\n"
        for rec in insights.recommendations:
            md += f"- {rec}\n"

        md += "\n---\n*End of Report.*"
        return md

    def generate_html_report(
        self, profile: DataProfile, insights: InsightsReport
    ) -> str:
        """Generates report content formatted as styled HTML.

        Args:
            profile: Metadata profiling of the dataset.
            insights: Generated LLM insights.

        Returns:
            An HTML string representing the report.
        """
        logger.info("Generating HTML report...")
        date_str = datetime.date.today().strftime("%B %d, %Y")

        schema_rows = ""
        for col, col_prof in profile.column_profiles.items():
            outliers = (
                str(col_prof.outliers_count)
                if col_prof.outliers_count is not None
                else "N/A"
            )
            schema_rows += f"""
            <tr>
                <td><strong>{col}</strong></td>
                <td><code>{col_prof.dtype}</code></td>
                <td>{col_prof.num_unique:,}</td>
                <td>{col_prof.missing_count:,} ({col_prof.missing_pct}%)</td>
                <td>{outliers}</td>
            </tr>"""

        trends_list = "".join(f"<li>{t}</li>" for t in insights.trends)
        patterns_list = "".join(f"<li>{p}</li>" for p in insights.patterns)
        anomalies_list = "".join(f"<li>{a}</li>" for a in insights.anomalies)
        recs_list = "".join(f"<li>{r}</li>" for r in insights.recommendations)

        # Build stylesheet link and title section wrapped to fit 88 chars
        fonts_link = (
            '<link href="https://fonts.googleapis.com/css2?'
            "family=Inter:wght@300;400;500;600;700&"
            'family=Outfit:wght@400;500;600;700&display=swap" '
            'rel="stylesheet">'
        )

        title_sub = f"Generated on {date_str} &bull; Powered by Local LLM Data Analyst"

        footer_text = (
            f"&copy; {datetime.date.today().year} "
            "Local LLM Data Analyst Dashboard. "
            "Confidential Executive Briefing."
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Data Analysis Report</title>
    {fonts_link}
    <style>
        :root {{
            --bg-color: #0B0F19;
            --card-bg: rgba(17, 25, 40, 0.75);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-color: #E2E8F0;
            --text-muted: #94A3B8;
            --accent-color: #3B82F6;
            --accent-glow: rgba(59, 130, 246, 0.15);
            --success-color: #10B981;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            color: #F8FAFC;
            margin-bottom: 10px;
            font-weight: 700;
            background: linear-gradient(135deg, #F8FAFC 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .meta-subtitle {{
            color: var(--text-muted);
            font-size: 1rem;
        }}
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }}
        h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            color: #F1F5F9;
            margin-top: 0;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }}
        h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.2rem;
            color: #E2E8F0;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-item {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .metric-val {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--accent-color);
            font-family: 'Outfit', sans-serif;
            margin-bottom: 5px;
        }}
        .metric-lbl {{
            color: var(--text-muted);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            color: #F1F5F9;
            background: rgba(255, 255, 255, 0.02);
            font-weight: 600;
        }}
        code {{
            background: rgba(255, 255, 255, 0.08);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9em;
            color: #F472B6;
        }}
        ul {{
            padding-left: 20px;
            margin: 0;
        }}
        li {{
            margin-bottom: 10px;
        }}
        footer.report-footer {{
            text-align: center;
            margin-top: 60px;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Executive Data Analysis Report</h1>
            <div class="meta-subtitle">{title_sub}</div>
        </header>

        <section class="card">
            <h2>1. Executive Summary</h2>
            <p style="font-size: 1.1rem; color: #F1F5F9; line-height: 1.7;">
                {insights.executive_summary}
            </p>
        </section>

        <section class="card">
            <h2>2. Dataset Ingestion & Profile</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-val">{profile.num_rows:,}</div>
                    <div class="metric-lbl">Total Rows</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{profile.num_cols:,}</div>
                    <div class="metric-lbl">Total Columns</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{profile.duplicate_rows:,}</div>
                    <div class="metric-lbl">Duplicates ({profile.duplicate_pct}%)</div>
                </div>
                <div class="metric-item">
                    <div class="metric-val">{profile.memory_usage_str}</div>
                    <div class="metric-lbl">Memory Size</div>
                </div>
            </div>

            <h3>Column Profile Table</h3>
            <table>
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Data Type</th>
                        <th>Unique Values</th>
                        <th>Missing Values (Pct)</th>
                        <th>Outliers (IQR)</th>
                    </tr>
                </thead>
                <tbody>
                    {schema_rows}
                </tbody>
            </table>
        </section>

        <section class="card">
            <h2>3. Deep Analytical Insights</h2>

            <h3>Key Trends</h3>
            <ul>{trends_list}</ul>

            <h3>Observed Patterns</h3>
            <ul>{patterns_list}</ul>

            <h3>Data Quality & Anomalies</h3>
            <ul>{anomalies_list}</ul>
        </section>

        <section class="card">
            <h2>4. Strategic Recommendations</h2>
            <ul style="color: #F1F5F9; font-weight: 500;">{recs_list}</ul>
        </section>

        <footer class="report-footer">
            {footer_text}
        </footer>
    </div>
</body>
</html>"""
        return html

    def generate_pdf_report(
        self,
        profile: DataProfile,
        insights: InsightsReport,
        output_path: str,
    ) -> None:
        """Generates a structured PDF report and saves it to output_path.

        Args:
            profile: Metadata profiling of the dataset.
            insights: Generated LLM insights.
            output_path: Local filepath to save the PDF.
        """
        logger.info(f"Generating PDF report at path: {output_path}")

        # Instantiate custom PDF class
        pdf = PDFReport(orientation="P", unit="mm", format="A4")
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_margins(15, 20, 15)

        # Title spacer
        pdf.ln(10)

        # 1. Executive Summary
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)  # slate-900
        pdf.cell(w=0, h=10, text="1. Executive Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)  # slate-700
        pdf.multi_cell(w=0, h=5, text=insights.executive_summary)
        pdf.ln(8)

        # 2. Metadata Profile
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w=0, h=10, text="2. Dataset Profile", new_x="LMARGIN", new_y="NEXT")
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(4)

        pdf.set_font("helvetica", "", 10)
        pdf.cell(w=50, h=6, text="Total Rows:")
        pdf.cell(w=40, h=6, text=f"{profile.num_rows:,}", new_x="LMARGIN", new_y="NEXT")

        pdf.cell(w=50, h=6, text="Total Columns:")
        pdf.cell(w=40, h=6, text=f"{profile.num_cols:,}", new_x="LMARGIN", new_y="NEXT")

        pdf.cell(w=50, h=6, text="Duplicate Rows:")
        pdf.cell(
            w=40,
            h=6,
            text=f"{profile.duplicate_rows:,} ({profile.duplicate_pct}%)",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.cell(w=50, h=6, text="Memory Footprint:")
        pdf.cell(
            w=40,
            h=6,
            text=profile.memory_usage_str,
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(6)

        # 3. Table of Schema
        pdf.set_font("helvetica", "B", 9)
        pdf.set_fill_color(241, 245, 249)  # light gray header background
        pdf.cell(w=45, h=7, text="Column Name", border=1, fill=True)
        pdf.cell(w=30, h=7, text="Type", border=1, align="C", fill=True)
        pdf.cell(w=30, h=7, text="Unique Val", border=1, align="C", fill=True)
        pdf.cell(w=40, h=7, text="Missing (Pct)", border=1, align="C", fill=True)
        pdf.cell(
            w=35,
            h=7,
            text="Outliers (IQR)",
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
            fill=True,
        )

        pdf.set_font("helvetica", "", 9)
        for col, col_prof in profile.column_profiles.items():
            outliers = (
                str(col_prof.outliers_count)
                if col_prof.outliers_count is not None
                else "N/A"
            )
            # Add page break check before printing row
            if pdf.get_y() > 250:
                pdf.add_page()
                pdf.set_font("helvetica", "B", 9)
                pdf.cell(w=45, h=7, text="Column Name", border=1, fill=True)
                pdf.cell(w=30, h=7, text="Type", border=1, align="C", fill=True)
                pdf.cell(w=30, h=7, text="Unique Val", border=1, align="C", fill=True)
                pdf.cell(
                    w=40, h=7, text="Missing (Pct)", border=1, align="C", fill=True
                )
                pdf.cell(
                    w=35,
                    h=7,
                    text="Outliers (IQR)",
                    border=1,
                    new_x="LMARGIN",
                    new_y="NEXT",
                    align="C",
                    fill=True,
                )
                pdf.set_font("helvetica", "", 9)

            # Clean name for PDF encoding
            clean_col = col[:22]
            pdf.cell(w=45, h=6, text=clean_col, border=1)
            pdf.cell(w=30, h=6, text=str(col_prof.dtype)[:12], border=1, align="C")
            pdf.cell(w=30, h=6, text=f"{col_prof.num_unique:,}", border=1, align="C")
            pdf.cell(
                w=40,
                h=6,
                text=f"{col_prof.missing_count:,} ({col_prof.missing_pct}%)",
                border=1,
                align="C",
            )
            pdf.cell(
                w=35,
                h=6,
                text=outliers,
                border=1,
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
            )

        # Page break check for insights
        if pdf.get_y() > 200:
            pdf.add_page()
        else:
            pdf.ln(8)

        # 4. Deep Analytical Insights
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(
            w=0,
            h=10,
            text="3. Deep Analytical Insights",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(4)

        # Helper method to print lists
        def print_bullet_section(title: str, bullets: list[str]) -> None:
            nonlocal pdf
            if pdf.get_y() > 230:
                pdf.add_page()
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(51, 65, 85)
            pdf.cell(w=0, h=6, text=title, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            pdf.set_font("helvetica", "", 10)
            for bullet in bullets:
                # Page break check for bullet point
                if pdf.get_y() > 265:
                    pdf.add_page()
                pdf.cell(w=5, h=5, text=chr(149), align="C")  # bullet character
                pdf.multi_cell(w=0, h=5, text=bullet)
                pdf.ln(1.5)
            pdf.ln(4)

        print_bullet_section("Key Trends", insights.trends)
        print_bullet_section("Observed Patterns", insights.patterns)
        print_bullet_section("Anomalies and Data Quality", insights.anomalies)

        # Page break check for recommendations
        if pdf.get_y() > 200:
            pdf.add_page()

        # 5. Recommendations
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(
            w=0,
            h=10,
            text="4. Strategic Recommendations",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(4)

        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        for rec in insights.recommendations:
            if pdf.get_y() > 265:
                pdf.add_page()
            pdf.cell(w=5, h=5, text=chr(149), align="C")
            pdf.multi_cell(w=0, h=5, text=rec)
            pdf.ln(1.5)

        # Output the PDF file
        pdf.output(output_path)
        logger.info("PDF report saved successfully.")
