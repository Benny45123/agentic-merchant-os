#!/usr/bin/env bash
# ==============================================================================
# Launch Telegram Bot Mobile Gateway (@agentic_merchant_store_bot)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🤖 Launching Telegram Bot Gateway (@agentic_merchant_store_bot)"
echo "=================================================================="

cd "$REPO_ROOT/backend"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$REPO_ROOT/backend:$PYTHONPATH"
python -m app.telegram.bot

