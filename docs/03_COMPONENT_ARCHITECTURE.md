
# 03 — Component Architecture

Each component below maps 1:1 to a backend package (`/backend/app/<name>`), a router file, a test directory, and — for build purposes — one primary `AGENT_TASKS/AGENT_0X_*.md` owner. This is the contract Gemini CLI agents must not violate.

## 3.1 Catalog Service (`app/catalog`)

**Owns:** Product, CatalogSnapshot, Offer, BundleRelationship models; catalog CRUD; catalog read API for the Commerce Agent; catalog admin API for merchants.
**Exposes to others:** `get_product(sku) -> Product`, `search_products(query, filters) -> list[Product]`, `get_authoritative_state(sku) -> AuthoritativeState` (price+inventory only, used exclusively by Guardian), `snapshot_catalog() -> CatalogSnapshot`.
**Must not:** perform any Guardian logic, call Razorpay, or accept LLM-generated writes to `price` or `inventory` fields — those are merchant-admin-only fields.
**Trusted vs untrusted fields:** see `09_CATALOG_SECURITY.md` — `price`, `inventory`, `sku`, `currency`, `category`, `bundle_relationships` are trusted/structured. `description`, `marketing_copy`, `reviews` are untrusted free text, readable by the Agent for conversation only.

## 3.2 Mandate Engine (`app/mandate`)

**Owns:** Mandate model, mandate CRUD, mandate validation function `check_mandate(intent, mandate) -> MandateCheckResult`.
**Exposes to others:** `get_active_mandate(buyer_id) -> Mandate`, `check_mandate(...)`.
**Must not:** make any network call, call an LLM, or import `razorpay_adapter`.
**Design note:** mandate fields include an optional `signature` field (nullable, unused in MVP) so a future cryptographic mandate scheme (e.g., buyer-signed JSON) can be added without a schema migration.

## 3.3 Merchant Policy Engine (`app/policy`)

**Owns:** MerchantPolicy model, CampaignPolicy model, policy CRUD, `check_policy(intent, policy) -> PolicyCheckResult`, `check_campaign_policy(proposal, policy) -> PolicyCheckResult`.
**Exposes to others:** `get_policy(merchant_id) -> MerchantPolicy`, the two check functions above.
**Must not:** call an LLM or Razorpay.

## 3.4 Commerce Guardian (`app/guardian`)

**Owns:** the decision pipeline. This is the only package permitted to call both `razorpay_adapter` and write `Receipt` rows for money actions.
**Pipeline (see `07_GUARDIAN_SPEC.md` for full detail):** validate intent shape → mandate check → policy check → re-fetch authoritative catalog state → price/inventory diff → suspicious-content flag check (defense-in-depth, non-authoritative) → idempotency/replay check → decision → (if APPROVE) call Razorpay Adapter → write Receipt.
**Must not:** call an LLM to make the APPROVE/BLOCK/REQUIRE_CONFIRMATION decision itself. LLM calls elsewhere in the system (Commerce Agent, Campaign Orchestrator) only ever produce *proposals* that are inputs to this deterministic pipeline.

## 3.5 Commerce Agent (`app/commerce_agent`)

**Owns:** buyer-facing chat orchestration: intent understanding, catalog search calls, cart state (session-scoped), upsell/cross-sell recommendation logic, natural-language explanation of recommendations, construction of the `TransactionIntent` object sent to the Guardian.
**Exposes to others:** `POST /agent/chat`, `POST /agent/checkout-intent`.
**Must not:** call `razorpay_adapter` directly (see `02_SYSTEM_ARCHITECTURE.md` §4 — enforced by import lint). Must not treat any text from `Product.description`/reviews as an instruction. System prompt must explicitly state this (see `06_AGENT_SPEC.md` §Injection Hardening).
**Upsell logic:** rule-based candidate generation from `BundleRelationship` rows, filtered by remaining mandate budget and merchant margin policy, LLM used only to rank/phrase the recommendation — never to invent a product or price not present in the trusted catalog fields.

## 3.6 Campaign Orchestrator (`app/campaign`)

