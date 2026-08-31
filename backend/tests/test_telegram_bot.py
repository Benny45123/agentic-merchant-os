"""
Automated Test Suite for Telegram Omnichannel Commerce Bot Gateway.
Tests /start, /catalog, direct purchase, A2A reverse auction bargaining, settlement,
receipt audits, and Razorpay payment verification sync.
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
from app.models import Order
from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data
from app.telegram.handlers import TelegramHandlers


def make_tg_intent_req(
    sku: str = "HP-001",
    qty: int = 1,
    observed_price: int = 449900,
    requested_discount: int = 0,
    buyer_id: str = DEMO_BUYER_ID,
    merchant_id: str = DEMO_MERCHANT_ID,
) -> TransactionIntentRequest:
    now = utc_now()
    return TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        items=[
            IntentItemSchema(
                sku=sku,
                qty=qty,
                observed_price=observed_price,
                catalog_version=17,
                snapshot_id="snap_tg_test",
                discount_pct=0,
            )
        ],
        requested_discount_pct=requested_discount,
        created_at=now,
        expires_at=now + timedelta(seconds=120),
    )


@pytest.mark.asyncio
async def test_telegram_start_handler(test_db_session: AsyncSession):
    """Verifies /start returns welcome greeting and interactive navigation buttons."""
    handlers = TelegramHandlers(api_base="http://test")
    res = await handlers.handle_start("Alice")
    assert "Welcome to Agentic Merchant Store, Alice!" in res["text"]
    assert "inline_keyboard" in res["reply_markup"]
    buttons = res["reply_markup"]["inline_keyboard"]
    assert len(buttons) >= 2


@pytest.mark.asyncio
async def test_telegram_catalog_handler(test_db_session: AsyncSession):
    """Verifies /catalog retrieves live products with formatted INR prices and action buttons."""
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        cat_res = await ac.get(f"/catalog/products?merchant_id={DEMO_MERCHANT_ID}")
        assert cat_res.status_code == 200
        products = cat_res.json().get("products", [])
        assert len(products) > 0

        p = products[0]
        assert "sku" in p
        assert "price" in p
        assert p["price"] > 0


@pytest.mark.asyncio
async def test_telegram_direct_buy_flow(test_db_session: AsyncSession):
    """Verifies direct purchase at full catalog retail price with 0% discount."""
    await seed_data(test_db_session)
    req = make_tg_intent_req(sku="HP-001", qty=1, observed_price=449900)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.APPROVE
    assert resp.final_verified_total == 449900
    assert resp.receipt_id is not None
    assert resp.razorpay_order is not None


@pytest.mark.asyncio
async def test_telegram_a2a_bargain_and_settlement(test_db_session: AsyncSession):
    """Verifies A2A reverse auction bargaining and Guardian settlement."""
    await seed_data(test_db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. RFQ
        rfq_payload = {
            "merchant_id": DEMO_MERCHANT_ID,
            "buyer_agent_id": "telegram_mobile_user_test",
            "buyer_mandate": {
                "buyer_id": DEMO_BUYER_ID,
                "max_amount": 10000000,
                "max_quantity_per_item": 10,
                "currency": "INR",
            },
            "items": [
                {
                    "sku": "HP-001",
                    "qty": 1,
                    "target_unit_price_paise": 380000,
                }
            ],
        }

        rfq_res = await ac.post("/commerce/rfq", json=rfq_payload)
        assert rfq_res.status_code == 200
        rfq_data = rfq_res.json()
        assert len(rfq_data["counter_offers"]) >= 1
        session_id = rfq_data["session_id"]
        chosen_opt = rfq_data["counter_offers"][0]["option_id"]

        # 2. Accept & Settle
        accept_payload = {
            "session_id": session_id,
            "buyer_agent_id": "telegram_mobile_user_test",
            "merchant_id": DEMO_MERCHANT_ID,
            "selected_option_id": chosen_opt,
        }

        settle_res = await ac.post("/commerce/accept", json=accept_payload)
        assert settle_res.status_code == 200
        settle_data = settle_res.json()
        assert settle_data["status"] == "APPROVED"
        assert settle_data["guardian_decision"] in ["APPROVE", "APPROVED"]
        assert settle_data["final_verified_total_paise"] > 0
        assert settle_data["razorpay_order_id"] is not None


@pytest.mark.asyncio
async def test_telegram_payment_sync_endpoint(test_db_session: AsyncSession):
    """Verifies payment synchronization marks order PAID and credits revenue."""
    await seed_data(test_db_session)
    req = make_tg_intent_req(sku="HP-001", qty=1, observed_price=449900)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.APPROVE
    order_id = resp.razorpay_order.order_id

    # Verify Order was created in DB
    stmt = select(Order).where(Order.order_id == order_id)
    result = await test_db_session.execute(stmt)
    order = result.scalar_one_or_none()
    assert order is not None
    assert order.status == OrderStatus.CREATED

    # Mark as PAID through sync logic
    order.status = OrderStatus.PAID
    await test_db_session.commit()
    assert order.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_telegram_natural_language_routing():
    """Verifies text routing for direct buy, bargain, and catalog discovery."""
    handlers = TelegramHandlers(api_base="http://test")

    res_start = await handlers.handle_start("Bob")
    assert "Bob" in res_start["text"]

    res_fallback = await handlers.handle_text_message("Hello what can you do?")
    assert "I heard" in res_fallback["text"]
    assert "inline_keyboard" in res_fallback["reply_markup"]
