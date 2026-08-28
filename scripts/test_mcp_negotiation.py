#!/usr/bin/env python3
"""
Live MCP Test for Autonomous A2A Dynamic Negotiation (Reverse Auction)
Tests submit_commerce_rfq and accept_negotiation_offer via JSON-RPC 2.0 stdio with mcp_server.py.
"""

import sys
import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER = REPO_ROOT / "backend" / "app" / "api" / "mcp_server.py"


def main():
    print("==================================================================")
    print("🔌 LIVE MCP NEGOTIATION TEST: Reverse Auction & Guardian Settlement")
    print("==================================================================")

    p = subprocess.Popen(
        [sys.executable, str(MCP_SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Step 1: Handshake
        print("\n[Step 1] Initializing MCP Handshake...")
        init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
        p.stdin.write(json.dumps(init_req) + "\n")
        p.stdin.flush()
        init_res = json.loads(p.stdout.readline().strip())
        print("  ✅ MCP Handshake Verified (Protocol: %s)" % init_res["result"]["protocolVersion"])

        # Step 2: Submit RFQ via MCP tool
        print("\n[Step 2] Calling MCP Tool: 'submit_commerce_rfq' (3x HP-001 @ ₹4,100.00)...")
        rfq_tool_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "submit_commerce_rfq",
                "arguments": {
                    "sku": "HP-001",
                    "quantity": 3,
                    "target_unit_price_paise": 410000,
                    "buyer_agent_id": "ai_buyer_agent_procure_42",
                },
            },
        }
        p.stdin.write(json.dumps(rfq_tool_req) + "\n")
        p.stdin.flush()

        rfq_raw = p.stdout.readline()
        rfq_res = json.loads(rfq_raw.strip())
        rfq_text = rfq_res.get("result", {}).get("content", [{}])[0].get("text", "")
        print("\n📥 MCP RFQ OUTPUT:\n%s" % rfq_text)

        # Extract session_id
        session_match = re.search(r"Session ID: (neg_sess_[a-f0-9]+)", rfq_text)
        session_id = session_match.group(1) if session_match else None
        assert session_id is not None, "Failed to extract session_id from MCP response"
        assert "OPT_BUNDLE_SWEETENER" in rfq_text

        # Step 3: Accept Negotiation Offer via MCP tool
        print("\n[Step 3] Calling MCP Tool: 'accept_negotiation_offer' (OPT_BUNDLE_SWEETENER)...")
        accept_tool_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "accept_negotiation_offer",
                "arguments": {
                    "session_id": session_id,
                    "selected_option_id": "OPT_BUNDLE_SWEETENER",
                    "buyer_agent_id": "ai_buyer_agent_procure_42",
                },
            },
        }
        p.stdin.write(json.dumps(accept_tool_req) + "\n")
        p.stdin.flush()

        accept_raw = p.stdout.readline()
        accept_res = json.loads(accept_raw.strip())
        accept_text = accept_res.get("result", {}).get("content", [{}])[0].get("text", "")
        print("\n📥 MCP SETTLEMENT OUTPUT:\n%s" % accept_text)

        assert "APPROVE" in accept_text or "Decision Receipt" in accept_text
        assert "Razorpay Order ID" in accept_text

        print("\n==================================================================")
        print("🎉 LIVE MCP NEGOTIATION TEST PASSED CLEANLY WITH 100% SUCCESS!")
        print("==================================================================")
        return True

    finally:
        p.terminate()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
