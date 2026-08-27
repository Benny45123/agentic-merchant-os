#!/usr/bin/env python3
"""
Demo Scenario 1 — The Happy Path (Discover -> Upsell -> Checkout -> Pay -> Receipt)
Per docs/15_DEMO_SCENARIOS.md Beat 1-4.
"""

import sys
import uuid
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 1: Happy Path (Discover -> Upsell -> Pay -> Receipt)")
    print("==================================================================")

    session_id = f"demo_session_happy_{uuid.uuid4().hex[:8]}"
    buyer_id = "b_001"
    merchant_id = "m_001"

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Health Check
        print("\n[1/5] Checking Backend Health...")
        res = client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("  ✅ Backend is healthy:", res.json())

        # Step 2: Chat & Discover Headphones
        print("\n[2/5] Buyer chats: 'Add headphones to my cart'...")
        res = client.post(
            "/agent/chat",
            json={
                "session_id": session_id,
                "buyer_id": buyer_id,
                "message": "Add headphones HP-001 to my cart",
            },
        )
        assert res.status_code == 200, f"Chat failed: {res.text}"
        chat_data = res.json()
        print(f"  🤖 Agent Reply: {chat_data['reply']}")
        print(f"  🛒 Cart Subtotal: ₹{chat_data['cart']['subtotal']/100:.2f}")
        print(f"  💡 Recommendations Received: {len(chat_data['recommendations'])}")
        assert len(chat_data["cart"]["items"]) == 1
        assert len(chat_data["recommendations"]) > 0

        # Step 3: Accept Warranty Upsell
        print("\n[3/5] Buyer accepts warranty recommendation...")
        res = client.post(
            "/agent/chat",
            json={
                "session_id": session_id,
                "buyer_id": buyer_id,
                "message": "Yes, please add the warranty WRNTY-1Y too",
            },
        )
        assert res.status_code == 200
        chat_data2 = res.json()
        print(f"  🤖 Agent Reply: {chat_data2['reply']}")
        print(f"  🛒 Cart Total: ₹{chat_data2['cart']['subtotal']/100:.2f} (2 items)")
        assert len(chat_data2["cart"]["items"]) == 2

        # Step 4: Checkout Intent (Guardian Evaluation)
        print("\n[4/5] Initiating Checkout Intent -> Guardian Evaluation...")
        res = client.post(
            "/agent/checkout-intent",
            json={
                "session_id": session_id,
                "buyer_id": buyer_id,
                "merchant_id": merchant_id,
            },
        )
        assert res.status_code == 200, f"Checkout intent failed: {res.text}"
        checkout_data = res.json()
        decision = checkout_data["decision"]
        print(f"  🛡️ Guardian Decision: {decision['decision']}")
        print(f"  📜 Primary Reason: {decision['primary_reason']}")
        print(f"  💰 Final Verified Total: ₹{decision['final_verified_total']/100:.2f}")
        print(f"  🧾 Decision Receipt ID: {decision['receipt_id']}")
        assert decision["decision"] == "APPROVE"
        assert checkout_data["razorpay_order"] is not None

        order_id = checkout_data["razorpay_order"]["order_id"]

        # Step 5: Simulate Payment Verification & Final Receipt Inspection
        print("\n[5/5] Completing Razorpay Payment Verification & Inspecting Audit Receipt...")
        res = client.post(
            "/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": f"pay_test_{order_id[-8:]}",
                "razorpay_signature": "mock_signature_test",
            },
        )
        # Verify receipt endpoint
        receipt_id = decision["receipt_id"]
        res_receipt = client.get(f"/receipts/{receipt_id}")
        assert res_receipt.status_code == 200, f"Get receipt failed: {res_receipt.text}"
        receipt = res_receipt.json()
        print(f"  ✅ Immutable Audit Receipt Verified:")
        print(f"     - Decision: {receipt['decision']}")
        print(f"     - Checks Passed: {len(receipt['guardian_checks'])}")
        print(f"     - Items Snapshotted: {len(receipt['items_snapshot'])}")

        print("\n🎉 SCENARIO 1 PASSED CLEANLY!\n")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
