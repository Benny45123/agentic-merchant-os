
# AGENT_03_COMMERCE_AGENT

## Objective

Implement the buyer-facing Commerce Agent: conversational discovery, cart construction, upsell/cross-sell recommendation, and the deterministic `TransactionIntent` builder that hands off to the Guardian. This is Side A of Track 01 made real.

## Scope

- `app/commerce_agent/service.py`: chat orchestration loop, session/cart state management
- `app/commerce_agent/tools.py`: LLM-callable tools (`search_catalog`, `get_product`, `add_to_cart`, `remove_from_cart`, `get_cart`, `request_checkout`)
- `app/commerce_agent/intent_builder.py`: pure code that assembles a `TransactionIntent` from `CartItem` state — **not** an LLM call
- `app/commerce_agent/upsell.py`: rule-based candidate generation + policy-safe filtering (LLM only ranks/phrases the pre-filtered list)
- `app/commerce_agent/router.py`: `POST /agent/chat`, `POST /agent/checkout-intent` per `04_API_CONTRACTS.md` §2
- System prompt file (`app/commerce_agent/prompts.py` or similar) implementing the injection-hardening language from `06_AGENT_SPEC.md` §3

## Files/Directories Owned

`backend/app/commerce_agent/`

## Dependencies

`app/core` (AGENT_01), `app/catalog` (AGENT_02) must exist. `app/guardian` (AGENT_04) may still be in progress — build against a `FakeGuardianClient` matching the exact `GuardianDecision` shape in `04_API_CONTRACTS.md` §4 until the real one lands, then swap the import.

## Interfaces/Contracts

```python
async def chat(session_id: str, buyer_id: str, message: str) -> ChatResponse: ...
async def build_checkout_intent(session_id: str, buyer_id: str, merchant_id: str) -> GuardianDecision: ...
```

Tool signatures must match `06_AGENT_SPEC.md` §5 exactly, including the quantity-clamp error behavior (return an explainable error tool-result, never a silent clamp).

## Implementation Requirements

1. Implement the full injection-hardening system prompt from `06_AGENT_SPEC.md` §3, verbatim in spirit.
2. `TransactionIntent` is built exclusively from real `CartItem`/`CatalogSnapshot` rows — verify the LLM's free-text output is never parsed into the intent object.
3. Upsell candidates are filtered before the LLM ever sees them: must be in stock, must fit remaining `mandate.max_amount`, must not breach `policy.minimum_margin_pct` (call `app/policy` if available, else stub per §Dependencies).
4. `request_checkout()` calls `POST /guardian/evaluate` server-side and returns the decision to the LLM as a tool result for narration only — the LLM cannot alter it.
5. On `REQUIRE_CONFIRMATION`, expose a chat action that calls `/guardian/confirm/{decision_id}`.

## Tests Required

- Injection fixture test (per `06_AGENT_SPEC.md` §6): malicious `description` text does not change resulting intent quantity
- Upsell candidate list never includes a margin-violating SKU
- Full chat→cart→checkout-intent flow tested against `FakeGuardianClient` for APPROVE/BLOCK/REQUIRE_CONFIRMATION
- Tool-call quantity clamp returns an explainable error, not a silent success

## Acceptance Criteria

- [ ] `/agent/chat` discovers real catalog products via natural language
- [ ] Cart state persists correctly across turns in a session
- [ ] Upsell recommendation appears after a relevant cart-add and is never auto-added
- [ ] `/agent/checkout-intent` produces a valid `TransactionIntent` and forwards to Guardian
- [ ] Injection fixture test passes
- [ ] `scripts/check_import_graph.py` passes (no `razorpay_adapter` import anywhere in this package)

## Must NOT Modify

`app/guardian`, `app/catalog`, `app/mandate`, `app/policy`, `app/razorpay_adapter`, `app/campaign`, `app/receipts`, `app/security`, `04_API_CONTRACTS.md`/`05_DATA_MODEL.md`.
