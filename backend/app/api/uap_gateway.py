import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.service import get_product, search_products
from app.core.base import generate_uuid, utc_now
from app.core.db import get_session
from app.core.enums import DecisionType
from app.guardian.pipeline import evaluate_transaction_intent
from app.guardian.schemas import IntentItemSchema, TransactionIntentRequest
from app.policy.service import get_active_policy

logger = logging.getLogger(__name__)
router = APIRouter(tags=["UAP & Agent-to-Agent Commerce Gateway"])


# ------------------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------------------

class MachineBuyerMandate(BaseModel):
    buyer_id: str
    max_amount: int = Field(default=1000000, description="Max amount in paise")
    max_quantity_per_item: int = Field(default=5, description="Max units per SKU")
    currency: str = "INR"
    signature: Optional[str] = None


class MachinePurchaseRequest(BaseModel):
    buyer_agent_id: str = Field(..., description="External AI Buyer Identifier (e.g. agent_gpt4_procure_007)")
    buyer_mandate: MachineBuyerMandate
    purchase_items: List[IntentItemSchema]
    agent_callback_url: Optional[str] = None


class MachinePurchaseResponse(BaseModel):
    status: str
    guardian_decision: str
    receipt_id: str
    final_verified_total: Optional[int]
    razorpay_order_id: Optional[str] = None
    payment_link: Optional[str] = None
    replay_hash: Optional[str] = None
    reason: Optional[str] = None
    high_value_notification: Optional[Dict[str, Any]] = None


class BundleMarginCheckRequest(BaseModel):
    merchant_id: str = "m_001"
    parent_sku: str
    addon_sku: str
    discount_pct: int = Field(default=30, ge=0, le=100)


class BundleMarginCheckResponse(BaseModel):
    approved: bool
    bundle_price: int
    parent_price: int
    discounted_addon_price: int
    total_cost: int
    projected_margin_pct: float
    min_margin_pct: float
    reason: str


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------

@router.get("/.well-known/agent.json")
async def get_uap_agent_manifest(
    merchant_id: str = "m_001",
    session: AsyncSession = Depends(get_session),
):
    """
    Universal Agent Protocol (UAP) & Model Context Protocol (MCP) Manifest.
    Allows external autonomous agents (ChatGPT, Claude, LangChain, AutoGPT) to auto-discover
    merchant catalog, prices, and allowed purchase APIs.
    """
    products = await search_products(merchant_id=merchant_id, session=session)
    catalog_version = max((p.catalog_version for p in products), default=1)

    return {
        "protocol": "UAP-1.0",
        "spec_compatibility": ["UAP-1.0", "ACP-Draft", "AP2", "x402", "MCP-2024-11-05"],
        "name": "AeroSound Official Store",
        "merchant_id": merchant_id,
        "catalog_version": catalog_version,
        "description": "Agentic Merchant OS flagship audio store with deterministic Guardian protection",
        "supported_payment_rails": ["razorpay_test_v1"],
        "capabilities": {
            "conversational_checkout": True,
            "headless_a2a_checkout": True,
            "instant_replay_audit": True,
            "margin_safe_bundling": True,
        },
        "tools": [
            {
                "name": "search_catalog",
                "description": "Query live product catalog with authoritative prices and stock",
                "endpoint": "/catalog/products",
                "method": "GET",
            },
            {
                "name": "submit_machine_purchase",
                "description": "Submit a signed mandate and transaction intent for deterministic Guardian authorization and Razorpay order creation",
                "endpoint": "/agent/v1/machine-purchase",
                "method": "POST",
            },
            {
                "name": "check_bundle_margin",
                "description": "Calculate margin-safe bundle discount headroom",
                "endpoint": "/catalog/bundles/margin-check",
                "method": "POST",
            },
        ],
        "catalog_summary": [
            {
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "inventory": p.inventory,
            }
            for p in products[:8]
        ],
    }


