@echo off
REM Bug2Fix AI — Windows startup script
echo.
echo  =====================================
echo   Bug2Fix AI — IBM Bob 2.0 Hackathon
echo  =====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist ".deps_installed" (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo installed > .deps_installed
)

echo [INFO] Starting Bug2Fix AI...
echo [INFO] Open http://localhost:8501 in your browser
echo.

streamlit run app/main.py --server.port 8501 --server.headless false
