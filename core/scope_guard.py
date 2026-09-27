"""
core/scope_guard.py — Validate that the fix only changed expected files.

The scope guard compares:
  - EXPECTED files to change (from root cause analysis)
  - ACTUAL files changed (from git diff or direct comparison)

If unexpected files changed, it reports SCOPE_CHANGE_DETECTED and
requires human review before marking the fix as verified.

States:
  CLEAN                  — Only expected files changed
  SCOPE_CHANGE_DETECTED  — Unexpected files changed (require review)
  NO_CHANGES_DETECTED    — No files changed at all (fix may have failed)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Core scope guard
# ---------------------------------------------------------------------------

def check_scope(
    expected_files: list[str],
    actual_files: list[str],
    workspace: Optional[str] = None,
) -> dict:
    """
    Compare expected vs actual changed files.

    Args:
        expected_files: Files we EXPECTED to change (from root cause analysis).
        actual_files:   Files that ACTUALLY changed (from git diff / file comparison).
        workspace:      Optional workspace path for normalizing relative paths.

    Returns a dict:
        {
          "status":       "CLEAN" | "SCOPE_CHANGE_DETECTED" | "NO_CHANGES_DETECTED",
          "expected":     [...],
          "actual":       [...],
          "expected_only": [...],   # expected but not changed
          "actual_only":  [...],    # changed but not expected (unexpected)
          "overlap":      [...],    # changed as expected
          "requires_review": bool,
          "message":      str,
        }
    """
    # Normalise paths: basename comparison is sufficient for the demo,
    # but we also try relative-path matching for precision.
    def _normalise(f: str) -> str:
        return f.replace("\\", "/").strip().lstrip("./")

    expected_norm = {_normalise(f) for f in expected_files if f}
    actual_norm   = {_normalise(f) for f in actual_files if f}

    overlap       = list(expected_norm & actual_norm)
    actual_only   = list(actual_norm - expected_norm)   # unexpected
    expected_only = list(expected_norm - actual_norm)   # expected but not changed

    if not actual_norm:
        status   = "NO_CHANGES_DETECTED"
        requires = False
        message  = "No files were changed. The fix may not have been applied."
    elif actual_only:
        status   = "SCOPE_CHANGE_DETECTED"
        requires = True
        files    = ", ".join(sorted(actual_only))
        message  = (
            f"WARNING: {len(actual_only)} unexpected file(s) changed: {files}. "
            "Review required before merging."
        )
    else:
        status   = "CLEAN"
        requires = False
        message  = (
            f"Scope is clean. {len(overlap)} expected file(s) changed, "
            "0 unexpected changes."
        )

    return {
        "status":         status,
        "expected":       list(expected_norm),
        "actual":         list(actual_norm),
        "expected_only":  expected_only,
        "actual_only":    actual_only,
        "overlap":        overlap,
        "requires_review": requires,
        "message":        message,
    }


def scope_status_label(scope_result: dict) -> str:
    """Return a human-readable one-line status."""
    return scope_result.get("message", "Scope unknown")


def is_scope_clean(scope_result: dict) -> bool:
    """Return True only if no unexpected files changed."""
    return scope_result.get("status") == "CLEAN"
