
# 13 — Threat Model

Format per threat: **Attack**, **Risk**, **Defense**, **Implementation Location**, **Test Case**.

## 1. Prompt Injection in Product Descriptions

- **Attack:** A merchant-content field (`description`) contains text instructing the AI to ignore buyer limits or add extra units.
- **Risk:** Unauthorized spend if the Commerce Agent complied.
- **Defense:** Structural — Guardian never reads free-text fields; `TransactionIntent` is assembled from actual `CartItem` state, not LLM free text. Agent system prompt explicitly instructs treating catalog text as data (`06_AGENT_SPEC.md` §3). Heuristic scanner flags the content for visibility (`09_CATALOG_SECURITY.md`).
- **Location:** `app/commerce_agent` (prompt + tool-call architecture), `app/guardian` (re-validation), `app/security` (flagging).
- **Test Case:** Fixture product with injected instruction in `description`; assert final `TransactionIntent.items[].qty` matches the buyer's actual chat request, and Guardian decision respects the real mandate regardless of the injected text.

## 2. Prompt Injection in Reviews

- **Attack:** A review field contains an instruction to apply a discount or skip confirmation.
- **Risk:** Same as #1, plus unauthorized discount.
- **Defense:** Same structural defense — discount values are only ever accepted from `Offer`/`CampaignProposal` rows validated by Policy check, never parsed out of review text.
- **Location:** `app/guardian` (policy check always re-validates `discount_pct` server-side), `app/security`.
- **Test Case:** Fixture review with injected discount instruction; assert Guardian rejects any discount not present in an actual validated `Offer` row.

## 3. Malicious Merchant Content (general)

- **Attack:** A merchant (or compromised merchant account) writes catalog content designed to manipulate buyer-side AI agents broadly (not just Razorpay Guardian — e.g., trying to get an *external* AI buyer platform to misbehave).
- **Risk:** Reputational/trust risk to the "agent-readable catalog" promise; could poison downstream AI buyers not built by us.
- **Defense:** All structured catalog fields are schema-validated at write time; free-text fields are scanned and flagged; flagged products are surfaced to the merchant dashboard for manual review (visibility, not auto-removal, for MVP).
- **Location:** `app/catalog` (write-time validation), `app/security` (scan).
- **Test Case:** Attempt to `PATCH` a product with a non-numeric `price` → rejected with 422. Attempt to write flagged `description` → accepted (content) but `suspicious_content_flag=true` set and visible via `GET /catalog/products/{sku}`.

## 4. Agent Attempting to Exceed Buyer Mandate

- **Attack:** Commerce Agent (bug or manipulation) builds a cart/intent beyond the buyer's declared limits.
- **Risk:** Unauthorized spend.
- **Defense:** `check_mandate()` in Guardian, independent of Agent behavior; `add_to_cart` tool also soft-clamps at cart-build time for good UX, but the authoritative check is Guardian-side.
- **Location:** `app/mandate`, `app/guardian` step 3.
- **Test Case:** Submit an intent with `qty > mandate.max_quantity_per_item` directly to `/guardian/evaluate` (bypassing the Agent) → `BLOCK: quantity_exceeds_mandate`.

## 5. Price Changing Between Discovery and Payment

- **Attack:** Merchant (or a race condition) changes `Product.price` after the Agent showed it to the buyer but before checkout completes.
- **Risk:** Buyer charged more than they agreed to, or merchant undercharged.
- **Defense:** Guardian re-fetches authoritative price at evaluation time and compares to `observed_price`; mismatch → `REQUIRE_CONFIRMATION` (price up) or auto-proceed at the lower price (price down). Charged amount is always the authoritative price. See `07_GUARDIAN_SPEC.md` §3.
- **Location:** `app/guardian` step 4, `app/catalog.get_authoritative_state()`.
- **Test Case:** Build a cart, then mutate `Product.price` via admin API, then submit checkout-intent → Guardian returns `REQUIRE_CONFIRMATION: price_changed` with both prices in the check detail. This is Failure Demo 2 (`15_DEMO_SCENARIOS.md`).

## 6. Inventory Changing Between Discovery and Payment

- **Attack:** Stock sells out between cart-build and checkout (e.g., another buyer, or merchant adjustment).
- **Risk:** Overselling.
- **Defense:** Guardian re-checks `authoritative.inventory >= qty` at evaluation time.
- **Location:** `app/guardian` step 4.
- **Test Case:** Set `Product.inventory = 0` after cart-build, submit checkout-intent → `BLOCK: insufficient_inventory`.

## 7. Agent Attempting Excessive Quantity

- **Attack:** Agent (bug, hallucination, or manipulated) sets an unreasonably high quantity.
- **Risk:** Large unauthorized order.
- **Defense:** `mandate.max_quantity_per_item` hard cap, enforced in both the `add_to_cart` tool (soft, UX) and Guardian (hard, authoritative).
- **Location:** `app/commerce_agent` (tool clamp+error), `app/guardian` step 3.
- **Test Case:** Direct `/guardian/evaluate` call with `qty=1000` → `BLOCK: quantity_exceeds_mandate`.

## 8. Agent Attempting Unauthorized Discount

- **Attack:** Agent tries to apply a `requested_discount_pct` not backed by a real `Offer`/campaign.
- **Risk:** Merchant revenue loss.
- **Defense:** Guardian only honors discounts present in active, unexpired `Offer` rows tied to the SKU; a `requested_discount_pct` in the intent that doesn't match a real offer is ignored/rejected, not trusted.
- **Location:** `app/guardian` step 5/7.
- **Test Case:** Submit intent with `requested_discount_pct=50` with no matching `Offer` row → Guardian computes total at full price, or `BLOCK` if intent explicitly asserts a discounted total that doesn't reconcile.

