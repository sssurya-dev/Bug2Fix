# Bug Report

**Title:** Application crashes when requesting a missing user

**Severity:** High

**Reported:** 2026-09-27

**Component:** User Service (`app/users.py`)

## Description

When a client requests a user ID that does not exist in the database, the
application crashes with an unhandled exception instead of returning a clear
error response.

## Steps to Reproduce

1. Start the application or run the test suite.
2. Call `get_user_profile(999)` (any non-existent user ID).
3. Observe the crash.

## Expected Behaviour

The system should raise `UserNotFoundError` with a message like:
`"User 999 not found."`

## Actual Behaviour

```
TypeError: 'NoneType' object is not subscriptable
```

The application crashes completely with an unhandled exception.

## Stack Trace

```
Traceback (most recent call last):
  File "app/main.py", line 22, in run_demo
    profile = get_user_profile(999)
  File "app/users.py", line 24, in get_user_profile
    "id":    user["id"],
             ~~~~^^^^^
TypeError: 'NoneType' object is not subscriptable
```

## Impact

- Any request for a non-existent user brings down the process.
- No graceful error message is returned to the caller.
- All downstream callers that depend on `get_user_profile()` are affected.

## Suggested Fix

In `app/users.py`, after calling `database.get_user()`, check for `None`
and raise `UserNotFoundError` if the user does not exist.
