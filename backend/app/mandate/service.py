from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import ensure_utc, generate_uuid, utc_now
from app.mandate.schemas import MandateCheckItem, MandateCheckResult, MandateCreate
from app.models import Mandate


async def get_active_mandate(buyer_id: str, session: AsyncSession) -> Optional[Mandate]:
    """Retrieve the single active, non-expired mandate for a buyer."""
    now = utc_now()
    stmt = (
        select(Mandate)
        .where(
            Mandate.buyer_id == buyer_id,
            Mandate.active == True,
        )
        .order_by(Mandate.created_at.desc())
    )
    result = await session.execute(stmt)
    mandates = list(result.scalars().all())
    for m in mandates:
        if m.expires_at is None or ensure_utc(m.expires_at) >= now:
            return m
    return None


async def create_mandate(
    buyer_id: str,
    data: MandateCreate,
    session: AsyncSession
) -> Mandate:
    """Create a new mandate, atomically deactivating previous active mandates."""
    # Deactivate existing active mandates for this buyer
    await session.execute(
        update(Mandate)
        .where(Mandate.buyer_id == buyer_id, Mandate.active == True)
        .values(active=False)
    )

    mandate = Mandate(
        mandate_id=generate_uuid(),
        buyer_id=buyer_id,
        max_amount=data.max_amount,
        max_quantity_per_item=data.max_quantity_per_item,
        allowed_categories=data.allowed_categories,
        allowed_merchants=data.allowed_merchants,
        allowed_products=data.allowed_products,
        currency=data.currency,
        expires_at=data.expires_at,
        confirmation_required_above=data.confirmation_required_above,
        signature=data.signature,
        active=True,
        created_at=utc_now(),
    )
    session.add(mandate)
    await session.flush()
    return mandate


def check_mandate(
    buyer_id: str,
    merchant_id: str,
    items: List[Dict[str, Any]],
    total_amount: int,
    mandate: Optional[Mandate],
    now: Optional[datetime] = None,
) -> MandateCheckResult:
    """
    Pure validation function. No I/O, no DB calls, no LLM.
    Evaluates buyer mandate constraints deterministically.
    """
    now_utc = ensure_utc(now) or utc_now()
    checks: List[MandateCheckItem] = []

    # 1. Mandate presence and active status
    if not mandate or not mandate.active:
        checks.append(
            MandateCheckItem(
                name="mandate.active",
                passed=False,
                detail="No active mandate found for buyer",
            )
        )
        return MandateCheckResult(
            passed=False,
            checks=checks,
            failure_reason="No active mandate declared for buyer",
        )

    # 2. Expiry check (Timezone normalized)
    mandate_expiry = ensure_utc(mandate.expires_at)
    if mandate_expiry and mandate_expiry < now_utc:
        checks.append(
            MandateCheckItem(
                name="mandate.active",
                passed=False,
                detail=f"Mandate expired at {mandate_expiry.isoformat()}",
            )
        )
        return MandateCheckResult(
            passed=False,
            checks=checks,
            failure_reason="Buyer mandate has expired",
        )

    checks.append(
        MandateCheckItem(
            name="mandate.active",
            passed=True,
            detail="Mandate is active and within valid time window",
        )
    )

    # 3. Allowed Merchant
    if mandate.allowed_merchants is not None:
        if merchant_id not in mandate.allowed_merchants:
            checks.append(
                MandateCheckItem(
                    name="mandate.allowed_merchants",
                    passed=False,
                    detail=f"Merchant '{merchant_id}' is not in allowed list {mandate.allowed_merchants}",
                )
            )
            return MandateCheckResult(
                passed=False,
                checks=checks,
                failure_reason=f"Merchant '{merchant_id}' is not authorized by buyer mandate",
            )
    checks.append(
        MandateCheckItem(
            name="mandate.allowed_merchants",
            passed=True,
            detail="Merchant is authorized",
        )
    )

    # 4. Item-level checks (Quantity, Allowed Categories, Allowed Products)
    for item in items:
        sku = item.get("sku", "")
        qty = item.get("qty", 1)
        category = item.get("category", "")

        # Quantity check
        if qty > mandate.max_quantity_per_item:
            checks.append(
                MandateCheckItem(
                    name="mandate.max_quantity_per_item",
                    passed=False,
                    detail=f"Quantity {qty} for SKU {sku} exceeds allowed max {mandate.max_quantity_per_item}",
                )
            )
            return MandateCheckResult(
                passed=False,
                checks=checks,
                failure_reason=f"Quantity {qty} for item {sku} exceeds mandate limit of {mandate.max_quantity_per_item}",
            )

        # Category check
        if mandate.allowed_categories is not None and category:
            if category.lower() not in [c.lower() for c in mandate.allowed_categories]:
                checks.append(
                    MandateCheckItem(
                        name="mandate.allowed_categories",
                        passed=False,
                        detail=f"Category '{category}' for SKU {sku} is not in allowed categories {mandate.allowed_categories}",
                    )
                )
                return MandateCheckResult(
                    passed=False,
                    checks=checks,
                    failure_reason=f"Category '{category}' is not authorized by buyer mandate",
                )

        # Allowed Products check
        if mandate.allowed_products is not None:
            if sku not in mandate.allowed_products:
                checks.append(
                    MandateCheckItem(
                        name="mandate.allowed_products",
                        passed=False,
                        detail=f"SKU '{sku}' is not in allowed products {mandate.allowed_products}",
                    )
                )
                return MandateCheckResult(
                    passed=False,
                    checks=checks,
                    failure_reason=f"Product '{sku}' is not authorized by buyer mandate",
                )

    checks.append(
        MandateCheckItem(
            name="mandate.max_quantity_per_item",
            passed=True,
            detail="All item quantities within mandate limits",
        )
    )
    checks.append(
        MandateCheckItem(
            name="mandate.allowed_categories",
            passed=True,
            detail="All item categories authorized",
        )
    )

    # 5. Total Amount Ceiling Check
    if total_amount > mandate.max_amount:
        checks.append(
            MandateCheckItem(
                name="mandate.max_amount",
                passed=False,
                detail=f"Total amount {total_amount} paise exceeds mandate limit {mandate.max_amount} paise",
            )
        )
        return MandateCheckResult(
            passed=False,
            checks=checks,
            failure_reason=f"Order total ₹{total_amount/100:.2f} exceeds buyer spending limit ₹{mandate.max_amount/100:.2f}",
        )

    checks.append(
        MandateCheckItem(
            name="mandate.max_amount",
            passed=True,
            detail=f"Total amount {total_amount} paise is within max amount {mandate.max_amount} paise",
        )
    )

    # 6. Confirmation Required Above Threshold
    requires_confirmation = False
    if (
        mandate.confirmation_required_above is not None
        and total_amount > mandate.confirmation_required_above
    ):
        requires_confirmation = True
        checks.append(
            MandateCheckItem(
                name="mandate.confirmation_required_above",
                passed=True,
                detail=f"Order total {total_amount} paise exceeds threshold {mandate.confirmation_required_above} paise -> explicit confirmation required",
            )
        )

    return MandateCheckResult(
        passed=True,
        requires_confirmation=requires_confirmation,
        checks=checks,
        failure_reason=None,
    )
