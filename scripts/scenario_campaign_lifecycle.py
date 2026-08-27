#!/usr/bin/env python3
"""
Demo Scenario 4 — Campaign Lifecycle & Live Measurement
Per docs/15_DEMO_SCENARIOS.md Beat 7-8.
"""

import sys
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 4: Campaign Orchestrator Lifecycle")
    print("==================================================================")

    merchant_id = "m_001"

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Merchant Proposes Campaign
        print("\n[1/4] Proposing Campaign for Objective: 'Boost weekend sales for wireless headphones'...")
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
        print(f"\n[2/4] Activating Campaign '{proposal_id}'...")
        res_act = client.post(f"/campaign/{proposal_id}/activate")
        assert res_act.status_code == 200, f"Activation failed: {res_act.text}"
        act_data = res_act.json()
        print(f"  ✅ Campaign Status: {act_data['status']}")
        assert act_data["status"] == "ACTIVE"

        # Step 3: Check Live Status
        print(f"\n[3/4] Checking Campaign Status...")
        res_status = client.get(f"/campaign/{proposal_id}/status")
        assert res_status.status_code == 200
        status_data = res_status.json()
        print(f"  📊 Budget Total: ₹{status_data['budget']/100:.2f}")
        print(f"  📈 Attributed Orders: {status_data['orders_attributed']}")
        print(f"  💵 Attributed Revenue: ₹{status_data['revenue_attributed']/100:.2f}")

        # Step 4: Dashboard Aggregation Verification
        print("\n[4/4] Verifying Merchant Dashboard Revenue Aggregations...")
        res_dash = client.get(f"/dashboard/revenue?merchant_id={merchant_id}")
        assert res_dash.status_code == 200
        dash = res_dash.json()
        print(f"  💰 Total Store Revenue: ₹{dash['total_revenue']/100:.2f}")
        print(f"  📦 Total Paid Orders: {dash['order_count']}")
        print(f"  🎯 Upsell Attach Rate: {dash['upsell_attach_rate']*100:.0f}%")
        print(f"  🛡️ Blocked Threat Attempts: {dash['blocked_attempt_count']}")

        print("\n🎉 SCENARIO 4 (CAMPAIGN LIFECYCLE) PASSED CLEANLY!\n")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
