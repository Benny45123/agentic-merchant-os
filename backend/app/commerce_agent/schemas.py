from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.guardian.schemas import GuardianDecisionResponse, RazorpayOrderSchema


class ChatRequest(BaseModel):
    session_id: str
    buyer_id: str
    message: str


class CartItemSchema(BaseModel):
    sku: str
    variant_id: Optional[str] = None
    qty: int = 1
    observed_price: int
    catalog_version: int = 1
    snapshot_id: Optional[str] = None
    source: str = "organic"  # organic | upsell


class CartSchema(BaseModel):
    items: List[CartItemSchema] = Field(default_factory=list)
    subtotal: int = 0


class RecommendationSchema(BaseModel):
    sku: str
    reason: str
    price: int


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    cart: CartSchema
    recommendations: List[RecommendationSchema] = Field(default_factory=list)


class CheckoutIntentRequest(BaseModel):
    session_id: str
    buyer_id: str
    merchant_id: str


class CheckoutIntentResponse(BaseModel):
    decision: GuardianDecisionResponse
    razorpay_order: Optional[RazorpayOrderSchema] = None
