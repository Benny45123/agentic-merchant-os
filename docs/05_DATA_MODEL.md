
# 05 — Data Model

SQLAlchemy 2.0 models, SQLite for MVP. All primary keys are UUID strings (`str(uuid4())`) except autoincrement is avoided so IDs are stable across a future Postgres migration. All monetary fields are integers (smallest currency unit). All tables have `created_at` (server default now). Mutable tables also have `updated_at`.

## Merchant

| Field           | Type     | Notes                |
| --------------- | -------- | -------------------- |
| merchant_id     | str (PK) |                      |
| name            | str      |                      |
| razorpay_key_id | str      | test-mode public key |
| created_at      | datetime |                      |

## Buyer

| Field      | Type     | Notes |
| ---------- | -------- | ----- |
| buyer_id   | str (PK) |       |
| name       | str      |       |
| created_at | datetime |       |

## Product

| Field                   | Type     | Trust                            | Notes                                                  |
| ----------------------- | -------- | -------------------------------- | ------------------------------------------------------ |
| sku                     | str (PK) | trusted                          |                                                        |
| merchant_id             | str (FK) | trusted                          |                                                        |
| name                    | str      | trusted                          | display name, not free-form marketing                  |
| category                | str      | trusted                          |                                                        |
| price                   | int      | **trusted, authoritative** | base price before offers                               |
| currency                | str      | trusted                          | ISO 4217, "INR" for MVP                                |
| inventory               | int      | **trusted, authoritative** |                                                        |
| description             | text     | **UNTRUSTED**              | free text, never read by Guardian                      |
| variants                | JSON     | trusted                          | list of`{variant_id, label, price_delta, inventory}` |
| shipping_info           | JSON     | trusted                          |                                                        |
| return_policy           | JSON     | trusted                          |                                                        |
| bundle_relationships    | JSON     | trusted                          | list of`{related_sku, relation}`                     |
| catalog_version         | int      | trusted                          | incremented on any price/inventory change              |
| suspicious_content_flag | bool     | derived                          | set by`security` scanner on `description`          |
| updated_at              | datetime |                                  |                                                        |

## CatalogSnapshot

| Field           | Type     | Notes                                              |
| --------------- | -------- | -------------------------------------------------- |
| snapshot_id     | str (PK) |                                                    |
| sku             | str (FK) |                                                    |
| catalog_version | int      | matches`Product.catalog_version` at capture time |
| price           | int      | frozen                                             |
| inventory       | int      | frozen                                             |
| captured_at     | datetime |                                                    |

Captured whenever the Commerce Agent adds an item to a cart, so the Guardian can later prove "this is what the agent saw."

## Offer

| Field               | Type               | Notes                                       |
| ------------------- | ------------------ | ------------------------------------------- |
| offer_id            | str (PK)           |                                             |
| sku                 | str (FK)           |                                             |
| type                | enum               | `merchant_defined`, `campaign_discount` |
| label               | str                |                                             |
| discount_pct        | int                | 0-100                                       |
| campaign_id         | str (FK, nullable) | set when`type=campaign_discount`          |
| starts_at / ends_at | datetime           |                                             |

## Mandate

| Field                       | Type                           | Notes                                                     |
| --------------------------- | ------------------------------ | --------------------------------------------------------- |
| mandate_id                  | str (PK)                       |                                                           |
| buyer_id                    | str (FK)                       |                                                           |
| max_amount                  | int                            | total cart ceiling, smallest unit                         |
| max_quantity_per_item       | int                            |                                                           |
| allowed_categories          | JSON (list[str], nullable)     | null = all allowed                                        |
| allowed_merchants           | JSON (list[str], nullable)     | null = all allowed                                        |
| allowed_products            | JSON (list[str] sku, nullable) | null = all allowed                                        |
| currency                    | str                            |                                                           |
| expires_at                  | datetime                       |                                                           |
| confirmation_required_above | int (nullable)                 | amount threshold                                          |
| signature                   | str (nullable)                 | reserved for future cryptographic mandates, unused in MVP |
| active                      | bool                           |                                                           |

## MerchantPolicy

| Field                         | Type                       | Notes                                               |
| ----------------------------- | -------------------------- | --------------------------------------------------- |
| policy_id                     | str (PK)                   |                                                     |
| merchant_id                   | str (FK)                   |                                                     |
| maximum_discount_pct          | int                        | applies to any single-order discount                |
| minimum_margin_pct            | int                        | computed against`Product.cost` (see below)        |
| maximum_order_value           | int                        |                                                     |
| allowed_products_for_discount | JSON (list[str], nullable) |                                                     |
| minimum_stock_to_sell         | int                        | block sale if inventory would go below this         |
| version                       | int                        | incremented on every update, referenced by Receipts |

**Note:** `Product` gains a `cost` field (trusted, merchant-admin only, not exposed via public catalog API) so `minimum_margin_pct` is computable: `margin_pct = (price_after_discount - cost) / price_after_discount * 100`.

## CampaignPolicy (subset of policy, campaign-specific — could be embedded in MerchantPolicy but kept separate for clarity)

| Field                         | Type     | Notes |
| ----------------------------- | -------- | ----- |
| merchant_id                   | str (FK) |       |
| allowed_campaign_discount_pct | int      |       |
| campaign_budget_default       | int      |       |
| daily_campaign_budget_cap     | int      |       |

## Campaign

