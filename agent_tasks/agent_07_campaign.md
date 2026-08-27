
# AGENT_07_CAMPAIGN

## Objective

Implement the Campaign Orchestrator: merchant objective → LLM proposal → Guardian validation → bounded, static campaign offers applied to the existing catalog/checkout flow.

## Scope

- `app/campaign/service.py`: `propose_campaign`, `activate_campaign`, `get_campaign_status`
- `app/campaign/router.py`: `POST /campaign/propose`, `POST /campaign/{id}/activate`, `GET /campaign/{id}/status` per `04_API_CONTRACTS.md` §6
- `app/campaign/proposal_prompt.py`: LLM prompt construction pulling real catalog + historical order data

## Files/Directories Owned

`backend/app/campaign/`

## Dependencies

`app/core` (AGENT_01), `app/catalog` (AGENT_02, for eligible-product lookup and writing `CampaignOffer` rows), `app/guardian` (AGENT_04, for `evaluate_campaign` — stub with `FakeGuardianClient` if not ready), `app/policy` (AGENT_04, read-only, for prompting the LLM with real current limits), `app/ai_provider` (for the LLM call).

## Interfaces/Contracts

```python
async def propose_campaign(merchant_id: str, objective: str) -> CampaignProposal: ...
async def activate_campaign(proposal_id: str) -> Campaign: ...
async def get_campaign_status(campaign_id: str) -> CampaignStatus: ...
```

Response shapes must match `04_API_CONTRACTS.md` §6 exactly.

## Implementation Requirements

1. `propose_campaign` gathers real inputs only: `catalog.search_products()` results and aggregated historical `Order`/`Receipt` data for relevant SKUs — never let the LLM invent a product, price, or historical figure.
2. LLM output is schema-validated JSON; malformed output is retried once, then surfaced as an error to the merchant, never guessed at.
3. `activate_campaign` is only permitted if the stored `guardian_decision.decision == APPROVE`, or the merchant has explicitly confirmed a `REQUIRE_CONFIRMATION` result via `/guardian/confirm/{decision_id}`.
4. Activation writes `Offer(type=campaign_discount, campaign_id=...)` rows only — no transaction execution happens here. The existing buyer checkout path (`app/commerce_agent` → `app/guardian`) picks these up automatically because they're just `Offer` data.
5. Implement the lifecycle state machine exactly as in `11_CAMPAIGN_ORCHESTRATOR.md` §7 (`DRAFT → PENDING_APPROVAL → ACTIVE → PAUSED/COMPLETED`).
6. `get_campaign_status` computes `budget_spent`, `orders_attributed`, `revenue_attributed` via live SQL aggregation over `Order` — never a maintained counter that could drift from reality.
7. You must never import `app/razorpay_adapter`.

## Tests Required

- Proposal with over-limit discount → Guardian returns BLOCK or correct partial eligibility (integration test against real or faked Guardian)
- Simulated multi-transaction sequence exhausting campaign budget → auto-PAUSE, `CampaignEvent` logged, triggering transaction itself still succeeds at full price
- `get_campaign_status` numbers match a hand-computed `SUM(Order.amount)` in a seeded scenario

## Acceptance Criteria

- [ ] `scenario_campaign_lifecycle.py` (see `14_TEST_PLAN.md` §7) passes
- [ ] No campaign offer is ever applied to the catalog without a prior Guardian APPROVE/confirmed decision
- [ ] `scripts/check_import_graph.py` passes (no `razorpay_adapter` import in this package)
- [ ] Campaign revenue dashboard numbers are traceable to real `Order` rows

## Must NOT Modify

`app/guardian`, `app/catalog` core CRUD (writing `Offer` rows via the documented catalog interface is fine; do not add new catalog endpoints yourself), `app/mandate`, `app/policy`, `app/commerce_agent`, `app/razorpay_adapter`, `app/receipts`.
