import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import utc_now
from app.core.db import get_session
from app.core.enums import OrderStatus
from app.models import Order, Payment
from app.razorpay_adapter.client import RazorpayAdapter, get_razorpay_adapter
from app.razorpay_adapter.schemas import (
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from app.receipts.service import finalize_receipt_payment

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Razorpay & Payments"])


@router.post("/payments/verify", response_model=PaymentVerifyResponse)
async def verify_payment(
    body: PaymentVerifyRequest,
    session: AsyncSession = Depends(get_session),
    adapter: RazorpayAdapter = Depends(get_razorpay_adapter),
):
    """
    Frontend calls this endpoint after Checkout widget succeeds.
    Verifies HMAC-SHA256 signature and finalizes payment & receipt.
    """
    is_valid = adapter.verify_payment(
        order_id=body.razorpay_order_id,
        payment_id=body.razorpay_payment_id,
        signature=body.razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment signature verification failed"
        )

    # 1. Update Order status
    stmt = select(Order).where(Order.order_id == body.razorpay_order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{body.razorpay_order_id}' not found"
        )

    order.status = OrderStatus.PAID

    # 2. Record Payment row
    payment = Payment(
        payment_id=body.razorpay_payment_id,
        order_id=order.order_id,
        status="captured",
        verified=True,
        raw_webhook_payload=None,
        created_at=utc_now(),
    )
    session.add(payment)

    # 3. Finalize Receipt with payment ID
    receipt = await finalize_receipt_payment(
        razorpay_order_id=order.order_id,
        razorpay_payment_id=body.razorpay_payment_id,
        session=session,
    )

    await session.commit()

    return PaymentVerifyResponse(
        verified=True,
        receipt_id=receipt.receipt_id if receipt else None,
        order_id=order.order_id,
        payment_id=body.razorpay_payment_id,
        status="PAID",
    )


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias="X-Razorpay-Signature"),
    session: AsyncSession = Depends(get_session),
    adapter: RazorpayAdapter = Depends(get_razorpay_adapter),
):
    """
    Durable webhook handler for Razorpay payment events.
    Verifies cryptographic signature, deduplicates idempotently, and updates state.
    """
    body_bytes = await request.body()

    if not x_razorpay_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Razorpay-Signature header"
        )

    if not adapter.verify_webhook_signature(body_bytes, x_razorpay_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON webhook payload"
        )

    event = payload.get("event")
    event_id = payload.get("event_id") or payload.get("id")

    # Handle payment events
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id")
    payment_id = payment_entity.get("id")

    if order_id and payment_id:
        stmt = select(Order).where(Order.order_id == order_id)
        res = await session.execute(stmt)
        order = res.scalar_one_or_none()

        if order:
            if event == "payment.captured" or event == "order.paid":
                order.status = OrderStatus.PAID
                # Check for existing payment to avoid duplicate insert
                p_stmt = select(Payment).where(Payment.payment_id == payment_id)
                p_res = await session.execute(p_stmt)
                existing_payment = p_res.scalar_one_or_none()

                if not existing_payment:
                    payment = Payment(
                        payment_id=payment_id,
                        order_id=order_id,
                        status="captured",
                        verified=True,
                        raw_webhook_payload=payload,
                        created_at=utc_now(),
                    )
                    session.add(payment)

                await finalize_receipt_payment(
                    razorpay_order_id=order_id,
                    razorpay_payment_id=payment_id,
                    session=session,
                )
            elif event == "payment.failed":
                order.status = OrderStatus.FAILED
            
            await session.commit()

    return {"status": "ok"}
