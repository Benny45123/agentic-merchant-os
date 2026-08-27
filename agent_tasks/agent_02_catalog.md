
# AGENT_02_CATALOG

## Objective

Implement the Agent-Readable Catalog: models (owned jointly with AGENT_01's schema but the *service logic* is yours), CRUD API, trusted/untrusted field separation, and the read functions the Guardian and Commerce Agent depend on.

## Scope

- `app/catalog/service.py`: `get_product`, `search_products`, `get_authoritative_state`, `snapshot_catalog`
- `app/catalog/router.py`: `GET /catalog/products`, `GET /catalog/products/{sku}`, `POST /catalog/products`, `PATCH /catalog/products/{sku}` per `04_API_CONTRACTS.md` §1
- Write-time validation (reject malformed `price`/`inventory`, enforce `catalog_version` increment on price/inventory change)
- `CatalogSnapshot` creation helper (called by Commerce Agent on cart-add, but the creation function lives here)

## Files/Directories Owned

`backend/app/catalog/`

## Dependencies

`app/core` (AGENT_01) must be merged first. Uses `Product`, `CatalogSnapshot`, `Offer` models from `05_DATA_MODEL.md`.

## Interfaces/Contracts

```python
def get_product(sku: str) -> Product | None: ...
def search_products(query: str | None, category: str | None, merchant_id: str) -> list[Product]: ...
def get_authoritative_state(sku: str) -> AuthoritativeState:  # {price, inventory, exists}
    """Guardian-only consumer. Must always hit the DB fresh, never a cache."""
def snapshot_catalog(sku: str) -> CatalogSnapshot: ...
```

Router responses must match `04_API_CONTRACTS.md` §1 exactly, including the `suspicious_content_flag` field (populated by AGENT_09's scanner once it lands — until then, default `false`).

## Implementation Requirements

1. `description`, `marketing_copy`, review fields are stored and returned to callers but must never be consumed by this package's own logic for anything beyond passthrough display.
2. `PATCH` that changes `price` or `inventory` increments `catalog_version` atomically in the same transaction.
3. `get_authoritative_state` must not be cached/memoized in a way that could serve stale data across requests — Guardian correctness depends on this being a fresh read every call.
4. Seed catalog (from AGENT_01) must include the headphones/warranty/case bundle trio and the malicious-content fixture — verify these are queryable via your search function.

## Tests Required

- CRUD round-trip test
- `catalog_version` increments correctly on price change, does not increment on description-only change
- `get_authoritative_state` reflects a change made via a separate `PATCH` call within the same test (no caching bug)
- Malformed `PATCH` (non-numeric price) returns 422 and does not mutate the row

## Acceptance Criteria

- [ ] All four catalog endpoints work against seed data
- [ ] `get_authoritative_state(sku)` is used (imported) by `app/guardian` — confirm via the Guardian agent's integration, but your job is to make it correct and fast
- [ ] Write-time validation rejects malformed structured fields
- [ ] All tests above pass

## Must NOT Modify

`app/guardian`, `app/mandate`, `app/policy`, `app/commerce_agent`, `app/campaign`, `app/razorpay_adapter`, `app/receipts`, `app/security`, `04_API_CONTRACTS.md`/`05_DATA_MODEL.md` (flag `[CONTRACT-CHANGE]` if a field is genuinely missing).
