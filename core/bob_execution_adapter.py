"""
core/bob_execution_adapter.py — IBM Bob 2.0 Integration Layer.

This adapter provides a clean, stable interface between Bug2Fix AI and IBM Bob.

TWO MODES:

A. LIVE MODE — When IBM Bob / Bob Shell is available as a CLI tool:
   - Detect Bob executable (bob, agy, or WatsonX-compatible CLI).
   - Execute structured Bob agent workflows.
   - Capture and parse structured JSON output.

B. DEMO MODE — When Bob is not available as a CLI:
   - Use stored, pre-computed analysis artifacts.
   - Clearly label all outputs as "Demo Mode".
   - Never claim demo outputs were generated live by IBM Bob.

The adapter detects the mode automatically at startup.

IMPORTANT: IBM Bob is the AI-powered IDE assistant (Antigravity IDE / AGY).
In this environment, Bob runs inside the IDE rather than as a subprocess CLI.
Demo Mode is the correct fallback and is clearly disclosed to the user.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def _detect_bob_executable() -> Optional[str]:
    """
    Try to find a Bob/AGY CLI executable in PATH.

    Returns the executable path, or None if unavailable.
    """
    candidates = ["bob", "agy", "watsonx-ai", "ibm-watsonx"]
    for name in candidates:
        exe = shutil.which(name)
        if exe:
            return exe
    return None


BOB_EXECUTABLE: Optional[str] = _detect_bob_executable()
BOB_AVAILABLE: bool = BOB_EXECUTABLE is not None

# ---------------------------------------------------------------------------
# Demo artifacts — pre-computed analysis for the sample project
# ---------------------------------------------------------------------------

_DEMO_REPO_ANALYSIS = {
    "mode": "demo",
    "relevant_files": [
        "app/users.py",
        "app/database.py",
        "app/main.py",
        "tests/test_users.py",
    ],
    "relevant_functions": [
        "get_user_profile",
        "get_user",
        "get_all_users",
        "run_demo",
    ],
    "execution_path": [
        "main.py:run_demo()",
        "→ users.py:get_user_profile(999)",
        "→ database.py:get_user(999)  [returns None]",
        "→ users.py:user['id']        [TypeError: NoneType not subscriptable]",
    ],
    "existing_tests": ["tests/test_users.py"],
    "dependencies":   ["pytest"],
    "analysis_summary": (
        "The bug originates in `app/users.py:get_user_profile()`. "
        "The function calls `database.get_user()` which returns `None` for "
        "missing user IDs, then immediately subscripts the result without a "
        "None-check, causing a `TypeError`."
    ),
}

_DEMO_ERROR_ANALYSIS = {
    "mode": "demo",
    "error_type":      "TypeError",
    "failure_location": "app/users.py:24 in get_user_profile",
    "likely_root_causes": [
        "database.get_user() returns None for missing user IDs",
        "get_user_profile() does not validate the return value before subscripting",
    ],
    "evidence": [
        "Stack trace shows: TypeError: 'NoneType' object is not subscriptable",
        "Line 24 in users.py: user['id'] where user is None",
        "database.get_user uses dict.get() which returns None by default",
    ],
    "analysis_summary": (
        "The `TypeError` is triggered when `user` is `None` and the code "
        "attempts `user['id']`. This is a classic 'missing null-check' bug. "
        "The fix must be applied in `get_user_profile()` before the dict subscript."
    ),
}

_DEMO_TEST_ANALYSIS = {
    "mode": "demo",
    "existing_coverage": (
        "3 of 7 test cases cover happy-path scenarios (users 1, 2, list). "
        "No test currently validates the missing-user case correctly — "
        "the test `test_get_missing_user_raises_error` FAILS before the fix."
    ),
    "missing_coverage": (
        "Missing: test that requesting a non-existent user raises `UserNotFoundError`. "
        "Also missing: edge cases for user_id=0 and very large IDs."
    ),
    "proposed_test": '''\
def test_get_missing_user_raises_error():
    """
    Regression test: requesting a non-existent user must raise
    UserNotFoundError, not crash with TypeError.
    """
    with pytest.raises(UserNotFoundError) as exc_info:
        get_user_profile(999)
    assert "999" in str(exc_info.value)
''',
    "test_file": "tests/test_users.py",
}

_DEMO_ROOT_CAUSE = {
    "mode": "demo",
    "root_cause": "Missing None-check after database.get_user() in users.get_user_profile()",
    "explanation": (
        "When a caller requests a user ID that does not exist in the database, "
        "`database.get_user()` returns `None` (Python's `dict.get()` default). "
        "The service layer function `get_user_profile()` immediately subscripts "
        "this `None` value as if it were a dict (`user['id']`), which raises "
        "`TypeError: 'NoneType' object is not subscriptable`. "
        "No exception handler exists to convert this into a meaningful error."
    ),
    "evidence": [
        "database.py:17 — `return _USERS.get(user_id)` — returns None silently",
        "users.py:24 — `user['id']` — subscript without prior None check",
        "Stack trace confirms failure at users.py:24",
        "Error log shows: `TypeError: 'NoneType' object is not subscriptable`",
    ],
    "affected_files": ["app/users.py"],
    "smallest_fix": (
        "After calling `get_user()`, check `if user is None: raise UserNotFoundError(...)`. "
        "No changes to database.py or any other file are required."
    ),
    "confidence": "HIGH — direct evidence from stack trace and source code inspection",
}

_DEMO_FIX = {
    "mode": "demo",
    "files_changed": ["app/users.py"],
    "changes": [
        {
            "file": "app/users.py",
            "before": (
                "    user = get_user(user_id)\n"
                "    # BUG LINE — subscripting None causes TypeError:\n"
                "    return {\n"
                "        \"id\":    user[\"id\"],        # crashes here when user is None\n"
            ),
            "after": (
                "    user = get_user(user_id)\n"
                "    if user is None:\n"
                "        raise UserNotFoundError(f\"User {user_id} not found.\")\n"
                "    return {\n"
                "        \"id\":    user[\"id\"],\n"
            ),
            "reason": "Add None-check to raise UserNotFoundError for missing users",
        }
    ],
    "explanation": (
        "Added a `None` guard immediately after `get_user()` returns. "
        "If the user does not exist, a `UserNotFoundError` is raised with a "
        "clear message including the user ID. No other code changed."
    ),
    "recommended_next_steps": [
        "Run the full test suite to confirm no regressions.",
        "Consider adding input validation for negative user IDs.",
        "Update API documentation to document UserNotFoundError.",
        "Add HTTP 404 mapping at the API layer if applicable.",
    ],
}


# ---------------------------------------------------------------------------
# BobExecutionAdapter
# ---------------------------------------------------------------------------

class BobExecutionAdapter:
    """
    Unified interface to IBM Bob 2.0 agent capabilities.

    In LIVE MODE (Bob CLI available):
        Executes Bob shell commands and parses structured outputs.

    In DEMO MODE (Bob CLI unavailable):
        Returns pre-computed analysis artifacts.
        All demo outputs are clearly tagged {"mode": "demo"}.

    Never claims demo results were generated live.
    """

    def __init__(self):
        self.bob_available = BOB_AVAILABLE
        self.bob_executable = BOB_EXECUTABLE
        self.mode = "live" if BOB_AVAILABLE else "demo"

    def get_mode(self) -> str:
        return self.mode

    def is_live(self) -> bool:
        return self.bob_available

    # ------------------------------------------------------------------
    # High-level workflow methods
    # ------------------------------------------------------------------

    def analyze_repository(self, project_path: str, bug_context: dict) -> dict:
        """Run Code Explorer Agent analysis."""
        if self.bob_available:
            return self._run_bob_agent("code_explorer", {
                "project_path": project_path,
                "bug_context":  bug_context,
            })
        return _DEMO_REPO_ANALYSIS.copy()

    def analyze_error(self, error_text: str, stack_trace: str, repo_context: dict) -> dict:
        """Run Error Analysis Agent."""
        if self.bob_available:
            return self._run_bob_agent("error_analyzer", {
                "error_text":  error_text,
                "stack_trace": stack_trace,
                "repo":        repo_context,
            })
        return _DEMO_ERROR_ANALYSIS.copy()

    def analyze_tests(self, test_files: list, bug_context: dict) -> dict:
        """Run Test Analysis Agent."""
        if self.bob_available:
            return self._run_bob_agent("test_analyzer", {
                "test_files":  test_files,
                "bug_context": bug_context,
            })
        return _DEMO_TEST_ANALYSIS.copy()

    def determine_root_cause(
        self,
        repo_analysis: dict,
        error_analysis: dict,
        test_analysis: dict,
        bug_report: dict,
    ) -> dict:
        """Run Root Cause Agent (combines parallel agent outputs)."""
        if self.bob_available:
            return self._run_bob_agent("root_cause", {
                "repo":  repo_analysis,
                "error": error_analysis,
                "tests": test_analysis,
                "bug":   bug_report,
            })
        return _DEMO_ROOT_CAUSE.copy()

    def generate_fix(self, root_cause: dict, project_path: str) -> dict:
        """Run Fix Agent."""
        if self.bob_available:
            return self._run_bob_agent("fix_agent", {
                "root_cause":   root_cause,
                "project_path": project_path,
            })
        return _DEMO_FIX.copy()

    def run_agent(self, agent_name: str, context: dict) -> dict:
        """Generic agent runner."""
        if self.bob_available:
            return self._run_bob_agent(agent_name, context)
        return {"mode": "demo", "agent": agent_name, "note": "Demo mode — Bob unavailable"}

    def verify(self, project_path: str, test_results_before: dict, test_results_after: dict) -> dict:
        """Run Verification Agent."""
        # Verification always uses real pytest results — no demo fabrication
        verified = (
            test_results_after.get("passed", 0) > test_results_before.get("passed", 0)
            and test_results_after.get("failed", 0) == 0
        )
        return {
            "mode":       self.mode,
            "verified":   verified,
            "summary": (
                "Fix verified: all tests pass and the regression test now passes."
                if verified else
                "Fix not verified: tests are still failing or no improvement detected."
            ),
            "regressions": [],
            "risks": [] if verified else [
                "Tests still failing — manual review required before merging."
            ],
        }

    # ------------------------------------------------------------------
    # Bob CLI execution (live mode only)
    # ------------------------------------------------------------------

    def _run_bob_agent(self, agent_name: str, payload: dict) -> dict:
        """
        Execute a Bob agent via the CLI.

        Expected interface (IBM Bob Shell / bob CLI):
            bob run-agent <agent_name> --input '<json>'

        Returns parsed JSON output or an error dict.
        """
        if not self.bob_executable:
            return {"error": "Bob executable not found", "mode": "live_failed"}

        payload_str = json.dumps(payload)
        cmd = [self.bob_executable, "run-agent", agent_name, "--input", payload_str]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {
                        "mode": "live",
                        "raw_output": result.stdout,
                        "note": "Could not parse JSON from Bob output",
                    }
            else:
                return {
                    "mode": "live_failed",
                    "error": result.stderr or "Bob command returned non-zero exit code",
                }
        except subprocess.TimeoutExpired:
            return {"mode": "live_failed", "error": "Bob agent timed out"}
        except Exception as exc:
            return {"mode": "live_failed", "error": str(exc)}
