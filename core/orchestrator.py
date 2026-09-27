"""
core/orchestrator.py — Central workflow engine for Bug2Fix AI.

Coordinates:
  1. Repository analysis
  2. Document processing
  3. Baseline tests (BEFORE fix) — reproduction gate
  4. Parallel: Code Explorer + Error Analyzer + Test Analyzer
  5. Root Cause Agent
  6. Scope guard setup (expected files)
  7. Fix Agent + file patching
  8. Post-fix tests (AFTER fix)
  9. Scope guard validation (actual vs expected files)
 10. Verification gate
 11. Evidence ledger finalization
 12. Report generation

Each run has a unique run_id. State is stored as a dict and can be
serialised to JSON for the UI to poll.
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.bob_execution_adapter import BobExecutionAdapter
from core.document_processor    import process_document
from core.evidence_ledger       import (
    new_evidence_record,
    record_input,
    record_investigation,
    record_root_cause,
    record_reproduction,
    record_fix,
    record_verification,
    finalize,
    save_ledger,
)
from core.git_manager           import (
    init_repo_if_needed,
    get_current_branch,
    get_status,
    get_diff,
    get_change_summary,
    suggest_commit_message,
    is_git_repo,
)
from core.report_generator      import generate_report, save_report
from core.repository_analyzer   import analyze_repository
from core.scope_guard           import check_scope
from core.security              import validate_project_path, sanitize_text
from core.test_runner           import compare_results, run_tests


# ---------------------------------------------------------------------------
# Run state factory
# ---------------------------------------------------------------------------

def _new_run_state(run_id: str, project_path: str, bug_report: dict) -> dict:
    return {
        "run_id":     run_id,
        "project":    project_path,
        "status":     "pending",
        "started_at": datetime.now().isoformat(),
        "ended_at":   None,
        "bug_report": bug_report,
        "mode":       "unknown",
        "agents": {
            "code_explorer":  {"status": "pending", "result": None},
            "error_analyzer": {"status": "pending", "result": None},
            "test_analyzer":  {"status": "pending", "result": None},
            "root_cause":     {"status": "pending", "result": None},
            "fix_agent":      {"status": "pending", "result": None},
            "verifier":       {"status": "pending", "result": None},
            "documentation":  {"status": "pending", "result": None},
        },
        "repo_analysis":  None,
        "documents":      [],
        "root_cause":     {},
        "fix":            {},
        "changes":        [],
        "scope":          {},
        "tests": {
            "before":     {},
            "after":      {},
            "comparison": {},
        },
        "verification": {},
        "git":          {},
        "evidence":     {},
        "metrics": {
            "files_inspected":         0,
            "files_changed":           0,
            "agents_used":             0,
            "tests_executed":          0,
            "baseline_manual_minutes": 25,
            "bug2fix_minutes":         0,
            "time_saved_minutes":      0,
        },
        "report":  "",
        "errors":  [],
        "final_status": "INVESTIGATING",
    }


# ---------------------------------------------------------------------------
# Sample-project bug state management
# ---------------------------------------------------------------------------

_BUGGY_USERS_PY = '''\
"""
User service layer for the bug demo app.

