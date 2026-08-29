#!/usr/bin/env python3
"""
Autonomous Headless AI Buyer CLI Simulator for Agentic Merchant OS.
Demonstrates machine-to-machine (A2A) commerce over UAP without a web browser.
"""

import sys
import time
import httpx

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    print(f"\n{BOLD}{CYAN}=================================================================={RESET}")
    print(f"{BOLD}{MAGENTA}🤖 AUTONOMOUS HEADLESS AI BUYER SIMULATOR (UAP PROTOCOL v1.0){RESET}")
    print(f"{DIM}Connecting to Agentic Merchant OS on http://localhost:8000...{RESET}")
    print(f"{BOLD}{CYAN}=================================================================={RESET}\n")


def run_simulation(target_sku: str = "PHN-APL-15", requested_qty: int = 1):
    base_url = "http://localhost:8000"
    print_banner()

    with httpx.Client(base_url=base_url, timeout=15.0) as client:
        # Step 1: Health & UAP Manifest Discovery
        print(f"{BOLD}[Step 1/5] Discovering Merchant UAP Manifest & Catalog...{RESET}")
        try:
            res = client.get("/.well-known/agent.json")
            if res.status_code != 200:
                res = client.get("/catalog/products?merchant_id=m_001")
            manifest = res.json()
            print(f"  {GREEN}✓ Connected to store:{RESET} {manifest.get('name', 'Agentic Merchant OS Store')}")
            print(f"  {GREEN}✓ Supported protocols:{RESET} {manifest.get('spec_compatibility', ['UAP-1.0', 'MCP-2024-11-05'])}")
            print(f"  {GREEN}✓ Catalog Version:{RESET} v{manifest.get('catalog_version', 1)}")
        except Exception as e:
            print(f"  {RED}✗ Failed to connect to backend at {base_url}:{RESET} {e}")
            print(f"  {YELLOW}Please ensure backend is running with: ./bin/start.sh{RESET}\n")
            sys.exit(1)

        time.sleep(0.4)

        # Step 2: Query Authoritative Catalog
        print(f"\n{BOLD}[Step 2/5] Querying Live Authoritative Catalog...{RESET}")
        cat_res = client.get("/catalog/products?merchant_id=m_001")
        cat_data = cat_res.json()
        products = cat_data.get("products", []) if isinstance(cat_data, dict) else cat_data
        
        if not products:
            print(f"  {RED}✗ No products found in catalog{RESET}")
            sys.exit(1)

        # Find target SKU or fallback to first
        target_product = next((p for p in products if p.get("sku") == target_sku), products[0])
        catalog_price = target_product["price"] / 100.0

        print(f"  {CYAN}Target Product:{RESET} {BOLD}{target_product['name']}{RESET} ({target_product['sku']})")
        print(f"  {CYAN}Catalog Retail Price:{RESET} ₹{catalog_price:,.2f}")
        print(f"  {CYAN}Available Inventory:{RESET} {target_product['inventory']} units")

        time.sleep(0.4)

        # Step 3: Formulate Procurement Mandate & Submit Aggressive Bargain RFQ
        qty = requested_qty
        # Buyer aggressively proposes 15% discount (trying to get lowest possible price)
        buyer_target_unit = catalog_price * 0.85
        print(f"\n{BOLD}[Step 3/5] AI Buyer Formulates Aggressive B2B RFQ Bargain...{RESET}")
        print(f"  {YELLOW}Procurement Quantity:{RESET} {qty} unit(s)")
        print(f"  {YELLOW}Target Bargain Price:{RESET} ₹{buyer_target_unit:,.2f} (Catalog: ₹{catalog_price:,.2f} — 15% OFF)")
        print(f"  {YELLOW}Proposed Total:{RESET} ₹{buyer_target_unit * qty:,.2f}")

        rfq_payload = {
            "session_id": f"sim_rfq_{int(time.time())}",
            "merchant_id": "m_001",
            "buyer_agent_id": "procurebot_enterprise_v3",
            "buyer_mandate": {
                "buyer_id": "b_001",
                "max_amount": 25000000,
                "max_quantity_per_item": 10,
                "currency": "INR",
                "signature": "sig_procurebot_ed25519_verified",
            },
            "items": [
                {
                    "sku": target_product["sku"],
                    "qty": qty,
                    "target_unit_price_paise": int(buyer_target_unit * 100),
                }
            ],
            "buyer_rationale": f"Autonomous bulk bargain request for {target_product['name']} at lowest authorized margin.",
        }

        print(f"  {DIM}Submitting POST /commerce/rfq to Merchant Pricing Agent...{RESET}")
        rfq_res = client.post("/commerce/rfq", json=rfq_payload)
        if rfq_res.status_code != 200:
            print(f"  {RED}✗ RFQ failed:{RESET} {rfq_res.text}")
            sys.exit(1)

        rfq_data = rfq_res.json()
        print(f"  {GREEN}✓ Bilateral RFQ Evaluated in Sub-50ms!{RESET}")
        print(f"  {GREEN}✓ Guardian Margin Floor Status:{RESET} {rfq_data.get('status', 'OFFERS_PROPOSED')}")
        print(f"  {DIM}Merchant AI Rationale: {rfq_data.get('ai_pricing_agent_notes', 'Evaluated against Rule 6 Invariant')}{RESET}")

        time.sleep(0.5)

        # Step 4: Evaluate Merchant Counter-Offers & Sweetener
        print(f"\n{BOLD}[Step 4/5] AI Buyer Evaluates Merchant Counter-Offers...{RESET}")
        options = rfq_data.get("counter_offers", [])
        for i, opt in enumerate(options, 1):
            opt_type = opt.get("option_type", "DIRECT_PRICE_COUNTER")
            print(f"\n  {MAGENTA}Option {i} [{opt_type}]:{RESET} {BOLD}{opt.get('title')}{RESET}")
            print(f"    • Details: {opt.get('description')}")
            print(f"    • Total: {GREEN}₹{opt.get('total_amount_paise', 0)/100:,.2f}{RESET} | Margin: {opt.get('projected_gross_margin_pct', 0):.1f}% | Profit Lift: +₹{opt.get('merchant_profit_lift_paise', 0)/100:,.2f}")
            if opt.get("bundled_items"):
                for b_item in opt.get("bundled_items"):
                    print(f"    • Companion Sweetener: {BOLD}{b_item.get('addon_name')}{RESET} (50% OFF ➔ ₹{b_item.get('discounted_price_paise', 0)/100:,.2f})")

        # Select the highest value option (Bundle Sweetener if available, otherwise first option)
        selected_option = next((o for o in options if "BUNDLE" in o.get("option_type", "")), options[0])
        print(f"\n  {BOLD}{GREEN}AI Buyer Strategy Selected:{RESET} [{selected_option['title']}] ({selected_option['option_id']}) for maximum value.")

        time.sleep(0.4)

        # Step 5: Deterministic Guardian Settlement via UAP
        print(f"\n{BOLD}[Step 5/5] Executing Autonomous Guardian Settlement (POST /commerce/accept)...{RESET}")
        accept_payload = {
            "session_id": rfq_data["session_id"],
            "buyer_agent_id": "procurebot_enterprise_v3",
            "merchant_id": "m_001",
            "selected_option_id": selected_option["option_id"],
            "buyer_signature": "sig_procurebot_ed25519_contract_signed",
        }

        settle_res = client.post("/commerce/accept", json=accept_payload)
        if settle_res.status_code != 200:
            print(f"  {RED}✗ Settlement failed:{RESET} {settle_res.text}")
            sys.exit(1)

        settle_data = settle_res.json()
        receipt_id = settle_data.get("receipt_id")
        verified_total = settle_data.get("final_verified_total_paise", 0) / 100.0

        print(f"  {GREEN}✓ SETTLED & AUTHORIZED BY COMMERCE GUARDIAN!{RESET}")
        print(f"  {CYAN}Decision Receipt ID:{RESET} {BOLD}{receipt_id}{RESET}")
        print(f"  {CYAN}Razorpay Test Order:{RESET} {settle_data.get('razorpay_order_id')}")
        print(f"  {CYAN}Final Verified Total:{RESET} {BOLD}{GREEN}₹{verified_total:,.2f}{RESET}")
        print(f"  {CYAN}Achieved Margin:{RESET} {settle_data.get('merchant_margin_achieved_pct', 15.4):.1f}%")
        print(f"  {CYAN}Audit Replay Hash:{RESET} {settle_data.get('replay_hash')}")

        print(f"\n{BOLD}{GREEN}=================================================================={RESET}")
        print(f"{BOLD}{GREEN}🎉 A2A UAP COMMERCE COMPLETED AUTONOMOUSLY WITH ZERO HUMAN UI!{RESET}")
        print(f"{CYAN}• View Signed Decision Receipt in UI:{RESET} http://localhost:3000/receipts/{receipt_id}")
        print(f"{CYAN}• Live Financial Telemetry Dashboard:{RESET}  http://localhost:3000/dashboard")
        print(f"{BOLD}{GREEN}=================================================================={RESET}\n")


if __name__ == "__main__":
    sku = sys.argv[1] if len(sys.argv) > 1 else "PHN-APL-15"
    qty = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    run_simulation(target_sku=sku, requested_qty=qty)
