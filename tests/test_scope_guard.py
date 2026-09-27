"""
tests/test_scope_guard.py — Tests for the scope guard module.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from core.scope_guard import check_scope, is_scope_clean, scope_status_label


def test_scope_clean_exact_match():
    result = check_scope(["app/users.py"], ["app/users.py"])
    assert result["status"] == "CLEAN"
    assert is_scope_clean(result)
    assert result["requires_review"] is False


def test_scope_clean_multiple_expected():
    result = check_scope(
        ["app/users.py", "tests/test_users.py"],
        ["app/users.py", "tests/test_users.py"],
    )
    assert result["status"] == "CLEAN"


def test_scope_change_detected_extra_file():
    result = check_scope(
        ["app/users.py"],
        ["app/users.py", "README.md"],
    )
    assert result["status"] == "SCOPE_CHANGE_DETECTED"
    assert not is_scope_clean(result)
    assert result["requires_review"] is True
    assert "readme.md" in result["actual_only"] or "README.md" in result["actual_only"]


def test_scope_no_changes():
    result = check_scope(["app/users.py"], [])
    assert result["status"] == "NO_CHANGES_DETECTED"
    assert not result["requires_review"]


def test_scope_normalises_slashes():
    result = check_scope(
        ["app\\users.py"],
        ["app/users.py"],
    )
    assert result["status"] == "CLEAN"


def test_scope_label_returns_string():
    result = check_scope(["app/users.py"], ["app/users.py"])
    label = scope_status_label(result)
    assert isinstance(label, str)
    assert len(label) > 0


def test_scope_empty_expected_and_actual():
    result = check_scope([], [])
    assert result["status"] == "NO_CHANGES_DETECTED"


def test_scope_subset_is_clean():
    """If only one of two expected files changed, that's still clean (not unexpected)."""
    result = check_scope(
        ["app/users.py", "tests/test_users.py"],
        ["app/users.py"],
    )
    # No unexpected changes — scope is clean even if not all expected files changed
    assert result["status"] == "CLEAN"
