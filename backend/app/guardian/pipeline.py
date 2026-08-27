from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.service import get_authoritative_state
from app.core.base import ensure_utc, generate_uuid, utc_now
from app.core.enums import CampaignStatus, DecisionType, OrderStatus
from app.guardian.schemas import (
    CampaignProposalRequest,
    GuardianCheckSchema,
    GuardianDecisionResponse,
    RazorpayOrderSchema,
    TransactionIntentRequest,
)
from app.mandate.service import check_mandate, get_active_mandate
from app.models import (
    Campaign,
    GuardianDecision,
    Order,
    TransactionIntent,
)
from app.policy.schemas import ResolvedItem
from app.policy.service import (
    check_campaign_policy,
    check_policy,
    get_active_policy,
    get_campaign_policy,
)
from app.razorpay_adapter.client import get_razorpay_adapter
from app.receipts.service import create_receipt


async def evaluate_transaction_intent(
    intent_req: TransactionIntentRequest,
    session: AsyncSession,
) -> GuardianDecisionResponse:
    """
    Deterministic Commerce Guardian pipeline for buyer purchase requests.
    Zero LLM calls. The only path that can authorize order creation with Razorpay.
    """
    now = utc_now()
    decision_id = generate_uuid()
    checks: List[GuardianCheckSchema] = []
    requires_confirmation = False
    is_blocked = False
    block_reasons: List[str] = []

    # --------------------------------------------------------------------------
    # 1. Replay & Intent Expiry Checks
    # --------------------------------------------------------------------------
    intent_expiry = ensure_utc(intent_req.expires_at)
    if intent_expiry and intent_expiry < now:
        is_blocked = True
        block_reasons.append("Transaction intent has expired")
        checks.append(
            GuardianCheckSchema(
                name="replay.not_expired",
                passed=False,
                detail=f"Intent expired at {intent_req.expires_at.isoformat()}",
            )
        )
    else:
        checks.append(
            GuardianCheckSchema(
                name="replay.not_expired",
                passed=True,
                detail="Transaction intent is within valid time window",
            )
        )

    # Check duplicate intent_id
    stmt = select(TransactionIntent).where(TransactionIntent.intent_id == intent_req.intent_id)
    res = await session.execute(stmt)
    existing_intent = res.scalar_one_or_none()
    if existing_intent:
        is_blocked = True
        block_reasons.append("Duplicate intent_id replay detected")
        checks.append(
            GuardianCheckSchema(
                name="replay.not_duplicate",
                passed=False,
                detail=f"Intent {intent_req.intent_id} has already been evaluated",
            )
        )
    else:
        checks.append(
            GuardianCheckSchema(
                name="replay.not_duplicate",
                passed=True,
                detail="Intent ID is unique and valid",
            )
        )

    # --------------------------------------------------------------------------
    # 2. Authoritative State Fetch & Price/Inventory Revalidation
    # --------------------------------------------------------------------------
    resolved_items: List[ResolvedItem] = []
    observed_total = 0
    authoritative_subtotal = 0
    has_suspicious_flag = False

    for item in intent_req.items:
        observed_total += item.observed_price * item.qty
        auth_state = await get_authoritative_state(item.sku, session)

        # 2a. Product existence check
        if not auth_state.exists:
            is_blocked = True
            block_reasons.append(f"Product '{item.sku}' no longer exists in catalog")
            checks.append(
                GuardianCheckSchema(
                    name="catalog.product_exists",
                    passed=False,
                    detail=f"SKU {item.sku} not found in database",
                )
            )
            continue
        else:
            checks.append(
                GuardianCheckSchema(
                    name="catalog.product_exists",
                    passed=True,
                    detail=f"SKU {item.sku} exists in catalog",
                )
            )

        if auth_state.suspicious_content_flag:
            has_suspicious_flag = True

        # 2b. Inventory sufficiency check
        if auth_state.inventory < item.qty:
            is_blocked = True
            block_reasons.append(
                f"Insufficient inventory for {item.sku} (requested {item.qty}, available {auth_state.inventory})"
            )
            checks.append(
                GuardianCheckSchema(
                    name="catalog.inventory_available",
                    passed=False,
                    detail=f"Requested {item.qty} exceeds available stock {auth_state.inventory} for {item.sku}",
                )
            )
        else:
            checks.append(
                GuardianCheckSchema(
                    name="catalog.inventory_available",
                    passed=True,
                    detail=f"Available stock ({auth_state.inventory}) satisfies request ({item.qty}) for {item.sku}",
                )
            )

        # 2c. Price Drift / Snapshot comparison check
        if auth_state.price > item.observed_price:
            requires_confirmation = True
            checks.append(
                GuardianCheckSchema(
                    name="catalog.price_match",
                    passed=False,
                    detail=f"SKU {item.sku} price increased from observed {item.observed_price} to authoritative {auth_state.price} paise",
                )
            )
            authoritative_subtotal += auth_state.price * item.qty
        elif auth_state.price < item.observed_price:
            # Price decreased: charge lower price, log discrepancy
            checks.append(
                GuardianCheckSchema(
                    name="catalog.price_match",
                    passed=True,
                    detail=f"SKU {item.sku} price decreased: charging lower authoritative price {auth_state.price} paise (observed {item.observed_price})",
                )
            )
            authoritative_subtotal += auth_state.price * item.qty
        else:
            checks.append(
                GuardianCheckSchema(
                    name="catalog.price_match",
                    passed=True,
                    detail=f"Authoritative price matches observed price {auth_state.price} paise for {item.sku}",
                )
            )
            authoritative_subtotal += auth_state.price * item.qty

        resolved_items.append(
            ResolvedItem(
                sku=item.sku,
                qty=item.qty,
                authoritative_price=auth_state.price,
                cost=auth_state.cost,
                inventory=auth_state.inventory,
                category=auth_state.category,
                discount_pct=intent_req.requested_discount_pct,
                catalog_version=auth_state.catalog_version,
                snapshot_id=item.snapshot_id,
            )
        )

    # Informational security scanner check
    checks.append(
        GuardianCheckSchema(
            name="security.catalog_content_flagged",
            passed=True,
            detail="Content security scanner flag: " + ("FLAGGED (informational only)" if has_suspicious_flag else "CLEAN"),
        )
    )

    # Compute final verified total with discount applied
    discount_factor = 1.0 - (intent_req.requested_discount_pct / 100.0)
    final_verified_total = int(round(authoritative_subtotal * discount_factor))

    # --------------------------------------------------------------------------
    # 3. Mandate Engine Check (Pure Function)
    # --------------------------------------------------------------------------
    active_mandate = await get_active_mandate(intent_req.buyer_id, session)
    item_dicts = [
        {"sku": ri.sku, "qty": ri.qty, "category": ri.category}
        for ri in resolved_items
    ]
    mandate_res = check_mandate(
        buyer_id=intent_req.buyer_id,
        merchant_id=intent_req.merchant_id,
        items=item_dicts,
        total_amount=final_verified_total,
        mandate=active_mandate,
        now=now,
    )
    for c in mandate_res.checks:
        checks.append(GuardianCheckSchema(name=c.name, passed=c.passed, detail=c.detail))

    if not mandate_res.passed:
        is_blocked = True
        if mandate_res.failure_reason:
            block_reasons.append(mandate_res.failure_reason)
    if mandate_res.requires_confirmation:
        requires_confirmation = True

    # --------------------------------------------------------------------------
    # 4. Policy Engine Check (Pure Function)
    # --------------------------------------------------------------------------
    active_policy = await get_active_policy(intent_req.merchant_id, session)
    policy_res = check_policy(
        merchant_id=intent_req.merchant_id,
        resolved_items=resolved_items,
        total_amount=final_verified_total,
        requested_discount_pct=intent_req.requested_discount_pct,
        policy=active_policy,
    )
    for c in policy_res.checks:
        checks.append(GuardianCheckSchema(name=c.name, passed=c.passed, detail=c.detail))

    if not policy_res.passed:
        is_blocked = True
        if policy_res.failure_reason:
            block_reasons.append(policy_res.failure_reason)
    if policy_res.requires_confirmation:
        requires_confirmation = True

    # --------------------------------------------------------------------------
    # 5. Determine Overall Decision
    # --------------------------------------------------------------------------
    if is_blocked:
        overall_decision = DecisionType.BLOCK
        primary_reason = "; ".join(block_reasons) if block_reasons else "Transaction blocked by Guardian validation rules"
        final_total_output = None
    elif requires_confirmation:
        overall_decision = DecisionType.REQUIRE_CONFIRMATION
        primary_reason = "Confirmation required due to price discrepancy or mandate threshold"
        final_total_output = final_verified_total
    else:
        overall_decision = DecisionType.APPROVE
        primary_reason = "All mandate, policy, inventory, and price checks passed successfully"
        final_total_output = final_verified_total

    # --------------------------------------------------------------------------
    # 6. Persist TransactionIntent & GuardianDecision
    # --------------------------------------------------------------------------
    if existing_intent:
        persisted_intent = existing_intent
    else:
        persisted_intent = TransactionIntent(
            intent_id=intent_req.intent_id,
            buyer_id=intent_req.buyer_id,
            merchant_id=intent_req.merchant_id,
            items=[item.model_dump() for item in intent_req.items],
            requested_discount_pct=intent_req.requested_discount_pct,
            created_at=intent_req.created_at,
            expires_at=intent_req.expires_at,
        )
        session.add(persisted_intent)

    decision_record = GuardianDecision(
        decision_id=decision_id,
        intent_id=persisted_intent.intent_id,
        campaign_proposal_id=None,
        decision=overall_decision,
        checks=[c.model_dump() for c in checks],
        primary_reason=primary_reason,
        final_verified_total=final_total_output,
        mandate_id=active_mandate.mandate_id if active_mandate else None,
        policy_version=active_policy.version if active_policy else None,
        created_at=utc_now(),
    )
    session.add(decision_record)
    await session.flush()

    # --------------------------------------------------------------------------
    # 7. Razorpay Order Creation (ONLY IF APPROVE)
    # --------------------------------------------------------------------------
    razorpay_order_payload = None
    created_order_id = None

    if overall_decision == DecisionType.APPROVE and final_verified_total is not None:
        adapter = get_razorpay_adapter()
        rzp_order = adapter.create_order(
            amount=final_verified_total,
            currency="INR",
            receipt_id=decision_id,
        )
        created_order_id = rzp_order.order_id
        razorpay_order_payload = RazorpayOrderSchema(
            order_id=rzp_order.order_id,
            amount=rzp_order.amount,
            currency=rzp_order.currency,
            key_id=rzp_order.key_id,
        )

        # Mirror in Order table
        order_row = Order(
            order_id=rzp_order.order_id,
            decision_id=decision_id,
            merchant_id=intent_req.merchant_id,
            buyer_id=intent_req.buyer_id,
            amount=final_verified_total,
            currency="INR",
            status=OrderStatus.CREATED,
            campaign_id=None,
            created_at=utc_now(),
        )
        session.add(order_row)

    # --------------------------------------------------------------------------
    # 8. Create Immutable Decision Receipt
    # --------------------------------------------------------------------------
    items_snapshot = [
        {
            "sku": ri.sku,
            "qty": ri.qty,
            "authoritative_price": ri.authoritative_price,
            "cost": ri.cost,
            "inventory": ri.inventory,
            "category": ri.category,
            "discount_pct": ri.discount_pct,
            "catalog_version": ri.catalog_version,
            "snapshot_id": ri.snapshot_id,
        }
        for ri in resolved_items
    ]
    catalog_snapshot_ids = [
        ri.snapshot_id for ri in resolved_items if ri.snapshot_id
    ]

    receipt = await create_receipt(
        decision=decision_record,
        intent=persisted_intent,
        mandate=active_mandate,
        policy=active_policy,
        merchant_id=intent_req.merchant_id,
        buyer_id=intent_req.buyer_id,
        items_snapshot=items_snapshot,
        catalog_snapshot_ids=catalog_snapshot_ids,
        observed_total=observed_total,
        final_verified_total=final_total_output,
        razorpay_order_id=created_order_id,
        failure_reason=primary_reason if overall_decision == DecisionType.BLOCK else None,
        session=session,
    )

    await session.commit()

    return GuardianDecisionResponse(
        decision_id=decision_record.decision_id,
        intent_id=persisted_intent.intent_id,
        decision=overall_decision,
        checks=checks,
        primary_reason=primary_reason,
        final_verified_total=final_total_output,
        receipt_id=receipt.receipt_id,
        razorpay_order=razorpay_order_payload,
    )


