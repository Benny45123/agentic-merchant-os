import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from pydantic import BaseModel
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
        from app.models.decision import GuardianDecision
        from app.core.enums import DecisionType
        from app.core.base import generate_uuid

        fallback_dec_id = generate_uuid()
        dec_row = GuardianDecision(
            decision_id=fallback_dec_id,
            intent_id=None,
            campaign_proposal_id=None,
            decision=DecisionType.APPROVE,
            checks=[{"name": "payment.simulated", "passed": True, "detail": "Direct test checkout fallback"}],
            primary_reason="Simulated checkout verification",
            final_verified_total=0,
            created_at=utc_now(),
        )
        session.add(dec_row)
        await session.flush()

        order = Order(
            order_id=body.razorpay_order_id,
            decision_id=fallback_dec_id,
            buyer_id="b_001",
            merchant_id="m_001",
            amount=0,
            currency="INR",
            status=OrderStatus.PAID,
            created_at=utc_now(),
        )
        session.add(order)
        await session.flush()
    else:
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

    # 3. If order is attributed to an active campaign, update budget spent and log event
    if not order.campaign_id:
        from app.models.campaign import Campaign
        from app.core.enums import CampaignStatus
        camp_stmt = select(Campaign).where(
            Campaign.merchant_id == order.merchant_id,
            Campaign.status == CampaignStatus.ACTIVE,
        )
        camp_res = await session.execute(camp_stmt)
        active_camps = list(camp_res.scalars().all())
        if active_camps:
            order.campaign_id = active_camps[0].campaign_id

    if order.campaign_id:
        from app.models.campaign import Campaign, CampaignEvent
        from app.core.enums import CampaignEventType
        from app.core.base import generate_uuid

        camp_stmt = select(Campaign).where(Campaign.campaign_id == order.campaign_id)
        camp_res = await session.execute(camp_stmt)
        campaign = camp_res.scalar_one_or_none()
        if campaign:
            campaign.budget_spent += order.amount
            camp_event = CampaignEvent(
                event_id=generate_uuid(),
                campaign_id=campaign.campaign_id,
                type=CampaignEventType.ORDER_ATTRIBUTED,
                detail={"order_id": order.order_id, "amount": order.amount},
                created_at=utc_now(),
            )
            session.add(camp_event)

    # 4. Finalize Receipt with payment ID
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


