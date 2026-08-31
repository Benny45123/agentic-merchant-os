from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RFQItem(BaseModel):
    sku: str = Field(..., description="Target Product SKU")
    qty: int = Field(default=1, gt=0, description="Requested Quantity")
    target_unit_price_paise: int = Field(..., gt=0, description="Target price proposed by Buyer Agent in paise")


class BuyerMandatePayload(BaseModel):
    buyer_id: str = "b_001"
    max_amount: int = 10000000  # ₹1,00,000 (1 Lakh) default max spend
    max_quantity_per_item: int = 10
    currency: str = "INR"
    signature: str = "sig_ed25519_buyer_mandate_attestation"



class RFQRequest(BaseModel):
    buyer_agent_id: str = Field(default="ai_buyer_agent_procure_42", description="Buyer Bot ID")
    merchant_id: str = "m_001"
    buyer_mandate: BuyerMandatePayload
    items: List[RFQItem]
    session_id: Optional[str] = None
    round_index: int = 1
    buyer_rationale: Optional[str] = "Seeking volume discount for bulk procurement"


class BundleSweetenerOption(BaseModel):
    addon_sku: str
    addon_name: str
    addon_qty: int
    original_price_paise: int
    discounted_price_paise: int
    discount_pct: int


class CounterOfferOption(BaseModel):
    option_id: str
    option_type: str  # "DIRECT_PRICE_COUNTER" or "BUNDLE_SWEETENER"
    title: str
    description: str
    unit_price_paise: int
    total_amount_paise: int
    discount_pct: float
    projected_gross_margin_pct: float
    margin_floor_satisfied: bool
    bundled_items: List[BundleSweetenerOption] = Field(default_factory=list)
    merchant_profit_lift_paise: int


class RFQResponse(BaseModel):
    status: str  # "OFFERS_PROPOSED", "AUTO_ACCEPTED", "REJECTED_MARGIN_FLOOR"
    session_id: str
    round_index: int
    merchant_id: str
    catalog_total_paise: int
    buyer_target_total_paise: int
    minimum_margin_floor_pct: float
    counter_offers: List[CounterOfferOption] = Field(default_factory=list)
    reason: str
    ai_pricing_agent_notes: str


class AcceptOfferRequest(BaseModel):
    session_id: str
    buyer_agent_id: str = "ai_buyer_agent_procure_42"
    merchant_id: str = "m_001"
    selected_option_id: Optional[str] = None
    option_id: Optional[str] = None
    buyer_signature: str = "sig_ed25519_buyer_accepted_contract"



class NegotiationSettlementResponse(BaseModel):
    status: str  # "APPROVED", "REQUIRE_CONFIRMATION", "BLOCKED"
    guardian_decision: str
    session_id: str
    receipt_id: str
    final_verified_total_paise: int
    razorpay_order_id: Optional[str] = None
    payment_link: Optional[str] = None
    replay_hash: str
    negotiated_items: List[Dict[str, Any]]
    merchant_margin_achieved_pct: float
    reason: str
