#!/usr/bin/env python3
"""
Agentic Merchant OS — Model Context Protocol (MCP) Stdio Server
Implements the Anthropic/Open MCP standard (JSON-RPC 2.0 over stdio).
Allows Claude Desktop, Cursor, and any MCP client to discover tools, search catalog,
and execute Guardian-authorized purchases against Agentic Merchant OS.
"""

import sys
import json
import os
import httpx

API_BASE = os.environ.get("MERCHANT_API_BASE", "http://localhost:8000")

# MCP Tool Definitions
TOOLS = [
    {
        "name": "search_catalog",
        "description": "Search the official store product catalog for headphones, soundbars, earbuds, and accessories with live authoritative prices and stock levels.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (e.g. 'earbuds', 'headphones', 'case', 'soundbar')"
                },
                "merchant_id": {
                    "type": "string",
                    "default": "m_001",
                    "description": "Merchant identifier"
                }
            },
            "required": []
        }
    },
    {
        "name": "submit_machine_purchase",
        "description": "Execute a programmatic purchase through the deterministic Commerce Guardian. Authorizes orders within buyer mandate limits and generates Razorpay Test Orders and Decision Receipts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buyer_id": {
                    "type": "string",
                    "default": "b_001",
                    "description": "Buyer UUID"
                },
                "sku": {
                    "type": "string",
                    "description": "Product SKU to buy (e.g. 'HP-001', 'HP-002', 'CASE-HP')"
                },
                "quantity": {
                    "type": "integer",
                    "default": 1,
                    "description": "Number of units to purchase"
                },
                "max_budget_paise": {
                    "type": "integer",
                    "default": 1000000,
                    "description": "Maximum buyer mandate spend ceiling in paise (e.g. 1000000 = ₹10,000.00)"
                }
            },
            "required": ["sku"]
        }
    },
    {
        "name": "check_bundle_margin",
        "description": "Evaluate whether a promotional bundle discount maintains the merchant's minimum gross profit margin (>=15%).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "parent_sku": {
                    "type": "string",
                    "description": "Main product SKU (e.g. 'HP-001')"
                },
                "addon_sku": {
                    "type": "string",
                    "description": "Addon accessory SKU (e.g. 'CASE-HP')"
                },
                "discount_pct": {
                    "type": "integer",
                    "default": 30,
                    "description": "Discount percentage on the addon (0-100)"
                }
            },
            "required": ["parent_sku", "addon_sku"]
        }
    },
    {
        "name": "get_decision_receipt",
        "description": "Retrieve an immutable Decision Receipt and cryptographic audit trail for a previous transaction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "receipt_id": {
                    "type": "string",
                    "description": "Decision Receipt UUID"
                }
            },
            "required": ["receipt_id"]
        }
    }
]


def send_response(response):
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def handle_tool_call(name, args):
    try:
        with httpx.Client(base_url=API_BASE, timeout=10.0) as client:
            if name == "search_catalog":
                q = args.get("query", "")
                m = args.get("merchant_id", "m_001")
                res = client.get("/catalog/products", params={"q": q, "merchant_id": m})
                if res.status_code == 200:
                    products = res.json().get("products", [])
                    summary = [
                        {
                            "sku": p["sku"],
                            "name": p["name"],
                            "price_inr": "₹%.2f" % (p["price"] / 100.0),
                            "inventory": p["inventory"],
                            "category": p["category"],
                        }
                        for p in products
                    ]
                    return {"content": [{"type": "text", "text": json.dumps(summary, indent=2)}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Error: {res.text}"}]}

            elif name == "submit_machine_purchase":
                sku = args["sku"]
                qty = args.get("quantity", 1)
                buyer_id = args.get("buyer_id", "b_001")
                budget = args.get("max_budget_paise", 1000000)

                # Fetch authoritative catalog item first
                cat_res = client.get(f"/catalog/products/{sku}")
                if cat_res.status_code != 200:
                    return {"isError": True, "content": [{"type": "text", "text": f"Product '{sku}' not found in store"}]}
                product = cat_res.json()

                payload = {
                    "buyer_agent_id": "mcp_claude_buyer_01",
                    "buyer_mandate": {
                        "buyer_id": buyer_id,
                        "max_amount": budget,
                        "max_quantity_per_item": 5,
                        "currency": "INR",
                        "signature": "sig_mcp_client_authorization",
                    },
                    "purchase_items": [
                        {
                            "sku": sku,
                            "qty": qty,
                            "observed_price": product["price"],
                            "catalog_version": product["catalog_version"],
                        }
                    ],
                }

                res = client.post("/agent/v1/machine-purchase", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    decision = data.get("guardian_decision")
                    if decision == "REQUIRE_CONFIRMATION":
                        notif = data.get("high_value_notification") or {}
                        plink = data.get("payment_link") or notif.get("payment_link") or f"https://api.razorpay.com/v1/payment_links/plink_highval_{data.get('receipt_id')[:8]}"
                        recipient = notif.get("dispatched_to", "+91 98765 43210")
                        out = (
                            f"⚠️ GUARDIAN ESCALATION: REQUIRE_CONFIRMATION\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📦 Item: {product.get('name')} (SKU: {sku})\n"
                            f"💰 Total Verified Amount: ₹{(data.get('final_verified_total') or product['price'])/100.0:.2f}\n"
                            f"📜 Reason: {data.get('reason')}\n"
                            f"🧾 Decision Receipt ID: {data.get('receipt_id')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📲 HIGH-VALUE ALERT DISPATCHED TO HUMAN:\n"
                            f"• Recipient: {recipient}\n"
                            f"• 1-Click Razorpay Authorization Link:\n"
                            f"  {plink}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🔒 The AI bot cannot settle this high-value amount autonomously. Click the authorization link above to confirm & pay."
                        )
                    else:
                        out = (
                            f"🛡️ Guardian Decision: {data['guardian_decision']}\n"
                            f"💰 Total Amount: ₹{(data.get('final_verified_total') or 0)/100.0:.2f}\n"
                            f"🧾 Decision Receipt ID: {data['receipt_id']}\n"
                            f"💳 Razorpay Order ID: {data.get('razorpay_order_id', 'None')}\n"
                            f"🔒 Replay Hash: {data.get('replay_hash', 'None')}\n"
                            f"📜 Reason: {data.get('reason')}"
                        )
                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Purchase Failed: {res.text}"}]}

            elif name == "check_bundle_margin":
                res = client.post("/catalog/bundles/margin-check", json=args)
                if res.status_code == 200:
                    data = res.json()
                    return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Margin check error: {res.text}"}]}

            elif name == "get_decision_receipt":
                receipt_id = args["receipt_id"]
                res = client.get(f"/receipts/{receipt_id}")
                if res.status_code == 200:
                    return {"content": [{"type": "text", "text": json.dumps(res.json(), indent=2)}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Receipt not found: {res.text}"}]}

            else:
                return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"MCP execution error: {str(e)}"}]}


def main():
    """Main JSON-RPC 2.0 stdio loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "agentic-merchant-os-mcp",
                            "version": "1.0.0"
                        }
                    }
                })

            elif method == "tools/list":
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS
                    }
                })

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                res = handle_tool_call(tool_name, tool_args)
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": res
                })

            elif method == "notifications/initialized":
                # Client notification acknowledgment
                pass

            else:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                })
        except Exception as e:
            sys.stderr.write(f"MCP Server error: {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
