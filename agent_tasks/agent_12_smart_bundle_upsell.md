# AGENT_12_SMART_BUNDLE_UPSELL

## Objective

Build the Dynamic Margin-Optimized Bundling Engine. Proactively computes gross margin headroom between high-margin parent products and compatible accessories/warranties to dynamically offer discounted bundles that maximize Average Order Value (AOV) while preserving the merchant's strict minimum profit margin policy.

## Scope

- `app/commerce_agent/upsell.py`: Upgraded bundling math and candidate evaluation
- `app/policy/service.py`: Add `calculate_bundle_margin(parent_sku, addon_sku, discount_pct)` helper
- `app/commerce_agent/schemas.py`: Add `BundleOfferSchema`
- Frontend UI bundle recommendation card with 1-click cart acceptance

## Dynamic Margin Formula

```text
Parent Item: Price P1, Cost C1
Addon Item: Price P2, Cost C2
Addon Discount: d %

Discounted Addon Price P2' = P2 * (1 - d/100)
Total Bundle Revenue = P1 + P2'
Total Bundle Cost = C1 + C2
Resulting Gross Margin % = ((Total Revenue - Total Cost) / Total Revenue) * 100

Safety Condition: Resulting Gross Margin % >= policy.minimum_margin_pct
```

## Example Dynamic Deal
- Parent: `HP-001` (Price: ₹4,499, Cost: ₹3,000, Margin: 33.3%)
- Addon: `CASE-HP` (Price: ₹999, Cost: ₹400)
- Standard Addon Margin: 60.0%
- At 30% discount on case (P2' = ₹699.30):
  - Total Revenue = ₹5,198.30, Total Cost = ₹3,400.00
  - Bundle Margin = 34.6% >= 15% Minimum Merchant Margin Policy ✅
- Offer Generated: *"Bundle the Hard Shell Case (`CASE-HP`) for 30% off (Save ₹300)!"*

## Acceptance Criteria

- [ ] Calculates mathematical gross margin for multi-item bundles before offering discount.
- [ ] Never suggests a bundle discount that breaches `policy.minimum_margin_pct`.
- [ ] 1-Click "Add Bundle" button in the frontend adds both items with discount cleanly to the cart.
- [ ] Pytest unit tests in `tests/test_smart_bundle_upsell.py` verifying mathematical safety boundaries.
