
# 14 — Test Plan

## 1. Testing Philosophy

Rule 8 (`01_PRODUCT_SPEC.md`): every implementation feature has tests. Guardian, Mandate, and Policy logic are pure functions — they get exhaustive unit tests with zero mocks. Everything touching Razorpay is tested against a mocked adapter in CI, with a small manual test-mode checklist for real API verification before demo day.

## 2. Test Layers

| Layer                                                                                 | Tool                                              | Owner                       | Runs                       |
| ------------------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------- | -------------------------- |
| Unit — pure logic (mandate, policy, guardian checks, security scanner)               | pytest                                            | each component's agent      | every commit               |
| Unit — API contract shape                                                            | pytest + pydantic schema validation               | AGENT_10                    | every commit               |
| Integration — module-to-module (e.g., agent→guardian→adapter with mocked Razorpay) | pytest + httpx test client                        | AGENT_10 + component agents | every commit               |
| Contract/import-graph lint                                                            | custom script (`scripts/check_import_graph.py`) | AGENT_01                    | every commit (CI)          |
| Security/injection fixtures                                                           | pytest, fixture catalog                           | AGENT_09                    | every commit               |
| End-to-end demo scenarios                                                             | manual + scripted`httpx` walkthrough            | AGENT_10                    | before each milestone demo |
| Razorpay real test-mode smoke test                                                    | manual, real test API keys                        | AGENT_05 + AGENT_10         | Day 7, Day 9               |
| Receipt replay determinism                                                            | pytest, replays every seeded receipt              | AGENT_06                    | every commit               |

## 3. Import-Graph Lint (enforces `02_SYSTEM_ARCHITECTURE.md` §4)

```
FAIL if: app/commerce_agent imports app/razorpay_adapter
FAIL if: app/campaign imports app/razorpay_adapter
FAIL if: app/guardian imports app/ai_provider
FAIL if: app/mandate or app/policy import anything from app/api, app/commerce_agent, app/campaign, app/ai_provider
```

Run as a pre-commit hook and a CI step; this is the mechanical enforcement of the Golden Rule and must exist before any agent starts writing business logic (Day 0-1, owned by AGENT_01).

## 4. Guardian Test Matrix (maps directly to `13_THREAT_MODEL.md`)

Minimum required cases, one test function each:

1. Valid intent within mandate & policy → `APPROVE`
2. Quantity exceeds `mandate.max_quantity_per_item` → `BLOCK`
3. Category not in `mandate.allowed_categories` → `BLOCK`
4. Merchant not in `mandate.allowed_merchants` → `BLOCK`
5. Total exceeds `mandate.max_amount` → `BLOCK`
6. Total exceeds `mandate.confirmation_required_above` but under `max_amount` → `REQUIRE_CONFIRMATION`
7. Total exceeds `policy.maximum_order_value` → `BLOCK`
8. Discount exceeds `policy.maximum_discount_pct` → `BLOCK`
9. Resulting margin below `policy.minimum_margin_pct` → `BLOCK`
10. Resulting inventory below `policy.minimum_stock_to_sell` → `BLOCK`
11. Price increased since snapshot → `REQUIRE_CONFIRMATION`
12. Price decreased since snapshot → `APPROVE` at lower price, discrepancy logged
13. Inventory insufficient → `BLOCK`
14. Product no longer exists → `BLOCK`
15. Expired intent → `BLOCK`
16. Duplicate `intent_id` → second call `BLOCK`
17. No active mandate → `BLOCK`
18. Expired mandate → `BLOCK`
19. `suspicious_content_flag=true` on SKU with otherwise-valid intent → `APPROVE` still (informational only), flag present in receipt
20. Campaign proposal exceeding `allowed_campaign_discount_pct` → `BLOCK`/partial
21. Campaign proposal exceeding `daily_campaign_budget_cap` → `REQUIRE_CONFIRMATION`
22. Per-transaction campaign budget exhaustion mid-campaign → auto-`PAUSE`, transaction proceeds at full price

## 5. Injection/Security Test Matrix

See `09_CATALOG_SECURITY.md` §6 and `13_THREAT_MODEL.md` items 1-3, 8, 14. Minimum: 3 malicious-content fixtures (description injection, review injection, discount-instruction injection) each proven not to affect the Guardian decision, plus ≥10 benign catalog copy samples proven not to false-positive on the security scanner.

## 6. Receipt Replay Test

For every seeded/generated Receipt in the test DB, call `replay()` and assert `matches_original == true`. This runs in CI on every commit once `AGENT_06` lands the replay function — it is the strongest correctness signal in the whole system and should be treated as a release blocker if it ever fails.

## 7. End-to-End Scenario Scripts (owned by AGENT_10, used for `15_DEMO_SCENARIOS.md` rehearsal)

Each scenario is a scripted sequence of HTTP calls against a running local stack, asserting on responses:

- `scenario_happy_path.py` — discover → upsell → checkout → pay → receipt
- `scenario_injection_attack.py` — Failure 1
- `scenario_price_change.py` — Failure 2
- `scenario_campaign_lifecycle.py` — propose → approve → activate → transact → measure

## 8. Manual Pre-Demo Checklist (Day 9)

- [ ] Real Razorpay test-mode payment completes end-to-end with a real test card **[VERIFY current test card numbers against Razorpay docs]**
- [ ] Webhook received and processed for at least one real test payment
- [ ] All four demo scenario scripts pass against the exact build being demoed
- [ ] Receipt replay passes for all receipts generated during rehearsal
- [ ] Dashboard numbers cross-checked by hand against the DB for at least one metric

## 9. What Is Explicitly Not Tested (documented, not an oversight)

- Load/performance testing (out of scope for a buildathon MVP)
- Multi-merchant concurrency edge cases (single-merchant demo scope)
- Cryptographic mandate verification (unbuilt stretch feature)
