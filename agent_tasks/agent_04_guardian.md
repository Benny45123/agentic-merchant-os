
# AGENT_04_GUARDIAN

## Objective

Implement the Commerce Guardian, Mandate Engine, and Merchant Policy Engine — the deterministic core that decides whether any money action is permitted. This is the highest-trust component in the system.

## Scope

- `app/mandate/models.py` (or shared with AGENT_01's models), `app/mandate/service.py`: `get_active_mandate`, `check_mandate` (pure function)
- `app/policy/service.py`: `get_policy`, `check_policy`, `check_campaign_policy` (pure functions)
- `app/guardian/pipeline.py`: the full buyer-flow pipeline (`07_GUARDIAN_SPEC.md` §2) and campaign-flow pipeline (§4), including per-transaction campaign budget enforcement (§5)
- `app/guardian/router.py`: `POST /guardian/evaluate`, `POST /guardian/evaluate_campaign`, `POST /guardian/confirm/{decision_id}` per `04_API_CONTRACTS.md` §4
- `app/mandate/router.py`: `GET /mandate/active`, `POST /mandate` per `04_API_CONTRACTS.md` §3
- `app/policy/router.py`: `GET/PUT /policy` per `04_API_CONTRACTS.md` §8

## Files/Directories Owned

`backend/app/guardian/`, `backend/app/mandate/`, `backend/app/policy/`

## Dependencies

`app/core` (AGENT_01). Calls `app/catalog.get_authoritative_state()` (AGENT_02 — stub if not ready, matching the exact return shape). Calls `app/razorpay_adapter.create_order()` (AGENT_05 — stub if not ready). Calls `app/receipts.create_receipt()` (AGENT_06 — stub if not ready, but every decision path must call it once the real one lands).

## Interfaces/Contracts

```python
def check_mandate(intent: TransactionIntent, mandate: Mandate) -> MandateCheckResult: ...
def check_policy(intent: TransactionIntent, resolved_items: list[ResolvedItem], policy: MerchantPolicy) -> PolicyCheckResult: ...
def check_campaign_policy(proposal: CampaignProposal, policy: MerchantPolicy, campaign_policy: CampaignPolicy) -> PolicyCheckResult: ...
async def evaluate(intent: TransactionIntent) -> GuardianDecision: ...
async def evaluate_campaign(proposal: CampaignProposal) -> GuardianDecision: ...
```

## Implementation Requirements

1. Implement every step of `07_GUARDIAN_SPEC.md` §2 in exact order, short-circuiting correctly, recording `skipped` for unreached checks.
2. Zero LLM calls anywhere in this package. Zero reads of `Product.description` or any UNTRUSTED field.
3. `get_authoritative_state()` is always called fresh — never cache the result across the pipeline run beyond the single evaluation.
4. On `APPROVE`, call the Razorpay adapter and attach the resulting `order_id` to both the response and the Receipt.
5. Every decision (all three types) calls `receipts.create_receipt()` exactly once, with no swallowed exceptions defaulting to APPROVE.
6. Implement campaign per-transaction budget enforcement per `07_GUARDIAN_SPEC.md` §5 — auto-`PAUSE` on exhaustion, never block the underlying purchase.
7. `MerchantPolicy` updates are versioned (new row, not mutation) per `08_MANDATE_AND_POLICY_SPEC.md` §3.

## Tests Required

Implement all 22 test matrix cases from `14_TEST_PLAN.md` §4, one test function each, no mocking of the pure `check_mandate`/`check_policy` functions themselves.

## Acceptance Criteria

- [ ] All 22 Guardian test matrix cases pass
- [ ] `check_mandate`/`check_policy` are provably pure (no I/O) via a test that calls them with plain Python objects, no DB session
- [ ] Receipt is written for every decision type, verified by a DB count assertion in tests
- [ ] `scripts/check_import_graph.py` passes with this package fully implemented
- [ ] Campaign budget auto-pause test passes without blocking the triggering transaction

## Must NOT Modify

`app/catalog`, `app/commerce_agent`, `app/campaign`, `app/razorpay_adapter`, `app/receipts`, `app/security`, `app/ai_provider`, `04_API_CONTRACTS.md`/`05_DATA_MODEL.md`.
