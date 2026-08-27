from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import generate_uuid, utc_now
from app.models import CampaignPolicy, MerchantPolicy
from app.policy.schemas import (
    MerchantPolicyUpdate,
    PolicyCheckItem,
    PolicyCheckResult,
    ResolvedItem,
)


async def get_active_policy(
    merchant_id: str,
    session: AsyncSession
) -> Optional[MerchantPolicy]:
    """Retrieve the latest version of merchant policy."""
    stmt = (
        select(MerchantPolicy)
        .where(MerchantPolicy.merchant_id == merchant_id)
        .order_by(MerchantPolicy.version.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_campaign_policy(
    merchant_id: str,
    session: AsyncSession
) -> Optional[CampaignPolicy]:
    """Retrieve campaign policy for a merchant."""
    stmt = select(CampaignPolicy).where(CampaignPolicy.merchant_id == merchant_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_policy(
    merchant_id: str,
    data: MerchantPolicyUpdate,
    session: AsyncSession
) -> MerchantPolicy:
    """
    Versioned policy replacement.
    Creates a NEW row with version = latest_version + 1. Never mutates historical rows.
    """
    current_latest = await get_active_policy(merchant_id, session)
    new_version = (current_latest.version + 1) if current_latest else 1

    new_policy = MerchantPolicy(
        policy_id=generate_uuid(),
        merchant_id=merchant_id,
        maximum_discount_pct=data.maximum_discount_pct,
        minimum_margin_pct=data.minimum_margin_pct,
        maximum_order_value=data.maximum_order_value,
        allowed_products_for_discount=data.allowed_products_for_discount,
        minimum_stock_to_sell=data.minimum_stock_to_sell,
        version=new_version,
        created_at=utc_now(),
    )
    session.add(new_policy)
    await session.flush()
    return new_policy


def check_policy(
    merchant_id: str,
    resolved_items: List[ResolvedItem],
    total_amount: int,
    requested_discount_pct: int,
    policy: Optional[MerchantPolicy],
) -> PolicyCheckResult:
    """
    Pure validation function. No I/O, no DB calls, no LLM.
    Evaluates merchant constraints deterministically.
    """
    checks: List[PolicyCheckItem] = []

    if not policy:
        checks.append(
            PolicyCheckItem(
                name="policy.exists",
                passed=False,
                detail="No merchant policy found",
            )
        )
        return PolicyCheckResult(
            passed=False,
            checks=checks,
            failure_reason="Merchant policy not configured",
        )

    checks.append(
        PolicyCheckItem(
            name="policy.exists",
            passed=True,
            detail=f"Using merchant policy version {policy.version}",
        )
    )

    # 1. Maximum Order Value Check
    if total_amount > policy.maximum_order_value:
        checks.append(
            PolicyCheckItem(
                name="policy.maximum_order_value",
                passed=False,
                detail=f"Order total {total_amount} paise exceeds maximum order value {policy.maximum_order_value} paise",
            )
        )
        return PolicyCheckResult(
            passed=False,
            checks=checks,
            failure_reason=f"Order total ₹{total_amount/100:.2f} exceeds merchant maximum order value limit",
        )

    checks.append(
        PolicyCheckItem(
            name="policy.maximum_order_value",
            passed=True,
            detail=f"Order total {total_amount} paise is within maximum order value {policy.maximum_order_value} paise",
        )
    )

    # 2. Maximum Discount Percentage Check
    effective_discount = max(
        requested_discount_pct,
        max([item.discount_pct for item in resolved_items], default=0),
    )
    if effective_discount > policy.maximum_discount_pct:
        checks.append(
            PolicyCheckItem(
                name="policy.maximum_discount_pct",
                passed=False,
                detail=f"Requested discount {effective_discount}% exceeds maximum allowed {policy.maximum_discount_pct}%",
            )
        )
        return PolicyCheckResult(
            passed=False,
            checks=checks,
            failure_reason=f"Discount of {effective_discount}% exceeds merchant policy ceiling of {policy.maximum_discount_pct}%",
        )

    checks.append(
        PolicyCheckItem(
            name="policy.maximum_discount_pct",
            passed=True,
            detail=f"Discount {effective_discount}% within limit {policy.maximum_discount_pct}%",
        )
    )

    # 3. Minimum Margin Check across all items
    # Formula: margin_pct = (price_after_discount - cost) / price_after_discount * 100
    for item in resolved_items:
        if item.cost is not None and item.cost > 0:
            item_discount = max(item.discount_pct, requested_discount_pct)
            price_after_discount = item.authoritative_price * (1 - item_discount / 100.0)
            
            if price_after_discount <= 0:
                checks.append(
                    PolicyCheckItem(
                        name="policy.min_margin",
                        passed=False,
                        detail=f"SKU {item.sku}: effective price after discount is <= 0",
                    )
                )
                return PolicyCheckResult(
                    passed=False,
                    checks=checks,
                    failure_reason=f"Item {item.sku} price after discount is zero or negative",
                )

            margin_pct = ((price_after_discount - item.cost) / price_after_discount) * 100.0

            if margin_pct < policy.minimum_margin_pct:
                checks.append(
                    PolicyCheckItem(
                        name="policy.min_margin",
                        passed=False,
                        detail=f"SKU {item.sku}: margin {margin_pct:.1f}% is below minimum {policy.minimum_margin_pct}%",
                    )
                )
                return PolicyCheckResult(
                    passed=False,
                    checks=checks,
                    failure_reason=f"Resulting margin on {item.sku} ({margin_pct:.1f}%) breaches merchant minimum margin policy ({policy.minimum_margin_pct}%)",
                )
        else:
            # If cost is None, skip check with informational note
            checks.append(
                PolicyCheckItem(
                    name="policy.min_margin",
                    passed=True,
                    detail=f"SKU {item.sku}: cost not set, minimum margin check skipped with warning",
                )
            )

    checks.append(
        PolicyCheckItem(
            name="policy.min_margin",
            passed=True,
            detail=f"All items satisfy minimum margin of {policy.minimum_margin_pct}%",
        )
    )

    # 4. Minimum Stock to Sell Check
    for item in resolved_items:
        resulting_inventory = item.inventory - item.qty
        if resulting_inventory < policy.minimum_stock_to_sell:
            checks.append(
                PolicyCheckItem(
                    name="policy.minimum_stock_to_sell",
                    passed=False,
                    detail=f"SKU {item.sku}: remaining inventory ({resulting_inventory}) would fall below minimum stock limit ({policy.minimum_stock_to_sell})",
                )
            )
            return PolicyCheckResult(
                passed=False,
                checks=checks,
                failure_reason=f"Insufficient remaining inventory for {item.sku} (policy requires minimum {policy.minimum_stock_to_sell} units held in reserve)",
            )

    checks.append(
        PolicyCheckItem(
            name="policy.minimum_stock_to_sell",
            passed=True,
            detail="Inventory levels remain above merchant reserve limit",
        )
    )

    # 5. Allowed Products for Discount Check
    if policy.allowed_products_for_discount is not None and effective_discount > 0:
        for item in resolved_items:
            if item.sku not in policy.allowed_products_for_discount:
                checks.append(
                    PolicyCheckItem(
                        name="policy.allowed_products_for_discount",
                        passed=False,
                        detail=f"SKU {item.sku} is not eligible for discounts under policy {policy.allowed_products_for_discount}",
                    )
                )
                return PolicyCheckResult(
                    passed=False,
                    checks=checks,
                    failure_reason=f"SKU {item.sku} is not authorized for promotional discounting",
                )

    return PolicyCheckResult(
        passed=True,
        requires_confirmation=False,
        checks=checks,
        failure_reason=None,
    )


def check_campaign_policy(
    proposal: Dict[str, Any],
    policy: MerchantPolicy,
    campaign_policy: CampaignPolicy,
    product_data: Dict[str, Dict[str, Any]],
) -> PolicyCheckResult:
    """
    Pure validation function for Campaign Proposals.
    Evaluates campaign constraints against MerchantPolicy and CampaignPolicy.
    """
    checks: List[PolicyCheckItem] = []
    discount_pct = proposal.get("discount_pct", 0)
    budget = proposal.get("budget", 0)
    eligible_skus = proposal.get("eligible_skus", [])
    requires_confirmation = False

    # 1. Campaign Discount Ceiling
    max_campaign_discount = min(
        policy.maximum_discount_pct,
        campaign_policy.allowed_campaign_discount_pct,
    )
    if discount_pct > max_campaign_discount:
        checks.append(
            PolicyCheckItem(
                name="policy.max_discount",
                passed=False,
                detail=f"Proposed discount {discount_pct}% exceeds allowed campaign discount {max_campaign_discount}%",
            )
        )
        return PolicyCheckResult(
            passed=False,
            checks=checks,
            failure_reason=f"Proposed campaign discount {discount_pct}% exceeds policy ceiling {max_campaign_discount}%",
        )

    checks.append(
        PolicyCheckItem(
            name="policy.max_discount",
            passed=True,
            detail=f"Proposed discount {discount_pct}% within policy limit {max_campaign_discount}%",
        )
    )

    # 2. Campaign Budget vs Daily Cap
    if budget > campaign_policy.daily_campaign_budget_cap:
        requires_confirmation = True
        checks.append(
            PolicyCheckItem(
                name="policy.campaign_budget",
                passed=True,
                detail=f"Proposed budget {budget} paise exceeds daily cap {campaign_policy.daily_campaign_budget_cap} paise -> merchant confirmation required",
            )
        )
    else:
        checks.append(
            PolicyCheckItem(
                name="policy.campaign_budget",
                passed=True,
                detail=f"Budget {budget} paise within daily cap {campaign_policy.daily_campaign_budget_cap} paise",
            )
        )

    # 3. Product Margin & Stock eligibility
    disqualified_skus: List[str] = []
    for sku in eligible_skus:
        p = product_data.get(sku)
        if not p:
            disqualified_skus.append(sku)
            continue

        price = p.get("price", 0)
        cost = p.get("cost")
        inventory = p.get("inventory", 0)

        if inventory < policy.minimum_stock_to_sell:
            disqualified_skus.append(sku)
            continue

        if cost is not None and cost > 0:
            price_after_discount = price * (1 - discount_pct / 100.0)
            if price_after_discount <= 0:
                disqualified_skus.append(sku)
                continue
            margin_pct = ((price_after_discount - cost) / price_after_discount) * 100.0
            if margin_pct < policy.minimum_margin_pct:
                disqualified_skus.append(sku)

    if disqualified_skus:
        if len(disqualified_skus) == len(eligible_skus):
            checks.append(
                PolicyCheckItem(
                    name="policy.min_margin",
                    passed=False,
                    detail=f"All proposed SKUs {disqualified_skus} breach margin or stock limits",
                )
            )
            return PolicyCheckResult(
                passed=False,
                checks=checks,
                failure_reason="No eligible SKUs satisfy margin and stock policies",
            )
        else:
            checks.append(
                PolicyCheckItem(
                    name="policy.allowed_products",
                    passed=True,
                    detail=f"Partial eligibility: disqualified SKUs {disqualified_skus} removed from proposal",
                )
            )

    checks.append(
        PolicyCheckItem(
            name="policy.min_margin",
            passed=True,
            detail="Eligible campaign products satisfy margin policy",
        )
    )

    return PolicyCheckResult(
        passed=True,
        requires_confirmation=requires_confirmation,
        checks=checks,
        failure_reason=None,
    )
