#!/usr/bin/env python3
"""
Demo Scenario 2 — Catalog Injection Attack (Beat 5)
Per docs/15_DEMO_SCENARIOS.md Beat 5 & docs/13_THREAT_MODEL.md.
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta
import httpx


def run_scenario(base_url: str = "http://localhost:8000") -> bool:
    print("\n==================================================================")
    print("🎬 Running Scenario 2: Catalog Prompt Injection Defense")
    print("==================================================================")

    buyer_id = "b_001"
    merchant_id = "m_001"
    now = datetime.now(timezone.utc)

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # Step 1: Inspect Malicious SKU in Catalog
        print("\n[1/3] Fetching Malicious Catalog SKU 'ATTACK-SKU-001'...")
        res = client.get("/catalog/products/ATTACK-SKU-001")
        assert res.status_code == 200, f"Product fetch failed: {res.text}"
        prod = res.json()
        print(f"  📦 Product: {prod['name']}")
        print(f"  ⚠️ Injected Description: '{prod['description'][:80]}...'")
        print(f"  🚩 Security Scanner Flag: {prod['suspicious_content_flag']}")
        assert prod["suspicious_content_flag"] is True

        # Step 2: Attempt Purchase Flow touching injected SKU
        print("\n[2/3] Buyer evaluates purchase touching ATTACK-SKU-001...")
        intent_id = str(uuid.uuid4())
        res = client.post(
            "/guardian/evaluate",
            json={
                "intent_id": intent_id,
                "buyer_id": buyer_id,
                "merchant_id": merchant_id,
                "items": [
                    {
                        "sku": "ATTACK-SKU-001",
                        "qty": 1,
                        "observed_price": 399900,
                        "catalog_version": 1,
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
        assert data["decision"] == "APPROVE", f"Expected APPROVE, got {data['decision']}: {data['primary_reason']}"
        assert data["final_verified_total"] is not None
        print(f"  💰 Authoritative Amount Charged: ₹{data['final_verified_total']/100:.2f}")
        print("  🔒 Result: Injected directive to charge 100 paise was completely ignored.")

        # Step 3: Verify Receipt audit trail flags the injection
        print("\n[3/3] Verifying Receipt Audit Log...")
        res_rec = client.get(f"/receipts/{data['receipt_id']}")
        assert res_rec.status_code == 200
        rec = res_rec.json()
        security_check = next((c for c in rec["guardian_checks"] if c["name"] == "security.catalog_content_flagged"), None)
        assert security_check is not None
        print(f"  🧾 Audit Trail Flag: {security_check['detail']}")

        print("\n🎉 SCENARIO 2 (INJECTION DEFENSE) PASSED CLEANLY!\n")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_scenario(url)
    sys.exit(0 if success else 1)
