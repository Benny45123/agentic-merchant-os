#!/usr/bin/env python3
"""
Demo Scenario 4 — Campaign Lifecycle & Live Measurement
Per docs/15_DEMO_SCENARIOS.md Beat 7-8.
"""

import sys
import uuid
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 4: Campaign Orchestrator Lifecycle")
    print("==================================================================")

    merchant_id = "m_001"
    session_id = f"sess_camp_demo_{uuid.uuid4().hex[:8]}"

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Merchant Proposes Campaign
        print("\n[1/5] Proposing Campaign for Objective: 'Boost weekend sales for wireless headphones'...")
        res = client.post(
            "/campaign/propose",
            json={
                "merchant_id": merchant_id,
                "objective": "Boost weekend sales for wireless headphones",
            },
        )
        assert res.status_code == 200, f"Propose failed: {res.text}"
        proposal = res.json()
        print(f"  💡 Proposed Discount: {proposal['discount_pct']}%")
        print(f"  💰 Proposed Budget: ₹{proposal['budget']/100:.2f}")
        print(f"  🛡️ Guardian Proposal Decision: {proposal['guardian_decision']['decision']}")
        print(f"  📝 LLM Rationale: {proposal['rationale']}")
        assert proposal["guardian_decision"]["decision"] in ["APPROVE", "REQUIRE_CONFIRMATION"]

        proposal_id = proposal["proposal_id"]

        # Step 2: Activate Campaign
        print(f"\n[2/5] Activating Campaign '{proposal_id}'...")
        res_act = client.post(f"/campaign/{proposal_id}/activate")
        assert res_act.status_code == 200, f"Activation failed: {res_act.text}"
        act_data = res_act.json()
        print(f"  ✅ Campaign Status: {act_data['status']}")
        assert act_data["status"] == "ACTIVE"

        # Step 3: Execute a Promotional Purchase in Chat with Active Campaign Discount Applied
        print(f"\n[3/5] Simulating Buyer Purchase with Active {proposal['discount_pct']}% Campaign Discount...")
        # 3a. Add Headphones to cart
        chat_res = client.post(
            "/agent/chat",
            json={
                "session_id": session_id,
                "buyer_id": "b_001",
                "message": "I want to buy AeroSound Wireless Headphones",
            },
        )
        assert chat_res.status_code == 200

        # 3b. Build Checkout Intent (Guardian discovers active campaign discount)
        checkout_res = client.post(
            "/agent/checkout-intent",
            json={
                "session_id": session_id,
                "buyer_id": "b_001",
                "merchant_id": merchant_id,
            },
        )
        assert checkout_res.status_code == 200
        checkout_data = checkout_res.json()
        final_total = checkout_data["decision"]["final_verified_total"]
        order_id = checkout_data["razorpay_order"]["order_id"]
        print(f"  🏷️ Original Catalog Price: ₹4,499.00")
        print(f"  🎉 Campaign Discounted Price: ₹{final_total/100:.2f} ({proposal['discount_pct']}% OFF)")
        print(f"  🛡️ Guardian Decision: {checkout_data['decision']['decision']}")
        print(f"  💳 Razorpay Order Created: {order_id}")

        # 3c. Capture Payment via Razorpay
        pay_res = client.post(
            "/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": f"pay_sim_{uuid.uuid4().hex[:10]}",
                "razorpay_signature": "sig_sim_valid_payment",
            },
        )
        assert pay_res.status_code == 200, f"Payment capture failed: {pay_res.text}"
        print(f"  ✅ Payment Captured & Attributed to Campaign '{proposal_id}'")

        # Step 4: Check Campaign Live Attribution Status
        print(f"\n[4/5] Checking Campaign Live Telemetry...")
        res_status = client.get(f"/campaign/{proposal_id}/status")
        assert res_status.status_code == 200
        status_data = res_status.json()
        print(f"  📊 Budget Cap: ₹{status_data['budget']/100:.2f}")
        print(f"  📈 Campaign Status: {status_data['status']}")
        print(f"  📈 Attributed Orders: {status_data['orders_attributed']}")
        print(f"  💵 Attributed Revenue: ₹{status_data['revenue_attributed']/100:.2f}")
        assert status_data["status"] == "ACTIVE"
        assert status_data["budget"] > 0

        # Step 5: Dashboard Aggregation Verification
        print("\n[5/5] Verifying Merchant Dashboard Revenue Aggregations...")
        res_dash = client.get(f"/dashboard/revenue?merchant_id={merchant_id}")
        assert res_dash.status_code == 200
        dash = res_dash.json()
        print(f"  💰 Total Store Revenue: ₹{dash['total_revenue']/100:.2f}")
        print(f"  🎯 Campaign Revenue: ₹{dash['campaign_revenue']/100:.2f}")
        print(f"  📦 Total Paid Orders: {dash['order_count']}")
        print(f"  🎯 Upsell Attach Rate: {dash['upsell_attach_rate']*100:.0f}%")
        print(f"  🛡️ Blocked Threat Attempts: {dash['blocked_attempt_count']}")
        assert dash["campaign_revenue"] > 0, "Campaign revenue must be greater than 0"

        print("\n🎉 SCENARIO 4 (CAMPAIGN LIFECYCLE & LIVE REVENUE ATTRIBUTION) PASSED CLEANLY!\n")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
