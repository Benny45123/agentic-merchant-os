#!/bin/bash
set -e

# Change to repository root
cd "$(dirname "$0")/.."

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required to run the AI buyer simulation."
    exit 1
fi

# Run the simulation script
python3 scripts/simulate_ai_buyer.py
