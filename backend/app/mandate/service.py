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

    open_jwt = data.open_mandate_jwt
    user_pub = data.user_public_key_pem
    agent_pub = data.agent_public_key_pem

    # Automatically mint Google AP2 Open Mandate if not explicitly supplied
    if not open_jwt:
        try:
            from app.mandate.ap2_service import mint_open_mandate, get_or_create_agent_keypair
            open_jwt, user_pub = mint_open_mandate(
                buyer_id=buyer_id,
                max_total_paise=data.max_amount,
                max_per_charge_paise=data.max_amount_per_charge,
                currency=data.currency,
                autopay_token=data.autopay_token,
                customer_id=data.customer_id,
            )
            _, agent_pub = get_or_create_agent_keypair()
        except Exception:
            pass

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
        autopay_enabled=data.autopay_enabled,
        autopay_token=data.autopay_token,
        customer_id=data.customer_id,
        max_amount_per_charge=data.max_amount_per_charge,
        recurring_auth_status=data.recurring_auth_status,
        autopay_bank_name=data.autopay_bank_name,
        autopay_vpa=data.autopay_vpa,
        open_mandate_jwt=open_jwt,
        user_public_key_pem=user_pub,
        agent_public_key_pem=agent_pub,
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

    # 5. Per-Transaction Limit Check (Round figured to mobile costs e.g. ₹75,000)
    max_per_charge = getattr(mandate, "max_amount_per_charge", 7500000) or 7500000
    if total_amount > max_per_charge:
        checks.append(
            MandateCheckItem(
                name="mandate.max_amount_per_charge",
                passed=False,
                detail=f"Order total ₹{total_amount/100:.2f} exceeds max per-transaction limit ₹{max_per_charge/100:.2f}",
            )
        )
        return MandateCheckResult(
            passed=False,
            checks=checks,
            failure_reason=f"Order total ₹{total_amount/100:.2f} exceeds mandate single-transaction ceiling ₹{max_per_charge/100:.2f}",
        )

    checks.append(
        MandateCheckItem(
            name="mandate.max_amount_per_charge",
            passed=True,
            detail=f"Transaction total ₹{total_amount/100:.2f} is within per-charge limit ₹{max_per_charge/100:.2f}",
        )
    )

    # 6. Cumulative Spending Ceiling Check (Spent + New <= Max Total)
    spent = getattr(mandate, "spent_amount", 0) or 0
    if spent + total_amount > mandate.max_amount:
        remaining = max(0, mandate.max_amount - spent)
        checks.append(
            MandateCheckItem(
                name="mandate.spending_ceiling",
                passed=False,
                detail=f"Cumulative spend ₹{(spent + total_amount)/100:.2f} exceeds total mandate pool ₹{mandate.max_amount/100:.2f} (Remaining: ₹{remaining/100:.2f})",
            )
        )
        return MandateCheckResult(
            passed=False,
            checks=checks,
            failure_reason=f"Mandate ceiling exceeded: ₹{spent/100:.2f} already spent of ₹{mandate.max_amount/100:.2f} pool (Remaining: ₹{remaining/100:.2f})",
        )

    checks.append(
        MandateCheckItem(
            name="mandate.spending_ceiling",
            passed=True,
            detail=f"Cumulative spend ₹{(spent + total_amount)/100:.2f} is within pool ₹{mandate.max_amount/100:.2f} (Remaining: ₹{(mandate.max_amount - spent - total_amount)/100:.2f})",
        )
    )

    # 7. Confirmation Required Above Threshold
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


def can_autopay(mandate: Optional[Mandate], amount: int, now: Optional[datetime] = None) -> tuple[bool, str]:
    """
    Deterministic Dual-Lock Evaluation:
    Evaluates whether autonomous payment is permissible under the active buyer mandate.
    """
    if not mandate or not mandate.active:
        return False, "Mandate is not active"

    now_utc = ensure_utc(now) or utc_now()
    mandate_expiry = ensure_utc(mandate.expires_at)
    if mandate_expiry and mandate_expiry < now_utc:
        return False, f"Mandate expired at {mandate_expiry.strftime('%Y-%m-%d')}"

    if not mandate.autopay_enabled or not mandate.autopay_token:
        return False, "AutoPay is not enabled on mandate"

    if mandate.recurring_auth_status != "ACTIVE":
        return False, f"AutoPay recurring status is {mandate.recurring_auth_status} (requires human authorization)"

    max_per_charge = getattr(mandate, "max_amount_per_charge", 7500000) or 7500000
    if amount > max_per_charge:
        return False, f"Transaction ₹{amount/100:.2f} exceeds per-charge limit ₹{max_per_charge/100:.2f}"

    spent = getattr(mandate, "spent_amount", 0) or 0
    if spent + amount > mandate.max_amount:
        remaining = max(0, mandate.max_amount - spent)
        return False, f"Transaction ₹{amount/100:.2f} exceeds remaining mandate pool ₹{remaining/100:.2f} (Total: ₹{mandate.max_amount/100:.2f})"

    return True, "Mandate constraints satisfied for autonomous execution"


async def record_mandate_spend(mandate: Mandate, amount: int, session: AsyncSession) -> None:
    """Updates accumulated spend on the active buyer mandate."""
    mandate.spent_amount = (getattr(mandate, "spent_amount", 0) or 0) + amount
    await session.flush()


