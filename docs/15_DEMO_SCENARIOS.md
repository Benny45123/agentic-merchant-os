
# 15 — Demo Scenarios (5-Minute Buildathon Demo)

## 0. Pre-Demo State

Seed data loaded: 1 merchant, catalog of ~8-12 products across 2-3 categories (must include headphones + warranty + case as a bundle trio for the upsell beat, and at least one product with intentionally injected malicious content for Failure 1), one buyer with an active mandate, default policy from `08_MANDATE_AND_POLICY_SPEC.md` §7, empty receipt/order history (so revenue numbers visibly start real and grow live).

## 1. Demo Script (target: ~5 minutes, timed beats)

**Beat 1 — Discovery & Upsell (60s)**
Buyer chat: "I want wireless headphones under ₹5000." Agent returns matching products from the real catalog (not scripted text). Buyer picks one, adds to cart. Agent proactively recommends the warranty add-on with a real-data reason ("₹499, most buyers add this"). Buyer accepts.
*Show:* the cart total updating from real catalog prices.

**Beat 2 — Checkout & Guardian Approval (45s)**
Buyer requests checkout. Show the Guardian's check list rendering (mandate checks, policy checks, price/inventory match) all green, decision `APPROVE`. Razorpay Checkout widget opens.
*Show:* the actual list of checks, not just a spinner — this is the "explainable" requirement.

**Beat 3 — Razorpay Payment (30s)**
Complete payment with a Razorpay test card. Payment confirms, webhook/verify completes.
*Show:* real Razorpay test-mode order id appearing.

**Beat 4 — Decision Receipt (30s)**
Open the Receipt view for this transaction. Walk through: intent → checks → decision → payment id.
*Show:* this is the audit trail, one click from the transaction.

**Beat 5 — Failure 1: Catalog Injection Attack (45s)**
Buyer (or a scripted "AI buyer" call) attempts to buy the pre-seeded product with injected malicious content in its description, saying something that would normally trigger a much larger quantity than the buyer's mandate allows. Show the Guardian `BLOCK`, the reason (`quantity_exceeds_mandate` — not a "we detected an attack" false narrative, the real reason is the mandate held), and note the `security.catalog_content_flagged: true` marker in the receipt showing the system also noticed the suspicious content independently.
*Show:* a Receipt exists for the blocked attempt too.

**Beat 6 — Failure 2: Price Change Mid-Flow (45s)**
Pre-arranged: a product's price is bumped via the merchant admin panel (or a quick script) after it's already in a demo cart from earlier in the show (or re-add to cart, then change price, then checkout). Guardian returns `REQUIRE_CONFIRMATION: price_changed`, showing observed vs. authoritative price side by side. Confirm to proceed at the new authoritative price, or cancel.
*Show:* the receipt records both prices.

**Beat 7 — Campaign Creation (45s)**
Switch to merchant view. Type objective: "Increase sales of headphones this weekend." Orchestrator proposes a bounded campaign (discount %, budget, eligible SKUs) with a rationale grounded in real historical order data. Guardian validates it live on screen → `APPROVE`. Merchant activates.
*Show:* the specific numeric constraints (max discount, budget) came from real policy, not invented by the LLM.

**Beat 8 — Campaign Constraint Enforcement + Revenue Impact (30s)**
Run 1-2 quick buyer purchases under the new campaign offer (can be scripted/fast-forwarded). Show `budget_spent` incrementing on the campaign status view, and the dashboard's `campaign_revenue`/`total_revenue` numbers changing — pulled live from the Order table.
*Show:* if time allows, show the budget-exhaustion auto-pause by pre-setting a tiny remaining budget for one final purchase.

## 2. What Judges Should Walk Away Believing

1. Every rupee movement went through one deterministic gate.
2. The system can explain, in plain language, every approve and every block.
3. It survived a real prompt-injection attempt and a real stale-price condition.
4. The AI grew revenue (upsell + campaign) without ever being trusted with unilateral spending power.
5. Nothing on screen was hardcoded — refreshing the dashboard mid-demo shows numbers that actually move.

## 3. Additional Optional Failure Scenarios (time-permitting / judge Q&A)

- **Duplicate submission:** double-click checkout → second attempt blocked as `duplicate_intent`.
- **Expired mandate:** buyer's mandate expiry set to the past → any checkout attempt `BLOCK: no_active_mandate`.
- **Campaign margin violation:** propose a campaign discount too steep for a low-margin SKU → that SKU excluded from the campaign, shown live in the proposal review.
- **Insufficient inventory:** set a product's inventory to 0 mid-cart → `BLOCK: insufficient_inventory` at checkout.
- **Invalid webhook signature:** curl a forged webhook payload → 400 rejected, no order state change (best shown via terminal/logs rather than UI).

## 4. Fallback Plan (if live LLM/Razorpay call fails during demo)

Keep a pre-recorded 90-second backup clip of Beats 1-4 and 5-6. Practice the live version at least 5 times before submission; if Wi-Fi/API flakiness is a real risk, have `.env` pointed at a stable network and confirm Razorpay test-mode + chosen LLM provider status right before presenting.

## 5. Presenter Checklist

- [ ] Fresh seeded DB (no stale receipts cluttering the demo)
- [ ] Merchant + buyer sessions pre-logged-in in separate browser windows
- [ ] Network connectivity confirmed for Razorpay test mode + LLM provider
- [ ] Timer rehearsed — this script is ~5:30 at a comfortable pace, trim Beat 8 first if running long