## 9. Campaign Exceeding Merchant Budget

- **Attack:** Campaign proposal (or many transactions against an active campaign) spends beyond `budget`.
- **Risk:** Uncontrolled marketing spend.
- **Defense:** Guardian checks `daily_campaign_budget_cap` at proposal time; per-transaction budget check at checkout time auto-pauses the campaign the moment spend would exceed budget (`07_GUARDIAN_SPEC.md` §5).
- **Location:** `app/guardian` (campaign pipeline + per-transaction check), `app/campaign`.
- **Test Case:** Seed a campaign with a small budget, run enough simulated transactions to exceed it → campaign auto-`PAUSED`, subsequent transaction gets full price, `CampaignEvent(type=PAUSED)` logged.

## 10. Campaign Violating Minimum Margin

- **Attack:** Proposed discount would sell below `minimum_margin_pct` on some SKUs.
- **Risk:** Merchant sells at a loss.
- **Defense:** Per-SKU margin check at proposal time (SKUs failing are dropped from eligibility) and, for merchant-set discounts generally, at every transaction via the same margin check.
- **Location:** `app/policy.check_campaign_policy()`, `app/guardian` §4 step 4.
- **Test Case:** Propose a campaign discount that would push a low-cost-margin SKU below `minimum_margin_pct` → that SKU excluded from `eligible_skus`, noted in `checks`.

## 11. Duplicate Payment / Order Attempts

- **Attack:** Frontend retries `checkout-intent` (double-click, network retry) causing two Razorpay orders for one purchase.
- **Risk:** Double charge.
- **Defense:** `intent_id` uniqueness constraint on `GuardianDecision` (replay check, step 2); Razorpay order creation uses `receipt_id` as idempotency key **[VERIFY against current Razorpay docs]**.
- **Location:** `app/guardian` step 2, `app/razorpay_adapter`.
- **Test Case:** Submit the same `intent_id` twice → second call returns `BLOCK: duplicate_intent` without a second Razorpay order.

## 12. Replay of Stale Transaction Intent

- **Attack:** An old, previously-evaluated (or never-submitted) intent is replayed later, possibly after prices/policy changed.
- **Risk:** Stale-priced or now-non-compliant transaction executes.
- **Defense:** `TransactionIntent.expires_at` (created_at + 2 min); Guardian step 1 rejects expired intents; even non-expired but already-decided intents are rejected by the uniqueness check (#11).
- **Location:** `app/guardian` step 1.
- **Test Case:** Submit an intent with `expires_at` in the past → `BLOCK: intent_expired`.

## 13. Webhook Verification

- **Attack:** Forged webhook call to `/webhooks/razorpay` claiming a payment succeeded without a real Razorpay event.
- **Risk:** Fraudulent order marked `PAID` without real payment.
- **Defense:** Signature verification against Razorpay webhook secret before any processing; reject unsigned/invalid immediately **[VERIFY exact algorithm against current docs]**.
- **Location:** `app/razorpay_adapter.handle_webhook()`, `app/api` webhook router.
- **Test Case:** POST to `/webhooks/razorpay` with an invalid signature → 400, no `Order` state change.

## 14. LLM Hallucinating Product/Price Information

- **Attack:** Commerce Agent LLM states a price, SKU, or product feature to the buyer that doesn't exist in the catalog (a generic LLM failure mode, not an external attack).
- **Risk:** Buyer is misinformed; if it flowed into the transaction it could cause a mismatched charge.
- **Defense:** The `TransactionIntent` is built from actual `CartItem`/`CatalogSnapshot` rows via tool calls (`add_to_cart(sku, qty)` returns the *real* catalog price, which is what's stored), never from the LLM's free-text claim about a price. Even if the LLM tells the buyer a wrong price in chat, the Guardian will only ever charge the authoritative price, and any mismatch between what the LLM said and what's charged surfaces via the price-revalidation `REQUIRE_CONFIRMATION` path if it also diverges from what was cart-snapshotted.
- **Location:** `app/commerce_agent` (tool-call architecture — LLM never free-hand writes price/SKU into intent), `app/guardian` step 4.
- **Test Case:** Prompt the Agent to claim an incorrect price in its chat reply (adversarial test prompt); assert the resulting `TransactionIntent.items[].observed_price` still equals the real `CatalogSnapshot` price, not the hallucinated figure.

## Summary Table

| #  | Threat                     | Decision Outcome             | Primary Location         |
| -- | -------------------------- | ---------------------------- | ------------------------ |
| 1  | Injection in description   | BLOCK/normal (mandate holds) | guardian, commerce_agent |
| 2  | Injection in reviews       | discount rejected            | guardian                 |
| 3  | Malicious merchant content | flagged, visible             | catalog, security        |
| 4  | Agent exceeds mandate      | BLOCK                        | mandate, guardian        |
| 5  | Price change               | REQUIRE_CONFIRMATION         | guardian, catalog        |
| 6  | Inventory change           | BLOCK                        | guardian, catalog        |
| 7  | Excessive quantity         | BLOCK                        | guardian                 |
| 8  | Unauthorized discount      | ignored/BLOCK                | guardian                 |
| 9  | Campaign over budget       | auto-PAUSE                   | guardian, campaign       |
| 10 | Campaign under-margin      | SKU excluded                 | policy, guardian         |
| 11 | Duplicate payment          | BLOCK (2nd attempt)          | guardian                 |
| 12 | Stale intent replay        | BLOCK                        | guardian                 |
| 13 | Webhook forgery            | 400 rejected                 | razorpay_adapter         |
| 14 | LLM hallucination          | authoritative price used     | commerce_agent, guardian |
