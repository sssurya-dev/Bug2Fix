FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configure git for the demo project
RUN git config --global user.email "bug2fix@demo.com" && \
    git config --global user.name "Bug2Fix AI"

# Ensure the sample project is in the buggy state
RUN python -c "
from pathlib import Path
import sys
sys.path.insert(0, '.')
from core.orchestrator import reset_sample_project, is_sample_project
ws = Path('sample_projects/python_bug_demo')
if is_sample_project(ws):
    reset_sample_project(ws)
    print('Sample project reset to buggy state.')
"

EXPOSE 8501
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start Streamlit (primary) — run FastAPI API in background
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port 8000 & streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0"]
