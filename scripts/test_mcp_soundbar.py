#!/usr/bin/env python3
"""
Test MCP High-Value SoundBar Pro Purchase & Human Escalation Notification
"""

import sys
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER = REPO_ROOT / "backend" / "app" / "api" / "mcp_server.py"


def main():
    print("==================================================================")
    print("🔌 EXECUTING LIVE MCP PURCHASE: SoundBar Pro (SPK-001 @ ₹8,999.00)")
    print("==================================================================")

    p = subprocess.Popen(
        [sys.executable, str(MCP_SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Step 1: Initialize MCP Handshake
        init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
        p.stdin.write(json.dumps(init_req) + "\n")
        p.stdin.flush()
        p.stdout.readline()

        # Step 2: Call submit_machine_purchase for SPK-001 (₹8,999.00)
        tool_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "submit_machine_purchase",
                "arguments": {
                    "sku": "SPK-001",
                    "quantity": 1,
                    "buyer_id": "b_001",
                    "max_budget_paise": 1000000,
                },
            },
        }
        p.stdin.write(json.dumps(tool_req) + "\n")
        p.stdin.flush()

        raw_resp = p.stdout.readline()
        res = json.loads(raw_resp.strip())

        print("\n📥 MCP TOOL CALL RESULT:\n")
        if "result" in res:
            content_list = res["result"].get("content", [])
            for c in content_list:
                print(c.get("text", ""))
        else:
            print("Error response:", res)

        print("\n==================================================================")
        print("✅ LIVE MCP TEST COMPLETED")
        print("==================================================================")

    finally:
        p.terminate()


if __name__ == "__main__":
    main()
