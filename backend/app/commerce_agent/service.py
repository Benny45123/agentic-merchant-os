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
    """Matches any canonical catalog SKU case-insensitively in text."""
    known_skus = [
        "HP-001", "HP-002", "SPK-001", "WCH-001", "WCH-APL-S9", "WCH-SAM-W6",
        "PHN-APL-15", "PHN-SAM-S24", "PHN-ONE-12R", "PHN-PIX-8A",
        "LAP-APL-M3", "LAP-DEL-XPS", "LAP-LEN-YOG", "LAP-ASU-ZEP",
        "ACC-MAG-CHG", "ACC-CASE-CL", "ACC-USB-HUB", "ACC-LAP-SLV", "PWR-BNK-65W",
        "CBL-USB-C", "STAND-ALU", "STRAP-LTH", "CASE-HP", "WRNTY-1Y", "WRNTY-PHN-2Y", "WRNTY-LAP-3Y",
        "ATTACK-SKU-001"
    ]
    t = text.upper()
    for s in known_skus:
        if re.search(rf"(?:\b|_){re.escape(s)}(?:\b|_)", t):
            return s
    
    return None


def match_product_keyword(text: str) -> Optional[str]:
    """Matches common product names / keywords to canonical SKUs."""
    t = text.lower()
    
    # Accessories & Cables (check specific compound items first)
    if "usb-c" in t or "charging cable" in t or "cable" in t:
        return "CBL-USB-C"
    if "docking hub" in t or "usb hub" in t or "dongle" in t:
        return "ACC-USB-HUB"
    if "magsafe" in t or "wireless charger" in t:
        return "ACC-MAG-CHG"
    if "phone case" in t or "clear case" in t:
        return "ACC-CASE-CL"
    if "laptop sleeve" in t or "laptop cover" in t:
        return "ACC-LAP-SLV"
    if "power bank" in t or "powerbank" in t or "65w" in t:
        return "PWR-BNK-65W"
    if "stand" in t:
        return "STAND-ALU"
    if "leather strap" in t or "watch strap" in t:
        return "STRAP-LTH"
    if "travel case" in t or "case-hp" in t or "headphone case" in t:
        return "CASE-HP"
    if "phone warranty" in t or "mobile shield" in t:
        return "WRNTY-PHN-2Y"
    if "laptop warranty" in t or "on-site" in t:
        return "WRNTY-LAP-3Y"
    if "warranty" in t or "care" in t:
        return "WRNTY-1Y"

    # Smartphones & Mobiles
    if "iphone" in t or "iphone 15" in t or "apple phone" in t:
        return "PHN-APL-15"
    if "galaxy s24" in t or "s24" in t or "samsung galaxy" in t:
        return "PHN-SAM-S24"
    if "oneplus" in t or "12r" in t:
        return "PHN-ONE-12R"
    if "pixel" in t or "8a" in t or "google phone" in t:
        return "PHN-PIX-8A"
        
    # Laptops
    if "macbook" in t or "macbook air" in t or "m3" in t:
        return "LAP-APL-M3"
    if "xps" in t or "dell" in t:
        return "LAP-DEL-XPS"
    if "yoga" in t or "lenovo" in t:
        return "LAP-LEN-YOG"
    if "zephyrus" in t or "rog" in t or "asus" in t or "gaming laptop" in t:
        return "LAP-ASU-ZEP"
        
    # Smartwatches
    if "apple watch" in t or "series 9" in t:
        return "WCH-APL-S9"
    if "galaxy watch" in t or "watch6" in t or "watch 6" in t:
        return "WCH-SAM-W6"
    if "aeropulse" in t or "smartwatch" in t:
        return "WCH-001"
        
    # Audio
    if "soundbar" in t or "speaker" in t:
        return "SPK-001"
    if "earbuds" in t or "earbud" in t:
        return "HP-002"
    if "headphone" in t or "headphones" in t or "aerosound" in t:
        return "HP-001"
        
    if "ultrabass" in t or "stealth" in t:
        return "ATTACK-SKU-001"
        
    return None


def extract_quantity(text: str) -> int:
    """Extracts integer quantity from text, ignoring prices (₹, $, rs), specs (2m, 16gb), and SKUs."""
    # 1. Clean out prices like ₹399, Rs 399, $399, 399.00
    cleaned = re.sub(r"[₹$€£]\s*\d+(?:\.\d+)?", "", text)
    cleaned = re.sub(r"\b(?:rs|inr|usd|price|cost)\.?\s*\d+(?:\.\d+)?", "", cleaned, flags=re.IGNORECASE)
    # Clean out technical specs like 2m, 16gb, 128gb, 512gb, 14-inch, 120hz, 5500mah, 65w
    cleaned = re.sub(r"\b\d+\s*(?:m|cm|mm|gb|tb|mb|inch|in|hz|w|mah|kg|g|k)\b", "", cleaned, flags=re.IGNORECASE)
    # Clean out SKUs like HP-001, PHN-15, etc.
    cleaned = re.sub(r"\b[A-Za-z]{2,6}-\d+\b", "", cleaned)

    # 2. Look for explicit quantity prefixes / suffixes (e.g., "qty: 2", "qty 2", "2x", "2 units", "2 pieces", "quantity 3", "3 of", "buy 2")
    qty_patterns = [
        r"(?:qty|quantity|count)\s*[:=]?\s*(\d+)",
        r"\b(\d+)\s*(?:x|units?|pcs?|pieces?|items?|nos?|copies?)\b",
        r"\b(?:add|buy|order|get|take|want)\s+(\d+)\b",
        r"\b(\d+)\s+of\b",
    ]
    for pattern in qty_patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            return max(1, int(match.group(1)))

    # 3. Word-based quantities (e.g. "two headphones", "three units")
    words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    for word, val in words.items():
        if re.search(rf"\b(?:add|buy|order|get|want)?\s*{word}\s*(?:x|units?|items?|pieces?)?\b", cleaned, re.IGNORECASE):
            if word == "one" and re.search(r"oneplus", text, re.IGNORECASE):
                continue
            return val

    # 4. If user message is just a number like "1" or "add 2"
    direct_num = re.search(r"^\s*(?:add\s+)?(\d+)\s*$", cleaned, re.IGNORECASE)
    if direct_num:
        return max(1, int(direct_num.group(1)))

    # Default to 1 unit
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
