
# 11 — Campaign Orchestrator Spec

## 1. Purpose

Lets a merchant state a plain-language revenue objective and get a **bounded, policy-validated** campaign live, without ever giving the LLM direct control over money. This is Side B of Track 01, and it reuses the exact same Guardian/Policy machinery as buyer checkout — it is not a parallel system.

## 2. Why This Is Not "A Fake Autonomous Loop"

The Orchestrator's LLM involvement is confined to **one proposal-generation step**. Everything after that is either (a) a deterministic Guardian validation, or (b) static data (`CampaignOffer` rows) that the *existing*, already-audited buyer checkout path picks up like any other offer. There is no background agent repeatedly making autonomous decisions — campaign "monitoring" is a deterministic check that runs synchronously on each transaction attempt, not a scheduled LLM loop.

```
Merchant objective (text)
        │
        ▼
 LLM proposes CampaignProposal (structured, from real catalog+history data)
        │
        ▼
 Guardian.evaluate_campaign()  ── deterministic, same engine as buyer checkout
        │
   APPROVE / REQUIRE_CONFIRMATION / BLOCK
        │
        ▼ (merchant confirms if needed)
 Orchestrator writes CampaignOffer rows (pure data, campaign_id tagged)
        │
        ▼
 Normal buyer checkout flow applies offers ── each transaction re-gated by Guardian
        │
        ▼
 Guardian decrements campaign.budget_spent per attributed order;
 auto-PAUSE if budget/margin would be breached
        │
        ▼
 Dashboard reads real Order/Receipt rows for revenue impact
```

## 3. Proposal Generation (`POST /campaign/propose`)

Inputs available to the LLM (all read-only, all real data — never invented):

- `catalog.search_products()` results relevant to the objective (e.g., category match for "headphones")
- Aggregated historical `Order`/`Receipt` data for those SKUs (units sold last 30 days, average order value, current margin at list price)
- Current `MerchantPolicy`/`CampaignPolicy` (so the LLM is prompted with the actual limits, reducing wasted `BLOCK` round-trips — though the Guardian re-checks regardless of what the prompt told the LLM)

Output: a `CampaignProposal` (see `04_API_CONTRACTS.md` §6) — `eligible_skus`, `discount_pct`, optional `bundle_offer`, `budget`, `starts_at`/`ends_at`, and a `rationale` string for merchant-facing explanation. This is parsed as structured JSON from the LLM response (schema-validated; a malformed/out-of-schema response is a hard error, retried once, then surfaced to the merchant rather than guessed at).

## 4. Guardian Validation

Exactly the pipeline in `07_GUARDIAN_SPEC.md` §4. Key outcomes:

- Discount too high → `BLOCK` (whole proposal) or, if only some SKUs qualify, a partial-approval with the disqualified SKUs removed and noted.
- Budget above daily cap → `REQUIRE_CONFIRMATION` (merchant can explicitly accept a one-off larger budget).
- Margin would go negative on any SKU → that SKU dropped from `eligible_skus`.

## 5. Activation (`POST /campaign/{id}/activate`)

Only allowed if the stored `guardian_decision.decision` is `APPROVE`, or the merchant has explicitly confirmed a `REQUIRE_CONFIRMATION` proposal (same confirm pattern as buyer checkout, reusing `/guardian/confirm/{decision_id}`). On activation:

1. `Campaign.status = ACTIVE`.
2. One `Offer(type=campaign_discount, campaign_id=...)` row is written per eligible SKU (and one for the bundle addon SKU if applicable).
3. `CampaignEvent(type=ACTIVATED)` logged.

## 6. Runtime Enforcement

Per `07_GUARDIAN_SPEC.md` §5 — every buyer transaction touching a campaign SKU re-validates the campaign budget at the moment of purchase. This prevents the classic race condition of "campaign budget looked fine when the agent priced the cart, but ran out by the time payment happened" — the same price/state revalidation principle applied to campaigns.

## 7. Campaign Lifecycle States

| State                | Meaning                                         | Transition                                                             |
| -------------------- | ----------------------------------------------- | ---------------------------------------------------------------------- |
| `DRAFT`            | Proposal generated, not yet validated           | →`PENDING_APPROVAL` on Guardian call                                |
| `PENDING_APPROVAL` | Guardian said`REQUIRE_CONFIRMATION`           | →`ACTIVE` on merchant confirm, or discarded                         |
| `ACTIVE`           | Offers live, buyers can use them                | →`PAUSED` (budget/margin breach) or `COMPLETED` (ends_at reached) |
| `PAUSED`           | Offers withdrawn, campaign visible but inactive | Manual merchant resume (SHOULD HAVE) or stays paused                   |
| `COMPLETED`        | Ended naturally                                 | Terminal                                                               |

## 8. Revenue Measurement (Rule 6 compliance)

`GET /campaign/{id}/status` computes `budget_spent`, `orders_attributed`, `revenue_attributed` by querying `Order` rows where `campaign_id` matches — never from a counter maintained by the LLM or a hardcoded projection.

## 9. Constraints Enforced (explicit list, matches `01_PRODUCT_SPEC.md`)

`maximum_discount`, `minimum_margin`, `maximum_campaign_budget` (= `daily_campaign_budget_cap` × days), `allowed_products` (via policy's `allowed_products_for_discount`, intersected with proposal's `eligible_skus`), `campaign_duration` (bounded to a sane max, e.g. 30 days, validated at shape-check step), `minimum_inventory` (via `minimum_stock_to_sell`, re-checked per transaction just like normal checkout).

## 10. Testing Requirements

- Unit test: proposal with discount above `allowed_campaign_discount_pct` → Guardian returns `BLOCK` or the correct partial-eligibility result.
- Integration test: simulate N transactions against an active campaign whose combined discount would exceed `budget` → campaign auto-pauses after the budget-exhausting transaction, subsequent transactions get full price (not blocked entirely — see `07_GUARDIAN_SPEC.md` §5).
- Integration test: campaign revenue dashboard number matches `SUM(Order.amount WHERE campaign_id=...)` exactly in a seeded scenario.
