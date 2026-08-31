@echo off
set "REPO_ROOT=%~dp0.."
cd /d "%REPO_ROOT%\backend"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo ==================================================================
echo 🤖 Launching Telegram Bot Gateway on Windows
echo ==================================================================

python -m app.telegram.bot
