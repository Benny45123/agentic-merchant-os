@echo off
setlocal enabledelayedexpansion

echo ==================================================================
echo 🚀 Setting up Agentic Merchant OS for Windows
echo ==================================================================

set "REPO_ROOT=%~dp0.."
cd /d "%REPO_ROOT%"

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not found in PATH. Please install Python 3.11 or 3.12 from python.org
    exit /b 1
)

:: Check if Node is installed
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js is not found in PATH. Please install Node.js 18+ from nodejs.org
    exit /b 1
)

:: Setup Backend
echo.
echo 📦 [1/2] Setting up Backend virtual environment...
cd /d "%REPO_ROOT%\backend"

if not exist ".env" (
    copy "%REPO_ROOT%\.env.example" ".env" >nul
)

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo 🔄 Running database migrations and seeding catalog...
python -m alembic upgrade head
python app\seed.py

:: Setup Frontend
echo.
echo 💻 [2/2] Installing Frontend dependencies...
cd /d "%REPO_ROOT%\frontend"
if not exist ".env.local" (
    if exist ".env.local.example" (
        copy ".env.local.example" ".env.local" >nul
    )
)
:: Optional Telegram Token Setup
echo.
echo ==================================================================
echo 🤖 Telegram Bot Mobile Gateway Setup
echo ==================================================================
set /p OPEN_TG="👉 Open Telegram @BotFather in browser? (Y/N, default N): "
if /i "%OPEN_TG%"=="Y" (
    start https://t.me/BotFather
)
set /p USER_TG="📝 Paste TELEGRAM_BOT_TOKEN (or press Enter to skip): "
if not "%USER_TG%"=="" (
    powershell -Command "(Get-Content '%REPO_ROOT%\backend\.env') -replace '^TELEGRAM_BOT_TOKEN=.*', 'TELEGRAM_BOT_TOKEN=%USER_TG%' | Set-Content '%REPO_ROOT%\backend\.env'"
    echo ✅ Saved TELEGRAM_BOT_TOKEN to backend\.env
)

echo.
echo ==================================================================
echo 🎉 SETUP COMPLETE! Run 'bin\start.bat' to launch the servers.
echo ==================================================================

