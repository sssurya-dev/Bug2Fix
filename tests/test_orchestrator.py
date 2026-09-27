"""
tests/test_orchestrator.py — Tests for the orchestration workflow.
"""

import sys
import os
from pathlib import Path

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest

SAMPLE_PROJECT = str(ROOT / "sample_projects" / "python_bug_demo")


# ---------------------------------------------------------------------------
# Orchestrator tests
# ---------------------------------------------------------------------------

def test_orchestrator_imports():
    """Orchestrator module must import without errors."""
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    assert orch is not None


def test_orchestrator_start_creates_run(tmp_path):
    """Starting a run must return a valid run_id and store state."""
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    bug_report = {
        "title":         "Test bug",
        "description":   "A test bug for unit testing.",
        "error_message": "ValueError: test",
        "stack_trace":   "  File test.py line 1\nValueError: test",
    }
    run_id = orch.start(SAMPLE_PROJECT, bug_report, documents=[])
    assert run_id
    assert run_id.startswith("run_")

    state = orch.get_state(run_id)
    assert state is not None
    assert state["status"] in ("done", "error", "running")


def test_orchestrator_run_completes(tmp_path):
    """A full run on the sample project must reach 'done' status."""
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    bug_report = {
        "title":         "Missing user crash",
        "description":   "Crash when user not found",
        "error_message": "TypeError: 'NoneType' object is not subscriptable",
        "stack_trace":   "  File app/users.py line 24\nTypeError: 'NoneType' object is not subscriptable",
    }
    run_id = orch.start(SAMPLE_PROJECT, bug_report)
    state  = orch.get_state(run_id)
    assert state["status"] == "done"


def test_orchestrator_has_root_cause():
    """After a completed run, root_cause must be populated."""
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    bug_report = {
        "title": "Bug", "description": "Desc",
        "error_message": "TypeError", "stack_trace": "",
    }
    run_id = orch.start(SAMPLE_PROJECT, bug_report)
    state  = orch.get_state(run_id)
    assert state.get("root_cause"), "root_cause should be populated"


def test_orchestrator_has_report():
    """After a completed run, a report string must be generated."""
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    bug_report = {
        "title": "Bug", "description": "Desc",
        "error_message": "TypeError", "stack_trace": "",
    }
    run_id = orch.start(SAMPLE_PROJECT, bug_report)
    state  = orch.get_state(run_id)
    report = state.get("report", "")
    assert isinstance(report, str)
    assert len(report) > 100, "Report should be non-trivial"


def test_orchestrator_parallel_agents_all_done():
    """All three parallel agents must reach 'done' status."""
    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    bug_report = {
        "title": "Bug", "description": "Desc",
        "error_message": "TypeError", "stack_trace": "",
    }
    run_id = orch.start(SAMPLE_PROJECT, bug_report)
    state  = orch.get_state(run_id)
    agents = state.get("agents", {})
    for key in ("code_explorer", "error_analyzer", "test_analyzer"):
        assert agents.get(key, {}).get("status") == "done", \
            f"Agent {key} did not reach 'done'"
