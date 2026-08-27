import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.seed import DEMO_BUYER_ID, seed_data


@pytest.mark.asyncio
async def test_uap_agent_manifest_discovery(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/.well-known/agent.json")
        assert res.status_code == 200
        data = res.json()
        assert data["protocol"] == "UAP-1.0"
        assert "submit_machine_purchase" in [t["name"] for t in data["tools"]]
        assert len(data["catalog_summary"]) > 0


@pytest.mark.asyncio
async def test_uap_headless_machine_purchase(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "buyer_agent_id": "external_procurement_bot_007",
            "buyer_mandate": {
                "buyer_id": DEMO_BUYER_ID,
                "max_amount": 1000000,
                "max_quantity_per_item": 5,
                "currency": "INR",
            },
            "purchase_items": [
                {
                    "sku": "HP-001",
                    "qty": 1,
                    "observed_price": 449900,
                    "catalog_version": 17,
                }
            ],
        }
        res = await ac.post("/agent/v1/machine-purchase", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "APPROVED"
        assert data["guardian_decision"] == "APPROVE"
        assert data["final_verified_total"] == 449900
        assert data["razorpay_order_id"] is not None


@pytest.mark.asyncio
async def test_bundle_margin_check(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/catalog/bundles/margin-check",
            json={
                "parent_sku": "HP-001",
                "addon_sku": "CASE-HP",
                "discount_pct": 30,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["approved"] is True
        assert data["projected_margin_pct"] >= 15.0
