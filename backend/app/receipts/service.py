from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import ensure_utc, generate_uuid, utc_now
from app.core.enums import DecisionType
from app.mandate.service import check_mandate
from app.models import (
    CatalogSnapshot,
    GuardianDecision,
    Mandate,
    MerchantPolicy,
    Receipt,
    TransactionIntent,
)
from app.policy.schemas import ResolvedItem
from app.policy.service import check_policy
from app.receipts.schemas import ReplayResponse


async def create_receipt(
    decision: GuardianDecision,
    intent: Optional[TransactionIntent],
    mandate: Optional[Mandate],
    policy: Optional[MerchantPolicy],
    merchant_id: str,
    buyer_id: Optional[str],
    items_snapshot: List[Dict[str, Any]],
    catalog_snapshot_ids: List[str],
    observed_total: int,
    final_verified_total: Optional[int],
    razorpay_order_id: Optional[str],
    failure_reason: Optional[str],
    session: AsyncSession,
    ap2_metadata: Optional[Dict[str, Any]] = None,
) -> Receipt:
    """
    Creates an immutable Decision Receipt capturing full frozen context.
    No live FK references for mandate/policy: they are snapshotted so historical
    audits are never corrupted by later edits.
    """
    mandate_snapshot = None
    if mandate:
        mandate_snapshot = {
            "mandate_id": mandate.mandate_id,
            "buyer_id": mandate.buyer_id,
            "max_amount": mandate.max_amount,
            "max_quantity_per_item": mandate.max_quantity_per_item,
            "allowed_categories": mandate.allowed_categories,
            "allowed_merchants": mandate.allowed_merchants,
            "allowed_products": mandate.allowed_products,
            "currency": mandate.currency,
            "expires_at": mandate.expires_at.isoformat() if mandate.expires_at else None,
            "confirmation_required_above": mandate.confirmation_required_above,
            "active": mandate.active,
            # Google AP2 Cryptographic Delegations
            "open_mandate_jwt": getattr(mandate, "open_mandate_jwt", None),
            "open_mandate_jti": ap2_metadata.get("open_jti") if ap2_metadata else None,
            "closed_mandate_jti": ap2_metadata.get("closed_jti") if ap2_metadata else None,
            "cart_digest": ap2_metadata.get("cart_digest") if ap2_metadata else None,
            "ap2_merkle_leaf": ap2_metadata.get("ap2_merkle_leaf") if ap2_metadata else None,
            "ap2_standard": "GOOGLE_AP2_ES256",
        }

    policy_snapshot = None
    if policy:
        policy_snapshot = {
            "policy_id": policy.policy_id,
            "merchant_id": policy.merchant_id,
            "maximum_discount_pct": policy.maximum_discount_pct,
            "minimum_margin_pct": policy.minimum_margin_pct,
            "maximum_order_value": policy.maximum_order_value,
            "allowed_products_for_discount": policy.allowed_products_for_discount,
            "minimum_stock_to_sell": policy.minimum_stock_to_sell,
            "version": policy.version,
        }

    receipt = Receipt(
        receipt_id=generate_uuid(),
        decision_id=decision.decision_id,
        intent_id=intent.intent_id if intent else None,
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        items_snapshot=items_snapshot,
        catalog_snapshot_ids=catalog_snapshot_ids,
        observed_total=observed_total,
        final_verified_total=final_verified_total,
        mandate_snapshot=mandate_snapshot,
        policy_snapshot=policy_snapshot,
        guardian_checks=decision.checks,
        decision=decision.decision,
        reason=decision.primary_reason,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=None,
        failure_reason=failure_reason,
        created_at=utc_now(),
    )
    session.add(receipt)
    await session.flush()
    return receipt


async def finalize_receipt_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    session: AsyncSession,
) -> Optional[Receipt]:
    """Appends confirmed Razorpay payment ID to existing Receipt."""
    stmt = select(Receipt).where(Receipt.razorpay_order_id == razorpay_order_id).order_by(Receipt.created_at.desc())
    result = await session.execute(stmt)
    receipt = result.scalars().first()
    if receipt:
        receipt.razorpay_payment_id = razorpay_payment_id
        await session.flush()
    return receipt



