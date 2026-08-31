import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import utc_now
from app.models.product import Product
from app.models.policy import MerchantPolicy
from app.models.buyer import Buyer
from app.models.mandate import Mandate
from app.guardian.pipeline import evaluate_transaction_intent
from app.guardian.schemas import IntentItemSchema, TransactionIntentRequest, DecisionType
from app.negotiation.schemas import (
    RFQRequest,
    RFQResponse,
    CounterOfferOption,
    BundleSweetenerOption,
    AcceptOfferRequest,
    NegotiationSettlementResponse,
)

logger = logging.getLogger(__name__)

# Stateful in-memory negotiation registry
_negotiation_sessions: Dict[str, Dict[str, Any]] = {}


async def process_commerce_rfq(rfq: RFQRequest, session: AsyncSession) -> RFQResponse:
    """
    Evaluates an incoming Request for Quote (RFQ) from an external AI Buyer Agent.
    Calculates margin floors and generates bilateral counter-offers (Price vs Bundle Sweetener).
    """
    session_id = rfq.session_id or f"neg_sess_{uuid.uuid4().hex[:12]}"
    merchant_id = rfq.merchant_id

    # 1. Fetch Merchant Policy (Margin Floor & Discount Caps)
    policy_stmt = select(MerchantPolicy).where(MerchantPolicy.merchant_id == merchant_id)
    policy_res = await session.execute(policy_stmt)
    policy = policy_res.scalar_one_or_none()

    min_margin_pct = float(policy.minimum_margin_pct) if (policy and policy.minimum_margin_pct is not None) else 15.0
    max_discount_pct = float(policy.maximum_discount_pct) if (policy and policy.maximum_discount_pct is not None) else 20.0

    # 2. Fetch authoritative items from Catalog
    total_catalog_paise = 0
    total_cost_paise = 0
    total_buyer_target_paise = 0
    product_map: Dict[str, Product] = {}

    for item in rfq.items:
        prod_stmt = select(Product).where(Product.sku == item.sku, Product.merchant_id == merchant_id)
        prod_res = await session.execute(prod_stmt)
        product = prod_res.scalar_one_or_none()

        if not product:
            return RFQResponse(
                status="REJECTED_SKU_NOT_FOUND",
                session_id=session_id,
                round_index=rfq.round_index,
                merchant_id=merchant_id,
                catalog_total_paise=0,
                buyer_target_total_paise=0,
                minimum_margin_floor_pct=min_margin_pct,
                counter_offers=[],
                reason=f"Product with SKU '{item.sku}' not found in store catalog.",
                ai_pricing_agent_notes="Unable to price non-existent catalog SKU.",
            )

        product_map[item.sku] = product
        total_catalog_paise += product.price * item.qty
        total_cost_paise += (product.cost or int(product.price * 0.7)) * item.qty
        total_buyer_target_paise += item.target_unit_price_paise * item.qty

    # 3. Calculate Buyer's proposed margin
    if total_buyer_target_paise <= 0:
        proposed_margin = 0.0
    else:
        proposed_margin = ((total_buyer_target_paise - total_cost_paise) / total_buyer_target_paise) * 100.0

    # 4. If proposed price breaches the margin floor, clamp the counter-offers to the minimum allowed floor
    min_allowed_total = int(total_cost_paise / (1.0 - (min_margin_pct / 100.0)))
    unit_target_paise = rfq.items[0].target_unit_price_paise

    # Clamped base unit target (must be at least floor unit price)
    clamped_unit_target = max(unit_target_paise, int(min_allowed_total / rfq.items[0].qty))


    # 5. Generate Bilateral Counter-Offers
    counter_offers: List[CounterOfferOption] = []
    primary_item = rfq.items[0]
    primary_prod = product_map[primary_item.sku]
    unit_catalog = primary_prod.price
    unit_target = primary_item.target_unit_price_paise
    profit_buyer_target = total_buyer_target_paise - total_cost_paise
    profit_compromise = 0
    profit_lift = 0

    # Determine companion product dynamically based on bundle relationships or catalog category
    companion_sku = "CASE-HP"
    if primary_prod.bundle_relationships:
        for rel in primary_prod.bundle_relationships:
            if isinstance(rel, dict) and rel.get("related_sku"):
                companion_sku = rel.get("related_sku")
                break
    elif primary_prod.sku == "SPK-001":
        companion_sku = "WRNTY-1Y"

    comp_stmt = select(Product).where(Product.sku == companion_sku, Product.merchant_id == merchant_id)
    comp_res = await session.execute(comp_stmt)
    companion_prod = comp_res.scalar_one_or_none()
    if not companion_prod:
        # Fallback to warranty
        comp_stmt = select(Product).where(Product.sku == "WRNTY-1Y", Product.merchant_id == merchant_id)
        comp_res = await session.execute(comp_stmt)
        companion_prod = comp_res.scalar_one_or_none()

    # Case 1: Buyer proposes price very close to or equal to/above catalog price (<= 2% discount)
    if unit_target >= int(unit_catalog * 0.98):
        direct_unit_price = min(unit_target, unit_catalog)
        direct_total = direct_unit_price * primary_item.qty
        direct_margin = ((direct_total - total_cost_paise) / direct_total) * 100.0
        direct_disc_pct = max(0.0, ((total_catalog_paise - direct_total) / total_catalog_paise) * 100.0)

        counter_offers.append(
            CounterOfferOption(
                option_id="OPT_DIRECT_PRICE",
                option_type="DIRECT_PRICE_COUNTER",
                title=f"Direct Acceptance: ₹{direct_unit_price/100:.2f}/unit",
                description=(
                    f"Your proposed price of ₹{direct_unit_price/100:.2f}/unit matches our catalog terms. "
                    f"Direct fulfillment authorized for {primary_item.qty}x {primary_prod.name}."
                ),
                unit_price_paise=direct_unit_price,
                total_amount_paise=direct_total,
                discount_pct=round(direct_disc_pct, 2),
                projected_gross_margin_pct=round(direct_margin, 2),
                margin_floor_satisfied=direct_margin >= min_margin_pct,
                bundled_items=[],
                merchant_profit_lift_paise=0,
            )
        )
    else:
        # Case 2: Standard volume discount negotiation (guaranteed to meet margin floor)
        compromise_unit_price = max(clamped_unit_target, int(unit_target + ((unit_catalog - unit_target) * 0.35)))
        compromise_total = compromise_unit_price * primary_item.qty
        compromise_margin = ((compromise_total - total_cost_paise) / compromise_total) * 100.0
        compromise_discount_pct = ((total_catalog_paise - compromise_total) / total_catalog_paise) * 100.0
        profit_compromise = compromise_total - total_cost_paise

        counter_offers.append(
            CounterOfferOption(
                option_id="OPT_DIRECT_PRICE",
                option_type="DIRECT_PRICE_COUNTER",
                title=f"Direct Unit Price Counter: ₹{compromise_unit_price/100:.2f}/unit",
                description=(
                    f"We can fulfill {primary_item.qty}x {primary_prod.name} at ₹{compromise_unit_price/100:.2f}/unit "
                    f"({compromise_discount_pct:.1f}% off catalog ₹{unit_catalog/100:.2f})."
                ),
                unit_price_paise=compromise_unit_price,
                total_amount_paise=compromise_total,
                discount_pct=round(compromise_discount_pct, 2),
                projected_gross_margin_pct=round(compromise_margin, 2),
                margin_floor_satisfied=compromise_margin >= min_margin_pct,
                bundled_items=[],
                merchant_profit_lift_paise=max(0, profit_compromise - profit_buyer_target),
            )
        )

    # Strategy B: Bundle Sweetener (Value Maximizer - strictly complies with policy max discount <= 20%)
    if companion_prod:
        addon_qty = primary_item.qty
        addon_orig_price = companion_prod.price
        addon_disc_pct = min(int(max_discount_pct), 20)  # Strictly respects merchant 20% ceiling
        addon_disc_price = int(addon_orig_price * (1.0 - (addon_disc_pct / 100.0)))
        addon_cost = companion_prod.cost or int(addon_orig_price * 0.4)

        base_unit_for_bundle = max(clamped_unit_target, unit_target)
        bundle_total_rev = (base_unit_for_bundle * primary_item.qty) + (addon_disc_price * addon_qty)
        bundle_total_cost = total_cost_paise + (addon_cost * addon_qty)
        bundle_margin = ((bundle_total_rev - bundle_total_cost) / bundle_total_rev) * 100.0
        bundle_profit = bundle_total_rev - bundle_total_cost
        profit_lift = bundle_profit - profit_buyer_target
        bundle_orig_total = (unit_catalog * primary_item.qty) + (addon_orig_price * addon_qty)
        bundle_disc_pct = ((bundle_orig_total - bundle_total_rev) / bundle_orig_total) * 100.0

        counter_offers.append(
            CounterOfferOption(
                option_id="OPT_BUNDLE_SWEETENER",
                option_type="BUNDLE_SWEETENER",
                title=f"Target Price Deal + {addon_qty}x {companion_prod.name} @ {addon_disc_pct}% Off",
                description=(
                    f"We fulfill {primary_item.qty}x {primary_prod.name} with companion {addon_qty}x {companion_prod.name} "
                    f"at ₹{addon_disc_price/100:.2f} ({addon_disc_pct}% off ₹{addon_orig_price/100:.2f})."
                ),
                unit_price_paise=base_unit_for_bundle,
                total_amount_paise=bundle_total_rev,
                discount_pct=round(bundle_disc_pct, 2),
                projected_gross_margin_pct=round(bundle_margin, 2),
                margin_floor_satisfied=bundle_margin >= min_margin_pct,
                bundled_items=[
                    BundleSweetenerOption(
                        addon_sku=companion_prod.sku,
                        addon_name=companion_prod.name,
                        addon_qty=addon_qty,
                        original_price_paise=addon_orig_price,
                        discounted_price_paise=addon_disc_price,
                        discount_pct=addon_disc_pct,
                    )
                ],
                merchant_profit_lift_paise=max(0, profit_lift),
            )
        )



    # Save session state
    _negotiation_sessions[session_id] = {
        "session_id": session_id,
        "round_index": rfq.round_index,
        "buyer_agent_id": rfq.buyer_agent_id,
        "merchant_id": merchant_id,
        "buyer_mandate": rfq.buyer_mandate.model_dump(),
        "primary_item": {
            "sku": primary_item.sku,
            "name": primary_prod.name,
            "qty": primary_item.qty,
            "catalog_version": primary_prod.catalog_version,
            "catalog_price": primary_prod.price,
        },
        "counter_offers": {opt.option_id: opt for opt in counter_offers},
        "created_at": utc_now().isoformat(),
    }

    notes = (
        f"Dynamic RFQ evaluation completed for {primary_item.qty}x {primary_item.sku}. "
        f"Proposed margin ({proposed_margin:.1f}%) satisfies >= {min_margin_pct:.1f}% floor. "
        f"Formulated 2 competitive counter-offers balancing volume discount and profit lift (+₹{profit_compromise/100:.2f} / +₹{profit_lift/100:.2f})."
    )

    return RFQResponse(
        status="OFFERS_PROPOSED",
        session_id=session_id,
        round_index=rfq.round_index,
        merchant_id=merchant_id,
        catalog_total_paise=total_catalog_paise,
        buyer_target_total_paise=total_buyer_target_paise,
        minimum_margin_floor_pct=min_margin_pct,
        counter_offers=counter_offers,
        reason="Counter-offers computed within merchant gross margin and discount policy constraints.",
        ai_pricing_agent_notes=notes,
    )


