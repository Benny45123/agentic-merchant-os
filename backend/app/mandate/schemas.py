from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MandateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mandate_id: str
    buyer_id: str
    max_amount: int
    max_quantity_per_item: int
    allowed_categories: Optional[List[str]] = None
    allowed_merchants: Optional[List[str]] = None
    allowed_products: Optional[List[str]] = None
    currency: str
    expires_at: datetime
    confirmation_required_above: Optional[int] = None
    signature: Optional[str] = None
    active: bool
    created_at: datetime


class MandateCreate(BaseModel):
    max_amount: int = Field(gt=0, description="Spending ceiling in paise")
    max_quantity_per_item: int = Field(default=5, gt=0)
    allowed_categories: Optional[List[str]] = None
    allowed_merchants: Optional[List[str]] = None
    allowed_products: Optional[List[str]] = None
    currency: str = "INR"
    expires_at: datetime
    confirmation_required_above: Optional[int] = None
    signature: Optional[str] = None


class MandateCheckItem(BaseModel):
    name: str
    passed: bool
    detail: str


class MandateCheckResult(BaseModel):
    passed: bool
    requires_confirmation: bool = False
    checks: List[MandateCheckItem] = Field(default_factory=list)
    failure_reason: Optional[str] = None
