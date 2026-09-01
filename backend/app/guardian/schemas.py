from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import DecisionType


class IntentItemSchema(BaseModel):
    sku: str
    variant_id: Optional[str] = None
    qty: int = Field(gt=0, default=1)
    observed_price: int = Field(gt=0)
    catalog_version: int = 1
    snapshot_id: Optional[str] = None
    discount_pct: Optional[int] = None



class TransactionIntentRequest(BaseModel):
    intent_id: str
    buyer_id: str
    merchant_id: str
    items: List[IntentItemSchema]
    requested_discount_pct: int = Field(ge=0, le=100, default=0)
    created_at: datetime
    expires_at: datetime


class GuardianCheckSchema(BaseModel):
    name: str
    passed: bool
    detail: str


class RazorpayOrderSchema(BaseModel):
    order_id: str
    amount: int
    currency: str = "INR"
    key_id: str


class GuardianDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: str
    intent_id: Optional[str] = None
    decision: DecisionType
    checks: List[GuardianCheckSchema]
    primary_reason: str
    final_verified_total: Optional[int] = None
    receipt_id: str
    razorpay_order: Optional[RazorpayOrderSchema] = None
    high_value_notification: Optional[Dict[str, Any]] = None
    payment_method: Optional[str] = "razorpay_modal"
    headless_autopay: Optional[bool] = False
    autopay_payment_id: Optional[str] = None
    payment_link: Optional[str] = None




class CampaignProposalRequest(BaseModel):
    proposal_id: str
    merchant_id: str
    objective: str
    eligible_skus: List[str]
    discount_pct: int
    bundle_offer: Optional[Dict[str, Any]] = None
    budget: int
    starts_at: datetime
    ends_at: datetime
    rationale: str
