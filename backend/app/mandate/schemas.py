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
    spent_amount: int = 0
    autopay_enabled: bool = False
    autopay_token: Optional[str] = None
    customer_id: Optional[str] = None
    max_amount_per_charge: int = 7500000
    recurring_auth_status: str = "NONE"
    autopay_bank_name: Optional[str] = None
    autopay_vpa: Optional[str] = None
    open_mandate_jwt: Optional[str] = None
    user_public_key_pem: Optional[str] = None
    agent_public_key_pem: Optional[str] = None
    created_at: datetime


class MandateCreate(BaseModel):
    max_amount: int = Field(default=15000000, gt=0, description="Spending ceiling in paise (e.g. ₹1,50,000)")
    max_quantity_per_item: int = Field(default=5, gt=0)
    allowed_categories: Optional[List[str]] = None
    allowed_merchants: Optional[List[str]] = None
    allowed_products: Optional[List[str]] = None
    currency: str = "INR"
    expires_at: datetime
    confirmation_required_above: Optional[int] = None
    signature: Optional[str] = None
    spent_amount: int = 0
    autopay_enabled: bool = False
    autopay_token: Optional[str] = None
    customer_id: Optional[str] = None
    max_amount_per_charge: int = 7500000
    recurring_auth_status: str = "NONE"
    autopay_bank_name: Optional[str] = None
    autopay_vpa: Optional[str] = None
    open_mandate_jwt: Optional[str] = None
    user_public_key_pem: Optional[str] = None
    agent_public_key_pem: Optional[str] = None




class MandateCheckItem(BaseModel):
    name: str
    passed: bool
    detail: str


class MandateCheckResult(BaseModel):
    passed: bool
    requires_confirmation: bool = False
    checks: List[MandateCheckItem] = Field(default_factory=list)
    failure_reason: Optional[str] = None


class AP2MintClosedRequest(BaseModel):
    open_mandate_jwt: Optional[str] = None
    buyer_id: str = "b_001"
    items: List[dict]
    amount_paise: int
    intent_id: Optional[str] = None
    currency: str = "INR"


class AP2VerifyChainRequest(BaseModel):
    open_mandate_jwt: str
    closed_mandate_jwt: str
    items: List[dict]
    amount_paise: int
    user_public_key_pem: Optional[str] = None
    agent_public_key_pem: Optional[str] = None


class AP2ChainResponse(BaseModel):
    valid: bool
    reason: str
    open_jti: Optional[str] = None
    closed_jti: Optional[str] = None
    cart_digest: Optional[str] = None
    ap2_merkle_leaf: Optional[str] = None
    checks: dict = Field(default_factory=dict)