| Field                | Type             | Notes                                                                   |
| -------------------- | ---------------- | ----------------------------------------------------------------------- |
| campaign_id          | str (PK)         |                                                                         |
| merchant_id          | str (FK)         |                                                                         |
| objective_text       | text             | raw merchant input, untrusted-for-authorization but trusted-for-display |
| eligible_skus        | JSON (list[str]) |                                                                         |
| discount_pct         | int              |                                                                         |
| bundle_offer         | JSON (nullable)  |                                                                         |
| budget               | int              |                                                                         |
| budget_spent         | int              | default 0, incremented per attributed order                             |
| starts_at / ends_at  | datetime         |                                                                         |
| status               | enum             | `DRAFT, PENDING_APPROVAL, ACTIVE, PAUSED, COMPLETED`                  |
| pause_reason         | str (nullable)   |                                                                         |
| guardian_decision_id | str (FK)         | the approving decision                                                  |

## CampaignEvent

| Field       | Type     | Notes                                              |
| ----------- | -------- | -------------------------------------------------- |
| event_id    | str (PK) |                                                    |
| campaign_id | str (FK) |                                                    |
| type        | enum     | `ACTIVATED, ORDER_ATTRIBUTED, PAUSED, COMPLETED` |
| detail      | JSON     |                                                    |
| created_at  | datetime |                                                    |

## TransactionIntent (persisted, not just a request DTO — needed for replay/audit)

| Field                  | Type     | Notes                                                                           |
| ---------------------- | -------- | ------------------------------------------------------------------------------- |
| intent_id              | str (PK) |                                                                                 |
| buyer_id               | str (FK) |                                                                                 |
| merchant_id            | str (FK) |                                                                                 |
| items                  | JSON     | list of`{sku, variant_id, qty, observed_price, catalog_version, snapshot_id}` |
| requested_discount_pct | int      | 0 unless a campaign/coupon applied                                              |
| created_at             | datetime |                                                                                 |
| expires_at             | datetime | `created_at` + 2 minutes; Guardian rejects expired intents (replay defense)   |

## GuardianDecision

| Field                | Type               | Notes                                     |
| -------------------- | ------------------ | ----------------------------------------- |
| decision_id          | str (PK)           |                                           |
| intent_id            | str (FK, nullable) | null for campaign decisions               |
| campaign_proposal_id | str (FK, nullable) | set for campaign decisions                |
| decision             | enum               | `APPROVE, BLOCK, REQUIRE_CONFIRMATION`  |
| checks               | JSON               | ordered list of`{name, passed, detail}` |
| primary_reason       | str                |                                           |
| final_verified_total | int (nullable)     |                                           |
| mandate_id           | str (FK, nullable) |                                           |
| policy_version       | int (nullable)     |                                           |
| created_at           | datetime           |                                           |

## Order (Razorpay order mirror)

| Field       | Type               | Notes                               |
| ----------- | ------------------ | ----------------------------------- |
| order_id    | str (PK)           | Razorpay order id                   |
| decision_id | str (FK)           |                                     |
| merchant_id | str (FK)           |                                     |
| buyer_id    | str (FK)           |                                     |
| amount      | int                |                                     |
| currency    | str                |                                     |
| status      | enum               | `CREATED, PAID, FAILED, REFUNDED` |
| campaign_id | str (FK, nullable) | for revenue attribution             |
| created_at  | datetime           |                                     |

## Payment (Razorpay payment mirror)

| Field               | Type            | Notes                         |
| ------------------- | --------------- | ----------------------------- |
| payment_id          | str (PK)        | Razorpay payment id           |
| order_id            | str (FK)        |                               |
| status              | str             | Razorpay status string        |
| verified            | bool            | signature verification result |
| raw_webhook_payload | JSON (nullable) | for debugging/audit           |
| created_at          | datetime        |                               |

## Receipt

| Field                | Type               | Notes                                    |
| -------------------- | ------------------ | ---------------------------------------- |
| receipt_id           | str (PK)           |                                          |
| decision_id          | str (FK)           |                                          |
| intent_id            | str (FK, nullable) |                                          |
| buyer_id             | str (FK, nullable) |                                          |
| merchant_id          | str (FK)           |                                          |
| items_snapshot       | JSON               | frozen copy of intent items              |
| catalog_snapshot_ids | JSON (list[str])   |                                          |
| observed_total       | int                |                                          |
| final_verified_total | int (nullable)     |                                          |
| mandate_snapshot     | JSON               | frozen copy of mandate at decision time  |
| policy_snapshot      | JSON               | frozen copy of policy at decision time   |
| guardian_checks      | JSON               | copy of`GuardianDecision.checks`       |
| decision             | enum               | `APPROVE, BLOCK, REQUIRE_CONFIRMATION` |
| reason               | str                |                                          |
| razorpay_order_id    | str (nullable)     |                                          |
| razorpay_payment_id  | str (nullable)     |                                          |
| failure_reason       | str (nullable)     |                                          |
| created_at           | datetime           |                                          |

This table is intentionally denormalized (it duplicates data already in `GuardianDecision`/`Mandate`/`MerchantPolicy`) **on purpose**: a Receipt must remain fully interpretable even if the live Mandate or Policy row is later edited. Immutability of the audit trail matters more than normalization here.

## Entity Relationship Summary

```
Merchant 1─* Product 1─* CatalogSnapshot
Merchant 1─* MerchantPolicy (current) ── versions tracked via `version` field, old versions kept
Merchant 1─* Campaign 1─* CampaignEvent
Buyer 1─* Mandate (only one `active=true` at a time)
Buyer 1─* TransactionIntent 1─1 GuardianDecision 1─1 Receipt
GuardianDecision 0..1─1 Order 1─1 Payment
Campaign 1─* Order (via Order.campaign_id, for attribution)
```
