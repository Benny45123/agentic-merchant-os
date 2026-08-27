
# AGENT_08_FRONTEND

## Objective

Build the Next.js frontend: buyer chat/cart/checkout experience with Razorpay Checkout embed and Receipt viewer, plus the merchant dashboard (policy editor, campaign composer, revenue view, receipt list).

## Scope

- Buyer chat UI (`/app/(buyer)/chat`) — message thread, cart sidebar, checkout button, Guardian check-list display, Razorpay Checkout embed
- Receipt viewer (`/app/(buyer)/receipts/[id]`) — readable timeline, not raw JSON
- Merchant dashboard (`/app/(merchant)/dashboard`) — revenue view (live-fetched), receipt list with filters
- Merchant policy editor (`/app/(merchant)/policy`)
- Merchant campaign composer (`/app/(merchant)/campaigns`) — objective input, proposal review (with Guardian decision visible), activate button, live status view

## Files/Directories Owned

`frontend/`

## Dependencies

`04_API_CONTRACTS.md` is your complete contract — you can build against it with mock responses before the backend is fully live, then point at the real backend.

## Implementation Requirements

1. Never call Razorpay order creation client-side. The frontend only ever opens Razorpay Checkout with a backend-issued `order_id`/`key_id` obtained from `/agent/checkout-intent`'s response.
2. Render the Guardian's `checks[]` list visibly during checkout — pass/fail per check, not hidden behind a generic spinner. This is core to the "explainable" requirement.
3. Receipt viewer renders: intent → checks (pass/fail list) → decision → payment outcome, as a timeline component.
4. Dashboard revenue numbers are fetched live from `GET /dashboard/revenue` on every page load/refresh — no hardcoded or cached-forever values.
5. Campaign composer must show the Guardian's decision on a proposal (including partial-eligibility SKU drops and budget confirmation prompts) before allowing activation.
6. Handle all three Guardian decision types distinctly in UI: `APPROVE` (proceed to payment), `BLOCK` (explain reason, no retry-as-is path), `REQUIRE_CONFIRMATION` (show discrepancy, offer explicit confirm action).

## Tests Required

- Component test: Guardian check-list renders correctly for a mocked APPROVE/BLOCK/REQUIRE_CONFIRMATION response
- Manual smoke test: full browser purchase completes with a real Razorpay test-mode payment
- Manual smoke test: campaign composer flow from objective text to active campaign

## Acceptance Criteria

- [ ] A human can complete a real purchase end-to-end in the browser (discover → upsell → checkout → pay → receipt)
- [ ] Guardian checks are visibly rendered, not hidden
- [ ] Both failure demos (`15_DEMO_SCENARIOS.md` Beats 5-6) are reproducible through the UI, not just via API calls
- [ ] Dashboard numbers visibly change immediately after a real transaction
- [ ] Merchant can create and activate a campaign end-to-end through the UI

## Must NOT Modify

Any file under `backend/`.
