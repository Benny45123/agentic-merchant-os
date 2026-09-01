import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.commerce_agent.schemas import CartItemSchema, CartSchema
from app.commerce_agent.service import build_checkout_intent, chat
from app.commerce_agent.tools import CommerceAgentTools
from app.core.base import generate_uuid
from app.core.enums import DecisionType
from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data


import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def setup_seed(test_db_session: AsyncSession):
    await seed_data(test_db_session)


@pytest.mark.asyncio
async def test_commerce_agent_chat_and_upsell(test_db_session: AsyncSession):
    session_id = generate_uuid()

    # 1. Buyer asks to add headphones
    resp = await chat(
        session_id=session_id,
        buyer_id=DEMO_BUYER_ID,
        message="Please add the wireless headphones HP-001 to my cart",
        merchant_id=DEMO_MERCHANT_ID,
        session=test_db_session,
    )
    assert len(resp.cart.items) == 1
    assert resp.cart.items[0].sku == "HP-001"
    assert resp.cart.items[0].qty == 1
    assert resp.cart.subtotal == 449900

    # 2. Verify upsell recommendations are generated and NOT auto-added to cart
    assert len(resp.recommendations) > 0
    assert any(r.sku == "WRNTY-1Y" or r.sku == "CASE-HP" for r in resp.recommendations)
    assert len(resp.cart.items) == 1  # Cart is still just 1 item

    # 3. Buyer accepts warranty upsell
    resp2 = await chat(
        session_id=session_id,
        buyer_id=DEMO_BUYER_ID,
        message="Yes please add warranty WRNTY-1Y too",
        merchant_id=DEMO_MERCHANT_ID,
        session=test_db_session,
    )
    assert len(resp2.cart.items) == 2
    assert any(item.sku == "WRNTY-1Y" for item in resp2.cart.items)
    assert resp2.cart.subtotal == 449900 + 49900

    # 4. Checkout intent creation and Guardian approval
    checkout_res = await build_checkout_intent(
        session_id=session_id,
        buyer_id=DEMO_BUYER_ID,
        merchant_id=DEMO_MERCHANT_ID,
        session=test_db_session,
    )
    assert checkout_res.decision.decision == DecisionType.APPROVE
    assert checkout_res.decision.final_verified_total == 449900 + 49900
    assert checkout_res.razorpay_order is not None


@pytest.mark.asyncio
async def test_tool_quantity_clamp_returns_error_not_silent_success(test_db_session: AsyncSession):
    cart = CartSchema(items=[], subtotal=0)
    tools = CommerceAgentTools(
        session_id="test_sess",
        buyer_id=DEMO_BUYER_ID,
        merchant_id=DEMO_MERCHANT_ID,
        cart=cart,
        session=test_db_session,
    )
    # Mandate max_quantity_per_item is 5. Attempting to add 10 should return explainable error
    res = await tools.add_to_cart("HP-001", qty=10)
    assert res["success"] is False
    assert "exceeds your buyer mandate limit" in res["error"]
    assert len(cart.items) == 0  # Not added


@pytest.mark.asyncio
async def test_commerce_agent_langgraph_rollback(test_db_session: AsyncSession):
    """Verifies that LangGraph can move backwards in state when the user requests an undo / rollback."""
    session_id = generate_uuid()

    # Step 1: Add HP-001
    r1 = await chat(session_id, DEMO_BUYER_ID, "Add HP-001", DEMO_MERCHANT_ID, test_db_session)
    assert len(r1.cart.items) == 1
    assert r1.cart.items[0].sku == "HP-001"

    # Step 2: Add Case
    r2 = await chat(session_id, DEMO_BUYER_ID, "Add case CASE-HP", DEMO_MERCHANT_ID, test_db_session)
    assert len(r2.cart.items) == 2

    # Step 3: Rollback / Undo
    r3 = await chat(session_id, DEMO_BUYER_ID, "Undo last action", DEMO_MERCHANT_ID, test_db_session)
    assert len(r3.cart.items) == 1
    assert r3.cart.items[0].sku == "HP-001"
    assert "Rolled Back" in r3.reply

    # Step 4: Rollback again to initial empty state
    r4 = await chat(session_id, DEMO_BUYER_ID, "revert", DEMO_MERCHANT_ID, test_db_session)
    assert len(r4.cart.items) == 0
    assert "Rolled Back" in r4.reply


@pytest.mark.asyncio
async def test_commerce_agent_http_endpoint(test_db_session: AsyncSession):
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/agent/chat", json={
            "session_id": "test_http_sess_01",
            "buyer_id": DEMO_BUYER_ID,
            "message": "Add headphones HP-001 to my cart",
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data["cart"]["items"]) == 1
        assert len(data["recommendations"]) > 0

