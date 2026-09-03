#!/usr/bin/env bash
set -e

# ==============================================================================
# Agentic Merchant OS — 1-Click Claude Desktop MCP Configurator
# ==============================================================================

SERVER_URL="${1:-http://localhost:8000}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_SCRIPT="$REPO_DIR/backend/app/api/mcp_server.py"

echo "========================================================="
echo "   Agentic Merchant OS — Claude Desktop MCP Configurator "
echo "========================================================="
echo "Target Backend API : $SERVER_URL"
echo "MCP Server Script  : $MCP_SCRIPT"
echo "========================================================="

# Detect Python interpreter
PYTHON_BIN="python3"
if [ -f "$REPO_DIR/backend/.venv/bin/python" ]; then
    PYTHON_BIN="$REPO_DIR/backend/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="$(command -v python3)"
elif command -v python &>/dev/null; then
    PYTHON_BIN="$(command -v python)"
fi
echo "Using Python       : $PYTHON_BIN"

# Detect OS and Claude Desktop config path
OS_NAME="$(uname -s)"
CONFIG_DIR=""

if [ "$OS_NAME" = "Darwin" ]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [ "$OS_NAME" = "Linux" ]; then
    CONFIG_DIR="$HOME/.config/Claude"
else
    # Windows / Git Bash
    CONFIG_DIR="$APPDATA/Claude"
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
mkdir -p "$CONFIG_DIR"

# Write configuration
python3 -c "
import json, os, sys

config_file, server_url, python_bin, mcp_script = sys.argv[1:5]

data = {}
if os.path.exists(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}

if 'mcpServers' not in data:
    data['mcpServers'] = {}

data['mcpServers']['agentic-merchant-os'] = {
    'command': python_bin,
    'args': [mcp_script],
    'env': {
        'MERCHANT_API_BASE': server_url
    }
}

with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f'Successfully updated: {config_file}')
" "$CONFIG_FILE" "$SERVER_URL" "$PYTHON_BIN" "$MCP_SCRIPT" 2>/dev/null || {
    echo "Writing configuration template directly..."
    cat << CFGEOF > "$CONFIG_FILE"
{
  "mcpServers": {
    "agentic-merchant-os": {
      "command": "$PYTHON_BIN",
      "args": ["$MCP_SCRIPT"],
      "env": {
        "MERCHANT_API_BASE": "$SERVER_URL"
      }
    }
  }
}
CFGEOF
}

echo ""
echo "✅ Claude Desktop MCP configuration installed successfully!"
echo "📍 Config path: $CONFIG_FILE"
echo ""
echo "Next Steps:"
echo "1. Restart Claude Desktop completely (Quit and re-open)."
echo "2. You will see the hammer (⚒️) tool icon in Claude!"
echo "3. Try asking Claude:"
echo "   \"Search the store catalog for iPhone 15, then negotiate the lowest wholesale price.\""
echo "========================================================="
