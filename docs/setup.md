# Local Installation & Setup Guide

This guide walks you through setting up and running the **Local LLM Data Analyst** project on your local machine.

---

## Prerequisites

Before getting started, make sure you have the following installed:

1. **Python 3.12+**
2. **uv Package Manager** (Fastest package manager for Python)
   - Install via PowerShell (Windows):
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - Install via terminal (macOS/Linux):
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
3. **Ollama** (For running LLMs locally)
   - Download and install from: [ollama.com](https://ollama.com)

---

## Step 1: Install Local LLM Models

The application auto-detects installed models. We recommend using `qwen2.5-coder:7b` as it has superior SQL and charting performance, or `llama3.3` for large language analytical tasks.

Open your terminal or command prompt and run:

```bash
# Pull the default coder model (4.7 GB)
ollama pull qwen2.5-coder:7b
```

Alternatively, you can pull any other model:
```bash
ollama pull llama3.3
```

---

## Step 2: Clone and Sync Dependencies

1. Clone the repository to your local computer.
2. Navigate into the project root directory and run `uv sync` to automatically set up the virtual environment (`.venv`) and install all required packages:

```bash
# Sync dependencies
uv sync
```

This installs Streamlit, Pandas, NumPy, Plotly, DuckDB, Pydantic, fpdf2, pytest, ruff, mypy, and pre-commit hooks.

---

## Step 3: Run the Application

Start the Streamlit application using `uv run`:

```bash
uv run streamlit run app/main.py
```

The application will launch in your default web browser (typically at `http://localhost:8501`).

---

## Troubleshooting

### Ollama Server Connection Failed
If the sidebar indicates "Ollama Server Status: Offline", the app will attempt to start the server automatically. If it fails:
1. Make sure the Ollama application is active in your system tray (Windows/macOS).
2. Manually start the server in a separate terminal:
   ```bash
   ollama serve
   ```
3. Verify connection in your browser by visiting `http://127.0.0.1:11434`.

### Package Ingestion Errors
If Excel loading fails, make sure you did not exclude `openpyxl` from the environment. Check that your virtual environment is up to date:
```bash
uv sync --clean
```
