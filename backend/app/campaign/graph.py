import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_provider.gemini_provider import get_ai_provider
from app.campaign.proposal_prompt import build_proposal_system_prompt
from app.catalog.service import search_products
from app.core.base import generate_uuid, utc_now
from app.core.enums import CampaignStatus, DecisionType
from app.guardian.pipeline import evaluate_campaign_proposal
from app.guardian.schemas import CampaignProposalRequest
from app.models import Campaign
from app.policy.service import get_active_policy, get_campaign_policy

logger = logging.getLogger(__name__)


class CampaignGraphState(TypedDict):
    """
    LangGraph State Schema for Autonomous Campaign Orchestration.
    Supports auto-revision loop-back when proposals breach merchant policies.
    """
    merchant_id: str
    objective: str
    proposal_id: str
    eligible_skus: List[str]
    discount_pct: int
    bundle_offer: Optional[Dict[str, Any]]
    budget: int
    duration_days: int
    rationale: str
    guardian_decision: Optional[Any]
    revision_count: int
    max_revisions: int
    is_approved: bool


# ------------------------------------------------------------------------------
# 1. Campaign Graph Nodes
# ------------------------------------------------------------------------------

async def synthesize_proposal_node(state: CampaignGraphState, session: AsyncSession) -> Dict[str, Any]:
    """Node 1: Synthesizes initial campaign strategy from objective using Multi-Provider LLM."""
    merchant_id = state["merchant_id"]
    objective = state["objective"]

    merchant_policy = await get_active_policy(merchant_id, session)
    campaign_policy = await get_campaign_policy(merchant_id, session)
    products = await search_products(merchant_id=merchant_id, session=session)

    ai_provider = get_ai_provider()
    system_prompt = build_proposal_system_prompt(merchant_policy, campaign_policy, products)
    
    llm_resp = await ai_provider.generate_structured_json(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": f"Merchant Objective: {objective}"}],
        temperature=0.1,
    )

    eligible_skus = llm_resp.get("eligible_skus") or ["HP-001"]
    discount_pct = min(llm_resp.get("discount_pct", 10), campaign_policy.allowed_campaign_discount_pct)
    bundle_data = llm_resp.get("bundle_offer")
    budget = llm_resp.get("budget", campaign_policy.campaign_budget_default)
    duration_days = min(llm_resp.get("duration_days", 7), 14)
    rationale = llm_resp.get("rationale") or "Boost top audio products while preserving healthy merchant margins."

    return {
        "eligible_skus": eligible_skus,
        "discount_pct": discount_pct,
        "bundle_offer": bundle_data,
        "budget": budget,
        "duration_days": duration_days,
        "rationale": rationale,
    }


async def guardian_validation_node(state: CampaignGraphState, session: AsyncSession) -> Dict[str, Any]:
    """Node 2: Deterministic Guardian pre-validation firewall."""
    now = utc_now()
    starts_at = now
    ends_at = now + timedelta(days=state["duration_days"])

    guardian_req = CampaignProposalRequest(
        proposal_id=state["proposal_id"],
        merchant_id=state["merchant_id"],
        objective=state["objective"],
        eligible_skus=state["eligible_skus"],
        discount_pct=state["discount_pct"],
        bundle_offer=state["bundle_offer"],
        budget=state["budget"],
        starts_at=starts_at,
        ends_at=ends_at,
        rationale=state["rationale"],
    )

    decision = await evaluate_campaign_proposal(guardian_req, session)
    is_approved = decision.decision == DecisionType.APPROVE

    return {
        "guardian_decision": decision,
        "is_approved": is_approved,
    }


async def auto_revision_node(state: CampaignGraphState, session: AsyncSession) -> Dict[str, Any]:
    """
    Node 3 (Loop-Back / Auto-Correction):
    If Guardian rejected proposal due to policy threshold breach, auto-corrects parameters
    and loops back to Guardian node.
    """
    campaign_policy = await get_campaign_policy(state["merchant_id"], session)
    new_discount = min(state["discount_pct"], campaign_policy.allowed_campaign_discount_pct)
    new_budget = min(state["budget"], campaign_policy.campaign_budget_default)

    logger.info(f"🔄 [LangGraph Campaign Loop-Back] Clamping discount {state['discount_pct']}% -> {new_discount}%")

    return {
        "discount_pct": new_discount,
        "budget": new_budget,
        "revision_count": state["revision_count"] + 1,
    }


# ------------------------------------------------------------------------------
# 2. Campaign LangGraph Orchestrator
# ------------------------------------------------------------------------------

class CampaignLangGraph:
    """
    LangGraph-compatible Campaign Orchestration State Graph.
    Features automated loop-back self-correction for policy compliance.
    """

    async def ainvoke(self, state: CampaignGraphState, session: AsyncSession) -> CampaignGraphState:
        # Step 1: Synthesize
        step1 = await synthesize_proposal_node(state, session)
        state.update(step1)

        # Step 2: Validate with Guardian
        step2 = await guardian_validation_node(state, session)
        state.update(step2)

        # Loop-Back / Self-Correction if not approved and under max_revisions
        while not state["is_approved"] and state["revision_count"] < state["max_revisions"]:
            rev = await auto_revision_node(state, session)
            state.update(rev)
            
            # Re-validate with Guardian
            step2 = await guardian_validation_node(state, session)
            state.update(step2)

        return state


campaign_graph = CampaignLangGraph()
