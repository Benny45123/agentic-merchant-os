#!/usr/bin/env bash
# ==============================================================================
# Stop All Background Servers for Agentic Merchant OS
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS_DIR="$REPO_ROOT/logs"

echo "=================================================================="
echo "🛑 Stopping Agentic Merchant OS Background Servers..."
echo "=================================================================="

# 1. Kill recorded PIDs if files exist
if [ -f "$LOGS_DIR/backend.pid" ]; then
    BPID=$(cat "$LOGS_DIR/backend.pid" 2>/dev/null || true)
    if [ -n "$BPID" ]; then
        kill "$BPID" 2>/dev/null || true
    fi
    rm -f "$LOGS_DIR/backend.pid"
fi

if [ -f "$LOGS_DIR/frontend.pid" ]; then
    FPID=$(cat "$LOGS_DIR/frontend.pid" 2>/dev/null || true)
    if [ -n "$FPID" ]; then
        kill "$FPID" 2>/dev/null || true
    fi
    rm -f "$LOGS_DIR/frontend.pid"
fi

# 2. Force free ports 8000 and 3000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "✅ All backend (:8000) and frontend (:3000) servers stopped cleanly."
echo "=================================================================="
