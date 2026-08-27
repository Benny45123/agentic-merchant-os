from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.guardian.schemas import GuardianDecisionResponse


class CampaignProposeRequest(BaseModel):
    merchant_id: str
    objective: str


class BundleOfferSchema(BaseModel):
    trigger_sku: str
    addon_sku: str
    addon_discount_pct: int


class CampaignProposal(BaseModel):
    proposal_id: str
    merchant_id: str
    objective: str
    eligible_skus: List[str]
    discount_pct: int
    bundle_offer: Optional[BundleOfferSchema] = None
    budget: int
    starts_at: datetime
    ends_at: datetime
    rationale: str
    guardian_decision: GuardianDecisionResponse


class CampaignActivateResponse(BaseModel):
    campaign_id: str
    status: str


class CampaignStatusResponse(BaseModel):
    campaign_id: str
    status: str
    budget: int
    budget_spent: int
    orders_attributed: int
    revenue_attributed: int
    pause_reason: Optional[str] = None