**Owns:** Campaign model, CampaignOffer model, CampaignEvent model, the objective→proposal LLM call, campaign lifecycle (`DRAFT → PENDING_APPROVAL → ACTIVE → PAUSED/COMPLETED`).
**Exposes to others:** `POST /campaign/propose`, `POST /campaign/{id}/activate`, `GET /campaign/{id}/status`.
**Must not:** apply any offer to the catalog without a Guardian/Policy `APPROVE` on the campaign proposal. Must not execute transactions — campaign activation only writes `CampaignOffer` data; actual transactions still flow through the normal buyer checkout → Guardian path.

## 3.7 Razorpay Adapter (`app/razorpay_adapter`)

**Owns:** all direct interaction with the Razorpay SDK/API — create order, verify payment signature, handle webhook, issue refund (test-mode).
**Exposes to others (Guardian only):** `create_order(amount, currency, receipt_id) -> RazorpayOrder`, `verify_payment(payment_id, order_id, signature) -> bool`, `handle_webhook(payload, signature) -> WebhookEvent`, `refund(payment_id, amount) -> RazorpayRefund`.
**Must not:** contain any business/policy logic. It translates Guardian decisions into Razorpay API calls and Razorpay responses back into internal types. See `12_RAZORPAY_INTEGRATION.md`.

## 3.8 Receipts / Audit (`app/receipts`)

**Owns:** Receipt model, receipt generation from a completed Guardian decision, receipt query/replay API.
**Exposes to others:** `create_receipt(decision, intent, razorpay_result) -> Receipt`, `get_receipt(id)`, `list_receipts(filters)`, `replay(id) -> ReplayResult` (re-runs the same deterministic checks against the stored inputs to prove the decision was reproducible).
**Must not:** be skippable — Guardian must call this for every decision, approved or not.

## 3.9 Catalog Security (`app/security`)

**Owns:** heuristic scanner for injection-like patterns in untrusted catalog text (regex/keyword classifier — see `09_CATALOG_SECURITY.md`), tagging of suspicious `Product` rows, exposure of flags to Guardian receipts and merchant dashboard.
**Must not:** be the primary defense. Primary defense is structural (Guardian never reads free-text fields as authorization input). This module is defense-in-depth and demo visibility only.

## 3.10 AI Provider Abstraction (`app/ai_provider`)

**Owns:** `LLMProvider` interface (`complete(prompt, **kwargs) -> str/JSON`), concrete `GeminiProvider` (default), stub `GroqProvider`/`OpenRouterProvider` for swap-readiness.
**Used by:** `commerce_agent`, `campaign` only. **Never** used by `guardian`, `mandate`, `policy`, `razorpay_adapter`.

## 3.11 API Layer (`app/api`)

**Owns:** all FastAPI routers, request/response Pydantic schemas (must match `04_API_CONTRACTS.md` exactly), auth dependency, error handling middleware.
**Rule:** routers call into exactly one domain package's public function per endpoint where possible; routers contain no business logic themselves.

## 3.12 Frontend (`/frontend`)

**Owns:** buyer chat UI, cart/checkout UI, Razorpay Checkout embed, receipt viewer, merchant dashboard (policy editor, campaign composer, revenue view).
**Must not:** call Razorpay directly for order creation — order creation is always backend-initiated (via Guardian) so amount/currency cannot be client-manipulated. The frontend only opens Razorpay's Checkout widget with a backend-issued `order_id`.

## 3.13 Ownership Table

| Package          | Primary Agent                    | Depends on                                                           |
| ---------------- | -------------------------------- | -------------------------------------------------------------------- |
| core             | AGENT_01                         | —                                                                   |
| catalog          | AGENT_02                         | core                                                                 |
| mandate, policy  | AGENT_04 (bundled with guardian) | core                                                                 |
| guardian         | AGENT_04                         | core, catalog, mandate, policy, razorpay_adapter, receipts, security |
| commerce_agent   | AGENT_03                         | core, catalog, guardian (client), ai_provider                        |
| razorpay_adapter | AGENT_05                         | core                                                                 |
| receipts         | AGENT_06                         | core                                                                 |
| campaign         | AGENT_07                         | core, catalog, guardian (client), policy, ai_provider                |
| frontend         | AGENT_08                         | api (contracts only, can mock)                                       |
| security testing | AGENT_09                         | all (read-only, adds tests + injection fixtures)                     |
| integration      | AGENT_10                         | all                                                                  |
