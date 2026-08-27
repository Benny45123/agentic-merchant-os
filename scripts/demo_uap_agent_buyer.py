#!/usr/bin/env python3
"""
Autonomous External AI Buyer Agent (UAP Protocol Demonstration)
1. Auto-discovers store capabilities via `GET /.well-known/agent.json`.
2. Locates Sport Earbuds (HP-002).
3. Executes a headless Agent-to-Agent (A2A) purchase via `POST /agent/v1/machine-purchase`.
4. Obtains Guardian Authorization and Razorpay Test Order with zero human UI.
"""

import sys
import httpx


def execute_uap_machine_purchase(base_url="http://localhost:8000"):
    print("==================================================================")
    print("🤖 EXTERNAL AI BUYER AGENT: Initializing UAP Purchase Flow")
    print("==================================================================")

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Auto-discover store manifest via UAP
        print("\n[Step 1] Fetching machine manifest from /.well-known/agent.json...")
        res_manifest = client.get("/.well-known/agent.json")
        assert res_manifest.status_code == 200, "Manifest discovery failed: %s" % res_manifest.text
        manifest = res_manifest.json()
        print("  ✅ Store Protocol: %s (%s)" % (manifest['protocol'], ", ".join(manifest['spec_compatibility'])))
        print("  🏪 Store Name: %s (Merchant ID: %s)" % (manifest['name'], manifest['merchant_id']))
        print("  🛠️ Discovered MCP Tools: %s" % [t['name'] for t in manifest['tools']])

        # Step 2: Query Catalog to find Earbuds
        print("\n[Step 2] Querying catalog for 'earbuds'...")
        res_cat = client.get("/catalog/products", params={"q": "earbuds", "merchant_id": manifest["merchant_id"]})
        assert res_cat.status_code == 200
        products = res_cat.json().get("products", [])
        earbuds = next((p for p in products if "earbud" in p["name"].lower() or p["sku"] == "HP-002"), None)
        assert earbuds is not None, "Could not find earbuds in store catalog"
        print("  📦 Found Product: %s (SKU: `%s`)" % (earbuds['name'], earbuds['sku']))
        print("  💰 Authoritative Price: ₹%.2f" % (earbuds['price'] / 100.0))
        print("  📊 Inventory Available: %s units" % earbuds['inventory'])

        # Step 3: Execute Headless Machine Purchase
        print("\n[Step 3] Submitting Headless Signed Mandate & Intent to /agent/v1/machine-purchase...")
        machine_payload = {
            "buyer_agent_id": "ai_agent_procure_alpha_001",
            "buyer_mandate": {
                "buyer_id": "b_001",
                "max_amount": 1000000,          # ₹10,000 max mandate spend
                "max_quantity_per_item": 5,     # Max 5 units
                "currency": "INR",
                "signature": "sig_ed25519_procurement_bot_attestation"
            },
            "purchase_items": [
                {
                    "sku": earbuds["sku"],
                    "qty": 1,
                    "observed_price": earbuds["price"],
                    "catalog_version": earbuds["catalog_version"],
                }
            ],
            "agent_callback_url": "https://ai-buyer.internal/webhook/order-confirmed"
        }

        res_purchase = client.post("/agent/v1/machine-purchase", json=machine_payload)
        assert res_purchase.status_code == 200, "Purchase failed: %s" % res_purchase.text
        purchase_data = res_purchase.json()

        print("\n==================================================================")
        print("🎉 HEADLESS AGENT-TO-AGENT (A2A) PURCHASE COMPLETED SUCCESSFULLY!")
        print("==================================================================")
        print("  🛡️ Guardian Decision:      %s" % purchase_data['guardian_decision'])
        print("  📜 Guardian Reason:        %s" % purchase_data['reason'])
        print("  💰 Final Verified Amount:  ₹%.2f" % (purchase_data['final_verified_total'] / 100.0))
        print("  🧾 Decision Receipt ID:    %s" % purchase_data['receipt_id'])
        print("  💳 Razorpay Order ID:      %s" % purchase_data['razorpay_order_id'])
        print("  🔒 Audit Replay Hash:      %s" % purchase_data['replay_hash'])
        print("==================================================================")
        return purchase_data


def run_scenario(base_url="http://localhost:8000"):
    """Wrapper to integrate with master scenario runner."""
    try:
        data = execute_uap_machine_purchase(base_url)
        return data.get("guardian_decision") == "APPROVE"
    except Exception as e:
        print("❌ UAP Machine Purchase Scenario Failed: %s" % e)
        return False


if __name__ == "__main__":
    execute_uap_machine_purchase()
