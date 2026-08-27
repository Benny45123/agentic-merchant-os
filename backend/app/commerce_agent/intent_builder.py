from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.commerce_agent.schemas import CartItemSchema
from app.core.base import generate_uuid, utc_now
from app.guardian.schemas import IntentItemSchema, TransactionIntentRequest


def build_transaction_intent(
    buyer_id: str,
    merchant_id: str,
    cart_items: List[CartItemSchema],
    requested_discount_pct: int = 0,
    expires_in_seconds: int = 120,
) -> TransactionIntentRequest:
    """
    Pure deterministic builder for TransactionIntent.
    Serializes verified CartItem state into a structured Guardian intent request.
    """
    now = utc_now()
    expires_at = now + timedelta(seconds=expires_in_seconds)

    intent_items = [
        IntentItemSchema(
            sku=item.sku,
            variant_id=item.variant_id,
            qty=item.qty,
            observed_price=item.observed_price,
            catalog_version=item.catalog_version,
            snapshot_id=item.snapshot_id,
        )
        for item in cart_items
    ]

    return TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        items=intent_items,
        requested_discount_pct=requested_discount_pct,
        created_at=now,
        expires_at=expires_at,
    )
