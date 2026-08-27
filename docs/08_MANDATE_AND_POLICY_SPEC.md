
# 08 — Mandate & Policy Spec

## Part A — Mandate Engine

### 1. Purpose

A Mandate is the buyer's **explicit, structured, pre-declared spending authorization**. It exists so that an AI buyer agent (or a human via the demo UI) can shop within a boundary the buyer set in advance — the Commerce Agent can never expand this boundary, and the Guardian is the only enforcer of it.

### 2. Fields (see `05_DATA_MODEL.md` for types)

`max_amount`, `max_quantity_per_item`, `allowed_categories`, `allowed_merchants`, `allowed_products`, `currency`, `expires_at`, `confirmation_required_above`, `signature` (reserved, unused).

### 3. Lifecycle

- Created via `POST /mandate` (demo: the buyer sets this once at the start of a session, simulating what a real AI-buyer platform would present as a consent screen).
- Exactly one `active=true` mandate per buyer at a time; creating a new one deactivates the previous.
- Expired mandates (`expires_at < now`) are treated as absent by the Guardian — `BLOCK: no_active_mandate`.

### 4. Design for Future Cryptographic Mandates (documented, not built)

The `signature` field is reserved for a future scheme where the buyer's own device/wallet signs the mandate JSON (e.g., Ed25519 over a canonical JSON encoding), and the Guardian verifies the signature against a known buyer public key before trusting `active=true`. **This is explicitly out of scope for the 10-day MVP** (see `01_PRODUCT_SPEC.md` §6 STRETCH) but the schema must not require a migration to add it — hence the nullable field now.

### 5. Validation Function Contract

```python
def check_mandate(intent: TransactionIntent, mandate: Mandate) -> MandateCheckResult:
    """Pure function. No I/O except the mandate/intent already passed in.
    Returns ordered list of individual check results, never raises for
    a failed business check (only for malformed input)."""
```

Must be unit-testable with zero mocks — no DB, no network, no LLM.

---

## Part B — Merchant Policy Engine

### 1. Purpose

The Policy Engine represents everything the merchant has decided about how their store may be discounted, sold, and campaigned — independent of any specific buyer. It is the merchant-side mirror of the Mandate.

### 2. Fields

`maximum_discount_pct`, `minimum_margin_pct`, `maximum_order_value`, `allowed_products_for_discount`, `minimum_stock_to_sell`, `version`. Plus `CampaignPolicy`: `allowed_campaign_discount_pct`, `campaign_budget_default`, `daily_campaign_budget_cap`.

### 3. Versioning

Every `PUT /policy` creates a **new row** with `version = old.version + 1` rather than mutating in place; the Guardian always reads the highest `version`. Old versions are retained (never deleted) because `Receipt.policy_snapshot` may reference them for historical replay — a policy change must never retroactively alter the interpretation of a past decision.

### 4. Validation Function Contracts

```python
def check_policy(intent: TransactionIntent, resolved_items: list[ResolvedItem], policy: MerchantPolicy) -> PolicyCheckResult: ...
def check_campaign_policy(proposal: CampaignProposal, policy: MerchantPolicy, campaign_policy: CampaignPolicy) -> PolicyCheckResult: ...
```

Both pure functions, unit-testable without I/O.

### 5. Margin Calculation

`Product.cost` (merchant-admin only, never exposed via public catalog endpoints) is required to compute margin:

```
price_after_discount = price * (1 - discount_pct/100)
margin_pct = (price_after_discount - cost) / price_after_discount * 100
```

If `cost` is null for a product (merchant didn't set it), `minimum_margin_pct` check is **skipped with a warning check entry**, not silently passed — this must be visible in the receipt so it's never mistaken for a verified margin.

### 6. Interaction With Guardian

Neither Mandate nor Policy checks call each other — the Guardian orchestrates both and combines results per `07_GUARDIAN_SPEC.md` §2/§4. This keeps each engine independently testable and independently ownable by a Gemini CLI agent.

### 7. Default Seed Policy (for demo)

```json
{
  "maximum_discount_pct": 20,
  "minimum_margin_pct": 15,
  "maximum_order_value": 2000000,
  "allowed_products_for_discount": null,
  "minimum_stock_to_sell": 2,
  "allowed_campaign_discount_pct": 15,
  "campaign_budget_default": 5000000,
  "daily_campaign_budget_cap": 5000000
}
```

This seed must be loaded by `AGENT_01_FOUNDATION` and referenced identically by every other agent's fixtures/tests.
