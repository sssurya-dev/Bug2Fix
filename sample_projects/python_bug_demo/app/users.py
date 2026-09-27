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
        TypeError: 'NoneType' object is not subscriptable
    """
    user = get_user(user_id)
    # BUG LINE — subscripting None causes TypeError:
    return {
        "id":    user["id"],        # crashes here when user is None
        "name":  user["name"],
        "email": user["email"],
        "role":  user["role"],
        "display": f"{user['name']} <{user['email']}>",
    }




def get_all_users() -> list:
    """Return all users with display-formatted profiles."""
    return [get_user_profile(u["id"]) for u in list_users()]


def register_user(user_id: int, name: str, email: str, role: str = "user") -> dict:
    """Register a new user and return their profile."""
    create_user(user_id, name, email, role)
    return get_user_profile(user_id)
