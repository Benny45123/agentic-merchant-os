#!/usr/bin/env bash
# ==============================================================================
# Start Full Stack in Background (Daemon Mode) with Live Logging
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS_DIR="$REPO_ROOT/logs"

mkdir -p "$LOGS_DIR"

echo "=================================================================="
echo "🚀 Launching Agentic Merchant OS in Background"
echo "=================================================================="

# 1. Stop any previous instances on ports 8000 or 3000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Initialize log files
touch "$LOGS_DIR/backend.log" "$LOGS_DIR/frontend.log"
> "$LOGS_DIR/backend.log"
> "$LOGS_DIR/frontend.log"

# 2. Launch Backend in background
echo "📦 [1/2] Starting FastAPI Backend on http://localhost:8000..."
cd "$REPO_ROOT/backend"
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run backend detached with nohup
nohup uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 > "$LOGS_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$LOGS_DIR/backend.pid"

# 3. Launch Frontend in background
echo "💻 [2/2] Starting Next.js Frontend on http://localhost:3000..."
cd "$REPO_ROOT/frontend"
nohup npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$LOGS_DIR/frontend.pid"

# Wait briefly for ports to initialize
sleep 2

echo ""
echo "=================================================================="
echo "🎉 AGENTIC MERCHANT OS IS RUNNING IN THE BACKGROUND!"
echo "=================================================================="
echo "👉 Frontend UI:       http://localhost:3000"
echo "👉 Buyer Chat:        http://localhost:3000/chat"
echo "👉 A2A Arena:         http://localhost:3000/negotiate"
echo "👉 Receipts Explorer: http://localhost:3000/receipts"
echo "👉 Merchant Control:  http://localhost:3000/dashboard"
echo "👉 Backend API Docs:  http://localhost:8000/docs"
echo "=================================================================="
echo "📜 LIVE LOGS STREAMING:"
echo "   • Stream All Logs:     ./bin/logs.sh"
echo "   • Backend Logs Only:   ./bin/logs.sh backend"
echo "   • Frontend Logs Only:  ./bin/logs.sh frontend"
echo "=================================================================="
echo "🛑 TO STOP BACKGROUND SERVERS:"
echo "   • Run: ./bin/stop.sh"
echo "=================================================================="
echo "✅ Terminal is now free. Background processes are running safely."
echo ""
