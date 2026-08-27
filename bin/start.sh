#!/usr/bin/env bash
# ==============================================================================
# Start Full Stack (Backend on :8000 + Frontend on :3000)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🚀 Starting Agentic Merchant OS (Full Stack)"
echo "=================================================================="

# Function to cleanly stop background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down backend and frontend servers..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    echo "✅ Shutdown complete."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 1. Start Backend in background
echo "📦 [1/2] Launching Backend on http://localhost:8000..."
cd "$REPO_ROOT/backend"
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# Wait briefly for backend port to bind
sleep 2

# 2. Start Frontend in background
echo "💻 [2/2] Launching Frontend on http://localhost:3000..."
cd "$REPO_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=================================================================="
echo "🎉 AGENTIC MERCHANT OS IS RUNNING!"
echo "=================================================================="
echo "👉 Frontend App:     http://localhost:3000"
echo "👉 Buyer Chat:       http://localhost:3000/chat"
echo "👉 Merchant Control: http://localhost:3000/dashboard"
echo "👉 Backend API Docs: http://localhost:8000/docs"
echo "=================================================================="
echo "Press Ctrl+C to stop all servers."
echo ""

# Wait for both processes
wait "$BACKEND_PID" "$FRONTEND_PID"
