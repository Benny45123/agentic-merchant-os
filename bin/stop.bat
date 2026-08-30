@echo off
echo ==================================================================
echo 🛑 Stopping Agentic Merchant OS Servers
echo ==================================================================

:: Kill any process listening on port 8000 and 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo ✅ Servers stopped on ports 8000 and 3000.
