#!/usr/bin/env bash
# ==============================================================================
# Run Unit/Integration Tests & Architecture Lint
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🧪 Running Agentic Merchant OS Test Suite & Architecture Lint"
echo "=================================================================="

cd "$REPO_ROOT/backend"
source .venv/bin/activate

echo ""
echo "🔍 [1/2] Running Architecture Import-Graph Linter..."
python "$REPO_ROOT/scripts/check_import_graph.py"

echo ""
echo "🔬 [2/2] Running Pytest Suite (Guardian 22-Matrix, Catalog, Receipts, Security, Commerce Agent)..."
pytest -v

echo ""
echo "=================================================================="
echo "✅ ALL TESTS & ARCHITECTURE CHECKS PASSED!"
echo "=================================================================="
