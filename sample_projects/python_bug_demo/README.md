# Sample Project — Python Bug Demo

## Description

A minimal Flask-style user service with an intentional reproducible bug.

## The Bug

When a client requests a **non-existent user ID**, the application crashes with:

```
TypeError: 'NoneType' object is not subscriptable
```

### Root Cause

`database.get_user()` returns `None` when a user is not found.  
`users.get_user_profile()` does not check for `None` before subscripting  
the result, causing a crash.

### Reproduction

```bash
cd sample_projects/python_bug_demo
python -m app.main
# Crashes when fetching user 999
```

Or via pytest (one test fails):

```bash
pytest tests/test_users.py -v
```

## Expected Behaviour

Requesting a missing user should raise `UserNotFoundError` with a clear message.

## Safe Fix

In `app/users.py`, after calling `get_user()`, check whether the result is  
`None` and raise `UserNotFoundError` if so.

## Files

| File | Role |
|------|------|
| `app/database.py` | In-memory data store |
| `app/users.py`    | Service layer — **contains the bug** |
| `app/main.py`     | Entry-point demonstration |
| `tests/test_users.py` | Test suite |
