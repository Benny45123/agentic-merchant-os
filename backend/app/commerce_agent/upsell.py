from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.service import get_authoritative_state, get_product
from app.commerce_agent.schemas import CartItemSchema, RecommendationSchema
from app.mandate.service import get_active_mandate
from app.policy.service import get_active_policy


async def generate_upsell_recommendations(
    merchant_id: str,
    buyer_id: str,
    last_added_sku: str,
    current_subtotal: int,
    session: AsyncSession,
) -> List[RecommendationSchema]:
    """
    Deterministically filters and ranks upsell candidates based on stock,
    mandate limit, and merchant margin policy before returning top 1-2 recommendations.
    """
    product = await get_product(last_added_sku, session)
    if not product or not product.bundle_relationships:
        return []

    mandate = await get_active_mandate(buyer_id, session)
    policy = await get_active_policy(merchant_id, session)

    candidates: List[dict] = []

    for bundle_rel in product.bundle_relationships:
        rel_sku = bundle_rel.get("related_sku")
        relation = bundle_rel.get("relation", "accessory")

        if not rel_sku:
            continue

        rel_state = await get_authoritative_state(rel_sku, session)
        if not rel_state.exists or rel_state.inventory <= 0:
            continue

        # Check stock reserve policy
        if policy and (rel_state.inventory - 1) < policy.minimum_stock_to_sell:
            continue

        # Check mandate limit
        new_total = current_subtotal + rel_state.price
        if mandate and new_total > mandate.max_amount:
            continue

        # Check category constraint
        if mandate and mandate.allowed_categories is not None:
            if rel_state.category.lower() not in [c.lower() for c in mandate.allowed_categories]:
                continue

        # Check margin policy
        if policy and rel_state.cost and rel_state.cost > 0:
            margin_pct = ((rel_state.price - rel_state.cost) / rel_state.price) * 100.0
            if margin_pct < policy.minimum_margin_pct:
                continue

        # Priority weight: warranty_addon = 10, accessory = 5, other = 1
        priority = 10 if relation == "warranty_addon" else (5 if relation == "accessory" else 1)

        rel_product = await get_product(rel_sku, session)
        item_name = rel_product.name if rel_product else rel_sku

        if relation == "warranty_addon":
            reason = f"Protect your purchase with {item_name} for ₹{rel_state.price/100:.2f}"
        else:
            reason = f"Commonly paired with this item: {item_name} for ₹{rel_state.price/100:.2f}"

        candidates.append({
            "sku": rel_sku,
            "reason": reason,
            "price": rel_state.price,
            "priority": priority,
        })

    # Sort by priority desc, then price asc
    candidates.sort(key=lambda c: (-c["priority"], c["price"]))

    return [
        RecommendationSchema(
            sku=c["sku"],
            reason=c["reason"],
            price=c["price"],
        )
        for c in candidates[:2]
    ]
