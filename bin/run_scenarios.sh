#!/usr/bin/env bash
# ==============================================================================
# Run All 6 Automated End-to-End Demo Scenarios
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🎬 Running 6 End-to-End Demo Scenarios (Including Autopay Failure Handling)"
echo "=================================================================="

cd "$REPO_ROOT/backend"
source .venv/bin/activate

python "$REPO_ROOT/scripts/run_scenarios.py" "http://localhost:8000"
