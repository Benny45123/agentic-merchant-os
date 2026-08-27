
# 04 — API Contracts

This is the frozen contract between frontend, Commerce Agent, Campaign Orchestrator, Guardian, and Razorpay Adapter. **Any change to this file after Day 2 requires updating the "Contract Changelog" at the bottom and notifying all agents** (see `17_MULTI_AGENT_WORKFLOW.md`).

All requests/responses are JSON. All money amounts are integers in the smallest currency unit (paise for INR), matching Razorpay convention. All timestamps are ISO-8601 UTC strings. All IDs are UUID v4 strings unless noted.

---

## Auth

`Authorization: Bearer <token>` on all endpoints except `/health` and `/webhooks/razorpay`.
Token payload: `{ "sub": "<buyer_id|merchant_id>", "role": "buyer"|"merchant", "exp": ... }`.

---

## 1. Catalog

### `GET /catalog/products`

Query params: `q` (string, optional), `category` (string, optional), `merchant_id` (string, required)
Response 200:

```json
{
  "products": [
    {
      "sku": "HP-001",
      "name": "AeroSound Wireless Headphones",
      "category": "audio",
      "price": 449900,
      "currency": "INR",
      "inventory": 42,
      "description": "string (UNTRUSTED - display only)",
      "variants": [{"variant_id": "HP-001-BLK", "label": "Black", "price_delta": 0, "inventory": 20}],
      "shipping_info": {"eta_days": 3, "free_above": 199900},
      "return_policy": {"window_days": 7, "conditions": "string"},
      "offers": [{"offer_id": "OFF-1", "type": "campaign_discount", "label": "Weekend Sale", "discount_pct": 10, "expires_at": "..."}],
      "bundle_relationships": [{"related_sku": "WRNTY-1Y", "relation": "warranty_addon"}, {"related_sku": "CASE-HP", "relation": "accessory"}],
      "catalog_version": 17,
      "suspicious_content_flag": false
    }
  ]
}
```

### `GET /catalog/products/{sku}`

Response 200: single product object as above.

### `POST /catalog/products` (merchant-admin only)

Body: product fields minus `catalog_version`. Response 201: created product.

### `PATCH /catalog/products/{sku}` (merchant-admin only)

Body: partial product fields. **`price` and `inventory` changes always increment `catalog_version`.** Response 200: updated product.

---

## 2. Commerce Agent (Buyer-facing)

### `POST /agent/chat`

Body:

```json
{ "session_id": "uuid", "buyer_id": "uuid", "message": "string" }
```

Response 200:

```json
{
  "session_id": "uuid",
  "reply": "string (natural language)",
  "cart": {
    "items": [{"sku": "HP-001", "variant_id": "HP-001-BLK", "qty": 1, "observed_price": 449900, "catalog_version": 17}],
    "subtotal": 449900
  },
  "recommendations": [
    {"sku": "WRNTY-1Y", "reason": "string explanation", "price": 49900}
  ]
}
```

### `POST /agent/checkout-intent`

Body:

```json
{ "session_id": "uuid", "buyer_id": "uuid", "merchant_id": "uuid" }
```

Builds a `TransactionIntent` from the current cart and forwards it to the Guardian (server-side call, not client-callable directly). Response 200: the `GuardianDecision` object (see §4) plus, if `APPROVE`, a `razorpay_order` block for the frontend to open Checkout with:

```json
{
  "decision": { "...GuardianDecision fields..." },
  "razorpay_order": {"order_id": "order_xxx", "amount": 499800, "currency": "INR", "key_id": "rzp_test_xxx"}
}
```

---

## 3. Mandate

### `GET /mandate/active?buyer_id=uuid`

Response 200:

```json
{
  "mandate_id": "uuid",
  "buyer_id": "uuid",
  "max_amount": 1000000,
  "max_quantity_per_item": 5,
  "allowed_categories": ["audio", "accessories"],
  "allowed_merchants": ["merchant_uuid"],
  "allowed_products": null,
  "currency": "INR",
  "expires_at": "2026-09-01T00:00:00Z",
  "confirmation_required_above": 500000,
  "signature": null
}
```

### `POST /mandate` (buyer creates/updates a demo mandate)

Body: same shape minus `mandate_id`. Response 201.

---

## 4. Guardian (internal — called by commerce_agent and campaign packages only; not exposed to frontend directly except via `/agent/checkout-intent` and `/campaign/*`)

### `POST /guardian/evaluate`

Body (`TransactionIntent`):

