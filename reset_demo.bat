@echo off
REM reset_demo.bat — Restore sample project to BUGGY state for fresh demo.
REM Run this before starting the Bug2Fix AI demo.

echo [Bug2Fix AI] Resetting sample project to buggy state...

python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').resolve())); from core.orchestrator import reset_sample_project, is_sample_project; w = Path('sample_projects/python_bug_demo'); print('  RESET: restored to buggy state.' if reset_sample_project(w) else '  OK: already buggy.')"

echo.
echo [Bug2Fix AI] Verifying buggy state...
python -m pytest sample_projects/python_bug_demo/tests/ -q --tb=no

echo.
echo [Bug2Fix AI] Demo is ready. Expected: 5 passed, 3 failed.
echo [Bug2Fix AI] Start the app: streamlit run app/main.py
