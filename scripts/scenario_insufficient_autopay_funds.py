#!/usr/bin/env python3
"""
Scenario 6 — Insufficient Autopay Funds & Mandate Spending Limit Exceeded (Graceful Failure Handling)
Demonstrates the Guardian intercepting an order where the buyer does not have enough
authorized funds in their Razorpay Autopay / e-Mandate ceiling.
"""

import sys
import uuid
from datetime import datetime, timezone
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 6: Insufficient Autopay Funds / Mandate Breach")
    print("==================================================================")

    buyer_id = "b_autopay_budget_limited_%s" % str(uuid.uuid4())[:8]
    merchant_id = "m_001"
    autopay_spend_limit_paise = 150000  # ₹1,500.00 Autopay Ceiling

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Declare an Autopay e-Mandate with a ₹1,500.00 spending ceiling
        print("\n[1/4] Registering Razorpay Autopay e-Mandate for Buyer '%s'..." % buyer_id)
        print("  💳 Autopay Spend Limit: ₹%.2f (150,000 paise)" % (autopay_spend_limit_paise / 100.0))

        mandate_res = client.post(
            "/mandate",
            params={"buyer_id": buyer_id},
            json={
                "max_amount": autopay_spend_limit_paise,
                "max_quantity_per_item": 5,
                "allowed_categories": ["audio", "accessories"],
                "allowed_merchants": [merchant_id],
                "currency": "INR",
                "expires_at": "2030-01-01T00:00:00Z",
                "confirmation_required_above": 100000,  # ₹1,000
                "signature": "sig_ed25519_autopay_limit_test",
            },
        )
        assert mandate_res.status_code in [200, 201], "Mandate registration failed: %s" % mandate_res.text
        print("  ✅ Razorpay Autopay Mandate Active (Max Balance Cap: ₹1,500.00)")

        # Step 2: Attempt to purchase ₹4,499.00 Headphones (HP-001)
        print("\n[2/4] Attempting to purchase AeroSound Headphones (HP-001 @ ₹4,499.00)...")
        intent_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        intent_payload = {
            "intent_id": intent_id,
            "buyer_id": buyer_id,
            "merchant_id": merchant_id,
            "items": [
                {
                    "sku": "HP-001",
                    "qty": 1,
                    "observed_price": 449900,  # ₹4,499.00
                    "catalog_version": 1,
                }
            ],
            "requested_discount_pct": 0,
            "created_at": now_iso,
            "expires_at": "2030-01-01T00:00:00Z",
        }

        eval_res = client.post("/guardian/evaluate", json=intent_payload)
        assert eval_res.status_code == 200, "Guardian evaluation failed: %s" % eval_res.text
        decision = eval_res.json()

        # Step 3: Assert Guardian BLOCKED the transaction gracefully
        print("\n[3/4] Evaluating Guardian Containment & Failure Handling...")
        print("  🛡️ Guardian Decision: %s" % decision["decision"])
        print("  📜 Primary Reason:   %s" % decision["primary_reason"])
        print("  💳 Razorpay Order:    %s" % decision.get("razorpay_order"))

        # Strict Security Assertions
        assert decision["decision"] == "BLOCK", "Expected Guardian to BLOCK due to insufficient Autopay funds"
        assert decision["razorpay_order"] is None, "Razorpay Order MUST NOT be created on insufficient funds!"
        assert "exceeds" in decision["primary_reason"].lower() or "limit" in decision["primary_reason"].lower()

        # Verify exact failing check
        failing_check = next((c for c in decision["checks"] if c["name"] == "mandate.max_amount"), None)
        assert failing_check is not None, "Expected mandate.max_amount check to be evaluated"
        assert failing_check["passed"] is False, "Expected mandate.max_amount check to FAIL"
        print("  🔍 Failed Check Detail: %s" % failing_check["detail"])

        # Step 4: Replay Audit Verification
        receipt_id = decision["receipt_id"]
        print("\n[4/4] Verifying Immutable Decision Receipt Replay Audit (%s)..." % receipt_id)
        replay_res = client.post("/receipts/%s/replay" % receipt_id)
        assert replay_res.status_code == 200
        replay_data = replay_res.json()
        assert replay_data["matches_original"] is True, "Replay must mathematically reproduce the BLOCK decision"
        assert replay_data["replay_decision"] == "BLOCK"
        print("  🔒 Replay Verification: ✅ 100% MATCH (Original: BLOCK == Replay: BLOCK)")

        print("\n==================================================================")
        print("🎉 SCENARIO 6 (INSUFFICIENT AUTOPAY FUNDS) PASSED CLEANLY!")
        print("==================================================================")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