async def get_receipt(receipt_id: str, session: AsyncSession) -> Optional[Receipt]:
    """Retrieve receipt by ID."""
    stmt = select(Receipt).where(Receipt.receipt_id == receipt_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_receipts(
    merchant_id: Optional[str] = None,
    buyer_id: Optional[str] = None,
    decision: Optional[str] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
    session: AsyncSession = None,
) -> List[Receipt]:
    """Query audit receipts with filters."""
    stmt = select(Receipt).order_by(Receipt.created_at.desc())

    if merchant_id:
        stmt = stmt.where(Receipt.merchant_id == merchant_id)
    if buyer_id:
        stmt = stmt.where(Receipt.buyer_id == buyer_id)
    if decision:
        stmt = stmt.where(Receipt.decision == DecisionType(decision))
    if from_ts:
        stmt = stmt.where(Receipt.created_at >= from_ts)
    if to_ts:
        stmt = stmt.where(Receipt.created_at <= to_ts)

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def replay(receipt_id: str, session: AsyncSession) -> ReplayResponse:
    """
    Deterministic replay of an immutable receipt against its frozen snapshot data.
    Re-executes mandate checks and policy checks without touching current live state.
    """
    receipt = await get_receipt(receipt_id, session)
    if not receipt:
        raise ValueError(f"Receipt with ID '{receipt_id}' not found")

    items = receipt.items_snapshot or []
    total_amount = receipt.final_verified_total or receipt.observed_total

    # Reconstruct Mandate from frozen snapshot
    mandate_obj = None
    if receipt.mandate_snapshot:
        ms = receipt.mandate_snapshot
        mandate_obj = Mandate(
            mandate_id=ms["mandate_id"],
            buyer_id=ms["buyer_id"],
            max_amount=ms["max_amount"],
            max_quantity_per_item=ms["max_quantity_per_item"],
            allowed_categories=ms.get("allowed_categories"),
            allowed_merchants=ms.get("allowed_merchants"),
            allowed_products=ms.get("allowed_products"),
            currency=ms.get("currency", "INR"),
            expires_at=ensure_utc(datetime.fromisoformat(ms["expires_at"])) if ms.get("expires_at") else utc_now(),
            confirmation_required_above=ms.get("confirmation_required_above"),
            active=ms.get("active", True),
        )

    # Reconstruct Policy from frozen snapshot
    policy_obj = None
    if receipt.policy_snapshot:
        ps = receipt.policy_snapshot
        policy_obj = MerchantPolicy(
            policy_id=ps["policy_id"],
            merchant_id=ps["merchant_id"],
            maximum_discount_pct=ps["maximum_discount_pct"],
            minimum_margin_pct=ps["minimum_margin_pct"],
            maximum_order_value=ps["maximum_order_value"],
            allowed_products_for_discount=ps.get("allowed_products_for_discount"),
            minimum_stock_to_sell=ps["minimum_stock_to_sell"],
            version=ps.get("version", 1),
        )

    # Reconstruct resolved items from snapshot
    resolved_items: List[ResolvedItem] = []
    for item in items:
        resolved_items.append(
            ResolvedItem(
                sku=item.get("sku", ""),
                qty=item.get("qty", 1),
                authoritative_price=item.get("authoritative_price", item.get("observed_price", 0)),
                cost=item.get("cost"),
                inventory=item.get("inventory", 999),
                category=item.get("category", "audio"),
                discount_pct=item.get("discount_pct", 0),
                catalog_version=item.get("catalog_version", 1),
                snapshot_id=item.get("snapshot_id"),
            )
        )

    # 1. Run Mandate Check
    mandate_res = check_mandate(
        buyer_id=receipt.buyer_id or "",
        merchant_id=receipt.merchant_id,
        items=items,
        total_amount=total_amount,
        mandate=mandate_obj,
        now=receipt.created_at,
    )

    # 2. Run Policy Check
    policy_res = check_policy(
        merchant_id=receipt.merchant_id,
        resolved_items=resolved_items,
        total_amount=total_amount,
        requested_discount_pct=0,
        policy=policy_obj,
    )

    # Combine replayed decision
    replayed_checks: List[Dict[str, Any]] = [
        {"name": c.name, "passed": c.passed, "detail": c.detail}
        for c in mandate_res.checks
    ] + [
        {"name": c.name, "passed": c.passed, "detail": c.detail}
        for c in policy_res.checks
    ]

    if not mandate_res.passed:
        replay_decision = DecisionType.BLOCK.value
        replayed_reason = mandate_res.failure_reason or "Mandate check failed"
    elif not policy_res.passed:
        replay_decision = DecisionType.BLOCK.value
        replayed_reason = policy_res.failure_reason or "Policy check failed"
    elif mandate_res.requires_confirmation or policy_res.requires_confirmation:
        replay_decision = DecisionType.REQUIRE_CONFIRMATION.value
        replayed_reason = "Confirmation required by policy or mandate threshold"
    else:
        replay_decision = DecisionType.APPROVE.value
        replayed_reason = "All mandate and merchant policy checks passed"

    original_decision_val = receipt.decision.value if hasattr(receipt.decision, "value") else str(receipt.decision)
    matches_original = (replay_decision == original_decision_val)

    return ReplayResponse(
        receipt_id=receipt.receipt_id,
        original_decision=original_decision_val,
        replay_decision=replay_decision,
        matches_original=matches_original,
        replayed_checks=replayed_checks,
        replayed_reason=replayed_reason,
    )
