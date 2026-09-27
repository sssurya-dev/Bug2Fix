"""
core/git_manager.py — Git-aware repository operations for Bug2Fix AI.

Provides:
- Current branch detection
- Working tree status
- Staged/unstaged diff
- Checkpoint (stash) before applying fixes
- Human-readable change summary
- Commit message suggestion

Uses subprocess with validated commands only.
Never pushes or destructively rewrites history.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from core.security import validate_command, SecurityError


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _run_git(args: list[str], cwd: Path, timeout: int = 15) -> tuple[str, str, int]:
    """
    Run a git subcommand inside *cwd*.

    Returns (stdout, stderr, returncode).
    Raises SecurityError if the command is unsafe.
    """
    cmd = ["git"] + args
    validate_command(cmd)
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        # Note: do NOT strip stdout — git status --porcelain uses leading spaces
        return result.stdout.rstrip("\n"), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "git command timed out", 1
    except FileNotFoundError:
        return "", "git not found in PATH", 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_git_repo(path: Path) -> bool:
    """Return True if *path* is inside a git repository."""
    _, _, code = _run_git(["rev-parse", "--is-inside-work-tree"], path)
    return code == 0


def get_current_branch(path: Path) -> str:
    """Return the current branch name, or 'DETACHED' if in detached HEAD."""
    stdout, _, code = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
    if code != 0 or not stdout:
        return "unknown"
    return stdout


def get_status(path: Path) -> list[dict]:
    """
    Return a list of changed file records.

    Each record: {"status": str, "file": str}
    Status codes follow `git status --porcelain` (e.g. "M ", " M", "??").
    """
    stdout, _, code = _run_git(["status", "--porcelain"], path)
    if code != 0 or not stdout:
        return []
    records = []
    for line in stdout.splitlines():
        # git status --porcelain format: XY filename
        # XY is exactly 2 characters, followed by a single space
        if len(line) >= 3:
            status   = line[:2]          # 2-char status code (may have spaces)
            filename = line[3:]          # filename starts at index 3
            records.append({"status": status.strip(), "file": filename})
    return records


def get_diff(path: Path, file_path: Optional[str] = None) -> str:
    """
    Return a unified diff of unstaged changes.

    If *file_path* is provided, diff is scoped to that file.
    """
    args = ["diff"]
    if file_path:
        args += ["--", file_path]
    stdout, _, _ = _run_git(args, path)
    return stdout


def get_diff_cached(path: Path) -> str:
    """Return diff of staged changes."""
    stdout, _, _ = _run_git(["diff", "--cached"], path)
    return stdout


def create_checkpoint(path: Path, message: str = "bug2fix-checkpoint") -> bool:
    """
    Stash current changes to create a safe checkpoint.

    Returns True on success.
    """
    _, _, code = _run_git(["stash", "push", "-m", message], path)
    return code == 0


def restore_checkpoint(path: Path) -> bool:
    """
    Pop the most recent stash (restore from checkpoint).

    Returns True on success.
    """
    _, _, code = _run_git(["stash", "pop"], path)
    return code == 0


def get_change_summary(path: Path) -> dict:
    """
    Return a human-readable summary of recent changes.

    Returns dict with files_changed, lines_added, lines_removed.
    """
    stdout, _, code = _run_git(
        ["diff", "--stat", "HEAD"], path
    )
    if code != 0 or not stdout:
        # Fall back to unstaged diff stat
        stdout, _, _ = _run_git(["diff", "--stat"], path)

    files_changed = 0
    lines_added = 0
    lines_removed = 0

    for line in stdout.splitlines():
        # Example: " 2 files changed, 14 insertions(+), 3 deletions(-)"
        if "file" in line and "changed" in line:
            import re
            m_files = re.search(r"(\d+) file", line)
            m_add   = re.search(r"(\d+) insertion", line)
            m_del   = re.search(r"(\d+) deletion", line)
            if m_files: files_changed = int(m_files.group(1))
            if m_add:   lines_added   = int(m_add.group(1))
            if m_del:   lines_removed = int(m_del.group(1))

    return {
        "files_changed": files_changed,
        "lines_added":   lines_added,
        "lines_removed": lines_removed,
        "raw_stat":      stdout,
    }


def suggest_commit_message(bug_title: str, files_changed: list[str]) -> str:
    """
    Generate a conventional-commit-style message.

    Example: "fix: handle missing user records safely"
    """
    title_lower = bug_title.lower().strip()
    # Strip common prefixes
    for prefix in ("bug:", "error:", "issue:", "fix:", "[bug]"):
        if title_lower.startswith(prefix):
            title_lower = title_lower[len(prefix):].strip()

    # Truncate
    summary = title_lower[:72] if len(title_lower) > 72 else title_lower

    return f"fix: {summary}"


def init_repo_if_needed(path: Path) -> bool:
    """
    If *path* is not a git repo, initialise one.

    Returns True if a new repo was created, False if one already existed.
    """
    if is_git_repo(path):
        return False
    _, _, code = _run_git(["init"], path)
    if code == 0:
        # Initial commit so diffs work
        _run_git(["add", "."], path)
        _run_git(
            ["commit", "--allow-empty", "-m", "chore: initial bug2fix checkpoint"],
            path,
        )
    return code == 0
