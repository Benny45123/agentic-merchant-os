@echo off
setlocal enabledelayedexpansion

echo ==================================================================
echo 🚀 Launching Agentic Merchant OS on Windows
echo ==================================================================

set "REPO_ROOT=%~dp0.."
cd /d "%REPO_ROOT%"

:: Start Backend in a new command window
echo 📦 [1/2] Starting FastAPI Backend on http://localhost:8000...
start "Agentic Merchant OS - Backend" cmd /k "cd /d %REPO_ROOT%\backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000 --host 127.0.0.1"

:: Start Frontend in a new command window
echo 💻 [2/2] Starting Next.js Frontend on http://localhost:3000...
start "Agentic Merchant OS - Frontend" cmd /k "cd /d %REPO_ROOT%\frontend && npm run dev"

echo.
echo ==================================================================
echo 🎉 AGENTIC MERCHANT OS IS RUNNING!
echo ==================================================================
echo 👉 Frontend UI:       http://localhost:3000
echo 👉 Buyer Chat:        http://localhost:3000/chat
echo 👉 A2A Arena:         http://localhost:3000/negotiate
echo 👉 Receipts Explorer: http://localhost:3000/receipts
echo 👉 Merchant Control:  http://localhost:3000/dashboard
echo 👉 Backend API Docs:  http://localhost:8000/docs
echo ==================================================================
echo Run 'bin\stop.bat' to stop the servers.