```json
{
  "intent_id": "uuid",
  "buyer_id": "uuid",
  "merchant_id": "uuid",
  "items": [{"sku": "HP-001", "variant_id": "HP-001-BLK", "qty": 1, "observed_price": 449900, "catalog_version": 17}],
  "requested_discount_pct": 0,
  "created_at": "iso-timestamp",
  "expires_at": "iso-timestamp (created_at + 2 min)"
}
```

Response 200 (`GuardianDecision`):

```json
{
  "decision_id": "uuid",
  "intent_id": "uuid",
  "decision": "APPROVE | BLOCK | REQUIRE_CONFIRMATION",
  "checks": [
    {"name": "mandate.max_amount", "passed": true, "detail": "string"},
    {"name": "mandate.allowed_categories", "passed": true, "detail": "string"},
    {"name": "policy.min_margin", "passed": true, "detail": "string"},
    {"name": "catalog.price_match", "passed": false, "detail": "observed 449900, authoritative 469900"},
    {"name": "catalog.inventory_available", "passed": true, "detail": "string"},
    {"name": "security.catalog_content_flagged", "passed": true, "detail": "informational only, non-authoritative"},
    {"name": "replay.not_duplicate", "passed": true, "detail": "string"}
  ],
  "primary_reason": "string, human-readable",
  "final_verified_total": 469900,
  "receipt_id": "uuid"
}
```

### `POST /guardian/evaluate_campaign`

Body (`CampaignProposal`) — see §6. Response: same `GuardianDecision` shape, `checks` populated with policy-specific check names (`policy.max_discount`, `policy.min_margin`, `policy.campaign_budget`, `policy.allowed_products`, `policy.min_stock`).

### `POST /guardian/confirm/{decision_id}`

Used when decision was `REQUIRE_CONFIRMATION` and the buyer/merchant explicitly confirms. Re-runs the full pipeline (never trusts the old decision blindly) and proceeds to Razorpay if it still passes.

---

## 5. Razorpay (internal, wrapped by Guardian — not called directly by frontend for order creation)

### `POST /webhooks/razorpay`

Public endpoint, Razorpay-signed. Verifies `X-Razorpay-Signature` header against webhook secret before processing. See `12_RAZORPAY_INTEGRATION.md`.

### Frontend-facing payment confirmation:

### `POST /payments/verify`

Body: `{ "razorpay_order_id": "...", "razorpay_payment_id": "...", "razorpay_signature": "..." }`
Response 200: `{ "verified": true, "receipt_id": "uuid" }` — internally calls Razorpay Adapter's `verify_payment`, then Guardian finalizes the Receipt.

---

## 6. Campaign Orchestrator (Merchant-facing)

### `POST /campaign/propose`

Body: `{ "merchant_id": "uuid", "objective": "Increase sales of headphones this weekend" }`
Response 200 (`CampaignProposal`):

```json
{
  "proposal_id": "uuid",
  "merchant_id": "uuid",
  "objective": "string",
  "eligible_skus": ["HP-001", "HP-002"],
  "discount_pct": 10,
  "bundle_offer": {"trigger_sku": "HP-001", "addon_sku": "CASE-HP", "addon_discount_pct": 50},
  "budget": 5000000,
  "starts_at": "iso-timestamp",
  "ends_at": "iso-timestamp",
  "rationale": "string, LLM explanation",
  "guardian_decision": { "...GuardianDecision..." }
}
```

### `POST /campaign/{proposal_id}/activate`

Only callable if `guardian_decision.decision == "APPROVE"` or merchant has explicitly confirmed a `REQUIRE_CONFIRMATION`. Writes `CampaignOffer` rows. Response 200: `{ "campaign_id": "uuid", "status": "ACTIVE" }`.

### `GET /campaign/{campaign_id}/status`

Response 200:

```json
{
  "campaign_id": "uuid",
  "status": "ACTIVE | PAUSED | COMPLETED",
  "budget": 5000000,
  "budget_spent": 1240000,
  "orders_attributed": 8,
  "revenue_attributed": 3890000,
  "pause_reason": null
}
```

---

## 7. Receipts

### `GET /receipts/{receipt_id}`

Response 200: full Receipt object (see `05_DATA_MODEL.md` §Receipt).

### `GET /receipts?buyer_id=&merchant_id=&decision=&from=&to=`

Response 200: `{ "receipts": [ ... ] }`

### `POST /receipts/{receipt_id}/replay`

