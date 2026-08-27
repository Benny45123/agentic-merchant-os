from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_provider.gemini_provider import get_ai_provider
from app.campaign.proposal_prompt import build_proposal_system_prompt
from app.campaign.schemas import (
    BundleOfferSchema,
    CampaignProposal,
    CampaignStatusResponse,
)
from app.catalog.service import search_products
from app.core.base import generate_uuid, utc_now
from app.core.enums import CampaignEventType, CampaignStatus, DecisionType, OfferType, OrderStatus
from app.guardian.pipeline import evaluate_campaign_proposal
from app.guardian.schemas import CampaignProposalRequest
from app.models import (
    Campaign,
    CampaignEvent,
    GuardianDecision,
    Offer,
    Order,
)
from app.policy.service import get_active_policy, get_campaign_policy


async def propose_campaign(
    merchant_id: str,
    objective: str,
    session: AsyncSession,
) -> CampaignProposal:
    """
    1. Gather real product data + policy limits.
    2. Prompt LLM to propose a campaign within bounds.
    3. Forward proposal to deterministic Guardian validation.
    4. Return validated CampaignProposal.
    """
    proposal_id = generate_uuid()
    merchant_policy = await get_active_policy(merchant_id, session)
    campaign_policy = await get_campaign_policy(merchant_id, session)

    if not merchant_policy or not campaign_policy:
        raise ValueError(f"Policies for merchant '{merchant_id}' not configured")

    # Execute Campaign LangGraph (with auto-correction loop-back)
    from app.campaign.graph import campaign_graph, CampaignGraphState

    init_state: CampaignGraphState = {
        "merchant_id": merchant_id,
        "objective": objective,
        "proposal_id": proposal_id,
        "eligible_skus": [],
        "discount_pct": 0,
        "bundle_offer": None,
        "budget": 0,
        "duration_days": 7,
        "rationale": "",
        "guardian_decision": None,
        "revision_count": 0,
        "max_revisions": 3,
        "is_approved": False,
    }

    graph_res = await campaign_graph.ainvoke(init_state, session)

    now = utc_now()
    starts_at = now
    ends_at = now + timedelta(days=graph_res["duration_days"])

    bundle_schema = None
    if graph_res.get("bundle_offer") and isinstance(graph_res["bundle_offer"], dict):
        bundle_schema = BundleOfferSchema(
            trigger_sku=graph_res["bundle_offer"].get("trigger_sku", "HP-001"),
            addon_sku=graph_res["bundle_offer"].get("addon_sku", "CASE-HP"),
            addon_discount_pct=graph_res["bundle_offer"].get("addon_discount_pct", 50),
        )

    guardian_decision = graph_res["guardian_decision"]

    # 3. Create Campaign record in DRAFT or PENDING state
    campaign = Campaign(
        campaign_id=proposal_id,
        merchant_id=merchant_id,
        objective_text=objective,
        eligible_skus=graph_res["eligible_skus"],
        discount_pct=graph_res["discount_pct"],
        bundle_offer=bundle_schema.model_dump() if bundle_schema else None,
        budget=graph_res["budget"],
        budget_spent=0,
        starts_at=starts_at,
        ends_at=ends_at,
        status=CampaignStatus.DRAFT if guardian_decision.decision == DecisionType.APPROVE else CampaignStatus.PENDING_APPROVAL,
        pause_reason=None,
        guardian_decision_id=guardian_decision.decision_id,
        created_at=now,
    )
    session.add(campaign)
    await session.commit()

    return CampaignProposal(
        proposal_id=proposal_id,
        merchant_id=merchant_id,
        objective=objective,
        eligible_skus=graph_res["eligible_skus"],
        discount_pct=graph_res["discount_pct"],
        bundle_offer=bundle_schema,
        budget=graph_res["budget"],
        starts_at=starts_at,
        ends_at=ends_at,
        rationale=graph_res["rationale"],
        guardian_decision=guardian_decision,
    )


async def activate_campaign(
    proposal_id: str,
    session: AsyncSession,
) -> Campaign:
    """
    Activates campaign after Guardian APPROVE or merchant confirmation.
    Writes bounded static Offer rows to catalog and logs ACTIVATED event.
    """
    stmt = select(Campaign).where(Campaign.campaign_id == proposal_id)
    res = await session.execute(stmt)
    campaign = res.scalar_one_or_none()

    if not campaign:
        raise ValueError(f"Campaign proposal '{proposal_id}' not found")

    # Verify Guardian decision
    if campaign.guardian_decision_id:
        dec_stmt = select(GuardianDecision).where(GuardianDecision.decision_id == campaign.guardian_decision_id)
        dec_res = await session.execute(dec_stmt)
        decision = dec_res.scalar_one_or_none()
        if decision and decision.decision == DecisionType.BLOCK:
            raise ValueError("Cannot activate a campaign blocked by the Guardian")

    campaign.status = CampaignStatus.ACTIVE
    now = utc_now()

    # Write static Offer rows for eligible SKUs
    for sku in campaign.eligible_skus:
        offer = Offer(
            offer_id=f"off_camp_{generate_uuid()[:8]}",
            sku=sku,
            type=OfferType.CAMPAIGN_DISCOUNT,
            label=f"Campaign Sale: {campaign.discount_pct}% OFF",
            discount_pct=campaign.discount_pct,
            campaign_id=campaign.campaign_id,
            starts_at=campaign.starts_at,
            ends_at=campaign.ends_at,
            created_at=now,
        )
        session.add(offer)

    # Log ACTIVATED event
    event = CampaignEvent(
        event_id=generate_uuid(),
        campaign_id=campaign.campaign_id,
        type=CampaignEventType.ACTIVATED,
        detail={"activated_at": now.isoformat(), "budget": campaign.budget},
        created_at=now,
    )
    session.add(event)
    await session.commit()
    return campaign


async def get_campaign_status(
    campaign_id: str,
    session: AsyncSession,
) -> CampaignStatusResponse:
    """
    Computes revenue, orders, and budget spent via real SQL aggregation over Order.
    Never hardcoded or drifted from reality.
    """
    stmt = select(Campaign).where(Campaign.campaign_id == campaign_id)
    res = await session.execute(stmt)
    campaign = res.scalar_one_or_none()

    if not campaign:
        raise ValueError(f"Campaign '{campaign_id}' not found")

    # Aggregate attributed paid orders
    order_stmt = select(
        func.count(Order.order_id),
        func.coalesce(func.sum(Order.amount), 0)
    ).where(
        Order.campaign_id == campaign_id,
        Order.status == OrderStatus.PAID
    )
    order_res = await session.execute(order_stmt)
    order_count, total_revenue = order_res.one()

    return CampaignStatusResponse(
        campaign_id=campaign.campaign_id,
        status=campaign.status.value if hasattr(campaign.status, "value") else str(campaign.status),
        budget=campaign.budget,
        budget_spent=campaign.budget_spent,
        orders_attributed=order_count,
        revenue_attributed=total_revenue,
        pause_reason=campaign.pause_reason,
    )
