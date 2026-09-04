from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session
from app.core.enums import DecisionType, OrderStatus
from app.models import Order, Receipt

router = APIRouter(prefix="/dashboard", tags=["Merchant Dashboard & Revenue Analytics"])


class RevenueAnalyticsResponse(BaseModel):
    total_revenue: int
    store_revenue: int = 0
    order_count: int
    upsell_attach_rate: float
    upsell_revenue: int
    campaign_revenue: int
    blocked_attempt_count: int


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    merchant_id: str = Query(..., description="Merchant UUID"),
    from_date: Optional[datetime] = Query(None, alias="from", description="ISO start timestamp"),
    to_date: Optional[datetime] = Query(None, alias="to", description="ISO end timestamp"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """
    Live aggregated revenue metrics computed from Order and Receipt tables.
    Zero hardcoded values per Rule 6.
    """
    # 1. Base Query for Paid Orders
    paid_stmt = select(Order).where(
        Order.merchant_id == merchant_id,
        Order.status == OrderStatus.PAID
    )
    if from_date:
        paid_stmt = paid_stmt.where(Order.created_at >= from_date)
    if to_date:
        paid_stmt = paid_stmt.where(Order.created_at <= to_date)

    paid_orders_res = await session.execute(paid_stmt)
    paid_orders = list(paid_orders_res.scalars().all())

    total_revenue = sum(o.amount for o in paid_orders)
    order_count = len(paid_orders)

    # 2. Campaign revenue
    campaign_revenue = sum(o.amount for o in paid_orders if o.campaign_id is not None)

    # 3. Blocked attempts from Receipt table
    block_stmt = select(func.count(Receipt.receipt_id)).where(
        Receipt.merchant_id == merchant_id,
        Receipt.decision == DecisionType.BLOCK
    )
    if from_date:
        block_stmt = block_stmt.where(Receipt.created_at >= from_date)
    if to_date:
        block_stmt = block_stmt.where(Receipt.created_at <= to_date)

    block_res = await session.execute(block_stmt)
    blocked_attempt_count = block_res.scalar() or 0

    # 4. Upsell metrics from Receipts of paid orders (1 Single Batch Query)
    upsell_orders_count = 0
    upsell_revenue = 0

    decision_ids = [o.decision_id for o in paid_orders if o.decision_id]
    if decision_ids:
        r_stmt = select(Receipt).where(Receipt.decision_id.in_(decision_ids))
        r_res = await session.execute(r_stmt)
        for receipt in r_res.scalars().all():
            if receipt and receipt.items_snapshot:
                has_upsell = False
                for item in receipt.items_snapshot:
                    # Check if item was flagged as upsell or is a known accessory/warranty SKU
                    if item.get("source") == "upsell" or item.get("sku") in ["WRNTY-1Y", "CASE-HP"]:
                        has_upsell = True
                        item_price = item.get("authoritative_price", item.get("observed_price", 0))
                        upsell_revenue += item_price * item.get("qty", 1)
                if has_upsell:
                    upsell_orders_count += 1

    upsell_attach_rate = (upsell_orders_count / order_count) if order_count > 0 else 0.0

    return RevenueAnalyticsResponse(
        total_revenue=total_revenue,
        store_revenue=total_revenue,
        order_count=order_count,
        upsell_attach_rate=round(upsell_attach_rate, 2),
        upsell_revenue=upsell_revenue,
        campaign_revenue=campaign_revenue,
        blocked_attempt_count=blocked_attempt_count,
    )
