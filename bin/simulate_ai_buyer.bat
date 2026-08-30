@echo off
set "REPO_ROOT=%~dp0.."
cd /d "%REPO_ROOT%"

if exist "backend\.venv\Scripts\activate.bat" (
    call backend\.venv\Scripts\activate.bat
)

python scripts\simulate_ai_buyer.py %*