@router.post("/agent/v1/machine-purchase", response_model=MachinePurchaseResponse)
async def submit_machine_purchase(
    body: MachinePurchaseRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Headless Agent-to-Agent (A2A) Purchase Endpoint.
    Allows external AI buyer agents to execute a complete purchase flow programmatically
    through the deterministic Commerce Guardian with zero human UI.
    """
    now = utc_now()
    intent_id = generate_uuid()

    # Assemble TransactionIntentRequest
    intent_req = TransactionIntentRequest(
        intent_id=intent_id,
        buyer_id=body.buyer_mandate.buyer_id,
        merchant_id="m_001",
        items=body.purchase_items,
        requested_discount_pct=0,
        created_at=now,
        expires_at=now.replace(hour=23, minute=59, second=59),
    )

    # Deterministic Guardian Evaluation
    decision_resp = await evaluate_transaction_intent(intent_req, session)

    if decision_resp.decision == DecisionType.APPROVE:
        order_id = decision_resp.razorpay_order.order_id if decision_resp.razorpay_order else None
        payment_link = f"https://api.razorpay.com/v1/checkout/hosted?order_id={order_id}" if order_id else None

        return MachinePurchaseResponse(
            status="APPROVED",
            guardian_decision="APPROVE",
            receipt_id=decision_resp.receipt_id,
            final_verified_total=decision_resp.final_verified_total,
            razorpay_order_id=order_id,
            payment_link=payment_link,
            replay_hash=f"sha256_{decision_resp.receipt_id[:16]}",
            reason=decision_resp.primary_reason,
        )
    elif decision_resp.decision == DecisionType.REQUIRE_CONFIRMATION:
        plink = None
        if decision_resp.high_value_notification:
            plink = decision_resp.high_value_notification.get("payment_link")
        return MachinePurchaseResponse(
            status="REQUIRE_CONFIRMATION",
            guardian_decision="REQUIRE_CONFIRMATION",
            receipt_id=decision_resp.receipt_id,
            final_verified_total=decision_resp.final_verified_total,
            razorpay_order_id=None,
            payment_link=plink,
            high_value_notification=decision_resp.high_value_notification,
            replay_hash=f"sha256_{decision_resp.receipt_id[:16]}",
            reason=decision_resp.primary_reason,
        )
    else:
        return MachinePurchaseResponse(
            status="BLOCKED",
            guardian_decision="BLOCK",
            receipt_id=decision_resp.receipt_id,
            final_verified_total=None,
            razorpay_order_id=None,
            payment_link=None,
            reason=decision_resp.primary_reason,
        )


@router.post("/catalog/bundles/margin-check", response_model=BundleMarginCheckResponse)
async def check_bundle_margin(
    body: BundleMarginCheckRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Evaluates dynamic bundle discount headroom against merchant minimum gross margin policy.
    """
    parent = await get_product(body.parent_sku, session)
    addon = await get_product(body.addon_sku, session)
    policy = await get_active_policy(body.merchant_id, session)

    if not parent or not addon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {body.parent_sku} or {body.addon_sku}"
        )

    min_margin = policy.minimum_margin_pct if policy else 15.0

    discounted_addon_price = int(addon.price * (1.0 - (body.discount_pct / 100.0)))
    bundle_price = parent.price + discounted_addon_price
    total_cost = parent.cost + addon.cost

    if bundle_price <= 0:
        raise HTTPException(status_code=400, detail="Invalid bundle price calculation")

    projected_margin = ((bundle_price - total_cost) / bundle_price) * 100.0
    approved = projected_margin >= min_margin

    reason = (
        f"Approved: Resulting bundle margin of {projected_margin:.1f}% exceeds merchant threshold of {min_margin:.1f}%"
        if approved
        else f"Blocked: Resulting bundle margin of {projected_margin:.1f}% is below merchant threshold of {min_margin:.1f}%"
    )

    return BundleMarginCheckResponse(
        approved=approved,
        bundle_price=bundle_price,
        parent_price=parent.price,
        discounted_addon_price=discounted_addon_price,
        total_cost=total_cost,
        projected_margin_pct=round(projected_margin, 2),
        min_margin_pct=min_margin,
        reason=reason,
    )
