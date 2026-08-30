@echo off
set "REPO_ROOT=%~dp0.."
cd /d "%REPO_ROOT%\backend"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo ==================================================================
echo 🧪 Running Pytest Test Suite & Architecture Import Linter
echo ==================================================================

python -m pytest -v
if %ERRORLEVEL% neq 0 (
    echo ❌ Pytest suite failed.
    exit /b %ERRORLEVEL%
)

echo.
echo 🔍 Checking Architecture Import Graph Linter...
python ..\scripts\check_import_graph.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Import graph violation found.
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ ALL TESTS AND ARCHITECTURE LINTS PASSED!
