# AGENT_15_VISUAL_BOUNDARY_GAUGES

## Objective

Build the Visual Mandate & Margin Safety Gauge UI in the Next.js Decision Receipt viewer (`/receipts/[id]`) and Merchant Dashboard (`/dashboard`). Proves to judges and merchants that every money action is bounded, gated, and visually explainable with zero guesswork.

## Scope

- `frontend/src/app/(merchant)/receipts/[id]/page.tsx`: Safety boundary meters and utilization gauges
- `frontend/src/app/(merchant)/dashboard/page.tsx`: Policy utilization & threat prevention overview
- Visual progress bars for:
  1. **Buyer Spending Mandate Gauge**: `₹4,998 / ₹10,000` (49.9% utilized) [🟢 SAFE]
  2. **Merchant Profit Margin Gauge**: `24.5%` Gross Margin (Threshold: ≥15.0%) [🟢 PROTECTED]
  3. **Order Quantity Limit Gauge**: `2 / 5` Max Units per SKU [🟢 COMPLIANT]
  4. **Inventory Reserve Buffer**: `41 units` remaining after sale (Reserve required: ≥2) [🟢 SECURE]

## Acceptance Criteria

- [ ] Visual color-coded gauge bars (Green for safe, Amber for threshold warning, Red for violation).
- [ ] Displays exact mathematical numerator, denominator, and threshold percentages.
- [ ] Renders seamlessly on desktop and mobile viewports.
