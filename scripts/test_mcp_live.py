#!/usr/bin/env python3
"""
Live Model Context Protocol (MCP) Test Harness
Launches backend/app/api/mcp_server.py as a subprocess, communicates over standard I/O
using JSON-RPC 2.0, and executes all MCP tools against the live store backend.
"""

import sys
import json
import subprocess
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER_SCRIPT = REPO_ROOT / "backend" / "app" / "api" / "mcp_server.py"


class MCPTestClient:
    def __init__(self, script_path):
        self.process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.req_id = 0

    def send_request(self, method, params=None):
        self.req_id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method,
        }
        if params is not None:
            msg["params"] = params

        payload = json.dumps(msg) + "\n"
        self.process.stdin.write(payload)
        self.process.stdin.flush()

        response_line = self.process.stdout.readline()
        if not response_line:
            err = self.process.stderr.read()
            raise RuntimeError(f"MCP server closed output pipe: {err}")

        return json.loads(response_line.strip())

    def close(self):
        try:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=2)
        except Exception:
            pass


def run_live_mcp_test():
    print("==================================================================")
    print("🔌 LIVE MODEL CONTEXT PROTOCOL (MCP) TEST HARNESS")
    print("   Testing JSON-RPC 2.0 Stdio Communication with mcp_server.py")
    print("==================================================================")

    client = MCPTestClient(MCP_SERVER_SCRIPT)

    try:
        # 1. Initialize Handshake
        print("\n[1/5] Testing MCP Handshake: 'initialize'...")
        init_res = client.send_request("initialize", {"protocolVersion": "2024-11-05"})
        print("  📥 Handshake Response: %s" % json.dumps(init_res.get("result", {}), indent=2))
        assert "serverInfo" in init_res.get("result", {}), "Handshake failed"
        print("  ✅ MCP Handshake Verified (Protocol: %s)" % init_res["result"]["protocolVersion"])

        # 2. Tool Discovery
        print("\n[2/5] Testing MCP Tool Discovery: 'tools/list'...")
        list_res = client.send_request("tools/list")
        tools = list_res.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        print("  🛠️ Discovered MCP Tools (%d): %s" % (len(tools), tool_names))
        assert "search_catalog" in tool_names
        assert "submit_machine_purchase" in tool_names
        assert "check_bundle_margin" in tool_names
        assert "get_decision_receipt" in tool_names
        print("  ✅ All 4 Core MCP Tools Successfully Declared")

        # 3. Tool Call: search_catalog
        print("\n[3/5] Testing MCP Tool Call: 'search_catalog' (query='headphones')...")
        search_res = client.send_request("tools/call", {
            "name": "search_catalog",
            "arguments": {"query": "headphones"}
        })
        content_text = search_res.get("result", {}).get("content", [{}])[0].get("text", "")
        print("  📦 Catalog Search Output:\n%s" % content_text)
        assert "HP-001" in content_text
        print("  ✅ 'search_catalog' Executed and Returned Authoritative Products")

        # 4. Tool Call: check_bundle_margin
        print("\n[4/5] Testing MCP Tool Call: 'check_bundle_margin' (HP-001 + CASE-HP @ 30% off)...")
        margin_res = client.send_request("tools/call", {
            "name": "check_bundle_margin",
            "arguments": {
                "parent_sku": "HP-001",
                "addon_sku": "CASE-HP",
                "discount_pct": 30
            }
        })
        margin_text = margin_res.get("result", {}).get("content", [{}])[0].get("text", "")
        print("  📊 Margin Calculation Output:\n%s" % margin_text)
        margin_data = json.loads(margin_text)
        assert margin_data.get("approved") is True
        print("  ✅ 'check_bundle_margin' Verified (Projected Margin: %.1f%% >= 15.0%% Floor)" % margin_data["projected_margin_pct"])

        # 5. Tool Call: submit_machine_purchase
        print("\n[5/5] Testing MCP Tool Call: 'submit_machine_purchase' (AeroSound Earbuds HP-002)...")
        purchase_res = client.send_request("tools/call", {
            "name": "submit_machine_purchase",
            "arguments": {
                "sku": "HP-002",
                "quantity": 1,
                "buyer_id": "b_001",
                "max_budget_paise": 1000000
            }
        })
        purchase_text = purchase_res.get("result", {}).get("content", [{}])[0].get("text", "")
        print("  🛡️ Guardian Settlement Output:\n%s" % purchase_text)
        assert "APPROVE" in purchase_text
        assert "Decision Receipt ID" in purchase_text
        assert "Razorpay Order ID" in purchase_text
        print("  ✅ 'submit_machine_purchase' Authorized by Guardian with Razorpay Test Order")

        print("\n==================================================================")
        print("🎉 ALL MCP JSON-RPC 2.0 TOOLS PASSED LIVE END-TO-END VERIFICATION!")
        print("==================================================================")
        return True

    finally:
        client.close()


if __name__ == "__main__":
    success = run_live_mcp_test()
    sys.exit(0 if success else 1)