Response 200: `{ "receipt_id": "uuid", "replay_decision": "APPROVE|BLOCK|REQUIRE_CONFIRMATION", "matches_original": true }`

---

## 8. Merchant Policy (Merchant-admin)

### `GET /policy?merchant_id=uuid`

### `PUT /policy` — full replace, versioned (see `05_DATA_MODEL.md`)

---

## 9. Revenue / Dashboard (read-only, derived from Receipts + Orders — never hardcoded)

### `GET /dashboard/revenue?merchant_id=uuid&from=&to=`

Response 200:

```json
{
  "total_revenue": 12450000,
  "order_count": 31,
  "upsell_attach_rate": 0.42,
  "upsell_revenue": 1980000,
  "campaign_revenue": 3890000,
  "blocked_attempt_count": 4
}
```

All fields computed via SQL aggregation over `Order`/`Receipt` tables at request time.

---

## 10. Universal Agent Protocol (UAP) & Machine Purchase Gateway

### `GET /.well-known/agent.json`

Public machine-readable manifest declaring store capabilities and MCP tools for external AI agents.
Response 200:

```json
{
  "protocol": "UAP-1.0",
  "name": "AeroSound Official Store",
  "merchant_id": "m_001",
  "catalog_version": 17,
  "supported_payment_rails": ["razorpay_test_v1"],
  "tools": [
    {
      "name": "search_catalog",
      "description": "Search products with real-time stock and prices",
      "endpoint": "/catalog/products"
    },
    {
      "name": "submit_machine_purchase",
      "description": "Submit a signed mandate and transaction intent for Guardian evaluation",
      "endpoint": "/agent/v1/machine-purchase"
    }
  ]
}
```

### `POST /agent/v1/machine-purchase`

Headless A2A purchase endpoint for external AI buyers (ChatGPT, Claude, AutoGPT).
Request:

```json
{
  "buyer_agent_id": "agent_procure_007",
  "buyer_mandate": {
    "buyer_id": "b_001",
    "max_amount": 1000000,
    "max_quantity_per_item": 5,
    "currency": "INR"
  },
  "purchase_items": [
    {
      "sku": "HP-001",
      "qty": 1,
      "observed_price": 449900,
      "catalog_version": 17
    }
  ],
  "agent_callback_url": "https://buyer-agent.internal/webhook"
}
```

Response 200:

```json
{
  "status": "APPROVED",
  "guardian_decision": "APPROVE",
  "receipt_id": "uuid-string",
  "final_verified_total": 449900,
  "razorpay_order_id": "order_test_xxxx",
  "payment_link": "https://api.razorpay.com/v1/checkout/hosted?order_id=order_test_xxxx",
  "replay_hash": "sha256_hash_of_decision_receipt"
}
```

---

## 11. Dynamic Margin Bundling

### `POST /catalog/bundles/margin-check`

Validates multi-item bundle discount against merchant minimum gross margin.
Request: `{ "parent_sku": "HP-001", "addon_sku": "CASE-HP", "discount_pct": 30 }`
Response 200: `{ "approved": true, "bundle_price": 519800, "projected_margin_pct": 34.6, "min_margin_pct": 15.0 }`

---

## 12. Campaign A/B Strategy Simulator

### `POST /campaign/simulate-ab`

Generates dual competing marketing strategies with Guardian pre-validation.
Request: `{ "merchant_id": "m_001", "objective": "string" }`
Response 200:

```json
{
  "objective": "string",
  "strategy_a": {
    "name": "Volume Catalyst (10% Off)",
    "discount_pct": 10,
    "eligible_skus": ["HP-001"],
    "projected_revenue_lift_pct": 28,
    "projected_gross_margin_pct": 21.5,
    "guardian_pre_check": "APPROVE"
  },
  "strategy_b": {
    "name": "Margin Protector (Bundle Deal)",
    "discount_pct": 50,
    "bundle_addon_sku": "CASE-HP",
    "eligible_skus": ["HP-001"],
    "projected_revenue_lift_pct": 36,
    "projected_gross_margin_pct": 29.8,
    "guardian_pre_check": "APPROVE"
  },
  "ai_recommendation": "Strategy B preserves 8.3% higher profit margin."
}
```

---

## Contract Changelog

| Date  | Change | Reason |
| ----- | ------ | ------ |
| Day 0 | Initial version | Baseline contracts |
| Day 2 | Added UAP Machine Gateway, Bundle Margin, Campaign A/B Simulator | Track 01 A2A Commerce & Revenue Extensions |