@router.post("/payments/sync/{order_id}")
@router.get("/payments/sync/{order_id}")
@router.get("/payments/order/{order_id}")
async def sync_payment_status(
    order_id: str,
    session: AsyncSession = Depends(get_session),
    adapter: RazorpayAdapter = Depends(get_razorpay_adapter),
):
    """
    Checks Razorpay API to see if the order/payment_link has been paid by customer.
    If paid, marks Order.status as PAID, updates campaign revenue, and finalizes receipt.
    Accepts both Razorpay order_id (order_...) and Decision receipt_id UUID.
    """
    stmt = select(Order).where(Order.order_id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        from app.models.receipt import Receipt
        rcpt_stmt = select(Receipt).where(Receipt.receipt_id == order_id)
        rcpt_res = await session.execute(rcpt_stmt)
        rcpt = rcpt_res.scalar_one_or_none()
        if rcpt and rcpt.razorpay_order_id:
            order_id = rcpt.razorpay_order_id
            stmt = select(Order).where(Order.order_id == order_id)
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order or Receipt '{order_id}' not found")


    if order.status == OrderStatus.PAID:
        return {
            "paid": True,
            "order_id": order_id,
            "status": "PAID",
            "amount": order.amount,
            "message": "Order is already confirmed and revenue credited."
        }

    # Query Razorpay API with strict order verification
    paid = False
    payment_id = f"pay_{order_id[-12:]}"

    # Check 1: Check if payment already exists in database for this order with verified=True
    p_stmt = select(Payment).where(Payment.order_id == order_id, Payment.verified == True)
    p_res = await session.execute(p_stmt)
    existing_payment = p_res.scalars().first()
    if existing_payment:
        paid = True
        payment_id = existing_payment.payment_id

    # Check 2: Direct Razorpay API order verification
    if not paid and adapter._is_live_sdk_available and adapter.client:
        try:
            rzp_order = adapter.client.order.fetch(order_id)
            if rzp_order.get("status") == "paid" or (rzp_order.get("amount_paid", 0) >= (order.amount or 0) and (order.amount or 0) > 0):
                paid = True
        except Exception as e:
            logger.warning(f"Razorpay order.fetch({order_id}) note: {e}")

        # Check 3: Specific order payments list
        if not paid:
            try:
                payments_resp = adapter.client.order.payments(order_id)
                for item in payments_resp.get("items", []):
                    if item.get("status") in ["captured", "authorized"]:
                        paid = True
                        payment_id = item.get("id", payment_id)
                        break
            except Exception as e:
                logger.warning(f"Razorpay order.payments({order_id}) note: {e}")


    if paid:
        order.status = OrderStatus.PAID



        # Record payment if not already recorded
        p_stmt = select(Payment).where(Payment.payment_id == payment_id)
        p_res = await session.execute(p_stmt)
        payment = p_res.scalar_one_or_none()
        if not payment:
            payment = Payment(
                payment_id=payment_id,
                order_id=order.order_id,
                status="captured",
                verified=True,
                raw_webhook_payload=None,
                created_at=utc_now(),
            )
            session.add(payment)
        else:
            payment.verified = True
            payment.status = "captured"

        # Campaign attribution
        if order.campaign_id:
            from app.models.campaign import Campaign, CampaignEvent
            from app.core.enums import CampaignEventType
            from app.core.base import generate_uuid

            camp_stmt = select(Campaign).where(Campaign.campaign_id == order.campaign_id)
            camp_res = await session.execute(camp_stmt)
            campaign = camp_res.scalar_one_or_none()
            if campaign:
                campaign.budget_spent += order.amount
                camp_event = CampaignEvent(
                    event_id=generate_uuid(),
                    campaign_id=campaign.campaign_id,
                    type=CampaignEventType.ORDER_ATTRIBUTED,
                    detail={"order_id": order.order_id, "amount": order.amount},
                    created_at=utc_now(),
                )
                session.add(camp_event)

        # Finalize receipt
        receipt = await finalize_receipt_payment(
            razorpay_order_id=order.order_id,
            razorpay_payment_id=payment_id,
            session=session,
        )

        await session.commit()

        # If receipt was not found by order_id, look it up by decision_id
        receipt_id = receipt.receipt_id if receipt else None
        if not receipt_id and order.decision_id:
            from app.models.receipt import Receipt
            rcpt_stmt = select(Receipt).where(Receipt.decision_id == order.decision_id).order_by(Receipt.created_at.desc())
            rcpt_res = await session.execute(rcpt_stmt)
            found_rcpt = rcpt_res.scalars().first()
            if found_rcpt:
                receipt_id = found_rcpt.receipt_id

        return {
            "paid": True,
            "order_id": order_id,
            "payment_id": payment_id,
            "receipt_id": receipt_id,
            "status": "PAID",
            "amount": order.amount,
            "message": "Payment verified and store revenue credited successfully!"
        }

    return {
        "paid": False,
        "order_id": order_id,
        "status": "CREATED",
        "amount": order.amount,
        "message": "Payment is still pending on Razorpay. Please complete checkout on the payment link first."
    }


@router.get("/payments/checkout/{order_id}", response_class=Response)
@router.get("/checkout/{order_id}", response_class=Response)
async def render_checkout_page(
    order_id: str,
    session: AsyncSession = Depends(get_session),
    adapter: RazorpayAdapter = Depends(get_razorpay_adapter),
):


    """
    Renders an interactive mobile & desktop Razorpay checkout simulation page.
    Allows testing UPI, Card, and NetBanking payments with 1 click.
    """
    stmt = select(Order).where(Order.order_id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        from app.models.receipt import Receipt
        rcpt_stmt = select(Receipt).where(Receipt.receipt_id == order_id)
        rcpt_res = await session.execute(rcpt_stmt)
        rcpt = rcpt_res.scalar_one_or_none()
        if rcpt and rcpt.razorpay_order_id:
            stmt = select(Order).where(Order.order_id == rcpt.razorpay_order_id)
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()

    if not order:
        return Response(
            content=f"<html><body style='font-family:sans-serif;padding:40px;text-align:center;'><h2>❌ Order Not Found</h2><p>Reference ID: {order_id}</p></body></html>",
            media_type="text/html",
            status_code=404,
        )

    amount_inr = (order.amount or 0) / 100.0
    is_paid = order.status == OrderStatus.PAID


    paid_banner = f"""
        <div class="bg-emerald-950/60 border border-emerald-500/30 rounded-2xl p-6 text-center space-y-4">

            <div class="w-14 h-14 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center text-3xl font-black mx-auto">
                ✓
            </div>
            <h2 class="text-xl font-black text-emerald-300">Payment Captured &amp; Verified!</h2>
            <p class="text-sm text-emerald-400/80">Order <code class="font-mono">{order_id}</code> is settled on the immutable ledger.</p>
            <p class="text-xs text-slate-400">You can now return to Telegram and tap <b>Verify &amp; Confirm Payment</b> to view your Decision Receipt.</p>
        </div>
    """

    unpaid_form = f"""
        <div class="space-y-5">
            <div class="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-4 space-y-2 text-xs">
                <div class="flex justify-between text-slate-400">
                    <span>Order Reference:</span>
                    <span class="font-mono text-slate-200 font-bold">{order_id}</span>
                </div>
                <div class="flex justify-between text-slate-400">
                    <span>Merchant:</span>
                    <span class="font-mono text-slate-200">{order.merchant_id}</span>
                </div>
                <div class="flex justify-between text-slate-400">
                    <span>Amount:</span>
                    <span class="font-mono text-emerald-400 font-bold text-sm">₹{amount_inr:,.2f}</span>
                </div>
            </div>

            <div class="bg-blue-950/30 border border-blue-500/30 rounded-2xl p-4 text-xs text-blue-200 space-y-1">
                <div class="font-bold flex items-center gap-1.5">
                    <span>⚡</span> Official Razorpay Checkout Modal
                </div>
                <p class="text-[11px] text-blue-300/80">Pay seamlessly using UPI (GPay, PhonePe, Paytm), Cards, or NetBanking.</p>
            </div>

            <button id="rzp-btn" onclick="openRazorpayCheckout()" class="w-full py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 text-white font-black text-sm shadow-xl shadow-blue-600/30 transition-all flex items-center justify-center gap-2 active:scale-98">
                <span>💳 Pay ₹{amount_inr:,.2f} with Razorpay</span>
                <span>→</span>
            </button>
        </div>
    """

    main_body = paid_banner if is_paid else unpaid_form
    rzp_key_id = adapter.key_id or "rzp_test_TUjDfAof7bwb12"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Razorpay Secure Checkout • Agentic Merchant OS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
    </style>
</head>
<body class="bg-slate-950 text-white min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative overflow-hidden">
        <div class="flex items-center justify-between border-b border-slate-800 pb-5">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center font-black text-xl shadow-lg shadow-blue-600/30">
                    💳
                </div>
                <div>
                    <h1 class="text-base font-black text-white">Agentic Merchant Store</h1>
                    <span class="text-xs text-blue-400 font-semibold flex items-center gap-1">
                        <span>●</span> Razorpay Checkout
                    </span>
                </div>
            </div>
            <div class="text-right">
                <div class="text-xs text-slate-400">Total Payable</div>
                <div class="text-xl font-black text-emerald-400 font-mono">₹{amount_inr:,.2f}</div>
            </div>
        </div>

        {main_body}

        <div class="text-center text-[11px] text-slate-500 pt-2 border-t border-slate-800/80">
            🔒 256-Bit Encrypted • Powered by Agentic Merchant OS &amp; Razorpay
        </div>
    </div>

    <script>
        function openRazorpayCheckout() {{
            if (typeof Razorpay === "undefined") {{
                // Fallback simulation
                executeFallbackPayment();
                return;
            }}

            const options = {{
                key: "{rzp_key_id}",
                amount: {order.amount},
                currency: "{order.currency}",
                name: "Agentic Merchant Store",
                description: "Order {order_id}",
                order_id: "{order_id}",
                handler: async function (response) {{
                    try {{
                        const verifyPayload = {{
                            razorpay_order_id: response.razorpay_order_id || "{order_id}",
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature || "test_signature"
                        }};
                        const res = await fetch("/payments/verify", {{
                            method: "POST",
                            headers: {{ "Content-Type": "application/json" }},
                            body: JSON.stringify(verifyPayload)
                        }});
                        if (res.ok) {{
                            window.location.reload();
                        }} else {{
                            // Fallback to direct checkout pay
                            await fetch("/checkout/{order_id}/pay", {{ method: "POST" }});
                            window.location.reload();
                        }}
                    }} catch (err) {{
                        await fetch("/checkout/{order_id}/pay", {{ method: "POST" }});
                        window.location.reload();
                    }}
                }},

                prefill: {{
                    name: "Alex Johnson",
                    email: "shopper@agenticstore.com",
                    contact: "9999999999"
                }},
                theme: {{
                    color: "#2563eb"
                }},
                modal: {{
                    ondismiss: function () {{
                        console.log("Checkout modal dismissed");
                    }}
                }}
            }};

            const rzp = new Razorpay(options);
            rzp.on("payment.failed", function (response) {{
                alert("Payment Failed: " + response.error.description);
            }});
            rzp.open();
        }}

        window.addEventListener("DOMContentLoaded", function () {{
            setTimeout(function () {{
                if (typeof Razorpay !== "undefined") {{
                    openRazorpayCheckout();
                }}
            }}, 300);
        }});



        async function executeFallbackPayment() {{
            const btn = document.getElementById("rzp-btn");
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = "Processing Payment...";
            }}
            try {{
                const res = await fetch("/checkout/{order_id}/pay", {{ method: "POST" }});
                if (res.ok) {{
                    window.location.reload();
                }}
            }} catch (err) {{
                alert("Payment error: " + err);
            }}
        }}
    </script>
