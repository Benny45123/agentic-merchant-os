import copy
import logging
from typing import Any, Dict, List, Optional, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_provider.gemini_provider import get_ai_provider
from app.catalog.service import search_products
from app.commerce_agent.intent_builder import build_transaction_intent
from app.commerce_agent.prompts import COMMERCE_AGENT_SYSTEM_PROMPT
from app.commerce_agent.schemas import CartItemSchema, CartSchema, RecommendationSchema
from app.commerce_agent.tools import CommerceAgentTools
from app.commerce_agent.upsell import generate_upsell_recommendations
from app.guardian.pipeline import evaluate_transaction_intent

logger = logging.getLogger(__name__)


class CommerceGraphState(TypedDict):
    """
    LangGraph State Schema for Agentic Commerce.
    Maintains conversation stream, active cart, and checkpoint history for time-travel/rollback.
    """
    session_id: str
    buyer_id: str
    merchant_id: str
    message: str
    history: List[Dict[str, str]]
    cart: CartSchema
    cart_history: List[Dict[str, Any]]  # Checkpoints for step-back / rollback
    recommendations: List[RecommendationSchema]
    reply: str
    action: str  # "add", "rollback", "checkout", "clear", "chat"
    target_sku: Optional[str]
    target_qty: int
    guardian_decision: Optional[Any]


# ------------------------------------------------------------------------------
# 1. Graph Nodes
# ------------------------------------------------------------------------------

async def intent_router_node(state: CommerceGraphState, session: AsyncSession = None) -> Dict[str, Any]:
    """
    Node 1: Evaluates user message to determine if it is a Rollback/Undo, Cart Add, Checkout, or General Chat.
    """
    msg_lower = state["message"].lower()

    # 1. Rollback / Undo Intent
    if any(kw in msg_lower for kw in ["undo", "go back", "rollback", "revert", "remove last", "take back"]):
        return {"action": "rollback"}

    # 2. Checkout Intent
    if any(kw in msg_lower for kw in [
        "checkout", "check out", "proceed to check out", "proceed to checkout",
        "submit", "pay now", "place order", "complete purchase", "complete my order",
        "do that for me", "buy now", "pay for this"
    ]):
        return {"action": "checkout"}

    # 3. Clear Intent
    if "clear cart" in msg_lower or "empty cart" in msg_lower or msg_lower == "clear":
        return {"action": "clear"}

    # 4. Add to Cart Intent
    is_add = any(kw in msg_lower for kw in ["add", "book", "buy", "order", "get", "take", "purchase", "want", "include", "yes"])
    
    # Identify SKU
    from app.commerce_agent.service import extract_sku_from_text, match_product_keyword, extract_quantity, _session_last_sku
    detected_sku = extract_sku_from_text(state["message"]) or match_product_keyword(state["message"])
    if detected_sku:
        _session_last_sku[state["session_id"]] = detected_sku
    elif state["session_id"] in _session_last_sku:
        if any(kw in msg_lower for kw in ["yes", "add it", "add that", "add this", "add to cart", "in the cart", "buy it", "book it", "please add", "add", "put in", "cart", "1", "2", "3", "4", "5"]):
            detected_sku = _session_last_sku[state["session_id"]]

    qty = extract_quantity(state["message"])

    if is_add and detected_sku:
        return {
            "action": "add",
            "target_sku": detected_sku,
            "target_qty": qty,
        }

    return {"action": "chat"}


async def rollback_node(state: CommerceGraphState, session: AsyncSession = None) -> Dict[str, Any]:
    """
    Node: Time-Travel / Rollback to previous state checkpoint.
    Allows moving back when a buyer changes their mind or makes a mistake.
    """
    cart_history = state.get("cart_history", [])
    if cart_history and len(cart_history) > 1:
        # Pop current state, restore previous checkpoint
        cart_history.pop()
        previous_snapshot = cart_history[-1]
        
        restored_items = [CartItemSchema(**item) for item in previous_snapshot.get("items", [])]
        restored_subtotal = previous_snapshot.get("subtotal", 0)
        
        new_cart = CartSchema(items=restored_items, subtotal=restored_subtotal)
        reply = (
            f"🔄 **State Rolled Back**: Restored your previous cart state. "
            f"You now have {len(restored_items)} item(s) in your cart (Subtotal: ₹{restored_subtotal/100:.2f})."
        )
        return {
            "cart": new_cart,
            "cart_history": cart_history,
            "reply": reply,
            "recommendations": [],
        }
    elif cart_history and len(cart_history) == 1:
        # Reset to empty
        new_cart = CartSchema(items=[], subtotal=0)
        cart_history.clear()
        return {
            "cart": new_cart,
            "cart_history": cart_history,
            "reply": "🔄 **State Rolled Back**: Emptied your cart back to starting state.",
            "recommendations": [],
        }
    else:
        return {
            "reply": "Nothing to roll back to. Your cart is already at its initial state.",
        }


