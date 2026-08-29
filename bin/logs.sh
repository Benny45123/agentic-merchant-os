#!/usr/bin/env bash
# ==============================================================================
# Stream Live Logs from Background Backend and Frontend Processes
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS_DIR="$REPO_ROOT/logs"

TARGET="${1:-combined}"

if [ ! -d "$LOGS_DIR" ]; then
    echo "❌ Logs directory not found at $LOGS_DIR. Please start the stack first via ./bin/start.sh"
    exit 1
fi

echo "=================================================================="
echo "📜 STREAMING LIVE LOGS: [Agentic Merchant OS]"
echo "=================================================================="
echo "Target: $TARGET (Options: combined | backend | frontend)"
echo "Press Ctrl+C anytime to exit log view (servers continue running)."
echo "=================================================================="
echo ""

case "$TARGET" in
    backend|api)
        tail -n 25 -f "$LOGS_DIR/backend.log"
        ;;
    frontend|ui|web)
        tail -n 25 -f "$LOGS_DIR/frontend.log"
        ;;
    *)
        # Default: Stream both files live simultaneously with last 25 lines
        tail -n 25 -f "$LOGS_DIR/backend.log" "$LOGS_DIR/frontend.log"
        ;;
esac
