from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MerchantPolicySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    policy_id: str
    merchant_id: str
    maximum_discount_pct: int
    minimum_margin_pct: int
    maximum_order_value: int
    allowed_products_for_discount: Optional[List[str]] = None
    minimum_stock_to_sell: int
    version: int
    created_at: datetime


class MerchantPolicyUpdate(BaseModel):
    maximum_discount_pct: int = Field(ge=0, le=100)
    minimum_margin_pct: int = Field(ge=0, le=100)
    maximum_order_value: int = Field(gt=0)
    allowed_products_for_discount: Optional[List[str]] = None
    minimum_stock_to_sell: int = Field(ge=0)


class CampaignPolicySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_id: str
    allowed_campaign_discount_pct: int
    campaign_budget_default: int
    daily_campaign_budget_cap: int
    created_at: datetime


class PolicyCheckItem(BaseModel):
    name: str
    passed: bool
    detail: str


class PolicyCheckResult(BaseModel):
    passed: bool
    requires_confirmation: bool = False
    checks: List[PolicyCheckItem] = Field(default_factory=list)
    failure_reason: Optional[str] = None


class ResolvedItem(BaseModel):
    sku: str
    qty: int
    authoritative_price: int
    cost: Optional[int] = None
    inventory: int
    category: str
    discount_pct: int = 0
    catalog_version: int
    snapshot_id: Optional[str] = None
