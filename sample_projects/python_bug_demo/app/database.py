"""
In-memory database simulation for the bug demo app.

This module simulates a simple user database with an intentional bug:
get_user() returns None for missing users instead of raising a clear error,
which causes downstream callers to crash with a cryptic TypeError.
"""

# Simulated user store — only users 1–3 exist
_USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "role": "user"},
    3: {"id": 3, "name": "Carol", "email": "carol@example.com", "role": "user"},
}


def get_user(user_id: int):
    """Return a user dict by ID, or None if not found.

    BUG: Returns None silently for missing IDs.
    Callers that subscript the result crash with TypeError.
    """
    return _USERS.get(user_id)          # <-- BUG: should raise UserNotFoundError


def list_users():
    """Return all users as a list of dicts."""
    return list(_USERS.values())


def create_user(user_id: int, name: str, email: str, role: str = "user"):
    """Add a new user to the store."""
    if user_id in _USERS:
        raise ValueError(f"User {user_id} already exists")
    _USERS[user_id] = {"id": user_id, "name": name, "email": email, "role": role}
    return _USERS[user_id]
