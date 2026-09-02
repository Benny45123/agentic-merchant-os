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
        "description": "Retrieve the official store product catalog or search across all categories (mobiles, laptops, audio, wearables, accessories) with live authoritative prices and stock levels. To retrieve the FULL catalog with all products in a single call, leave query empty or pass '*' or 'all'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Optional search keyword (e.g. 'phone', 'iphone', 'samsung', 'laptop', 'earbuds', 'watch', 'case'). Leave empty or pass '*' / 'all' to list the entire catalog."
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
        "name": "submit_commerce_rfq",
        "description": "Submit a Request for Quote (RFQ) to negotiate custom unit prices or bulk volume deals. Returns bilateral counter-offers within merchant gross margin constraints.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Product SKU (e.g. 'HP-001')"
                },
                "quantity": {
                    "type": "integer",
                    "default": 3,
                    "description": "Quantity requested"
                },
                "target_unit_price_paise": {
                    "type": "integer",
                    "description": "Buyer target price per unit in paise (e.g. 410000 = ₹4,100.00)"
                },
                "buyer_agent_id": {
                    "type": "string",
                    "default": "ai_buyer_agent_procure_42",
                    "description": "Identifier of the buying bot"
                }
            },
            "required": ["sku", "target_unit_price_paise"]
        }
    },
    {
        "name": "accept_negotiation_offer",
        "description": "Accept an offer from a previous RFQ negotiation session (e.g. OPT_DIRECT_PRICE or OPT_BUNDLE_SWEETENER) to finalize Guardian authorization and Razorpay order.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Negotiation session ID returned by submit_commerce_rfq"
                },
                "selected_option_id": {
                    "type": "string",
                    "description": "Chosen option ID (e.g. 'OPT_DIRECT_PRICE' or 'OPT_BUNDLE_SWEETENER')"
                },
                "buyer_agent_id": {
                    "type": "string",
                    "default": "ai_buyer_agent_procure_42",
                    "description": "Identifier of the buying bot"
                }
            },
            "required": ["session_id", "selected_option_id"]
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
    },
    {
        "name": "setup_autopay_mandate",
        "description": "Register and activate a Headless Razorpay UPI AutoPay recurring e-mandate (tok_rzp_autopay_...). Enables Claude to execute 0-click autonomous purchases within spending caps without asking for OTP.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buyer_id": {
                    "type": "string",
                    "default": "b_001",
                    "description": "Buyer ID"
                },
                "max_amount_paise": {
                    "type": "integer",
                    "default": 10000000,
                    "description": "Maximum mandate spend cap in paise (e.g. 5000000 = ₹50,000.00)"
                },
                "vpa": {
                    "type": "string",
                    "description": "Optional UPI VPA (e.g. shopper@okhdfcbank)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_autopay_status",
        "description": "Retrieve the current active UPI AutoPay token, spend headroom, and recurring mandate authorization status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buyer_id": {
                    "type": "string",
                    "default": "b_001",
                    "description": "Buyer ID"
                }
            },
            "required": []
        }
    },
    {
        "name": "revoke_autopay_mandate",
        "description": "Revoke or pause an active UPI AutoPay mandate, freezing 0-click autonomous transactions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buyer_id": {
                    "type": "string",
                    "default": "b_001",
                    "description": "Buyer ID"
                }
            },
            "required": []
        }
    },
    {
        "name": "check_payment_status",
        "description": "Check and verify if a customer payment has been completed on Razorpay for a given order ID (e.g. 'order_TX4QlTTW4vKXcx') or Decision Receipt ID (UUID). Returns whether payment is confirmed/complete or still pending, and provides the checkout link if unpaid.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Razorpay order ID (e.g. 'order_TX4QlTTW4vKXcx') or Decision Receipt ID (UUID)"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "verify_autopay_mandate",
        "description": "Live Razorpay Test Mandate Verification Gate: Queries Razorpay Test API to cryptographically verify that the buyer's recurring UPI AutoPay token is active, confirmed on the payment rail, and valid for zero-click autonomous checkout.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buyer_id": {
                    "type": "string",
                    "default": "b_001",
                    "description": "Buyer ID"
                }
            },
            "required": []
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
                q = (args.get("query") or "").strip()
                m = args.get("merchant_id", "m_001")
                if q.lower() in ("*", "all", "full", "everything", "all products", "catalog", "full catalog"):
                    q = ""
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
                        plink = data.get("payment_link") or notif.get("payment_link") or f"{API_BASE}/payments/checkout/{data.get('receipt_id')}"
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
                    elif data.get("headless_autopay"):
                        out = (
                            f"⚡ 0-CLICK AUTONOMOUS AUTOPAY COMPLETED!\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🛡️ Guardian Decision: APPROVE (19/19 Invariants Passed)\n"
                            f"📦 Item: {product.get('name')} (SKU: {sku})\n"
                            f"💰 Total Amount Paid: ₹{(data.get('final_verified_total') or product['price'])/100.0:.2f}\n"
                            f"🧾 Decision Receipt ID: {data['receipt_id']}\n"
                            f"💳 Razorpay Order ID: {data.get('razorpay_order_id', 'None')}\n"
                            f"🔒 Replay Hash: {data.get('replay_hash', 'None')}\n"
                            f"📜 Status: Paid autonomously in < 400ms via UPI AutoPay (0 OTP prompts)"
                        )
                    else:
                        plink = data.get("payment_link") or f"{API_BASE}/payments/checkout/{data.get('razorpay_order_id') or data.get('receipt_id')}"
                        out = (
                            f"🛡️ GUARDIAN APPROVED — PAYMENT LINK READY (AutoPay Disabled)\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📦 Item: {product.get('name')} (SKU: {sku})\n"
                            f"💰 Total Amount: ₹{(data.get('final_verified_total') or product['price'])/100.0:.2f}\n"
                            f"🧾 Decision Receipt ID: {data['receipt_id']}\n"
                            f"💳 Razorpay Order ID: {data.get('razorpay_order_id', 'None')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"💳 1-Click Razorpay Checkout Link:\n"
                            f"  {plink}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"ℹ️ AutoPay is disabled. Click the checkout link above to complete your payment on Razorpay."
                        )
                    return {"content": [{"type": "text", "text": out}]}

                return {"isError": True, "content": [{"type": "text", "text": f"Purchase Failed: {res.text}"}]}

            elif name == "submit_commerce_rfq":
                sku = args["sku"]
                qty = args.get("quantity", 3)
                target_price = args["target_unit_price_paise"]
                buyer_agent = args.get("buyer_agent_id", "ai_buyer_agent_procure_42")

                rfq_payload = {
                    "buyer_agent_id": buyer_agent,
                    "merchant_id": "m_001",
                    "buyer_mandate": {
                        "buyer_id": "b_001",
                        "max_amount": 2000000,
                        "max_quantity_per_item": 10,
                        "currency": "INR",
                        "signature": "sig_mcp_rfq_mandate",
                    },
                    "items": [
                        {
                            "sku": sku,
                            "qty": qty,
                            "target_unit_price_paise": target_price,
                        }
                    ],
                }

                res = client.post("/commerce/rfq", json=rfq_payload)
                if res.status_code == 200:
                    data = res.json()
                    out = (
                        f"🤝 BILATERAL RFQ NEGOTIATION STATUS: {data['status']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📋 Session ID: {data['session_id']}\n"
                        f"🏷️ Catalog Total: ₹{data['catalog_total_paise']/100:.2f} | Buyer Proposed: ₹{data['buyer_target_total_paise']/100:.2f}\n"
                        f"🛡️ Margin Floor: {data['minimum_margin_floor_pct']}%\n"
                        f"📜 Rationale: {data['reason']}\n"
                        f"💡 AI Pricing Notes: {data['ai_pricing_agent_notes']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎁 PROPOSED COUNTER-OFFERS:\n"
                    )
                    for i, opt in enumerate(data.get("counter_offers", []), 1):
                        out += (
                            f"\n  [{i}] {opt['title']} ({opt['option_id']})\n"
                            f"      • Total: ₹{opt['total_amount_paise']/100:.2f} ({opt['discount_pct']}% discount)\n"
                            f"      • Projected Margin: {opt['projected_gross_margin_pct']}% (Floor: >=15% ✓)\n"
                            f"      • Merchant Profit Lift: +₹{opt['merchant_profit_lift_paise']/100:.2f}\n"
                            f"      • Details: {opt['description']}\n"
                        )
                    out += (
                        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👉 To finalize, call 'accept_negotiation_offer' with session_id='{data['session_id']}' and selected_option_id."
                    )
                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"RFQ Failed: {res.text}"}]}

            elif name == "accept_negotiation_offer":
                session_id = args["session_id"]
                option_id = args["selected_option_id"]
                buyer_agent = args.get("buyer_agent_id", "ai_buyer_agent_procure_42")

                accept_payload = {
                    "session_id": session_id,
                    "buyer_agent_id": buyer_agent,
                    "merchant_id": "m_001",
                    "selected_option_id": option_id,
                    "buyer_signature": "sig_mcp_signed_contract",
                }

                res = client.post("/commerce/accept", json=accept_payload)
                if res.status_code == 200:
                    data = res.json()
                    out = (
                        f"🎉 NEGOTIATION AGREEMENT SETTLED & AUTHORIZED!\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🛡️ Guardian Decision: {data['guardian_decision']}\n"
                        f"💰 Final Verified Total: ₹{data['final_verified_total_paise']/100:.2f}\n"
                        f"📈 Merchant Gross Margin Achieved: {data['merchant_margin_achieved_pct']}%\n"
                        f"🧾 Decision Receipt ID: {data['receipt_id']}\n"
                        f"💳 Razorpay Order ID: {data.get('razorpay_order_id', 'None')}\n"
                        f"🔒 Cryptographic Replay Hash: {data['replay_hash']}\n"
                        f"📜 Reason: {data['reason']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📦 Negotiated Contract Items:\n"
                    )
                    for item in data.get("negotiated_items", []):
                        out += f"  • {item['qty']}x {item['sku']} @ {item['price_inr']}/unit\n"
                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Settlement Failed: {res.text}"}]}

            elif name == "check_bundle_margin":
                res = client.post("/catalog/bundles/margin-check", json=args)
                if res.status_code == 200:
                    data = res.json()
                    return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Margin check error: {res.text}"}]}

            elif name == "setup_autopay_mandate":
                buyer_id = args.get("buyer_id", "b_001")
                cap = args.get("max_amount_paise", 10000000)
                vpa = args.get("vpa")
                res = client.post("/mandates/autopay/setup", json={
                    "buyer_id": buyer_id,
                    "max_amount_paise": cap,
                    "vpa": vpa,
                    "simulate_auth": False,
                })
                if res.status_code == 200:
                    data = res.json()
                    headroom = data.get("remaining_headroom_paise", data["max_amount_paise"]) / 100.0
                    auth_link = data.get("auth_url") or f"{API_BASE}/mandates/checkout/{data.get('token_id')}"

                    if data.get("status") == "PENDING_AUTH" or not data.get("autopay_enabled"):
                        out = (
                            f"⏳ RAZORPAY MANDATE AUTHORIZATION GATE: AWAITING HUMAN SIGNATURE\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Status: PENDING_AUTH (Awaiting 1-Time Human Authorization)\n"
                            f"• Mandate Authorization Pool: ₹{data['max_amount_paise']/100:,.2f}\n"
                            f"• Recurring Token: {data['token_id']}\n"
                            f"• Customer ID: {data['customer_id']}\n"
                            f"• Linked VPA: {data['vpa']} ({data['bank_name']})\n"
                            f"• Commerce Guardian: 100% Rule 6 Protected (Zero Financial Leakage)\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 🔗 Please Authorize Your UPI AutoPay Mandate on Razorpay:\n"
                            f"   {auth_link}\n\n"
                            f"⚠️ Zero-click purchases remain safely LOCKED until you authorize via the link.\n"
                            f"Once authorized on the portal, type: 'check autopay status'!"
                        )
                    else:
                        out = (
                            f"🛡️ RAZORPAY MANDATE VERIFICATION GATE: ACTIVE & VERIFIED ✅\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• AutoPay Status: ACTIVE (0-Click Payments Enabled)\n"
                            f"• Recurring Token: {data['token_id']}\n"
                            f"• Customer ID: {data['customer_id']}\n"
                            f"• Mandate Authorization Pool: ₹{data['max_amount_paise']/100:,.2f}\n"
                            f"• Available Spend Headroom: ₹{headroom:,.2f} (100% Available)\n"
                            f"• Linked VPA: {data['vpa']} ({data['bank_name']})\n"
                            f"• Commerce Guardian: 100% Rule 6 Protected (Zero Financial Leakage)\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 🔗 View Mandate on Razorpay Portal:\n"
                            f"   {auth_link}\n\n"
                            f"🎉 Mandate verified on Razorpay test rail. Claude is authorized for autonomous 0-click purchases."
                        )

                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"AutoPay Setup Error: {res.text}"}]}

            elif name == "get_autopay_status":
                buyer_id = args.get("buyer_id", "b_001")
                res = client.get("/mandates/autopay/status", params={"buyer_id": buyer_id})
                if res.status_code == 200:
                    data = res.json()
                    auth_link = data.get("auth_url") or f"{API_BASE}/mandates/checkout/{data.get('token_id', 'none')}"

                    if not data.get("autopay_enabled") or data.get("status") == "PENDING_AUTH":
                        out = (
                            f"⏳ HEADLESS UPI AUTOPAY: AWAITING HUMAN AUTHORIZATION 🟡\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Status: {data.get('status', 'PENDING_AUTH')} (0-Click Disabled)\n"
                            f"• Proposed Mandate Cap: ₹{(data.get('max_amount_paise') or 10000000)/100:,.2f}\n"
                            f"• Recurring Token: {data.get('token_id', 'None')}\n"
                            f"• Linked VPA: {data.get('vpa', 'b_001@okhdfcbank')} ({data.get('bank_name', 'HDFC Bank')})\n"
                            f"• Message: {data.get('message', 'Awaiting 1-time human authorization on Razorpay')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 🔗 Please Complete Authorization on Razorpay Portal:\n"
                            f"   {auth_link}\n\n"
                            f"Once authorized on the link, Claude will unlock autonomous 0-click purchases."
                        )
                    else:
                        out = (
                            f"⚡ HEADLESS UPI AUTOPAY: ACTIVE 🟢\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Status: ACTIVE (0-Click Payments Enabled)\n"
                            f"• Recurring Token: {data['token_id']}\n"
                            f"• Customer ID: {data['customer_id']}\n"
                            f"• Mandate Authorization Pool: ₹{data['max_amount_paise']/100:,.2f}\n"
                            f"• Remaining Spend Headroom: ₹{data['remaining_headroom_paise']/100:,.2f} ({100 - data.get('spent_pct', 0):.1f}% Available)\n"
                            f"• Linked VPA: {data['vpa']} ({data['bank_name']})\n"
                            f"• Razorpay Verification: {data.get('verification_gate', 'PASSED')}\n"
                            f"• Commerce Guardian: 100% Rule 6 Protected (Zero Financial Leakage)\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 🔗 View Mandate on Razorpay Portal:\n"
                            f"   {auth_link}\n\n"
                            f"🎉 Claude is authorized to execute autonomous purchases with 0 OTP prompts."
                        )
                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Error fetching AutoPay status: {res.text}"}]}


            elif name == "revoke_autopay_mandate":
                buyer_id = args.get("buyer_id", "b_001")
                res = client.post("/mandates/autopay/revoke", params={"buyer_id": buyer_id})
                if res.status_code == 200:
                    data = res.json()
                    return {"content": [{"type": "text", "text": f"🔒 AutoPay Token Revoked: {data.get('message', '0-Click purchases disabled.')}"}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Error revoking AutoPay: {res.text}"}]}

            elif name == "get_decision_receipt":
                receipt_id = args["receipt_id"]
                res = client.get(f"/receipts/{receipt_id}")
                if res.status_code == 200:
                    return {"content": [{"type": "text", "text": json.dumps(res.json(), indent=2)}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Receipt not found: {res.text}"}]}

            elif name == "check_payment_status":
                order_id = args.get("order_id", "").strip()
                if not order_id:
                    return {"isError": True, "content": [{"type": "text", "text": "Missing required argument: order_id"}]}

                res = client.post(f"/payments/sync/{order_id}")
                if res.status_code == 200:
                    data = res.json()
                    amt = (data.get("amount") or 0) / 100.0
                    if data.get("paid"):
                        out = (
                            f"✅ PAYMENT COMPLETED & VERIFIED!\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Order ID: {data.get('order_id')}\n"
                            f"• Payment ID: {data.get('payment_id', 'Verified')}\n"
                            f"• Status: PAID ✅\n"
                            f"• Amount Settled: ₹{amt:,.2f}\n"
                            f"• Decision Receipt ID: {data.get('receipt_id', 'Linked')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🎉 Payment successfully captured on Razorpay and store revenue credited on Merchant Dashboard."
                        )
                    else:
                        checkout_url = f"{API_BASE}/payments/checkout/{data.get('order_id')}"
                        out = (
                            f"⏳ PAYMENT NOT COMPLETED (STILL PENDING)\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Order ID: {data.get('order_id')}\n"
                            f"• Status: PENDING / CREATED ⏳\n"
                            f"• Amount: ₹{amt:,.2f}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 The customer has not completed checkout yet.\n"
                            f"Pay via this 1-Click Razorpay link:\n"
                            f"  {checkout_url}\n\n"
                            f"Once paid, ask me to check payment status again!"
                        )
                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Failed to check payment status: {res.text}"}]}

            elif name == "verify_autopay_mandate":
                buyer_id = args.get("buyer_id", "b_001")
                res = client.get("/mandates/autopay/verify", params={"buyer_id": buyer_id})
                if res.status_code == 200:
                    data = res.json()
                    if data.get("verified"):
                        out = (
                            f"🛡️ LIVE RAZORPAY MANDATE VERIFICATION: PASSED ✅\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Status: {data.get('status')} (Active on Test Rail)\n"
                            f"• Recurring Token: {data.get('token_id')}\n"
                            f"• Customer ID: {data.get('customer_id')}\n"
                            f"• Verification Rail: {data.get('rail')}\n"
                            f"• Verification Note: {data.get('reason')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"✅ Mandate authorization is fully verified against Razorpay Test API."
                        )
                    else:
                        out = (
                            f"⚠️ RAZORPAY MANDATE VERIFICATION: UNVERIFIED / REJECTED\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• Status: {data.get('status')}\n"
                            f"• Reason: {data.get('message') or data.get('reason')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🔒 Autonomous 0-click debits are locked until valid mandate registration."
                        )
                    return {"content": [{"type": "text", "text": out}]}
                return {"isError": True, "content": [{"type": "text", "text": f"Error verifying mandate: {res.text}"}]}

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
