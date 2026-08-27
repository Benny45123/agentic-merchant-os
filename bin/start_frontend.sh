#!/usr/bin/env bash
# ==============================================================================
# Start Frontend Dev Server (Next.js on http://localhost:3000)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Agentic Merchant OS Frontend..."
cd "$REPO_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "❌ Error: node_modules not found. Run ./bin/setup_env.sh or 'npm install' in ./frontend first."
    exit 1
fi

echo "🌐 Frontend running at: http://localhost:3000"
echo ""

npm run dev
