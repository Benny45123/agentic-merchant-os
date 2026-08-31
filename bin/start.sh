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

# 1. Stop any previous instances on ports 8000 or 3000 and any previous bot listener
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
pkill -9 -f "app.telegram.bot" 2>/dev/null || true
sleep 1


# Initialize log files
touch "$LOGS_DIR/backend.log" "$LOGS_DIR/frontend.log" "$LOGS_DIR/telegram_bot.log"
> "$LOGS_DIR/backend.log"
> "$LOGS_DIR/frontend.log"
> "$LOGS_DIR/telegram_bot.log"


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

# 4. Launch Telegram Bot Gateway if TELEGRAM_BOT_TOKEN is set
TG_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" "$REPO_ROOT/backend/.env" 2>/dev/null | cut -d '=' -f2- | tr -d '"' | tr -d "'" || true)
if [ -n "$TG_TOKEN" ] && [ "$TG_TOKEN" != "placeholder_token" ] && [ ${#TG_TOKEN} -gt 15 ]; then
    echo "🤖 [3/3] Starting Telegram Bot Gateway (@agentic_merchant_store_bot)..."
    touch "$LOGS_DIR/telegram_bot.log"
    > "$LOGS_DIR/telegram_bot.log"
    cd "$REPO_ROOT/backend"
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    export PYTHONPATH="$REPO_ROOT/backend:$PYTHONPATH"
    nohup python -m app.telegram.bot > "$LOGS_DIR/telegram_bot.log" 2>&1 &
    TG_PID=$!
    echo "$TG_PID" > "$LOGS_DIR/telegram_bot.pid"
fi


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
echo "👉 Telegram Bot:      https://t.me/agentic_merchant_store_bot"
echo "👉 Backend API Docs:  http://localhost:8000/docs"
echo "=================================================================="
echo "📜 LIVE LOGS STREAMING:"
echo "   • Stream All Logs:     ./bin/logs"
echo "   • Stream Backend:      ./bin/logs backend"
echo "   • Stream Frontend:     ./bin/logs frontend"
echo "   • Stream Telegram Bot: tail -f logs/telegram_bot.log"
echo "=================================================================="
echo "🛑 TO STOP BACKGROUND SERVERS:"
echo "   • Run: ./bin/stop.sh"
echo "=================================================================="
echo "✅ Terminal is now free. Background processes are running safely."
echo ""
