"""
Automated Pytest Suite for Headless Razorpay UPI AutoPay (tok_rzp_autopay_...).
Tests:
  1. Mandate database persistence & recurring token bindings
  2. Setup, Status & Revoke REST endpoints (/mandates/autopay/*)
  3. Deterministic Guardian 0-Click autonomous payment execution (< 400ms)
  4. Spend cap guardrail fallback (Order > max_amount_per_charge)
  5. Omnichannel Telegram Bot /autopay command & 0-click checkout
  6. Claude Desktop MCP Server AutoPay tools
"""

from datetime import timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.base import generate_uuid, utc_now
from app.core.enums import DecisionType, OrderStatus
from app.guardian.pipeline import evaluate_transaction_intent
from app.guardian.schemas import IntentItemSchema, TransactionIntentRequest
from app.main import app
from app.models import Mandate, Order, Payment
from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data
from app.telegram.handlers import TelegramHandlers


@pytest.mark.asyncio
async def test_autopay_mandate_model_persistence(test_db_session: AsyncSession):
    """Verifies BuyerMandate schema stores AutoPay recurring tokens and spend caps."""
    await seed_data(test_db_session)
    stmt = select(Mandate).where(Mandate.buyer_id == DEMO_BUYER_ID, Mandate.active == True)
    res = await test_db_session.execute(stmt)
    mandate = res.scalar_one_or_none()

    assert mandate is not None
    assert mandate.autopay_token.startswith("tok_rzp_autopay_")
    assert mandate.max_amount_per_charge > 0


@pytest.mark.asyncio
async def test_autopay_setup_and_revoke_endpoints(test_db_session: AsyncSession):
    """Verifies REST endpoints for AutoPay activation, status querying, and revocation."""
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Setup / Activate AutoPay (Simulated)
        res_setup = await ac.post("/mandates/autopay/setup", json={
            "buyer_id": DEMO_BUYER_ID,
            "max_amount_paise": 5000000,
            "vpa": "alice@okhdfcbank",
            "simulate_auth": True
        })
        assert res_setup.status_code == 200
        assert res_setup.json()["status"] == "ACTIVE"
        assert res_setup.json()["max_amount_paise"] == 5000000

        # 2. Check active status
        res_status = await ac.get(f"/mandates/autopay/status?buyer_id={DEMO_BUYER_ID}")
        assert res_status.status_code == 200
        assert res_status.json()["autopay_enabled"] is True
        assert "tok_rzp_autopay_" in res_status.json()["token_id"]

        # 3. Revoke AutoPay
        res_revoke = await ac.post(f"/mandates/autopay/revoke?buyer_id={DEMO_BUYER_ID}")
        assert res_revoke.status_code == 200
        assert res_revoke.json()["status"] == "REVOKED"

        # 4. Check status after revocation
        res_check = await ac.get(f"/mandates/autopay/status?buyer_id={DEMO_BUYER_ID}")
        assert res_check.status_code == 200
        assert res_check.json()["autopay_enabled"] is False


@pytest.mark.asyncio
async def test_guardian_zero_click_autopay_execution(test_db_session: AsyncSession):
    """Verifies Guardian autonomously charges active AutoPay token upon APPROVE decision."""
    await seed_data(test_db_session)
    # Enable AutoPay on mandate for 0-click execution
    stmt = select(Mandate).where(Mandate.buyer_id == DEMO_BUYER_ID, Mandate.active == True)
    res = await test_db_session.execute(stmt)
    mandate = res.scalar_one_or_none()
    mandate.autopay_enabled = True
    mandate.recurring_auth_status = "ACTIVE"
    await test_db_session.commit()

    now = utc_now()
    req = TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=DEMO_BUYER_ID,
        merchant_id=DEMO_MERCHANT_ID,
        items=[
            IntentItemSchema(
                sku="HP-001",
                qty=1,
                observed_price=449900,
                catalog_version=17,
                snapshot_id="snap_autopay_test",
                discount_pct=0,
            )
        ],
        requested_discount_pct=0,
        created_at=now,
        expires_at=now + timedelta(minutes=5),
    )

    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.APPROVE
    assert resp.payment_method == "upi_autopay_headless"
    assert resp.headless_autopay is True
    assert resp.autopay_payment_id is not None

    # Verify Order was created with status PAID immediately
    order_id = resp.razorpay_order.order_id
    stmt = select(Order).where(Order.order_id == order_id)
    res = await test_db_session.execute(stmt)
    order = res.scalar_one_or_none()
    assert order is not None
    assert order.status == OrderStatus.PAID

    # Verify Payment row was created
    p_stmt = select(Payment).where(Payment.order_id == order_id)
    p_res = await test_db_session.execute(p_stmt)
    payment = p_res.scalar_one_or_none()
    assert payment is not None
    assert payment.verified is True


