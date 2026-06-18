# Deployment & Containerization Guide

This document describes how to deploy, containerize, and share the **Local LLM Data Analyst** application.

---

## 1. Local Network Sharing
You can share your Streamlit analytics dashboard with colleagues on the same Wi-Fi or Local Area Network (LAN):

1. Start the application:
   ```bash
   uv run streamlit run app/main.py
   ```
2. Note the **Network URL** outputted in the terminal (typically `http://192.168.X.X:8501`).
3. Other devices on the same network can access the dashboard by visiting that URL.

---

## 2. Docker Containerization

To run the application inside a container, you can write a `Dockerfile`.

### Step 1: Create Dockerfile
Create a `Dockerfile` in the project root:

```dockerfile
# Use a lightweight python image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /workspace

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY app/ ./app/

# Expose ports (Streamlit defaults to 8501, Ollama defaults to 11434)
EXPOSE 8501

# Command to run Streamlit
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
```

### Step 2: Configure Ollama for Docker
By default, Docker containers run in an isolated bridge network. If you want the containerized Streamlit app to speak to an Ollama server running on the *host* machine (your computer):

1. Make sure your local Ollama server is listening on all interfaces (or at least on your local host gateway):
   - On Windows, set the environment variable `OLLAMA_HOST=0.0.0.0:11434` and restart Ollama.
2. In the Docker container, point Streamlit's Ollama service to the host IP by setting `OLLAMA_HOST` in the environment, or targeting `http://host.docker.internal:11434`:
   ```bash
   docker build -t local-llm-data-analyst .
   docker run -p 8501:8501 -e OLLAMA_HOST=http://host.docker.internal:11434 local-llm-data-analyst
   ```

---

## 3. GitHub Pages or Vercel
Streamlit apps require a running Python server back-end to execute Pandas and DuckDB commands. Therefore, they **cannot** be deployed to static hosting providers like GitHub Pages or Vercel static deployments.

If you wish to host it online, you can use:
- **Streamlit Community Cloud** (free, connect to a public GitHub repo).
- **Hugging Face Spaces** (free, supports Docker and Streamlit runtimes).
- **Render** or **Railway** (paid, runs Docker containers).
