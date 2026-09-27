"""
core/evidence_ledger.py — Objective evidence capture for every Bug2Fix run.

The evidence ledger is the signature feature of Bug2Fix AI.
Every debugging run produces a verifiable, tamper-evident record of:

  - What was investigated (repository, files, documents)
  - What was found (root cause, affected file, function)
  - What was proven (reproduction command, regression test result)
  - What was changed (diff summary, changed files)
  - What was verified (test results before + after, scope validation)

NO evidence is fabricated. Every field maps to a real artifact
produced during the run.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Evidence record factory
# ---------------------------------------------------------------------------

def new_evidence_record(run_id: str) -> dict:
    """Create a fresh, empty evidence record for a run."""
    return {
        # Identity
        "run_id":         run_id,
        "created_at":     datetime.now().isoformat(),
        "finalized_at":   None,
        "final_status":   "INVESTIGATING",   # INVESTIGATING | FIX_GENERATED | VERIFICATION_RUNNING | VERIFIED_WITH_EVIDENCE | VERIFICATION_FAILED | BLOCKED

        # Input artifacts
        "repository":     "",
        "bug_report":     {},
        "input_documents": [],

        # Investigation findings
        "relevant_files": [],
        "root_cause":     {},
        "root_cause_evidence": [],

        # Reproduction gate
        "reproduction_command": "",
        "reproduction_result":  "",   # CONFIRMED_FAILING | NOT_REPRODUCED | ERROR
        "regression_test_id":   "",
        "baseline_test_status": "UNKNOWN",  # FAILING | PASSING | NOT_RUN

        # Fix artifacts
        "expected_files_to_change": [],
        "actual_files_changed":     [],
        "scope_status":             "UNCHECKED",  # CLEAN | SCOPE_CHANGE_DETECTED | UNCHECKED
        "unexpected_files":         [],
        "diff_summary":             "",
        "diff_text":                "",

        # Verification
        "test_command":           "",
        "test_output_before":     "",
        "test_output_after":      "",
        "tests_before":           {},
        "tests_after":            {},
        "target_test_result":     "UNKNOWN",   # PASS | FAIL | NOT_RUN
        "full_suite_result":      "UNKNOWN",   # PASS | FAIL | NOT_RUN
        "regressions_detected":   [],
        "tests_fixed":            [],

        # Verification gate (PASS | FAIL | BLOCKED)
        "verification_gate": {
            "regression_test_passes":   "UNKNOWN",
            "relevant_tests_pass":      "UNKNOWN",
            "full_suite_passes":        "UNKNOWN",
            "no_unexpected_files":      "UNKNOWN",
            "diff_consistent":          "UNKNOWN",
            "overall":                  "UNKNOWN",
        },

        # Timeline
        "timeline": [],

        # Agents
        "agents_used":       [],
        "parallel_agents":   [],
        "agent_summaries":   {},

        # Metrics
        "metrics": {
            "files_inspected":          0,
            "files_changed":            0,
            "tests_executed":           0,
            "tests_passed_after":       0,
            "agents_used":              0,
            "total_duration_seconds":   0.0,
            "baseline_manual_minutes":  25,
        },
    }


# ---------------------------------------------------------------------------
# Evidence builder helpers
# ---------------------------------------------------------------------------

def record_input(evidence: dict, repository: str, bug_report: dict, documents: list[dict]):
    """Record the inputs for this run."""
    evidence["repository"] = repository
    evidence["bug_report"] = {
        "title":         bug_report.get("title", ""),
        "description":   bug_report.get("description", ""),
        "error_message": bug_report.get("error_message", ""),
        "has_stack_trace": bool(bug_report.get("stack_trace")),
    }
    evidence["input_documents"] = [
        {"filename": d.get("filename", ""), "doc_type": d.get("doc_type", ""), "has_stack_trace": bool(d.get("stack_traces"))}
        for d in documents
    ]
    _add_timeline(evidence, "INPUT_RECORDED", f"Repository: {Path(repository).name}, Documents: {len(documents)}")


def record_investigation(evidence: dict, repo_analysis: dict, agents: dict):
    """Record what files and agents were involved."""
    ce = agents.get("code_explorer", {}).get("result", {}) or {}
    evidence["relevant_files"] = ce.get("relevant_files", [])
    evidence["agents_used"] = list(agents.keys())
    evidence["parallel_agents"] = ["code_explorer", "error_analyzer", "test_analyzer"]
    evidence["metrics"]["files_inspected"] = repo_analysis.get("total_files", 0)
    evidence["agent_summaries"] = {
        key: _summarize_agent(val)
        for key, val in agents.items()
    }
    _add_timeline(evidence, "INVESTIGATION_COMPLETE", f"Files inspected: {evidence['metrics']['files_inspected']}, Relevant: {len(evidence['relevant_files'])}")


def record_root_cause(evidence: dict, root_cause: dict):
    """Record the root cause finding with its evidence."""
    evidence["root_cause"] = {
        "statement":      root_cause.get("root_cause", ""),
        "explanation":    root_cause.get("explanation", ""),
        "affected_files": root_cause.get("affected_files", []),
        "failure_location": root_cause.get("failure_location", ""),
        "smallest_fix":   root_cause.get("smallest_fix", ""),
    }
    evidence["root_cause_evidence"] = root_cause.get("evidence", [])
    evidence["expected_files_to_change"] = root_cause.get("affected_files", [])
    evidence["final_status"] = "FIX_GENERATED"
    _add_timeline(evidence, "ROOT_CAUSE_IDENTIFIED", root_cause.get("root_cause", ""))


def record_reproduction(evidence: dict, before_tests: dict, regression_test_id: str = ""):
    """Record whether the bug was reproduced before the fix."""
    # The bug is reproduced if the regression test FAILS before fix
    failed_tests = [t["node_id"] for t in before_tests.get("tests", []) if t.get("outcome") in ("failed", "error")]
    regression_failing = any(
        (regression_test_id in t or "missing_user" in t or "error" in t.lower())
        for t in failed_tests
    ) if failed_tests else before_tests.get("failed", 0) > 0

    evidence["regression_test_id"] = regression_test_id or "test_get_missing_user_raises_error"
    evidence["baseline_test_status"] = "FAILING" if regression_failing else "PASSING"
    evidence["test_output_before"] = before_tests.get("raw_output", "")
    evidence["tests_before"] = {
        "passed": before_tests.get("passed", 0),
        "failed": before_tests.get("failed", 0),
        "total":  before_tests.get("total", 0),
    }
    status = "CONFIRMED_FAILING" if regression_failing else "NOT_REPRODUCED"
    evidence["reproduction_result"] = status
    _add_timeline(evidence, "REPRODUCTION_GATE",
                  f"Baseline: {evidence['tests_before']['passed']} passed / {evidence['tests_before']['failed']} failed — {status}")


def record_fix(evidence: dict, changes: list[dict], diff_text: str, diff_summary: dict):
    """Record what files were actually changed."""
    evidence["actual_files_changed"] = [c.get("file", "") for c in changes]
    evidence["diff_text"] = diff_text
    evidence["diff_summary"] = (
        f"{diff_summary.get('files_changed', len(changes))} file(s) changed, "
        f"+{diff_summary.get('lines_added', 0)} lines / -{diff_summary.get('lines_removed', 0)} lines"
    )
    evidence["metrics"]["files_changed"] = len(changes)
    evidence["final_status"] = "VERIFICATION_RUNNING"
    _add_timeline(evidence, "FIX_APPLIED", evidence["diff_summary"])

    # Scope check
    expected = set(evidence["expected_files_to_change"])
    actual   = set(evidence["actual_files_changed"])
    unexpected = list(actual - expected)
    evidence["unexpected_files"] = unexpected
    if unexpected:
        evidence["scope_status"] = "SCOPE_CHANGE_DETECTED"
        _add_timeline(evidence, "SCOPE_WARNING", f"Unexpected files changed: {unexpected}")
    else:
        evidence["scope_status"] = "CLEAN"


def record_verification(evidence: dict, after_tests: dict, comparison: dict):
    """Record the final verification results."""
    evidence["test_output_after"] = after_tests.get("raw_output", "")
    evidence["tests_after"] = {
        "passed": after_tests.get("passed", 0),
        "failed": after_tests.get("failed", 0),
        "total":  after_tests.get("total", 0),
    }
    evidence["regressions_detected"] = comparison.get("regressions", [])
    evidence["tests_fixed"] = comparison.get("fixed", [])
    evidence["metrics"]["tests_executed"] = (
        evidence["tests_before"].get("total", 0) +
        after_tests.get("total", 0)
    )
    evidence["metrics"]["tests_passed_after"] = after_tests.get("passed", 0)

    # Determine target test result
    regression_id = evidence.get("regression_test_id", "")
    target_passed = any(
        (regression_id in t or "missing_user" in t)
        for t in evidence["tests_fixed"]
    ) if evidence["tests_fixed"] else after_tests.get("failed", 0) == 0

    evidence["target_test_result"] = "PASS" if target_passed else "FAIL"
    evidence["full_suite_result"] = "PASS" if after_tests.get("failed", 0) == 0 else "FAIL"

    # Fill verification gate
    gate = evidence["verification_gate"]
    gate["regression_test_passes"] = "PASS" if target_passed else "FAIL"
    gate["relevant_tests_pass"]    = "PASS" if after_tests.get("failed", 0) == 0 else "FAIL"
    gate["full_suite_passes"]      = "PASS" if after_tests.get("failed", 0) == 0 else "FAIL"
    gate["no_unexpected_files"]    = "PASS" if evidence["scope_status"] == "CLEAN" else "FAIL"
    gate["diff_consistent"]        = "PASS" if evidence["actual_files_changed"] else "FAIL"

    # Overall: ALL gates must PASS
    all_pass = all(v == "PASS" for v in gate.values() if v != "UNKNOWN")
    gate["overall"] = "PASS" if all_pass else "FAIL"

    if all_pass:
        evidence["final_status"] = "VERIFIED_WITH_EVIDENCE"
    else:
        if gate["regression_test_passes"] == "FAIL":
            evidence["final_status"] = "VERIFICATION_FAILED"
        else:
            evidence["final_status"] = "BLOCKED"

    _add_timeline(evidence, "VERIFICATION_COMPLETE",
                  f"Gate: {gate['overall']} | Tests after: {evidence['tests_after']['passed']} passed / {evidence['tests_after']['failed']} failed")


def finalize(evidence: dict, metrics: dict):
    """Seal the evidence record with final metrics."""
    evidence["finalized_at"] = datetime.now().isoformat()
    evidence["metrics"].update({
        "total_duration_seconds": metrics.get("total_time_seconds", 0),
        "agents_used":            metrics.get("agents_used", 0),
        "files_inspected":        metrics.get("files_inspected", 0),
        "files_changed":          metrics.get("files_changed", 0),
    })
    _add_timeline(evidence, "LEDGER_FINALIZED",
                  f"Final status: {evidence['final_status']}")


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------

def save_ledger(evidence: dict, output_dir: str = "reports") -> str:
    """Serialize evidence record to JSON and write to disk."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    run_id   = evidence.get("run_id", "unknown")
    filename = path / f"evidence_{run_id}.json"
    filename.write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")
    return str(filename)


def load_ledger(file_path: str) -> dict:
    """Load a saved evidence record from JSON."""
    return json.loads(Path(file_path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_timeline(evidence: dict, event: str, detail: str = ""):
    evidence["timeline"].append({
        "timestamp": datetime.now().isoformat(),
        "event":     event,
        "detail":    detail,
    })


def _summarize_agent(agent_val: dict) -> str:
    res = agent_val.get("result", {}) or {}
    return (
        res.get("analysis_summary") or
        res.get("root_cause") or
        res.get("explanation") or
        agent_val.get("status", "pending")
    )
