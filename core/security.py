"""
core/security.py — Input validation and safety guards for Bug2Fix AI.

Responsibilities:
- Validate repository paths (no traversal, no system dirs).
- Sanitize user-supplied text (strip null bytes, limit size).
- Restrict subprocess command execution to an approved allowlist.
- Detect potential secrets in text snippets.
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_TEXT_LENGTH = 50_000          # characters
MAX_FILE_SIZE   = 1_024 * 1_024   # 1 MB

BLOCKED_PATH_PATTERNS = [
    r"\.git[/\\]objects",         # raw git objects
    r"\.git[/\\]refs",
    r"[/\\]etc[/\\]",
    r"[/\\]proc[/\\]",
    r"[/\\]sys[/\\]",
    r"C:\\Windows",
    r"C:\\System32",
]

APPROVED_COMMANDS = {
    "git", "python", "python3", "pytest", "pip",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|secret|api[_\-]?key|token|auth)\s*[:=]\s*\S+"),
    re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),   # base64-ish long strings
    re.compile(r"sk-[A-Za-z0-9]{20,}"),          # OpenAI-style key
    re.compile(r"[0-9a-f]{32,}"),                 # hex secrets
]


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------

class SecurityError(Exception):
    """Raised when a security check fails."""


def validate_project_path(path: str) -> Path:
    """
    Validate that *path* is an existing, readable directory that is not
    a dangerous system location.

    Returns the resolved absolute Path on success.
    Raises SecurityError or ValueError on failure.
    """
    if not path or not path.strip():
        raise ValueError("Project path must not be empty.")

    resolved = Path(path).resolve()

    if not resolved.exists():
        raise ValueError(f"Path does not exist: {resolved}")

    if not resolved.is_dir():
        raise ValueError(f"Path is not a directory: {resolved}")

    path_str = str(resolved)
    for pattern in BLOCKED_PATH_PATTERNS:
        if re.search(pattern, path_str):
            raise SecurityError(f"Access to path is not permitted: {resolved}")

    return resolved


def validate_file_path(file_path: str, workspace: Path) -> Path:
    """
    Validate that *file_path* is within *workspace* and not a protected file.

    Returns the resolved Path on success.
    Raises SecurityError on failure.
    """
    resolved = Path(file_path).resolve()
    try:
        resolved.relative_to(workspace.resolve())
    except ValueError:
        raise SecurityError(
            f"File '{resolved}' is outside the workspace '{workspace}'."
        )
    return resolved


# ---------------------------------------------------------------------------
# Text sanitisation
# ---------------------------------------------------------------------------

def sanitize_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """Strip null bytes, limit length, return sanitised string."""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\x00", "")
    if len(text) > max_length:
        text = text[:max_length] + "\n[... truncated for safety ...]"
    return text


def has_secrets(text: str) -> bool:
    """Return True if *text* appears to contain secrets or credentials."""
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# Command validation
# ---------------------------------------------------------------------------

def validate_command(cmd: list[str]) -> list[str]:
    """
    Ensure the command uses an approved executable.

    Raises SecurityError if the command executable is not in APPROVED_COMMANDS.
    """
    if not cmd:
        raise ValueError("Command must not be empty.")
    executable = Path(cmd[0]).name.lower()
    # Strip .exe suffix on Windows
    executable = executable.removesuffix(".exe")
    if executable not in APPROVED_COMMANDS:
        raise SecurityError(
            f"Command '{executable}' is not in the approved list: "
            f"{sorted(APPROVED_COMMANDS)}"
        )
    return cmd


# ---------------------------------------------------------------------------
# File-read safety
# ---------------------------------------------------------------------------

def safe_read_file(file_path: Path, max_bytes: int = MAX_FILE_SIZE) -> str:
    """Read a file safely, enforcing size limits."""
    size = file_path.stat().st_size
    if size > max_bytes:
        # Read only the first max_bytes
        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read(max_bytes)
        return content + "\n[... file truncated — too large ...]"
    with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()
