# ==============================================================================
# Start Full Stack on Windows via PowerShell
# ==============================================================================
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "🚀 Launching Agentic Merchant OS on Windows" -ForegroundColor Magenta
Write-Host "=================================================================="

# Start Backend
Write-Host "📦 [1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\backend'; if (Test-Path '.venv\Scripts\Activate.ps1') { .\.venv\Scripts\Activate.ps1 }; uvicorn app.main:app --reload --port 8000 --host 127.0.0.1"

# Start Frontend
Write-Host "💻 [2/2] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "🎉 AGENTIC MERCHANT OS IS RUNNING!" -ForegroundColor Green
Write-Host "=================================================================="
Write-Host "👉 Frontend UI:       http://localhost:3000"
Write-Host "👉 Buyer Chat:        http://localhost:3000/chat"
Write-Host "👉 A2A Arena:         http://localhost:3000/negotiate"
Write-Host "👉 Receipts Explorer: http://localhost:3000/receipts"
Write-Host "👉 Merchant Control:  http://localhost:3000/dashboard"
Write-Host "👉 Backend API Docs:  http://localhost:8000/docs"
Write-Host "=================================================================="
Write-Host "To stop servers, run: .\bin\stop.bat or .\bin\stop.ps1"