async def cart_mutation_node(state: CommerceGraphState, session: AsyncSession = None) -> Dict[str, Any]:
    """
    Node: Executes Cart Add with checkpoint snapshot recording.
    """
    cart = state["cart"]
    tools = CommerceAgentTools(
        session_id=state["session_id"],
        buyer_id=state["buyer_id"],
        merchant_id=state["merchant_id"],
        cart=cart,
        session=session,
    )

    sku = state["target_sku"]
    qty = state.get("target_qty", 1)
    is_upsell = sku in ["WRNTY-1Y", "CASE-HP", "CBL-USB-C", "STAND-ALU"] and len(cart.items) > 0

    add_res = await tools.add_to_cart(sku, qty=qty, source="upsell" if is_upsell else "organic")
    
    # Save checkpoint to cart_history
    cart_history = state.get("cart_history", [])
    cart_snapshot = {
        "items": [item.model_dump() for item in cart.items],
        "subtotal": cart.subtotal,
    }
    cart_history.append(cart_snapshot)

    if add_res.get("success"):
        name = add_res.get("name", sku)
        from app.commerce_agent.service import _session_last_sku
        _session_last_sku[state["session_id"]] = sku

        # Check for active promotional campaigns on this SKU
        from sqlalchemy import select
        from app.models.campaign import Campaign
        from app.core.enums import CampaignStatus

        camp_discount_pct = 0
        camp_stmt = select(Campaign).where(
            Campaign.merchant_id == state["merchant_id"],
            Campaign.status == CampaignStatus.ACTIVE,
        )
        camp_res = await session.execute(camp_stmt) if session else None
        if camp_res:
            import json
            for camp in camp_res.scalars().all():
                skus = camp.eligible_skus
                if isinstance(skus, str):
                    try:
                        skus = json.loads(skus)
                    except Exception:
                        skus = [skus]
                skus = skus or []
                if sku in skus:
                    camp_discount_pct = max(camp_discount_pct, camp.discount_pct)



        if camp_discount_pct > 0:
            disc_subtotal = int(cart.subtotal * (1.0 - camp_discount_pct / 100.0))
            reply = (
                f"I've added {qty}x **{name}** (`{sku}`) to your cart! "
                f"🎉 **Active Promotion ({camp_discount_pct}% OFF)**: Click **'🛡️ Check Out via Commerce Guardian'** "
                f"on the right panel to authorize your discounted price of **₹{disc_subtotal/100:.2f}** (Catalog: ₹{cart.subtotal/100:.2f})."
            )
        else:
            reply = (
                f"I've added {qty}x **{name}** (`{sku}`) to your cart! "
                f"Your cart subtotal is **₹{cart.subtotal/100:.2f}**. "
                f"Click **'🛡️ Check Out via Commerce Guardian'** on the right panel to proceed."
            )

        # Generate recommendations
        recs = await generate_upsell_recommendations(
            merchant_id=state["merchant_id"],
            buyer_id=state["buyer_id"],
            last_added_sku=sku,
            current_subtotal=cart.subtotal,
            session=session,
        )
        return {
            "cart": cart,
            "cart_history": cart_history,
            "reply": reply,
            "recommendations": recs,
        }
    else:
        return {
            "reply": f"Could not add to cart: {add_res.get('error')}",
        }


async def conversational_chat_node(state: CommerceGraphState, session: AsyncSession = None) -> Dict[str, Any]:
    """
    Node: Handles conversational shopping via Resilient Multi-Provider Pool (Groq/Gemini/OpenRouter).
    """
    ai_provider = get_ai_provider()
    history = state.get("history", [])
    history.append({"role": "user", "content": state["message"]})

    products = await search_products(merchant_id=state["merchant_id"], session=session)
    catalog_summary = "\n".join([f"- {p.name} (SKU: {p.sku}, Category: {p.category}, Price: ₹{p.price/100:.2f})" for p in products])
    
    grounded_prompt = (
        f"{COMMERCE_AGENT_SYSTEM_PROMPT}\n\n"
        f"OFFICIAL STORE CATALOG:\n{catalog_summary}\n\n"
        f"CURRENT CART: {len(state['cart'].items)} items, Subtotal: ₹{state['cart'].subtotal/100:.2f}\n"
        f"Capabilities: You support 1-click add, checkout, and state rollbacks (buyer can type 'undo' to go back)."
    )

    reply = await ai_provider.generate_text(
        system_prompt=grounded_prompt,
        messages=history,
        temperature=0.2,
    )
    history.append({"role": "assistant", "content": reply})

    from app.commerce_agent.service import extract_sku_from_text, match_product_keyword, _session_last_sku
    last_mentioned = extract_sku_from_text(reply) or match_product_keyword(reply) or extract_sku_from_text(state["message"]) or match_product_keyword(state["message"])
    if last_mentioned:
        _session_last_sku[state["session_id"]] = last_mentioned

    return {
        "reply": reply,
        "history": history,
    }


# ------------------------------------------------------------------------------
# 2. Graph Pipeline Orchestrator (LangGraph Pattern)
# ------------------------------------------------------------------------------

class CommerceLangGraph:
    """
    LangGraph-compatible State Graph Engine for Agentic Commerce.
    Executes conditional node routing with state checkpointing and backward transitions.
    """

    async def ainvoke(self, state: CommerceGraphState, session: AsyncSession = None) -> CommerceGraphState:
        # 1. Route Intent
        route_update = await intent_router_node(state, session)
        state.update(route_update)

        action = state.get("action", "chat")

        # 2. Execute Branch
        if action == "rollback":
            node_res = await rollback_node(state, session)
            state.update(node_res)
        elif action == "add":
            node_res = await cart_mutation_node(state, session)
            state.update(node_res)
        elif action == "clear":
            state["cart"].items = []
            state["cart"].subtotal = 0
            state["reply"] = "Your cart has been cleared."
            state["recommendations"] = []
        elif action == "checkout":
            if not state["cart"].items:
                state["reply"] = "Your cart is currently empty! Please add an item first."
            else:
                items_summary = ", ".join(f"{item.qty}x {item.sku}" for item in state["cart"].items)
                state["reply"] = (
                    f"Your cart with {items_summary} (Total: ₹{state['cart'].subtotal/100:.2f}) is ready! "
                    f"Click **'🛡️ Check Out via Commerce Guardian'** on the right panel to execute the security evaluation."
                )
        else:
            node_res = await conversational_chat_node(state, session)
            state.update(node_res)

        return state


# Singleton graph instance
commerce_graph = CommerceLangGraph()
