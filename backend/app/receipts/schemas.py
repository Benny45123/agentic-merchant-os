from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import DecisionType


class ReceiptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    receipt_id: str
    decision_id: str
    intent_id: Optional[str] = None
    buyer_id: Optional[str] = None
    merchant_id: str
    items_snapshot: List[Dict[str, Any]] = Field(default_factory=list)
    catalog_snapshot_ids: List[str] = Field(default_factory=list)
    observed_total: int
    final_verified_total: Optional[int] = None
    mandate_snapshot: Optional[Dict[str, Any]] = None
    policy_snapshot: Optional[Dict[str, Any]] = None
    guardian_checks: List[Dict[str, Any]] = Field(default_factory=list)
    decision: DecisionType
    reason: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime


class ReceiptListResponse(BaseModel):
    receipts: List[ReceiptResponse]


class ReplayResponse(BaseModel):
    receipt_id: str
    original_decision: str
    replay_decision: str
    matches_original: bool
    replayed_checks: List[Dict[str, Any]]
    replayed_reason: str