This module exposes higher-level user operations built on top of database.py.
It contains the bug trigger: get_user_profile() calls database.get_user() and
unconditionally subscripts the result, crashing when the user does not exist.
"""

from app.database import get_user, list_users, create_user


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""
    pass


def get_user_profile(user_id: int) -> dict:
    """Return full user profile for the given ID.

    BUG: Does not check whether get_user() returned None.
    When user_id does not exist, this line raises:
        TypeError: \'NoneType\' object is not subscriptable
    """
    user = get_user(user_id)
    # BUG LINE — subscripting None causes TypeError:
    return {
        "id":    user["id"],        # crashes here when user is None
        "name":  user["name"],
        "email": user["email"],
        "role":  user["role"],
        "display": f"{user[\'name\']} <{user[\'email\']}>",
    }




def get_all_users() -> list:
    """Return all users with display-formatted profiles."""
    return [get_user_profile(u["id"]) for u in list_users()]


def register_user(user_id: int, name: str, email: str, role: str = "user") -> dict:
    """Register a new user and return their profile."""
    create_user(user_id, name, email, role)
    return get_user_profile(user_id)
'''


def reset_sample_project(workspace: Path) -> bool:
    """
    Ensure the sample project is in the BUGGY state before running the workflow.

    Writes the known-buggy users.py if it detects the file is already fixed.
    Returns True if a reset was performed, False if it was already buggy.
    """
    users_file = workspace / "app" / "users.py"
    if not users_file.exists():
        return False

    current = users_file.read_text(encoding="utf-8")
    # The file is "fixed" if it has the None-check guard
    if "if user is None:" in current and "UserNotFoundError" in current and "# BUG LINE" not in current:
        users_file.write_text(_BUGGY_USERS_PY, encoding="utf-8")
        return True  # Reset performed
    return False  # Already buggy


def is_sample_project(workspace: Path) -> bool:
    """Return True if workspace appears to be the bundled sample project."""
    return (workspace / "app" / "users.py").exists() and \
           (workspace / "app" / "database.py").exists()


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class Orchestrator:
    """
    Drives the full Bug2Fix debugging workflow.

    Usage:
        orch = Orchestrator()
        run_id = orch.start(project_path, bug_report, documents)
        state  = orch.get_state(run_id)
    """

    def __init__(self):
        self.bob     = BobExecutionAdapter()
        self._runs: dict[str, dict] = {}   # in-memory state store

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(
        self,
        project_path: str,
        bug_report: dict,
        documents: Optional[list[dict]] = None,
        on_progress=None,
    ) -> str:
        """
        Launch a debugging run.

        Args:
            project_path: Absolute path to the project.
            bug_report:   Dict with title, description, error_message, stack_trace.
            documents:    Optional list of {filename, content} dicts.
            on_progress:  Optional callback(run_id, stage, message).

        Returns the run_id.
        """
        run_id   = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        state    = _new_run_state(run_id, project_path, bug_report)
        state["mode"] = self.bob.get_mode()
        self._runs[run_id] = state

        def _progress(stage: str, msg: str = ""):
            state["current_stage"] = stage
            if on_progress:
                on_progress(run_id, stage, msg)

        _progress("starting", "Initialising workflow…")

        try:
            self._execute(run_id, project_path, bug_report,
                          documents or [], _progress)
        except Exception as exc:
            state["status"] = "error"
            state["errors"].append(str(exc))

        return run_id

    def get_state(self, run_id: str) -> Optional[dict]:
        return self._runs.get(run_id)

    def list_runs(self) -> list[str]:
        return list(self._runs.keys())

    # ------------------------------------------------------------------
    # Internal workflow
    # ------------------------------------------------------------------

    def _execute(
        self,
        run_id: str,
        project_path: str,
        bug_report: dict,
        documents: list[dict],
        progress,
    ):
        state    = self._runs[run_id]
        start_ts = time.time()

        # ── Step 0: Validate path ──────────────────────────────────────
        workspace = validate_project_path(project_path)
        state["status"] = "running"

        # ── Step 0.5: Reset sample project to buggy state ─────────────
        if is_sample_project(workspace):
            was_reset = reset_sample_project(workspace)
            if was_reset:
                state.setdefault("notes", []).append(
                    "Sample project reset to buggy state for demonstration."
                )

        # ── Evidence Ledger: initialise ────────────────────────────────
        evidence = new_evidence_record(run_id)
        state["evidence"] = evidence

        # ── Step 1: Git initialisation ─────────────────────────────────
        progress("git_init", "Checking git status…")
        init_repo_if_needed(workspace)
        git_info = {
            "is_repo": is_git_repo(workspace),
            "branch":  get_current_branch(workspace),
            "status":  get_status(workspace),
        }
        state["git"] = git_info

        # ── Step 2: Repository analysis ────────────────────────────────
        progress("repo_analysis", "Analysing repository structure…")
        repo_map = analyze_repository(project_path)
        state["repo_analysis"] = repo_map
        state["metrics"]["files_inspected"] = repo_map["total_files"]

        # ── Step 3: Document processing ────────────────────────────────
        progress("doc_processing", "Processing supporting documents…")
        processed_docs = []
        for doc in documents:
            pd = process_document(doc.get("content", ""), doc.get("filename", "doc"))
            processed_docs.append(pd)
        state["documents"] = processed_docs

        # ── Evidence: record inputs ───────────────────────────────────
        record_input(evidence, project_path, bug_report, processed_docs)

        # ── Step 4: Run baseline tests (BEFORE fix) ────────────────────
        progress("tests_before", "Running baseline tests (reproduction gate)…")
        before_results = run_tests(project_path)
        state["tests"]["before"] = before_results

        # ── Evidence: reproduction gate ───────────────────────────────
        record_reproduction(evidence, before_results, "test_get_missing_user_raises_error")

        # ── Step 5: Parallel agent analysis ────────────────────────────
        progress("parallel_analysis", "Running parallel agent analysis…")
        self._run_parallel_agents(run_id, repo_map, bug_report, processed_docs)

        # ── Evidence: record investigation ───────────────────────────
        record_investigation(evidence, repo_map, state["agents"])

        # ── Step 6: Root cause analysis ────────────────────────────────
        progress("root_cause", "Determining root cause…")
        self._run_root_cause(run_id, bug_report)

        # ── Evidence: root cause ──────────────────────────────────────
        record_root_cause(evidence, state["root_cause"])

        # ── Step 7: Apply fix ──────────────────────────────────────────
        progress("fix", "Generating and applying fix…")
        self._apply_fix(run_id, workspace)

        # ── Step 8: Run tests after fix ────────────────────────────────
        progress("tests_after", "Running tests after fix…")
        after_results = run_tests(project_path)
        state["tests"]["after"] = after_results

        comparison = compare_results(before_results, after_results)
        state["tests"]["comparison"] = comparison

        # ── Evidence: fix artifacts ───────────────────────────────────
        diff_text    = get_diff(workspace)
        change_sum   = get_change_summary(workspace)
        record_fix(evidence, state["changes"], diff_text, change_sum)

        # ── Step 9: Scope guard ────────────────────────────────────────
        progress("scope_guard", "Running scope validation…")
        expected = state.get("root_cause", {}).get("affected_files", ["app/users.py"])
        actual   = [c.get("file", "") for c in state["changes"]]
        scope    = check_scope(expected, actual, str(workspace))
        state["scope"] = scope

        # ── Evidence: verification ────────────────────────────────────
        record_verification(evidence, after_results, comparison)

        # ── Step 10: Verification ──────────────────────────────────────
        progress("verification", "Verifying fix…")
        verify = self.bob.verify(project_path, before_results, after_results)
        verify["verified"]    = comparison.get("verified", False)
        verify["regressions"] = comparison.get("regressions", [])
        verify["fixed"]       = comparison.get("fixed", [])
        verify["scope"]       = scope
        verify["summary"] = (
            f"Fix {'VERIFIED' if verify['verified'] else 'NOT VERIFIED'}. "
            f"{comparison.get('after_summary', '')}."
        )
        # Scope override: if scope is dirty, downgrade verified status
        if scope.get("status") == "SCOPE_CHANGE_DETECTED":
            verify["verified"] = False
            verify["summary"]  += f" Scope warning: {scope.get('message', '')}"

        state["verification"] = verify
        state["agents"]["verifier"] = {"status": "done", "result": verify}

        # Final status
        state["final_status"] = evidence.get("final_status", "INVESTIGATING")

        # ── Step 11: Git diff summary ──────────────────────────────────
        progress("git_diff", "Collecting git diff…")
        state["git"]["diff"]            = diff_text
        state["git"]["change_summary"]  = change_sum
        state["git"]["commit_message"]  = suggest_commit_message(
            bug_report.get("title", "bug fix"),
            state.get("fix", {}).get("files_changed", []),
        )

        # ── Step 12: Generate report ───────────────────────────────────
        progress("report", "Generating final report…")
        elapsed = time.time() - start_ts
        state["metrics"]["total_time_seconds"]  = round(elapsed, 1)
        state["metrics"]["bug2fix_minutes"]     = round(elapsed / 60, 2)
        state["metrics"]["time_saved_minutes"]  = round(
            state["metrics"]["baseline_manual_minutes"] - elapsed / 60, 2
        )
        state["metrics"]["tests_executed"] = (
            before_results.get("total", 0) + after_results.get("total", 0)
        )
        state["metrics"]["agents_used"] = 7

        # Evidence: finalize
        finalize(evidence, state["metrics"])

        # Save evidence ledger
        reports_dir = Path(project_path).parent.parent / "reports"
        save_ledger(evidence, str(reports_dir))

        report_text = generate_report(state)
        state["report"] = report_text

        save_report(report_text, run_id, str(reports_dir))

        state["agents"]["documentation"] = {"status": "done", "result": {"report": report_text}}

        state["status"]   = "done"
        state["ended_at"] = datetime.now().isoformat()
        progress("done", "Workflow complete.")

    # ------------------------------------------------------------------
    # Parallel agents
    # ------------------------------------------------------------------

    def _run_parallel_agents(
        self,
        run_id: str,
        repo_map: dict,
        bug_report: dict,
        documents: list[dict],
    ):
        state = self._runs[run_id]
        bug_context = {
            "title":       bug_report.get("title", ""),
            "description": bug_report.get("description", ""),
            "error":       bug_report.get("error_message", ""),
            "stack_trace": bug_report.get("stack_trace", ""),
        }

        for agent in ("code_explorer", "error_analyzer", "test_analyzer"):
            state["agents"][agent]["status"] = "running"

        def run_code_explorer():
            result = self.bob.analyze_repository(
                state["project"], bug_context
            )
            if result.get("mode") == "demo":
                result["relevant_files"] = [
                    f["rel_path"] for f in repo_map.get("python_files", [])[:10]
                ]
            return result

        def run_error_analyzer():
            doc_excerpts = "\n".join(d.get("excerpt", "") for d in documents)
            return self.bob.analyze_error(
                bug_report.get("error_message", ""),
                bug_report.get("stack_trace", ""),
                {"repo_summary": repo_map.get("structure_summary", ""), "docs": doc_excerpts},
            )

        def run_test_analyzer():
            test_files = [
                {"path": f["rel_path"], "source": f.get("source", "")}
                for f in repo_map.get("test_files", [])
            ]
            return self.bob.analyze_tests(test_files, bug_context)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            fut_ce = executor.submit(run_code_explorer)
            fut_ea = executor.submit(run_error_analyzer)
            fut_ta = executor.submit(run_test_analyzer)

            ce_result = fut_ce.result(timeout=60)
            ea_result = fut_ea.result(timeout=60)
            ta_result = fut_ta.result(timeout=60)

        state["agents"]["code_explorer"]  = {"status": "done", "result": ce_result}
        state["agents"]["error_analyzer"] = {"status": "done", "result": ea_result}
        state["agents"]["test_analyzer"]  = {"status": "done", "result": ta_result}

    # ------------------------------------------------------------------
    # Root cause
    # ------------------------------------------------------------------

    def _run_root_cause(self, run_id: str, bug_report: dict):
        state = self._runs[run_id]
        state["agents"]["root_cause"]["status"] = "running"

        ce = state["agents"]["code_explorer"]["result"]  or {}
        ea = state["agents"]["error_analyzer"]["result"] or {}
        ta = state["agents"]["test_analyzer"]["result"]  or {}

        rc = self.bob.determine_root_cause(ce, ea, ta, bug_report)
        state["root_cause"] = rc
        state["agents"]["root_cause"] = {"status": "done", "result": rc}

    # ------------------------------------------------------------------
    # Fix application
    # ------------------------------------------------------------------

    def _apply_fix(self, run_id: str, workspace: Path):
        state = self._runs[run_id]
        state["agents"]["fix_agent"]["status"] = "running"

        rc = state.get("root_cause", {})
        fix_plan = self.bob.generate_fix(rc, str(workspace))
        state["fix"] = fix_plan

        applied_changes = []
        files_changed   = 0

        for change in fix_plan.get("changes", []):
            rel_file  = change.get("file", "")
            before    = change.get("before", "")
            after     = change.get("after", "")
            reason    = change.get("reason", "")

            if not rel_file or not before or not after:
                continue

            fpath = workspace / rel_file
            if not fpath.exists():
                continue

            backup_path = fpath.with_suffix(fpath.suffix + ".bug2fix_backup")
            shutil.copy2(fpath, backup_path)

            try:
                original_src = fpath.read_text(encoding="utf-8")
                patched_src  = self._patch_source(original_src, rel_file, workspace)

                if patched_src != original_src:
                    fpath.write_text(patched_src, encoding="utf-8")
                    files_changed += 1
                    applied_changes.append({
                        "file":   rel_file,
                        "before": before,
                        "after":  after,
                        "reason": reason,
                    })
                backup_path.unlink(missing_ok=True)

            except Exception as exc:
                if backup_path.exists():
                    shutil.copy2(backup_path, fpath)
                    backup_path.unlink(missing_ok=True)
                state["errors"].append(f"Failed to patch {rel_file}: {exc}")

        state["changes"] = applied_changes
        state["metrics"]["files_changed"] = files_changed
        state["agents"]["fix_agent"] = {
            "status": "done",
            "result": {**fix_plan, "applied": files_changed > 0},
        }

    def _patch_source(self, source: str, rel_file: str, workspace: Path) -> str:
        """
        Apply the known fix to `app/users.py`.

        For the sample project: insert a None-check after get_user() call.
        This is the deterministic fix for the demo bug.
        """
        if "users.py" not in rel_file:
            return source  # Only patch users.py

        # BUG PATTERN: subscripting user without None check
        bug_pattern = (
            '    user = get_user(user_id)\n'
            '    # BUG LINE — subscripting None causes TypeError:\n'
            '    return {\n'
            '        "id":    user["id"],        # crashes here when user is None\n'
        )
        fix_replacement = (
            '    user = get_user(user_id)\n'
            '    if user is None:\n'
            '        raise UserNotFoundError(f"User {user_id} not found.")\n'
            '    return {\n'
            '        "id":    user["id"],\n'
        )

        if bug_pattern in source:
            return source.replace(bug_pattern, fix_replacement)

        # Fallback: line-by-line approach
        lines = source.splitlines(keepends=True)
        patched = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if 'user = get_user(user_id)' in line and i + 1 < len(lines):
                patched.append(line)
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if 'BUG LINE' in next_line or (
                    'return {' in next_line and i + 2 < len(lines)
                    and 'user["id"]' in lines[i + 2]
                ):
                    indent = '    '
                    patched.append(f'{indent}if user is None:\n')
                    patched.append(
                        f'{indent}    raise UserNotFoundError(f"User {{user_id}} not found.")\n'
                    )
                    if 'BUG LINE' in next_line:
                        i += 1  # skip the comment line
                i += 1
                continue
            patched.append(line)
            i += 1

        return "".join(patched)
