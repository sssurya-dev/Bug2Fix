"""
Tests for the bug demo application.

BEFORE FIX:
  test_get_missing_user_raises_error  — FAILS (TypeError instead of clear error)
  test_get_existing_user              — PASSES
  test_list_all_users                 — PASSES

AFTER FIX:
  All tests PASS.
"""

import pytest
import sys
import os

# Ensure the sample project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.users import get_user_profile, get_all_users, UserNotFoundError
from app.database import get_user, create_user, _USERS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_user_store():
    """Reset the in-memory user store to its original state before each test."""
    original = dict(_USERS)
    yield
    _USERS.clear()
    _USERS.update(original)


# ---------------------------------------------------------------------------
# Happy-path tests (should pass before and after fix)
# ---------------------------------------------------------------------------

def test_get_existing_user_returns_profile():
    """Fetching a known user should return a complete profile dict."""
    profile = get_user_profile(1)
    assert profile["id"] == 1
    assert profile["name"] == "Alice"
    assert profile["email"] == "alice@example.com"
    assert "display" in profile


def test_list_all_users_returns_three():
    """Listing all users should return exactly 3 profiles."""
    users = get_all_users()
    assert len(users) == 3


def test_get_user_2_profile():
    """Fetching user 2 should return Bob's details."""
    profile = get_user_profile(2)
    assert profile["name"] == "Bob"
    assert profile["role"] == "user"


# ---------------------------------------------------------------------------
# Regression test for the bug (FAILS before fix, PASSES after fix)
# ---------------------------------------------------------------------------

def test_get_missing_user_raises_error():
    """
    Requesting a non-existent user ID must raise UserNotFoundError,
    NOT crash with TypeError: 'NoneType' object is not subscriptable.

    This is the regression test for the reported bug.
    """
    with pytest.raises(UserNotFoundError) as exc_info:
        get_user_profile(999)
    assert "999" in str(exc_info.value)


def test_get_missing_user_zero():
    """User ID 0 does not exist — must raise UserNotFoundError."""
    with pytest.raises(UserNotFoundError):
        get_user_profile(0)


def test_get_missing_user_large_id():
    """Very large user IDs should not crash with TypeError."""
    with pytest.raises(UserNotFoundError):
        get_user_profile(99999)


# ---------------------------------------------------------------------------
# Database-layer tests
# ---------------------------------------------------------------------------

def test_database_returns_none_for_missing():
    """Raw database.get_user returns None for missing IDs (expected)."""
    result = get_user(999)
    assert result is None


def test_create_and_fetch_user():
    """Creating a user and then fetching it should work."""
    create_user(10, "Dave", "dave@example.com", "user")
    profile = get_user_profile(10)
    assert profile["name"] == "Dave"
