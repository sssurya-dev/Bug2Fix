"""
tests/test_evidence_ledger.py — Tests for the evidence ledger module.
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from core.evidence_ledger import (
    new_evidence_record,
    record_input,
    record_investigation,
    record_root_cause,
    record_reproduction,
    record_fix,
    record_verification,
    finalize,
    save_ledger,
    load_ledger,
)


SAMPLE_PROJECT = str(ROOT / "sample_projects" / "python_bug_demo")


def _make_evidence():
    return new_evidence_record("run_test_12345678")


def test_new_evidence_has_required_fields():
    ev = _make_evidence()
    assert ev["run_id"] == "run_test_12345678"
    assert ev["final_status"] == "INVESTIGATING"
    assert isinstance(ev["timeline"], list)
    assert isinstance(ev["verification_gate"], dict)


def test_record_input_populates_fields():
    ev = _make_evidence()
    bug = {"title": "Test bug", "description": "desc", "error_message": "err", "stack_trace": "trace"}
    record_input(ev, SAMPLE_PROJECT, bug, [])
    assert ev["repository"] == SAMPLE_PROJECT
    assert ev["bug_report"]["title"] == "Test bug"
    assert len(ev["timeline"]) >= 1


def test_record_root_cause_updates_status():
    ev = _make_evidence()
    rc = {
        "root_cause": "Missing None check",
        "explanation": "code detail",
        "affected_files": ["app/users.py"],
        "evidence": ["evidence 1", "evidence 2"],
    }
    record_root_cause(ev, rc)
    assert ev["root_cause"]["statement"] == "Missing None check"
    assert ev["expected_files_to_change"] == ["app/users.py"]
    assert ev["final_status"] == "FIX_GENERATED"


def test_record_reproduction_confirms_failure():
    ev = _make_evidence()
    before = {
        "passed": 5, "failed": 3, "total": 8,
        "tests": [
            {"node_id": "tests/test_users.py::test_get_missing_user_raises_error", "outcome": "failed"},
        ],
        "raw_output": "3 failed",
    }
    record_reproduction(ev, before, "test_get_missing_user_raises_error")
    assert ev["baseline_test_status"] == "FAILING"
    assert ev["reproduction_result"] == "CONFIRMED_FAILING"


def test_record_reproduction_not_reproduced():
    ev = _make_evidence()
    before = {"passed": 8, "failed": 0, "total": 8, "tests": [], "raw_output": "8 passed"}
    record_reproduction(ev, before, "test_something")
    assert ev["reproduction_result"] == "NOT_REPRODUCED"


def test_record_fix_scope_clean():
    ev = _make_evidence()
    ev["expected_files_to_change"] = ["app/users.py"]
    changes = [{"file": "app/users.py", "before": "x", "after": "y", "reason": "fix"}]
    record_fix(ev, changes, "diff text", {"files_changed": 1, "lines_added": 3, "lines_removed": 1})
    assert ev["actual_files_changed"] == ["app/users.py"]
    assert ev["scope_status"] == "CLEAN"
    assert ev["unexpected_files"] == []


def test_record_fix_scope_change_detected():
    ev = _make_evidence()
    ev["expected_files_to_change"] = ["app/users.py"]
    changes = [
        {"file": "app/users.py", "before": "x", "after": "y", "reason": "fix"},
        {"file": "README.md", "before": "a", "after": "b", "reason": "unrelated"},
    ]
    record_fix(ev, changes, "", {})
    assert ev["scope_status"] == "SCOPE_CHANGE_DETECTED"
    assert "README.md" in ev["unexpected_files"] or "readme.md" in ev["unexpected_files"]


def test_record_verification_all_pass():
    ev = _make_evidence()
    ev["expected_files_to_change"] = ["app/users.py"]
    ev["actual_files_changed"] = ["app/users.py"]
    ev["scope_status"] = "CLEAN"
    ev["tests_before"] = {"passed": 5, "failed": 3, "total": 8}
    ev["tests_fixed"] = ["tests/test_users.py::test_get_missing_user_raises_error"]

    after = {"passed": 8, "failed": 0, "total": 8, "tests": [], "raw_output": "8 passed"}
    comparison = {
        "regressions": [],
        "fixed": ["tests/test_users.py::test_get_missing_user_raises_error"],
    }
    record_verification(ev, after, comparison)
    assert ev["final_status"] == "VERIFIED_WITH_EVIDENCE"
    assert ev["verification_gate"]["overall"] == "PASS"


def test_record_verification_fails_with_regressions():
    ev = _make_evidence()
    ev["expected_files_to_change"] = ["app/users.py"]
    ev["actual_files_changed"] = ["app/users.py"]
    ev["scope_status"] = "CLEAN"
    ev["tests_before"] = {"passed": 5, "failed": 3, "total": 8}
    ev["tests_fixed"] = []

    after = {"passed": 6, "failed": 2, "total": 8, "tests": [], "raw_output": "2 failed"}
    comparison = {"regressions": ["tests/test_users.py::test_existing"], "fixed": []}
    record_verification(ev, after, comparison)
    assert ev["final_status"] in ("VERIFICATION_FAILED", "BLOCKED")
    assert ev["verification_gate"]["full_suite_passes"] == "FAIL"


def test_finalize_adds_metrics():
    ev = _make_evidence()
    finalize(ev, {"total_time_seconds": 3.5, "agents_used": 7, "files_inspected": 14, "files_changed": 1})
    assert ev["finalized_at"] is not None
    assert ev["metrics"]["total_duration_seconds"] == 3.5


def test_save_and_load_ledger(tmp_path):
    ev = _make_evidence()
    ev["final_status"] = "VERIFIED_WITH_EVIDENCE"
    path = save_ledger(ev, str(tmp_path))
    loaded = load_ledger(path)
    assert loaded["run_id"] == ev["run_id"]
    assert loaded["final_status"] == "VERIFIED_WITH_EVIDENCE"