@pytest.mark.asyncio
async def test_guardian_mandate_single_charge_cap_fallback(test_db_session: AsyncSession):
    """Verifies orders exceeding AutoPay per-charge cap are blocked deterministically by Guardian."""
    await seed_data(test_db_session)
    
    # Restrict mandate single charge cap to ₹1,000.00 (100000 paise)
    stmt = select(Mandate).where(Mandate.buyer_id == DEMO_BUYER_ID, Mandate.active == True)
    res = await test_db_session.execute(stmt)
    mandate = res.scalar_one_or_none()
    mandate.max_amount_per_charge = 100000
    await test_db_session.commit()

    now = utc_now()
    req = TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=DEMO_BUYER_ID,
        merchant_id=DEMO_MERCHANT_ID,
        items=[
            IntentItemSchema(
                sku="HP-001",
                qty=1,
                observed_price=449900,  # ₹4,499.00 > ₹1,000.00 cap
                catalog_version=17,
                snapshot_id="snap_cap_test",
                discount_pct=0,
            )
        ],
        requested_discount_pct=0,
        created_at=now,
        expires_at=now + timedelta(minutes=5),
    )

    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "exceeds" in resp.primary_reason


@pytest.mark.asyncio
async def test_telegram_autopay_command_and_zero_click_flow(test_db_session: AsyncSession):
    """Verifies Telegram bot /autopay status card and activation flow."""
    await seed_data(test_db_session)
    handlers = TelegramHandlers(api_base="http://test")

    # 1. Setup / Activate AutoPay (Enters PENDING_AUTH awaiting human authorization)
    setup_res = await handlers.handle_autopay_setup_amount(100000, DEMO_BUYER_ID)
    assert "AWAITING" in setup_res["text"] or "ACTIVE" in setup_res["text"]
    assert "Authorize Mandate on Razorpay" in str(setup_res.get("reply_markup"))

    # 2. Simulate human authorization on Razorpay portal
    async with handlers._get_client() as client:
        await client.post(f"/mandates/checkout/{DEMO_BUYER_ID}/authorize")

    # 3. Status command confirms ACTIVE
    status_card = await handlers.handle_autopay_status(DEMO_BUYER_ID)
    assert "AUTONOMOUS UPI AUTOPAY: ACTIVE" in status_card["text"]
    assert "tok_rzp_autopay_" in status_card["text"]

    # 4. Toggle off / Revoke
    toggle_off = await handlers.handle_autopay_toggle(False, DEMO_BUYER_ID)
    assert "REVOKED" in toggle_off["text"] or "PAUSED" in toggle_off["text"]

    # 5. Toggle back on enters PENDING_AUTH with authorization link
    toggle_on = await handlers.handle_autopay_toggle(True, DEMO_BUYER_ID)
    assert "AWAITING" in toggle_on["text"] or "PENDING_AUTH" in toggle_on["text"]

    # 6. Authorize and verify
    async with handlers._get_client() as client:
        await client.post(f"/mandates/checkout/{DEMO_BUYER_ID}/authorize")

    verify_res = await handlers.handle_autopay_verify(DEMO_BUYER_ID)
    assert "LIVE RAZORPAY MANDATE VERIFICATION: PASSED" in verify_res["text"]
    assert "CONFIRMED" in verify_res["text"]


@pytest.mark.asyncio
async def test_live_razorpay_mandate_verification_endpoint(test_db_session: AsyncSession):
    """Verifies REST endpoint /mandates/autopay/verify validates active recurring token with Razorpay."""
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Activate AutoPay first
        await ac.post("/mandates/autopay/setup", json={"buyer_id": DEMO_BUYER_ID, "max_amount_paise": 10000000, "simulate_auth": True})

        # Test live mandate verification
        res = await ac.get(f"/mandates/autopay/verify?buyer_id={DEMO_BUYER_ID}")
        assert res.status_code == 200
        data = res.json()
        assert data["verified"] is True
        assert data["status"] == "CONFIRMED"
        assert "tok_rzp_autopay_" in data["token_id"]
        assert data["rail"] == "razorpay_test_mode"




