#!/usr/bin/env bash
# ==============================================================================
# Start Backend API Server (FastAPI on http://localhost:8000)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Agentic Merchant OS Backend..."
cd "$REPO_ROOT/backend"

if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment .venv not found. Run ./bin/setup_env.sh first."
    exit 1
fi

source .venv/bin/activate
echo "🌐 API running at: http://localhost:8000"
echo "📚 Swagger docs at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
