
# AGENT_06_RECEIPTS

## Objective

Implement the Decision Receipt / audit trail system: generation from every Guardian decision, storage, query API, and deterministic replay.

## Scope

- `app/receipts/service.py`: `create_receipt`, `get_receipt`, `list_receipts`, `replay`
- `app/receipts/router.py`: `GET /receipts/{id}`, `GET /receipts`, `POST /receipts/{id}/replay` per `04_API_CONTRACTS.md` §7

## Files/Directories Owned

`backend/app/receipts/`

## Dependencies

`app/core` (AGENT_01). Called by `app/guardian` (AGENT_04) — coordinate the exact `create_receipt()` signature early since Guardian calls it on every decision path.

## Interfaces/Contracts

```python
def create_receipt(decision: GuardianDecision, intent: TransactionIntent | None,
                    mandate: Mandate | None, policy: MerchantPolicy,
                    razorpay_result: RazorpayOrder | None) -> Receipt: ...
def get_receipt(receipt_id: str) -> Receipt | None: ...
def list_receipts(buyer_id: str | None, merchant_id: str | None,
                   decision: str | None, from_ts, to_ts) -> list[Receipt]: ...
def replay(receipt_id: str) -> ReplayResult: ...  # {receipt_id, replay_decision, matches_original}
```

## Implementation Requirements

1. `create_receipt` freezes copies (not FK references) of mandate, policy, and catalog snapshot state — see `10_COMMERCE_TRUTH_AND_RECEIPTS.md` §3 for why this denormalization is intentional and correct.
2. No update/delete endpoint exists anywhere for `Receipt` — it is immutable by design.
3. `replay()` re-runs `check_mandate()`/`check_policy()`/the price-inventory comparison against the **frozen data stored in the receipt itself**, not live DB state, and compares to the stored decision.
4. Every Guardian decision (APPROVE, BLOCK, REQUIRE_CONFIRMATION) produces exactly one Receipt — coordinate with AGENT_04 to confirm this invariant holds in integration testing.
5. Frontend-ready shape: `list_receipts` supports the filter params in `04_API_CONTRACTS.md` §7 for the merchant dashboard.

## Tests Required

- Round-trip: create a receipt, fetch it, all fields present and correctly frozen
- Replay determinism: for a seeded set of receipts covering APPROVE/BLOCK/REQUIRE_CONFIRMATION, `replay()` returns `matches_original: true` for all
- Immutability: no code path anywhere allows mutating an existing Receipt row
- BLOCK decision produces a receipt with `razorpay_order_id: null` and a populated `failure_reason`

## Acceptance Criteria

- [ ] Every Guardian decision type produces exactly one Receipt (verified via integration test with AGENT_04's pipeline)
- [ ] Replay passes for 100% of a seeded receipt set
- [ ] `GET /receipts` filtering works correctly across all documented params
- [ ] No receipt is ever mutated after creation (spot-checked via test)

## Must NOT Modify

`app/guardian`, `app/catalog`, `app/mandate`, `app/policy`, `app/commerce_agent`, `app/campaign`, `app/razorpay_adapter`.