async def evaluate_campaign_proposal(
    proposal: CampaignProposalRequest,
    session: AsyncSession,
) -> GuardianDecisionResponse:
    """
    Deterministic campaign validation against MerchantPolicy and CampaignPolicy.
    """
    decision_id = generate_uuid()
    active_policy = await get_active_policy(proposal.merchant_id, session)
    campaign_policy = await get_campaign_policy(proposal.merchant_id, session)

    checks: List[GuardianCheckSchema] = []

    if not active_policy or not campaign_policy:
        decision_record = GuardianDecision(
            decision_id=decision_id,
            intent_id=None,
            campaign_proposal_id=proposal.proposal_id,
            decision=DecisionType.BLOCK,
            checks=[{"name": "policy.exists", "passed": False, "detail": "Merchant or campaign policy not found"}],
            primary_reason="Merchant policies not configured",
            final_verified_total=None,
            policy_version=active_policy.version if active_policy else None,
            created_at=utc_now(),
        )
        session.add(decision_record)
        await session.commit()
        return GuardianDecisionResponse(
            decision_id=decision_record.decision_id,
            decision=DecisionType.BLOCK,
            checks=[GuardianCheckSchema(name="policy.exists", passed=False, detail="Policies not configured")],
            primary_reason="Merchant policies not configured",
            final_verified_total=None,
            receipt_id="",
            razorpay_order=None,
        )

    # Fetch product data for proposed eligible skus
    product_data: Dict[str, Dict[str, Any]] = {}
    for sku in proposal.eligible_skus:
        state = await get_authoritative_state(sku, session)
        if state.exists:
            product_data[sku] = {
                "price": state.price,
                "cost": state.cost,
                "inventory": state.inventory,
            }

    policy_res = check_campaign_policy(
        proposal=proposal.model_dump(),
        policy=active_policy,
        campaign_policy=campaign_policy,
        product_data=product_data,
    )

    for c in policy_res.checks:
        checks.append(GuardianCheckSchema(name=c.name, passed=c.passed, detail=c.detail))

    if not policy_res.passed:
        overall_decision = DecisionType.BLOCK
        primary_reason = policy_res.failure_reason or "Campaign proposal breaches policy limits"
    elif policy_res.requires_confirmation:
        overall_decision = DecisionType.REQUIRE_CONFIRMATION
        primary_reason = "Campaign budget exceeds daily cap -> requires merchant confirmation"
    else:
        overall_decision = DecisionType.APPROVE
        primary_reason = "Campaign proposal conforms to all merchant and discount policies"

    decision_record = GuardianDecision(
        decision_id=decision_id,
        intent_id=None,
        campaign_proposal_id=proposal.proposal_id,
        decision=overall_decision,
        checks=[c.model_dump() for c in checks],
        primary_reason=primary_reason,
        final_verified_total=proposal.budget,
        policy_version=active_policy.version,
        created_at=utc_now(),
    )
    session.add(decision_record)
    await session.commit()

    return GuardianDecisionResponse(
        decision_id=decision_record.decision_id,
        decision=overall_decision,
        checks=checks,
        primary_reason=primary_reason,
        final_verified_total=proposal.budget,
        receipt_id="",
        razorpay_order=None,
    )