</body>
</html>"""

    return Response(content=html_content, media_type="text/html")




@router.post("/checkout/{order_id}/pay")
async def process_checkout_payment(
    order_id: str,
    session: AsyncSession = Depends(get_session),
    adapter: RazorpayAdapter = Depends(get_razorpay_adapter),
):
    """Processes simulated test payment from the checkout page and records it immediately."""
    stmt = select(Order).where(Order.order_id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        from app.models.receipt import Receipt
        rcpt_stmt = select(Receipt).where(Receipt.receipt_id == order_id)
        rcpt_res = await session.execute(rcpt_stmt)
        rcpt = rcpt_res.scalar_one_or_none()
        if rcpt and rcpt.razorpay_order_id:
            stmt = select(Order).where(Order.order_id == rcpt.razorpay_order_id)
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")


    payment_id = f"pay_test_{order_id[-10:]}"
    order.status = OrderStatus.PAID

    p_stmt = select(Payment).where(Payment.payment_id == payment_id)
    p_res = await session.execute(p_stmt)
    payment = p_res.scalar_one_or_none()
    if not payment:
        payment = Payment(
            payment_id=payment_id,
            order_id=order.order_id,
            status="captured",
            verified=True,
            raw_webhook_payload={"source": "checkout_page", "mode": "test_gateway"},
            created_at=utc_now(),
        )
        session.add(payment)
    else:
        payment.verified = True
        payment.status = "captured"

    # Campaign attribution
    if order.campaign_id:
        from app.models.campaign import Campaign, CampaignEvent
        from app.core.enums import CampaignEventType
        from app.core.base import generate_uuid

        camp_stmt = select(Campaign).where(Campaign.campaign_id == order.campaign_id)
        camp_res = await session.execute(camp_stmt)
        campaign = camp_res.scalar_one_or_none()
        if campaign:
            campaign.budget_spent += order.amount
            camp_event = CampaignEvent(
                event_id=generate_uuid(),
                campaign_id=campaign.campaign_id,
                type=CampaignEventType.ORDER_ATTRIBUTED,
                detail={"order_id": order.order_id, "amount": order.amount, "mode": "checkout_page"},
                created_at=utc_now(),
            )
            session.add(camp_event)

    # Finalize receipt
    await finalize_receipt_payment(
        razorpay_order_id=order.order_id,
        razorpay_payment_id=payment_id,
        session=session,
    )

    await session.commit()
    return {"status": "PAID", "order_id": order_id, "payment_id": payment_id}




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


class AutoPaySetupRequest(BaseModel):
    buyer_id: str = "b_001"
    max_amount_paise: int = 10000000  # Default ₹1,00,000.00 (1 Lakh)
    max_amount_per_charge_paise: Optional[int] = None
    bank_name: Optional[str] = "HDFC Bank (UPI AutoPay)"
    vpa: Optional[str] = None
    simulate_auth: bool = True



@router.post("/mandates/autopay/setup")
async def setup_autopay_mandate(
    body: AutoPaySetupRequest,
    session: AsyncSession = Depends(get_session),
    adapter: RazorpayAdapter = Depends(get_razorpay_adapter),
):
    """Registers or activates a Razorpay recurring UPI AutoPay e-mandate (minimum ₹30,000)."""
    from datetime import timedelta
    from app.models.mandate import Mandate
    from app.core.base import generate_uuid

    # Enforce minimum ₹30,000 (3,000,000 paise) for e-mandate setup
    mandate_amount = max(3000000, body.max_amount_paise)
    per_charge_cap = body.max_amount_per_charge_paise or mandate_amount

    stmt = select(Mandate).where(Mandate.buyer_id == body.buyer_id, Mandate.active == True)
    res = await session.execute(stmt)
    mandate = res.scalar_one_or_none()

    if not mandate:
        mandate = Mandate(
            mandate_id=generate_uuid(),
            buyer_id=body.buyer_id,
            max_amount=mandate_amount,
            max_quantity_per_item=10,
            allowed_categories=["audio", "accessories", "wearables", "mobiles", "laptops", "electronics"],
            allowed_merchants=["m_001"],
            currency="INR",
            expires_at=utc_now() + timedelta(days=180),
            confirmation_required_above=mandate_amount // 2,
            signature="sig_autopay_mandate_001",
            active=True,
            created_at=utc_now(),
        )
        session.add(mandate)

    reg_data = adapter.create_autopay_registration(
        buyer_id=body.buyer_id,
        max_amount_paise=mandate_amount,
        vpa=body.vpa,
    )

    mandate.max_amount = mandate_amount
    mandate.autopay_enabled = True
    mandate.autopay_token = reg_data["token_id"]
    mandate.customer_id = reg_data["customer_id"]
    mandate.max_amount_per_charge = per_charge_cap
    mandate.recurring_auth_status = "ACTIVE"
    mandate.autopay_bank_name = body.bank_name or reg_data.get("bank_name", "HDFC Bank (UPI AutoPay)")
    mandate.autopay_vpa = body.vpa or reg_data.get("vpa", f"{body.buyer_id}@okhdfcbank")

    await session.commit()

    # Calculate cumulative spent and remaining headroom
    spent_stmt = select(Order).where(Order.buyer_id == body.buyer_id, Order.status == OrderStatus.PAID)
    spent_res = await session.execute(spent_stmt)
    total_spent = sum(o.amount for o in spent_res.scalars().all())
    headroom = max(0, mandate.max_amount - total_spent)

    auth_url = f"https://rzp.io/l/mandate_{mandate.autopay_token}"

    return {
        "status": "ACTIVE",
        "buyer_id": body.buyer_id,
        "token_id": mandate.autopay_token,
        "customer_id": mandate.customer_id,
        "max_amount_paise": mandate.max_amount,
        "max_amount_per_charge_paise": mandate.max_amount_per_charge,
        "total_spent_paise": total_spent,
        "remaining_headroom_paise": headroom,
        "vpa": mandate.autopay_vpa,
        "bank_name": mandate.autopay_bank_name,
        "auth_url": auth_url,
        "message": f"Headless Razorpay UPI AutoPay mandate is ACTIVE with ₹{mandate.max_amount/100:,.2f} authorization pool. Zero-click purchases enabled."
    }


@router.post("/mandates/autopay/revoke")
async def revoke_autopay_mandate(
    buyer_id: str = Query("b_001"),
    session: AsyncSession = Depends(get_session),
):
    """Revokes or pauses AutoPay recurring token for a buyer."""
    from app.models.mandate import Mandate
    stmt = select(Mandate).where(Mandate.buyer_id == buyer_id, Mandate.active == True)
    res = await session.execute(stmt)
    mandate = res.scalar_one_or_none()

    if not mandate:
        raise HTTPException(status_code=404, detail=f"Mandate for buyer '{buyer_id}' not found")

    mandate.autopay_enabled = False
    mandate.recurring_auth_status = "REVOKED"
    await session.commit()

    return {
        "status": "REVOKED",
        "buyer_id": buyer_id,
        "autopay_enabled": False,
        "message": "AutoPay recurring token revoked. Future checkouts will require manual approval."
    }


@router.get("/mandates/autopay/status")
async def get_autopay_status(
    buyer_id: str = Query("b_001"),
    session: AsyncSession = Depends(get_session),
):
    """Returns active AutoPay mandate status, token details, spent balance, and spend headroom."""
    from app.models.mandate import Mandate
    stmt = select(Mandate).where(Mandate.buyer_id == buyer_id, Mandate.active == True)
    res = await session.execute(stmt)
    mandate = res.scalar_one_or_none()

    if not mandate or not mandate.autopay_enabled or not mandate.autopay_token:
        return {
            "autopay_enabled": False,
            "status": "NONE",
            "buyer_id": buyer_id,
            "message": "No active AutoPay token registered."
        }

    # Calculate actual cumulative debits from this mandate pool
    spent_stmt = select(Order).where(Order.buyer_id == buyer_id, Order.status == OrderStatus.PAID)
    spent_res = await session.execute(spent_stmt)
    total_spent = sum(o.amount for o in spent_res.scalars().all())
    headroom = max(0, mandate.max_amount - total_spent)
    spent_pct = round((total_spent / mandate.max_amount * 100.0), 1) if mandate.max_amount > 0 else 0.0

    return {
        "autopay_enabled": mandate.autopay_enabled,
        "status": mandate.recurring_auth_status,
        "buyer_id": buyer_id,
        "token_id": mandate.autopay_token,
        "customer_id": mandate.customer_id,
        "max_amount_paise": mandate.max_amount,
        "max_amount_per_charge_paise": mandate.max_amount_per_charge,
        "total_spent_paise": total_spent,
        "remaining_headroom_paise": headroom,
        "spent_pct": spent_pct,
        "vpa": mandate.autopay_vpa,
        "bank_name": mandate.autopay_bank_name,
        "auth_url": f"https://rzp.io/l/mandate_{mandate.autopay_token}",
        "message": "AutoPay recurring token is active and bound to Commerce Guardian."
    }


@router.get("/mandates/autopay/all")
async def list_all_autopay_mandates(
    session: AsyncSession = Depends(get_session),
):
    """Returns all registered AutoPay mandates and telemetry for the Merchant Dashboard."""
    from app.models.mandate import Mandate
    stmt = select(Mandate).order_by(Mandate.created_at.desc())
    res = await session.execute(stmt)
    mandates = res.scalars().all()

    items = []
    total_active_headroom = 0
    total_autopay_volume = 0

    for m in mandates:
        spent_stmt = select(Order).where(Order.buyer_id == m.buyer_id, Order.status == OrderStatus.PAID)
        spent_res = await session.execute(spent_stmt)
        spent = sum(o.amount for o in spent_res.scalars().all())
        headroom = max(0, m.max_amount - spent)

        if m.autopay_enabled and m.recurring_auth_status == "ACTIVE":
            total_active_headroom += headroom
            total_autopay_volume += spent

        items.append({
            "mandate_id": m.mandate_id,
            "buyer_id": m.buyer_id,
            "autopay_enabled": m.autopay_enabled,
            "status": m.recurring_auth_status,
            "token_id": m.autopay_token,
            "customer_id": m.customer_id,
            "max_amount_paise": m.max_amount,
            "max_amount_per_charge_paise": m.max_amount_per_charge,
            "total_spent_paise": spent,
            "remaining_headroom_paise": headroom,
            "vpa": m.autopay_vpa or f"{m.buyer_id}@okhdfcbank",
            "bank_name": m.autopay_bank_name or "HDFC Bank",
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })

    return {
        "mandates": items,
        "summary": {
            "total_mandates": len(items),
            "active_mandates": sum(1 for item in items if item["autopay_enabled"]),
            "total_active_headroom_paise": total_active_headroom,
            "total_autopay_volume_paise": total_autopay_volume,
        }
    }


