#!/usr/bin/env python3
"""
Price Tampering & Underpayment Attack Test
Demonstrates the Guardian's defense when an attacker tries to pay ₹1,000 for a ₹4,499 product.
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Price Tampering Test: Client attempts to pay ₹1,000 for ₹4,499 item")
    print("==================================================================")

    buyer_id = "b_001"
    merchant_id = "m_001"
    now = datetime.now(timezone.utc)

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Check authoritative catalog price
        print("\n[1/3] Fetching Authoritative Catalog Price for HP-001...")
        res = client.get("/catalog/products/HP-001")
        assert res.status_code == 200
        p = res.json()
        real_price = p["price"]  # 449900 paise (₹4,499.00)
        print(f"  📦 HP-001 Authoritative Price in DB: ₹{real_price/100:.2f} ({real_price} paise)")

        # Step 2: Attacker submits TransactionIntent claiming price is ₹1,000 (100,000 paise)
        tampered_price = 100000  # ₹1,000.00
        print(f"\n[2/3] Attacker submits intent claiming observed_price is ₹{tampered_price/100:.2f}...")
        intent_id = str(uuid.uuid4())
        res_intent = client.post(
            "/guardian/evaluate",
            json={
                "intent_id": intent_id,
                "buyer_id": buyer_id,
                "merchant_id": merchant_id,
                "items": [
                    {
                        "sku": "HP-001",
                        "qty": 1,
                        "observed_price": tampered_price,
                        "catalog_version": 17,
                    }
                ],
                "requested_discount_pct": 0,
                "created_at": now.isoformat(),
                "expires_at": (now + timedelta(minutes=5)).isoformat(),
            },
        )
        assert res_intent.status_code == 200
        data = res_intent.json()
        print(f"  🛡️ Guardian Decision: {data['decision']}")
        print(f"  📜 Primary Reason: {data['primary_reason']}")

        # Verify Guardian caught the price drift and required confirmation / blocked underpayment
        assert data["decision"] == "REQUIRE_CONFIRMATION", f"Expected REQUIRE_CONFIRMATION, got {data['decision']}"
        
        price_check = next((c for c in data["checks"] if c["name"] == "catalog.price_match"), None)
        assert price_check is not None
        print(f"  🔍 Price Match Check Result: {price_check['detail']}")
        print(f"  🔒 Result: Attacker cannot pay ₹1,000! Guardian requires confirmation at the authoritative ₹4,499 price.")

        # Step 3: Verify Decision Receipt captures the audit record
        print("\n[3/3] Inspecting Decision Receipt Audit Trail...")
        res_rec = client.get(f"/receipts/{data['receipt_id']}")
        assert res_rec.status_code == 200
        rec = res_rec.json()
        print(f"  🧾 Audit Receipt ID: {rec['receipt_id']}")
        print(f"  📋 Observed Total Recorded: ₹{rec['observed_total']/100:.2f}")
        print(f"  📋 Guardian Verification Decision: {rec['decision']}")

        print("\n🎉 PRICE TAMPERING DEFENSE TEST PASSED CLEANLY!\n")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
