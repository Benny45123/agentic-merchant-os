from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RazorpayOrder(BaseModel):
    order_id: str
    amount: int
    currency: str = "INR"
    receipt: str
    key_id: str
    status: str = "created"


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentVerifyResponse(BaseModel):
    verified: bool
    receipt_id: Optional[str] = None
    order_id: str
    payment_id: str
    status: str


class RazorpayRefund(BaseModel):
    refund_id: str
    payment_id: str
    amount: int
    currency: str = "INR"
    status: str
