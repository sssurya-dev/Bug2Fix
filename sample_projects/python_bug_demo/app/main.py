"""
Main entry point for the bug demo application.

Demonstrates the crash when requesting a user that does not exist.
"""

from app.users import get_user_profile, get_all_users


def run_demo():
    print("=== Bug Demo Application ===\n")

    # This works — user 1 exists
    print("Fetching user 1 (exists):")
    profile = get_user_profile(1)
    print(f"  {profile['display']}\n")

    # This works — user 2 exists
    print("Listing all users:")
    for u in get_all_users():
        print(f"  {u['display']}")
    print()

    # This CRASHES — user 999 does not exist
    print("Fetching user 999 (does NOT exist):")
    profile = get_user_profile(999)   # <-- crashes here
    print(f"  {profile['display']}")


if __name__ == "__main__":
    run_demo()
