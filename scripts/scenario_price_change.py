#!/usr/bin/env python3
"""
Demo Scenario 3 — Price Drift Mid-Flow (Beat 6)
Per docs/15_DEMO_SCENARIOS.md Beat 6.
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 3: Price Change Mid-Flow Detection")
    print("==================================================================")

    buyer_id = "b_001"
    merchant_id = "m_001"
    now = datetime.now(timezone.utc)

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Check Current Authoritative Price
        print("\n[1/3] Fetching HP-001 Catalog Details...")
        res = client.get("/catalog/products/HP-001")
        assert res.status_code == 200
        p = res.json()
        current_price = p["price"]
        print(f"  📦 HP-001 Authoritative Price: ₹{current_price/100:.2f} ({current_price} paise)")

        # Step 2: Simulate Buyer Cart Captured at Older Stale Price (e.g. ₹3,999 vs current ₹4,499)
        stale_observed_price = 399900
        print(f"\n[2/3] Submitting checkout intent with stale observed price ₹{stale_observed_price/100:.2f}...")
        intent_id = str(uuid.uuid4())
        res = client.post(
            "/guardian/evaluate",
            json={
                "intent_id": intent_id,
                "buyer_id": buyer_id,
                "merchant_id": merchant_id,
                "items": [
                    {
                        "sku": "HP-001",
                        "qty": 1,
                        "observed_price": stale_observed_price,
                        "catalog_version": 16,
                    }
                ],
                "requested_discount_pct": 0,
                "created_at": now.isoformat(),
                "expires_at": (now + timedelta(minutes=5)).isoformat(),
            },
        )
        assert res.status_code == 200
        data = res.json()
        print(f"  🛡️ Guardian Decision: {data['decision']}")
        print(f"  📜 Primary Reason: {data['primary_reason']}")
        assert data["decision"] == "REQUIRE_CONFIRMATION"

        # Step 3: Inspect Check Detail
        price_check = next((c for c in data["checks"] if c["name"] == "catalog.price_match"), None)
        assert price_check is not None
        print(f"  🔍 Price Match Detail: {price_check['detail']}")
        assert "price increased" in price_check["detail"].lower() or "increased" in price_check["detail"]

        print("\n🎉 SCENARIO 3 (PRICE DRIFT DETECTION) PASSED CLEANLY!\n")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