async def confirm_guardian_decision(
    decision_id: str,
    session: AsyncSession,
) -> GuardianDecisionResponse:
    """
    Re-runs full pipeline for a decision that previously returned REQUIRE_CONFIRMATION.
    Never trusts old decisions blindly: verifies current authoritative state.
    """
    stmt = select(GuardianDecision).where(GuardianDecision.decision_id == decision_id)
    res = await session.execute(stmt)
    old_decision = res.scalar_one_or_none()

    if not old_decision or not old_decision.intent_id:
        raise ValueError(f"Valid intent decision '{decision_id}' not found")

    intent_stmt = select(TransactionIntent).where(TransactionIntent.intent_id == old_decision.intent_id)
    intent_res = await session.execute(intent_stmt)
    intent = intent_res.scalar_one_or_none()

    if not intent:
        raise ValueError(f"Intent for decision '{decision_id}' not found")

    # Generate a fresh confirmed intent request
    re_req = TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=intent.buyer_id,
        merchant_id=intent.merchant_id,
        items=intent.items,
        requested_discount_pct=intent.requested_discount_pct,
        created_at=utc_now(),
        expires_at=datetime.fromtimestamp(utc_now().timestamp() + 120, tz=timezone.utc),
    )

    return await evaluate_transaction_intent(re_req, session)
