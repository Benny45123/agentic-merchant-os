#!/usr/bin/env python3
"""
Scenario 7 — Autonomous A2A Dynamic Negotiation (Reverse Auction) & Guardian Settlement
Demonstrates:
1. External AI Buyer Agent submits Request for Quote (RFQ) for 3x HP-001 @ ₹4,100 (Catalog ₹4,499).
2. Merchant Pricing Agent formulates 2 margin-safe counter-offers (Price compromise & Bundle Sweetener).
3. Buyer Agent accepts Bundle Sweetener (Headphones + 3x Travel Cases @ 50% off).
4. Deterministic Commerce Guardian authorizes the negotiated contract & creates Razorpay Order.
5. Replay Engine proves 100% mathematical auditability.
6. Adversarial Defense: Rejects predatory buyer offer of ₹3,200 (< 15% margin floor).
"""

import sys
import uuid
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 7: Autonomous A2A Dynamic Negotiation")
    print("==================================================================")

    buyer_agent_id = "ai_buyer_procure_agent_%s" % str(uuid.uuid4())[:6]
    merchant_id = "m_001"

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Submit RFQ proposing ₹4,100.00 for 3x HP-001
        print("\n[1/5] Submitting Autonomous RFQ: 3x AeroSound Headphones (HP-001 @ ₹4,100.00)...")
        print("  🏷️ Catalog Unit Price: ₹4,499.00 | Buyer Target: ₹4,100.00 (8.9% discount)")

        rfq_payload = {
            "buyer_agent_id": buyer_agent_id,
            "merchant_id": merchant_id,
            "buyer_mandate": {
                "buyer_id": "b_001",
                "max_amount": 2000000,
                "max_quantity_per_item": 10,
                "currency": "INR",
                "signature": "sig_ed25519_procurement_rfq_mandate",
            },
            "items": [
                {
                    "sku": "HP-001",
                    "qty": 3,
                    "target_unit_price_paise": 410000,  # ₹4,100.00
                }
            ],
            "buyer_rationale": "Enterprise bulk procurement order",
        }

        rfq_res = client.post("/commerce/rfq", json=rfq_payload)
        assert rfq_res.status_code == 200, "RFQ failed: %s" % rfq_res.text
        rfq_data = rfq_res.json()

        print("  📥 Negotiation Status:     %s" % rfq_data["status"])
        print("  🛡️ Merchant Margin Floor:  %s%%" % rfq_data["minimum_margin_floor_pct"])
        print("  💡 Pricing Agent Notes:    %s" % rfq_data["ai_pricing_agent_notes"])
        assert rfq_data["status"] == "OFFERS_PROPOSED"
        assert len(rfq_data["counter_offers"]) >= 2

        # Step 2: Inspect Formulated Counter-Offers
        print("\n[2/5] Inspecting Formulated Bilateral Counter-Offers:")
        for opt in rfq_data["counter_offers"]:
            print("  • [%s] %s" % (opt["option_id"], opt["title"]))
            print("    - Total: ₹%.2f | Margin: %.1f%% | Merchant Lift: +₹%.2f" % (
                opt["total_amount_paise"] / 100.0,
                opt["projected_gross_margin_pct"],
                opt["merchant_profit_lift_paise"] / 100.0,
            ))
            assert opt["margin_floor_satisfied"] is True

        # Step 3: Accept Option 2 (Bundle Sweetener)
        session_id = rfq_data["session_id"]
        print("\n[3/5] Buyer Agent Accepting Option 2 (OPT_BUNDLE_SWEETENER)...")

        accept_payload = {
            "session_id": session_id,
            "buyer_agent_id": buyer_agent_id,
            "merchant_id": merchant_id,
            "selected_option_id": "OPT_BUNDLE_SWEETENER",
            "buyer_signature": "sig_ed25519_contract_accepted",
        }

        accept_res = client.post("/commerce/accept", json=accept_payload)
        assert accept_res.status_code == 200, "Accept failed: %s" % accept_res.text
        settle_data = accept_res.json()

        print("  🛡️ Guardian Decision:      %s" % settle_data["guardian_decision"])
        print("  💰 Final Verified Total:   ₹%.2f" % (settle_data["final_verified_total_paise"] / 100.0))
        print("  📈 Achieved Margin:        %.1f%%" % settle_data["merchant_margin_achieved_pct"])
        print("  🧾 Decision Receipt ID:    %s" % settle_data["receipt_id"])
        print("  💳 Razorpay Order ID:      %s" % settle_data["razorpay_order_id"])
        assert settle_data["guardian_decision"] in ["APPROVE", "REQUIRE_CONFIRMATION"]

        # Step 4: Verify Replay Audit
        receipt_id = settle_data["receipt_id"]
        print("\n[4/5] Verifying Immutable Replay Audit for Receipt '%s'..." % receipt_id)
        replay_res = client.post("/receipts/%s/replay" % receipt_id)
        assert replay_res.status_code == 200
        replay_data = replay_res.json()
        assert replay_data["matches_original"] is True, "Replay must mathematically reproduce Guardian approval"
        print("  🔒 Replay Match:           ✅ 100% MATHEMATICAL MATCH")

        # Step 5: Adversarial Test: Predatory Buyer Offer (< 15% margin floor)
        print("\n[5/5] Testing Adversarial Defense: Predatory Offer of ₹3,200.00 (Breaches Margin Floor)...")
        bad_rfq_payload = {
            "buyer_agent_id": buyer_agent_id,
            "merchant_id": merchant_id,
            "buyer_mandate": {
                "buyer_id": "b_001",
                "max_amount": 2000000,
                "max_quantity_per_item": 10,
                "currency": "INR",
                "signature": "sig_bad_rfq",
            },
            "items": [
                {
                    "sku": "HP-001",
                    "qty": 3,
                    "target_unit_price_paise": 320000,  # ₹3,200 (Cost is ₹3,000 -> 6.25% margin < 15%)
                }
            ],
        }

        bad_res = client.post("/commerce/rfq", json=bad_rfq_payload)
        assert bad_res.status_code == 200
        bad_data = bad_res.json()
        print("  🛡️ Pricing Defense Result: %s" % bad_data["status"])
        print("  📜 Rejection Reason:       %s" % bad_data["reason"])
        assert bad_data["status"] == "REJECTED_MARGIN_FLOOR"
        print("  ✅ Predatory price successfully contained by deterministic margin floor!")

        print("\n==================================================================")
        print("🎉 SCENARIO 7 (A2A DYNAMIC NEGOTIATION) PASSED CLEANLY!")
        print("==================================================================")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
