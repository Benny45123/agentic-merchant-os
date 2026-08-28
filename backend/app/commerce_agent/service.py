import re
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.commerce_agent.intent_builder import build_transaction_intent
from app.commerce_agent.schemas import (
    CartSchema,
    ChatResponse,
    CheckoutIntentResponse,
)
from app.guardian.pipeline import evaluate_transaction_intent

# In-memory session stores for active chat sessions
_session_carts: Dict[str, CartSchema] = {}
_session_history: Dict[str, List[Dict[str, str]]] = {}
_session_last_sku: Dict[str, str] = {}
_session_checkpoints: Dict[str, List[Dict]] = {}


def get_or_create_cart(session_id: str) -> CartSchema:
    if session_id not in _session_carts:
        _session_carts[session_id] = CartSchema(items=[], subtotal=0)
    return _session_carts[session_id]


def extract_sku_from_text(text: str) -> Optional[str]:
    """Matches known SKUs case-insensitively in text."""
    sku_pattern = r"(hp-001|hp-002|spk-001|wch-001|cbl-usb-c|stand-alu|case-hp|wrnty-1y|attack-sku-001)"
    match = re.search(sku_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def match_product_keyword(text: str) -> Optional[str]:
    """Matches product names / keywords to canonical SKUs."""
    t = text.lower()
    if "usb-c" in t or "cable" in t:
        return "CBL-USB-C"
    if "stand" in t:
        return "STAND-ALU"
    if "earbuds" in t or "earbud" in t:
        return "HP-002"
    if "soundbar" in t or "speaker" in t:
        return "SPK-001"
    if "watch" in t or "smartwatch" in t or "pulsefit" in t:
        return "WCH-001"
    if "headphone" in t or "headphones" in t or "aerosound" in t:
        return "HP-001"
    if "warranty" in t:
        return "WRNTY-1Y"
    if "case" in t or "pouch" in t:
        return "CASE-HP"
    if "ultrabass" in t or "stealth" in t:
        return "ATTACK-SKU-001"
    return None


def extract_quantity(text: str) -> int:
    """Extracts integer or word quantity from text."""
    words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    for word, val in words.items():
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return val

    match = re.search(r"\b(\d+)\b", text)
    if match:
        return max(1, int(match.group(1)))
    return 1


async def chat(
    session_id: str,
    buyer_id: str,
    message: str,
    merchant_id: str = "m_001",
    session: AsyncSession = None,
) -> ChatResponse:
    """
    Buyer conversational chat turn orchestrated via LangGraph StateGraph engine.
    Supports state checkpointing, backward transitions ('undo' / 'rollback'), and margin upsell routing.
    """
    cart = get_or_create_cart(session_id)
    if session_id not in _session_history:
        _session_history[session_id] = []
    if session_id not in _session_checkpoints:
        _session_checkpoints[session_id] = []

    from app.commerce_agent.graph import commerce_graph, CommerceGraphState

    init_state: CommerceGraphState = {
        "session_id": session_id,
        "buyer_id": buyer_id,
        "merchant_id": merchant_id,
        "message": message,
        "history": _session_history[session_id],
        "cart": cart,
        "cart_history": _session_checkpoints[session_id],
        "recommendations": [],
        "reply": "",
        "action": "chat",
        "target_sku": None,
        "target_qty": 1,
        "guardian_decision": None,
    }

    result_state = await commerce_graph.ainvoke(init_state, session)

    # Update session cart reference
    _session_carts[session_id] = result_state["cart"]
    _session_checkpoints[session_id] = result_state.get("cart_history", [])

    return ChatResponse(
        session_id=session_id,
        reply=result_state["reply"],
        cart=result_state["cart"],
        recommendations=result_state.get("recommendations", []),
    )


async def build_checkout_intent(
    session_id: str,
    buyer_id: str,
    merchant_id: str,
    session: AsyncSession,
) -> CheckoutIntentResponse:
    """
    Builds a TransactionIntent from CartItem state (pure code) and forwards to Guardian.
    Automatically discovers active promotions from Campaign & Offer tables.
    """
    cart = get_or_create_cart(session_id)
    if not cart.items:
        raise ValueError("Cannot checkout with an empty cart")

    # Discover active promotional campaigns for eligible cart items
    from sqlalchemy import select
    from app.models.campaign import Campaign
    from app.core.enums import CampaignStatus

    discount_pct = 0
    camp_stmt = select(Campaign).where(
        Campaign.merchant_id == merchant_id,
        Campaign.status == CampaignStatus.ACTIVE,
    )
    camp_res = await session.execute(camp_stmt)
    active_campaigns = list(camp_res.scalars().all())

    for camp in active_campaigns:
        skus = camp.eligible_skus
        if isinstance(skus, str):
            import json
            try:
                skus = json.loads(skus)
            except Exception:
                skus = [skus]
        skus = skus or []
        for it in cart.items:
            if it.sku in skus:
                discount_pct = max(discount_pct, camp.discount_pct)
                break

    # Build TransactionIntentRequest using pure code with promotional discount
    intent_req = build_transaction_intent(
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        cart_items=cart.items,
        requested_discount_pct=discount_pct,
    )

    # Forward to deterministic Guardian evaluation
    decision_resp = await evaluate_transaction_intent(intent_req, session)

    return CheckoutIntentResponse(
        decision=decision_resp,
        razorpay_order=decision_resp.razorpay_order,
    )
