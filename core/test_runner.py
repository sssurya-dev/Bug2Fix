"""
core/test_runner.py — Execute pytest and parse results for Bug2Fix AI.

Responsibilities:
- Run pytest on a project (whole suite or specific file/test).
- Parse the JSON output into structured results.
- Compare before/after test results.
- Detect regressions.
- Never execute arbitrary commands — only pytest via the approved list.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Optional

from core.security import validate_project_path, validate_command


PYTEST_TIMEOUT = 60   # seconds


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

def _empty_result() -> dict:
    return {
        "passed":    0,
        "failed":    0,
        "errors":    0,
        "skipped":   0,
        "total":     0,
        "duration":  0.0,
        "tests":     [],
        "raw_output": "",
        "success":   False,
        "error_msg": "",
    }


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run_tests(
    project_path: str,
    test_file: Optional[str] = None,
    extra_args: Optional[list[str]] = None,
    timeout: int = PYTEST_TIMEOUT,
) -> dict:
    """
    Run pytest in *project_path* and return structured results.

    Args:
        project_path: Absolute path to the project root.
        test_file:    Optional path to a specific test file (relative to project).
        extra_args:   Additional pytest arguments (validated).
        timeout:      Maximum seconds to allow pytest to run.

    Returns a dict with passed/failed/errors/skipped/total/tests/raw_output.
    """
    workspace = validate_project_path(project_path)
    result    = _empty_result()

    # Build command
    cmd = [
        "python", "-m", "pytest",
        "--tb=short",
        "--no-header",
        "-q",
        "--json-report",
        "--json-report-file=.bug2fix_pytest_report.json",
    ]
    if test_file:
        cmd.append(test_file)
    if extra_args:
        # Only allow safe extra args
        safe_args = [a for a in extra_args if a.startswith("-") or a.endswith(".py")]
        cmd.extend(safe_args)

    validate_command(cmd)

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        result["error_msg"] = f"pytest timed out after {timeout}s"
        return result
    except FileNotFoundError:
        result["error_msg"] = "Python / pytest not found in PATH"
        return result

    elapsed = time.time() - start
    result["duration"]   = round(elapsed, 2)
    result["raw_output"] = proc.stdout + proc.stderr

    # Try JSON report first
    report_path = workspace / ".bug2fix_pytest_report.json"
    if report_path.exists():
        try:
            with open(report_path, "r", encoding="utf-8") as fh:
                report = json.load(fh)
            result = _parse_json_report(report, result)
            report_path.unlink(missing_ok=True)
            return result
        except (json.JSONDecodeError, KeyError):
            report_path.unlink(missing_ok=True)

    # Fallback: parse raw output
    result = _parse_raw_output(proc.stdout + proc.stderr, result)
    return result


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_json_report(report: dict, base: dict) -> dict:
    summary  = report.get("summary", {})
    base["passed"]  = summary.get("passed",  0)
    base["failed"]  = summary.get("failed",  0)
    base["errors"]  = summary.get("error",   0)
    base["skipped"] = summary.get("skipped", 0)
    base["total"]   = summary.get("total",   0)
    base["success"] = base["failed"] == 0 and base["errors"] == 0

    tests = []
    for t in report.get("tests", []):
        tests.append({
            "node_id":  t.get("nodeid", ""),
            "outcome":  t.get("outcome", ""),
            "duration": t.get("duration", 0.0),
            "message":  _safe_get(t, "call", "longrepr") or
                        _safe_get(t, "setup", "longrepr") or "",
        })
    base["tests"] = tests
    return base


def _safe_get(d: dict, *keys):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return None
    return d


def _parse_raw_output(output: str, base: dict) -> dict:
    """Fallback parser for pytest -q output."""
    import re
    # e.g.  "3 passed, 1 failed in 0.45s"
    m = re.search(
        r"(\d+) passed(?:,\s*(\d+) failed)?(?:,\s*(\d+) error)?",
        output,
    )
    if m:
        base["passed"]  = int(m.group(1) or 0)
        base["failed"]  = int(m.group(2) or 0)
        base["errors"]  = int(m.group(3) or 0)
        base["total"]   = base["passed"] + base["failed"] + base["errors"]
        base["success"] = base["failed"] == 0 and base["errors"] == 0
    else:
        # Count PASSED / FAILED markers
        base["passed"] = output.count(" PASSED")
        base["failed"] = output.count(" FAILED")
        base["total"]  = base["passed"] + base["failed"]
        base["success"] = base["failed"] == 0
    return base


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_results(before: dict, after: dict) -> dict:
    """
    Compare two test run results and detect regressions.

    Returns:
        {
          "regressions": [...],   # tests that newly failed
          "fixed": [...],         # tests that newly passed
          "net_change": int,      # positive = more passing
          "verified": bool,       # True if no new failures
        }
    """
    before_failing = {
        t["node_id"] for t in before.get("tests", [])
        if t["outcome"] in ("failed", "error")
    }
    after_failing = {
        t["node_id"] for t in after.get("tests", [])
        if t["outcome"] in ("failed", "error")
    }
    after_passing = {
        t["node_id"] for t in after.get("tests", [])
        if t["outcome"] == "passed"
    }

    regressions = list(after_failing - before_failing)
    fixed       = list(before_failing & after_passing)
    net_change  = after.get("passed", 0) - before.get("passed", 0)

    return {
        "regressions": regressions,
        "fixed":       fixed,
        "net_change":  net_change,
        "verified":    len(regressions) == 0 and len(fixed) > 0,
        "before_summary": f"{before.get('passed',0)} passed / {before.get('failed',0)} failed",
        "after_summary":  f"{after.get('passed',0)} passed / {after.get('failed',0)} failed",
    }
