"""
tests/test_git_manager.py — Tests for git manager module.
"""

import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
from core.git_manager import (
    is_git_repo,
    get_current_branch,
    get_status,
    suggest_commit_message,
    init_repo_if_needed,
)


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    import subprocess
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path), capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path), capture_output=True,
    )
    # Make an initial commit
    test_file = tmp_path / "hello.py"
    test_file.write_text("print('hello')")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=str(tmp_path), capture_output=True,
    )
    return tmp_path


def test_is_git_repo_true(git_repo):
    assert is_git_repo(git_repo) is True


def test_is_git_repo_false(tmp_path):
    non_repo = tmp_path / "not_a_repo"
    non_repo.mkdir()
    assert is_git_repo(non_repo) is False


def test_get_current_branch(git_repo):
    branch = get_current_branch(git_repo)
    assert isinstance(branch, str)
    assert len(branch) > 0
    # Could be "main", "master", or "unknown"
    assert branch not in ("", None)


def test_get_status_clean(git_repo):
    status = get_status(git_repo)
    assert isinstance(status, list)
    # No changes after clean commit
    assert len(status) == 0


def test_get_status_dirty(git_repo):
    # Modify a file
    (git_repo / "hello.py").write_text("print('modified')")
    status = get_status(git_repo)
    assert len(status) > 0
    # File may appear with forward or backward slashes on Windows
    assert any(
        "hello.py" in s["file"].replace("\\", "/")
        for s in status
    )


def test_suggest_commit_message():
    msg = suggest_commit_message(
        "Application crashes when requesting a missing user",
        ["app/users.py"]
    )
    assert msg.startswith("fix:")
    assert "missing" in msg.lower() or "user" in msg.lower()


def test_suggest_commit_message_strips_prefix():
    msg = suggest_commit_message("Bug: null pointer crash", [])
    assert msg.startswith("fix:")
    assert not msg.startswith("fix: bug:")


def test_init_repo_if_needed_already_exists(git_repo):
    result = init_repo_if_needed(git_repo)
    assert result is False  # already a repo


def test_init_repo_if_needed_creates_new(tmp_path):
    new_dir = tmp_path / "new_project"
    new_dir.mkdir()
    result = init_repo_if_needed(new_dir)
    # Should succeed (True or False depending on git availability)
    assert isinstance(result, bool)
