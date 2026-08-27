# AGENT_13_CAMPAIGN_AB_SIMULATOR

## Objective

Build the Autonomous Campaign A/B Strategy Simulator & Flash Budget Guard. Allows merchants to input a natural language revenue objective, generates two competing bounded marketing strategies (e.g. Strategy A: Flat Discount vs Strategy B: High-Margin Bundle Incentive), forecasts expected gross revenue and profit margin impact, and implements proactive budget threshold alerting.

## Scope

- `app/campaign/simulator.py`: Strategy simulation and financial projection logic
- `app/campaign/router.py`: `POST /campaign/simulate-ab` endpoint
- `app/campaign/service.py`: Automated Flash Budget Guard evaluating daily spend velocity
- Next.js Campaign Creator UI (`/campaigns`) with visual A/B Strategy comparison cards

## Strategy A vs Strategy B Projection Model

### Strategy A: Volume Driver (Direct Price Cut)
- Mechanics: 10% – 15% flat discount on primary SKUs
- Tradeoff: Higher conversion volume, lower margin per unit

### Strategy B: Margin Protector (Accessory Bundle Incentive)
- Mechanics: Full price on hero SKU + 40% – 50% discount on high-margin accessory
- Tradeoff: Preserves hero product price equity, increases units per transaction, higher gross profit

## Endpoint: `POST /campaign/simulate-ab`
Request:
```json
{
  "merchant_id": "m_001",
  "objective": "Boost audio sales this weekend while protecting profit margin"
}
```

Response:
```json
{
  "objective": "Boost audio sales this weekend while protecting profit margin",
  "strategy_a": {
    "name": "Volume Catalyst (Flat 10% Discount)",
    "discount_pct": 10,
    "eligible_skus": ["HP-001", "HP-002"],
    "projected_revenue_lift_pct": 28,
    "projected_gross_margin_pct": 21.5,
    "guardian_pre_check": "APPROVE"
  },
  "strategy_b": {
    "name": "Margin Protector (Free Case with Headphone Bundle)",
    "discount_pct": 50,
    "bundle_addon_sku": "CASE-HP",
    "eligible_skus": ["HP-001"],
    "projected_revenue_lift_pct": 36,
    "projected_gross_margin_pct": 29.8,
    "guardian_pre_check": "APPROVE"
  },
  "ai_recommendation": "Strategy B provides 8.3% higher profit margin retention."
}
```

## Acceptance Criteria

- [ ] `POST /campaign/simulate-ab` synthesizes dual bounded proposals with Guardian pre-validation.
- [ ] Merchant can click "Activate Strategy A" or "Activate Strategy B" with 1-click execution.
- [ ] Flash Budget Guard triggers automated pause if campaign expenditure hits 80% within 24h.
- [ ] Pytest unit test `tests/test_campaign_ab_simulator.py`.
