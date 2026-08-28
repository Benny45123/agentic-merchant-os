import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.enums import CampaignStatus
from app.models import Campaign, Order, CampaignEvent
from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data


@pytest.mark.asyncio
async def test_campaign_lifecycle_and_revenue_attribution(test_db_session: AsyncSession):
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Propose Campaign
        prop_res = await ac.post(
            "/campaign/propose",
            json={
                "merchant_id": DEMO_MERCHANT_ID,
                "objective": "Increase sales of wireless headphones this weekend with 15% discount",
            },
        )
        assert prop_res.status_code == 200
        prop_data = prop_res.json()
        proposal_id = prop_data["proposal_id"]
        assert "HP-001" in prop_data["eligible_skus"]
        assert prop_data["discount_pct"] <= 25  # Respects max discount policy

        # 2. Activate Campaign
        act_res = await ac.post(
            f"/campaign/{proposal_id}/activate",
        )
        assert act_res.status_code == 200
        act_data = act_res.json()
        campaign_id = act_data["campaign_id"]
        assert act_data["status"] == "ACTIVE"

        # Verify campaign is active via status API
        status_res = await ac.get(f"/campaign/{campaign_id}/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["status"] == "ACTIVE"

        # 3. Simulate Commerce Agent Checkout Intent with Active Campaign
        # Add HP-001 to session cart
        session_id = "test_attribution_session_1"
        chat_res = await ac.post(
            "/agent/chat",
            json={
                "session_id": session_id,
                "buyer_id": DEMO_BUYER_ID,
                "message": "Please add HP-001 to my cart",
            },
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert len(chat_data["cart"]["items"]) == 1

        # Checkout Cart (Commerce Agent builds TransactionIntentRequest with automated campaign discovery)
        checkout_res = await ac.post(
            "/agent/checkout-intent",
            json={
                "session_id": session_id,
                "buyer_id": DEMO_BUYER_ID,
                "merchant_id": DEMO_MERCHANT_ID,
            },
        )
        assert checkout_res.status_code == 200
        checkout_data = checkout_res.json()
        decision = checkout_data["decision"]
        assert decision["decision"] == "APPROVE"
        
        # Verify campaign discount was applied to the verified total
        orig_subtotal = 449900
        assert decision["final_verified_total"] < orig_subtotal

        # 4. Verify Razorpay Payment to complete the order & attribute revenue
        order_id = (
            decision["razorpay_order"]["order_id"]
            if decision.get("razorpay_order")
            else checkout_data["razorpay_order"]["order_id"]
        )
        pay_res = await ac.post(
            "/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": f"pay_test_{order_id}",
                "razorpay_signature": "mock_signature_test",
            },
        )
        assert pay_res.status_code == 200
        pay_data = pay_res.json()
        assert pay_data["verified"] is True
        assert pay_data["status"] in ["PAID", "captured"]

        # 5. Check Campaign Revenue Telemetry on /dashboard/revenue (verifying attributed order)
        analytics_res = await ac.get(f"/dashboard/revenue?merchant_id={DEMO_MERCHANT_ID}")
        assert analytics_res.status_code == 200
        analytics_data = analytics_res.json()
        assert analytics_data["campaign_revenue"] > 0
        assert analytics_data["total_revenue"] > 0
        assert analytics_data["order_count"] >= 1
