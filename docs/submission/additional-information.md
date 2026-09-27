# Additional Information

## Demo Requirements

**To run the full demo from a clean state:**

```bash
# 1. Reset sample project to buggy state
reset_demo.bat

# 2. Verify buggy state (expect: 3 failed)
python -m pytest sample_projects/python_bug_demo/tests/ -q

# 3. Start application
streamlit run app/main.py
```

## Known Limitations

1. **Bob CLI mode** — The application runs in Demo Mode when the IBM Bob CLI is not installed. Demo Mode uses pre-computed analysis artifacts clearly labeled `"mode": "demo"`. Real test execution and file patching always occur regardless of mode.

2. **Python only** — The current implementation is specific to Python projects with pytest test suites. The architecture supports extension to other languages.

3. **Sample project reset** — The orchestrator automatically resets the sample project to its buggy state before each run. This is intentional for deterministic demo behavior.

4. **In-memory state** — Run state is stored in memory and lost on app restart. This is acceptable for the hackathon scope; production would use a database.

## Evidence Integrity

The Evidence Ledger is designed to be objective:

- Every field maps to a real artifact produced during the run
- No evidence is fabricated or inflated
- Demo mode outputs are always tagged `mode: demo`
- The verification gate requires ALL 5 checks to pass — not a majority

## Security Notes

- All repository paths are validated before use (`core/security.py`)
- Subprocess commands are restricted to an allowlist (`git`, `python`, `pytest`, `pip`)
- File operations are bounded to the workspace directory
- No secrets are logged or exposed
- Uploaded documents are sanitized (null bytes removed, size limited to 1MB)

## Test Coverage

61 automated tests pass across all core modules:
- `test_orchestrator.py` — workflow integration tests
- `test_document_processor.py` — document extraction tests
- `test_git_manager.py` — git operation tests
- `test_security.py` — security validation tests
- `test_test_runner.py` — pytest runner tests
- `test_evidence_ledger.py` — evidence ledger verification tests
- `test_scope_guard.py` — fix scope guard tests
