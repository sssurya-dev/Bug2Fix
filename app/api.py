"""
app/api.py — FastAPI health check and status API for Bug2Fix AI.

Provides:
  GET /health       — service liveness check
  GET /status       — application version info
  GET /runs         — list recent run IDs (read-only)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Bug2Fix AI API",
    description="IBM Bob 2.0 Evidence-First Debugging Workflow",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_start_time = datetime.now()


@app.get("/health")
async def health():
    """
    Service liveness check.

    Returns HTTP 200 when the service is up.
    """
    return {
        "status":    "ok",
        "service":   "bug2fix-ai",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - _start_time).total_seconds(),
    }


@app.get("/status")
async def status():
    """Application version and configuration summary."""
    try:
        from core.bob_execution_adapter import BOB_AVAILABLE, BOB_EXECUTABLE
    except Exception:
        BOB_AVAILABLE  = False
        BOB_EXECUTABLE = None

    reports_dir = Path("reports")
    report_count = len(list(reports_dir.glob("bug2fix_report_*.md"))) if reports_dir.exists() else 0

    return {
        "service":      "bug2fix-ai",
        "version":      "1.0.0",
        "bob_available": BOB_AVAILABLE,
        "bob_mode":      "live" if BOB_AVAILABLE else "demo",
        "bob_executable": BOB_EXECUTABLE,
        "reports_generated": report_count,
        "timestamp":    datetime.now().isoformat(),
    }


@app.get("/runs")
async def list_runs():
    """List recent debugging run report IDs."""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        return {"runs": []}

    runs = sorted(reports_dir.glob("bug2fix_report_*.md"), reverse=True)[:20]
    return {
        "runs": [r.stem.replace("bug2fix_report_", "") for r in runs],
        "count": len(runs),
    }
