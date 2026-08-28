import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data
from app.negotiation.schemas import RFQRequest, RFQItem, BuyerMandatePayload, AcceptOfferRequest


@pytest.mark.asyncio
async def test_rfq_valid_counter_offers_formulation(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        rfq_payload = {
            "buyer_agent_id": "ai_buyer_procure_test_1",
            "merchant_id": DEMO_MERCHANT_ID,
            "round_index": 1,
            "buyer_mandate": {
                "buyer_id": DEMO_BUYER_ID,
                "max_amount": 1000000,
                "max_quantity_per_item": 5,
                "currency": "INR",
            },
            "items": [
                {
                    "sku": "HP-001",
                    "qty": 3,
                    "target_unit_price_paise": 410000,  # ₹4,100 (Passes 15% floor)
                }
            ],
        }

        res = await ac.post("/commerce/rfq", json=rfq_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ["OFFERS_PROPOSED", "COUNTER_OFFER_FORMULATED"]
        assert len(data["counter_offers"]) >= 1
        
        # Check counter offers
        opt_ids = [opt["option_id"] for opt in data["counter_offers"]]
        assert "OPT_DIRECT_PRICE" in opt_ids or "OPT_BUNDLE_SWEETENER" in opt_ids

        # Check bundle sweetener contains warranty or accessory
        bundle_opt = next((opt for opt in data["counter_offers"] if opt["option_type"] == "BUNDLE_SWEETENER"), None)
        if bundle_opt:
            assert bundle_opt["projected_gross_margin_pct"] >= 15.0
            assert len(bundle_opt["bundled_items"]) > 0


@pytest.mark.asyncio
async def test_rfq_adversarial_margin_floor_breach(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Proposed unit price ₹3,200 on HP-001 (COGS = ₹3,000) yields 6.25% margin, breaching 15% floor
        rfq_payload = {
            "buyer_agent_id": "adversarial_buyer_bot",
            "merchant_id": DEMO_MERCHANT_ID,
            "round_index": 1,
            "buyer_mandate": {
                "buyer_id": DEMO_BUYER_ID,
                "max_amount": 1000000,
                "max_quantity_per_item": 5,
                "currency": "INR",
            },
            "items": [
                {
                    "sku": "HP-001",
                    "qty": 3,
                    "target_unit_price_paise": 320000,  # Below 15% floor
                }
            ],
        }

        res = await ac.post("/commerce/rfq", json=rfq_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "REJECTED_MARGIN_FLOOR"
        assert "breaches" in data["reason"].lower() or "floor" in data["reason"].lower() or "15" in data["reason"]
        
        # All counter-offers formulated must satisfy 15% floor
        for opt in data["counter_offers"]:
            assert opt["projected_gross_margin_pct"] >= 15.0


@pytest.mark.asyncio
async def test_accept_negotiated_offer_settlement(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Submit RFQ
        rfq_res = await ac.post(
            "/commerce/rfq",
            json={
                "buyer_agent_id": "ai_buyer_settle_test",
                "merchant_id": DEMO_MERCHANT_ID,
                "round_index": 1,
                "buyer_mandate": {
                    "buyer_id": DEMO_BUYER_ID,
                    "max_amount": 1000000,
                    "max_quantity_per_item": 5,
                    "currency": "INR",
                },
                "items": [
                    {
                        "sku": "HP-001",
                        "qty": 2,
                        "target_unit_price_paise": 420000,
                    }
                ],
            },
        )
        assert rfq_res.status_code == 200
        rfq_data = rfq_res.json()
        chosen_option = rfq_data["counter_offers"][0]["option_id"]

        # 2. Settle Offer
        settle_res = await ac.post(
            "/commerce/accept",
            json={
                "session_id": rfq_data["session_id"],
                "selected_option_id": chosen_option,
                "buyer_agent_id": "ai_buyer_settle_test",
                "merchant_id": DEMO_MERCHANT_ID,
            },
        )
        assert settle_res.status_code == 200
        settle_data = settle_res.json()
        assert settle_data["guardian_decision"] in ["APPROVE", "APPROVED"]
        assert settle_data["receipt_id"] is not None
        assert settle_data["merchant_margin_achieved_pct"] >= 15.0
        assert settle_data["replay_hash"] is not None