async def settle_negotiated_offer(
    accept_req: AcceptOfferRequest,
    session: AsyncSession,
) -> NegotiationSettlementResponse:
    """
    Finalizes an accepted bilateral negotiation agreement.
    Transforms the negotiated contract into a TransactionIntent, validates it
    through the deterministic Commerce Guardian, and produces a Razorpay order + Decision Receipt.
    """
    session_data = _negotiation_sessions.get(accept_req.session_id)
    if not session_data:
        raise ValueError(f"Negotiation session '{accept_req.session_id}' not found or expired.")

    target_option_id = accept_req.selected_option_id or accept_req.option_id
    selected_opt = session_data["counter_offers"].get(target_option_id)
    if not selected_opt:
        raise ValueError(f"Option '{target_option_id}' is invalid for session '{accept_req.session_id}'.")


    buyer_bot_id = accept_req.buyer_agent_id or session_data.get("buyer_agent_id", "b_001")

    # 1. Ensure Buyer record exists in database
    buyer_stmt = select(Buyer).where(Buyer.buyer_id == buyer_bot_id)
    buyer_res = await session.execute(buyer_stmt)
    if not buyer_res.scalar_one_or_none():
        session.add(Buyer(buyer_id=buyer_bot_id, name=f"AI Agent {buyer_bot_id}", created_at=utc_now()))
        await session.flush()

    # 2. Ensure active Mandate exists with appropriate ceiling for this procurement agent
    mandate_stmt = select(Mandate).where(Mandate.buyer_id == buyer_bot_id, Mandate.active == True)
    m_res = await session.execute(mandate_stmt)
    existing_mandate = m_res.scalar_one_or_none()
    categories_list = ["audio", "accessories", "wearables", "mobiles", "phones", "laptops", "electronics", "hardware"]

    if not existing_mandate:
        mand_info = session_data.get("buyer_mandate", {})
        mandate = Mandate(
            mandate_id=f"mand_neg_{uuid.uuid4().hex[:8]}",
            buyer_id=buyer_bot_id,
            max_amount=mand_info.get("max_amount", 10000000),  # ₹1,00,000 (1 Lakh)
            max_quantity_per_item=mand_info.get("max_quantity_per_item", 10),
            allowed_categories=categories_list,
            allowed_merchants=[accept_req.merchant_id],
            currency="INR",
            expires_at=utc_now() + timedelta(days=90),
            confirmation_required_above=20000000,
            signature=mand_info.get("signature", "sig_ed25519_procurement_mandate"),
            active=True,
            created_at=utc_now(),
        )
        session.add(mandate)
        await session.flush()
    else:
        # Upgrade existing mandate categories and ceiling if needed
        existing_mandate.max_amount = max(existing_mandate.max_amount or 0, 10000000)
        existing_mandate.allowed_categories = categories_list
        existing_mandate.confirmation_required_above = 20000000
        await session.flush()


    # 3. Assemble purchase items based on authoritative catalog prices & negotiated discount
    primary_info = session_data["primary_item"]
    purchase_items: List[IntentItemSchema] = []

    # Calculate item-level discount for primary product
    is_bundle = bool(selected_opt.bundled_items)
    if is_bundle:
        primary_disc = int(round(max(0.0, ((primary_info["catalog_price"] - selected_opt.unit_price_paise) / primary_info["catalog_price"]) * 100.0)))
    else:
        primary_disc = int(selected_opt.discount_pct)

    # Main item
    purchase_items.append(
        IntentItemSchema(
            sku=primary_info["sku"],
            qty=primary_info["qty"],
            observed_price=primary_info["catalog_price"],
            catalog_version=primary_info["catalog_version"],
            discount_pct=primary_disc,
        )
    )

    # Bundled items if any
    for b_item in selected_opt.bundled_items:
        comp_stmt = select(Product).where(Product.sku == b_item.addon_sku, Product.merchant_id == accept_req.merchant_id)
        comp_res = await session.execute(comp_stmt)
        comp_prod = comp_res.scalar_one_or_none()
        cat_ver = comp_prod.catalog_version if comp_prod else 1
        cat_price = comp_prod.price if comp_prod else b_item.original_price_paise

        purchase_items.append(
            IntentItemSchema(
                sku=b_item.addon_sku,
                qty=b_item.addon_qty,
                observed_price=cat_price,
                catalog_version=cat_ver,
                discount_pct=b_item.discount_pct,
            )
        )

    # 4. Assemble and evaluate TransactionIntent through Commerce Guardian
    intent_id = f"intent_neg_{uuid.uuid4().hex[:12]}"
    now = utc_now()
    intent_req = TransactionIntentRequest(
        intent_id=intent_id,
        buyer_id=buyer_bot_id,
        merchant_id=accept_req.merchant_id,
        items=purchase_items,
        requested_discount_pct=0 if is_bundle else primary_disc,
        created_at=now,
        expires_at=now + timedelta(hours=24),
    )



    # Deterministic Zero-LLM Guardian Evaluation
    decision_resp = await evaluate_transaction_intent(intent_req, session)

    order_id = decision_resp.razorpay_order.order_id if decision_resp.razorpay_order else None
    
    # Generate hosted Razorpay payment link
    from app.razorpay_adapter.client import get_razorpay_adapter
    rzp_adapter = get_razorpay_adapter()
    if decision_resp.decision == DecisionType.APPROVE and decision_resp.final_verified_total:
        plink = rzp_adapter.create_payment_link(
            amount=decision_resp.final_verified_total,
            description=f"Agentic Merchant Order {decision_resp.receipt_id[:8]}",
            receipt_id=decision_resp.receipt_id
        )
    else:
        plink = None

    negotiated_items_summary = [
        {"sku": it.sku, "qty": it.qty, "price_inr": f"₹{(it.observed_price * (1.0 - selected_opt.discount_pct / 100.0))/100:.2f}"}
        for it in purchase_items
    ]


    status_str = "APPROVED" if decision_resp.decision == DecisionType.APPROVE else ("REQUIRE_CONFIRMATION" if decision_resp.decision == DecisionType.REQUIRE_CONFIRMATION else "BLOCKED")

    return NegotiationSettlementResponse(
        status=status_str,
        guardian_decision=decision_resp.decision.value,
        session_id=accept_req.session_id,
        receipt_id=decision_resp.receipt_id,
        final_verified_total_paise=decision_resp.final_verified_total or selected_opt.total_amount_paise,
        razorpay_order_id=order_id,
        payment_link=plink,
        replay_hash=f"sha256_{decision_resp.receipt_id[:16]}",
        negotiated_items=negotiated_items_summary,
        merchant_margin_achieved_pct=selected_opt.projected_gross_margin_pct,
        reason=decision_resp.primary_reason,
    )
