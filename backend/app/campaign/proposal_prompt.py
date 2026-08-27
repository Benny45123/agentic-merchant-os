from typing import Any, Dict, List
from app.models import CampaignPolicy, MerchantPolicy, Product


def build_proposal_system_prompt(
    merchant_policy: MerchantPolicy,
    campaign_policy: CampaignPolicy,
    products: List[Product],
) -> str:
    """
    Builds the LLM prompt with real current catalog state and real policy limits.
    """
    catalog_summary = []
    for p in products:
        margin_pct = "N/A"
        if p.cost and p.cost > 0:
            margin_pct = f"{((p.price - p.cost) / p.price * 100):.1f}%"
        catalog_summary.append(
            f"- SKU: {p.sku} | Name: {p.name} | Category: {p.category} | Price: ₹{p.price/100:.2f} | Stock: {p.inventory} | List Margin: {margin_pct}"
        )

    products_str = "\n".join(catalog_summary)

    prompt = f"""You are the Campaign Strategy Orchestrator for an e-commerce merchant.
Your goal is to propose an effective promotional campaign to satisfy the merchant's revenue objective.

MERCHANT POLICY LIMITS (HARD RULES - Guardian will reject proposals that violate these):
- Max Single Discount: {merchant_policy.maximum_discount_pct}%
- Max Allowed Campaign Discount: {campaign_policy.allowed_campaign_discount_pct}%
- Minimum Margin Required: {merchant_policy.minimum_margin_pct}%
- Campaign Budget Default: ₹{campaign_policy.campaign_budget_default/100:.2f} ({campaign_policy.campaign_budget_default} paise)
- Daily Budget Cap: ₹{campaign_policy.daily_campaign_budget_cap/100:.2f} ({campaign_policy.daily_campaign_budget_cap} paise)

CURRENT PRODUCT CATALOG:
{products_str}

OUTPUT REQUIREMENTS:
Output a single valid JSON object with the following fields:
{{
  "eligible_skus": ["SKU1", "SKU2"],
  "discount_pct": int (must be <= {campaign_policy.allowed_campaign_discount_pct}),
  "bundle_offer": {{"trigger_sku": "SKU1", "addon_sku": "ADDON_SKU", "addon_discount_pct": int}} or null,
  "budget": int in paise (e.g. {campaign_policy.campaign_budget_default}),
  "duration_days": int (between 1 and 14),
  "rationale": "Clear 1-2 sentence explanation of why this proposal maximizes merchant revenue while respecting margins."
}}
"""
    return prompt
