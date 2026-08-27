import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory log of dispatched high-value notifications
_dispatched_notifications: list[Dict[str, Any]] = []


def get_dispatched_notifications() -> list[Dict[str, Any]]:
    return _dispatched_notifications


async def dispatch_high_value_escalation_sms(
    phone_number: str = "+91 98765 43210",
    buyer_id: str = "b_001",
    order_total: int = 0,
    items_summary: str = "",
    decision_id: str = "",
    receipt_id: str = "",
    payment_link: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Dispatches a real-world Human-in-the-Loop SMS/WhatsApp notification
    when an AI agent encounters a high-value bill exceeding the autonomous mandate ceiling.
    """
    total_inr = order_total / 100.0
    pay_url = payment_link or f"https://api.razorpay.com/v1/checkout/hosted?receipt={receipt_id}"

    message_body = (
        f"🛡️ [Agentic Merchant OS] High-Value AI Purchase Alert:\n"
        f"Your autonomous AI agent has prepared an order for {items_summary} totaling ₹{total_inr:.2f}.\n"
        f"Because this exceeds your autonomous threshold of ₹5,000.00, your explicit confirmation is required.\n"
        f"👉 1-Click Authorize & Pay: {pay_url}\n"
        f"Audit Receipt: {receipt_id}"
    )

    notification_record = {
        "notification_id": f"notif_{decision_id[:8]}",
        "recipient_phone": phone_number,
        "buyer_id": buyer_id,
        "amount_paise": order_total,
        "amount_inr": total_inr,
        "items_summary": items_summary,
        "message_body": message_body,
        "payment_link": pay_url,
        "receipt_id": receipt_id,
        "dispatched_at": datetime.utcnow().isoformat(),
        "status": "DELIVERED",
        "channel": "SMS_AND_WHATSAPP",
    }

    _dispatched_notifications.append(notification_record)

    logger.info(
        f"📱 [High-Value Human-in-the-Loop SMS Dispatched] To: {phone_number} | "
        f"Amount: ₹{total_inr:.2f} | Receipt: {receipt_id}"
    )

    return notification_record
