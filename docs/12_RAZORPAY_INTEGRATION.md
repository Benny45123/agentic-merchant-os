
# 12 — Razorpay Integration Spec

**Test mode only.** Everything in this document must be verified against current official Razorpay documentation before implementation — this document describes the *shape* of the integration and the architectural boundary, not a guaranteed-current API reference. Anywhere marked **[VERIFY]** the implementing agent must check `https://razorpay.com/docs/` (Orders API, Payments API, Webhooks) before writing code, since exact field names/flows can change.

## 1. Adapter Boundary (recap of `03_COMPONENT_ARCHITECTURE.md` §3.7)

`app/razorpay_adapter` is the only code that imports the Razorpay SDK. It exposes a narrow, business-logic-free interface. Only `app/guardian` calls it.

```python
class RazorpayAdapter:
    def create_order(self, amount: int, currency: str, receipt_id: str) -> RazorpayOrder: ...
    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool: ...
    def handle_webhook(self, payload: bytes, signature_header: str) -> WebhookEvent: ...
    def refund(self, payment_id: str, amount: int) -> RazorpayRefund: ...
```

## 2. Order Creation Flow

1. Guardian reaches an `APPROVE` decision with `final_verified_total`.
2. Guardian calls `create_order(amount=final_verified_total, currency, receipt_id=<the receipt about to be written>)`. **[VERIFY]** exact Razorpay Orders API request/response shape (`amount`, `currency`, `receipt`, `notes` fields) against current docs — do not assume prior training knowledge is current.
3. Razorpay returns an `order_id`. Guardian returns this to the caller (`/agent/checkout-intent` response) alongside `key_id` (public test key) for the frontend.
4. Frontend opens Razorpay Checkout (`Razorpay` JS widget) with `order_id`, `amount`, `currency`, `key_id`. **[VERIFY]** current Checkout.js integration snippet against docs — do not hand-write from memory.
5. On success, Checkout returns `razorpay_payment_id`, `razorpay_order_id`, `razorpay_signature` to the frontend, which POSTs them to `/payments/verify`.

## 3. Payment Verification

`/payments/verify` calls `verify_payment()`, which **[VERIFY]** must replicate Razorpay's documented HMAC-SHA256 signature verification (`order_id + '|' + payment_id` signed with the key secret) against the current docs — do not assume the exact algorithm without checking, since Razorpay's verification approach must match their SDK version precisely. On success: `Order.status = PAID`, `Payment` row created with `verified=true`, `receipts.finalize_receipt()` attaches `razorpay_payment_id` to the existing Receipt (the Receipt was already written at Guardian decision time with `razorpay_order_id`, per `07_GUARDIAN_SPEC.md` step 11 — payment success only appends the payment ID, it does not retroactively change the `APPROVE` decision).

## 4. Webhook Handling

`POST /webhooks/razorpay` is the durable source of truth for payment status (the frontend `/payments/verify` call is a UX fast-path, not the only path — if the browser tab closes mid-flow, the webhook still lands). **[VERIFY]** current webhook event names (e.g., `payment.captured`, `payment.failed`) and the `X-Razorpay-Signature` verification method against official docs. Webhook must:

1. Verify signature before parsing payload (reject unsigned/invalid immediately, return 400, log).
2. Be idempotent — processing the same webhook event twice (Razorpay may retry) must not double-write `Order`/`Payment` state. Use the Razorpay event id as a dedupe key.
3. Update `Order.status`/`Payment.status` and, on failure events, ensure the Receipt already on file (`BLOCK` was never issued for an `APPROVE`d-then-failed payment — this is a distinct case) gets a `failure_reason` appended without altering the original `decision` field (the Guardian's decision to approve was correct given what it knew; the payment simply failed afterward — these are different facts and both must be visible).

## 5. Refunds (SHOULD HAVE)

`refund(payment_id, amount)` — **[VERIFY]** Razorpay Refunds API shape. Triggers `Order.status = REFUNDED`. Refunds do not go through the buyer-mandate/policy Guardian pipeline (there's no new "purchase" being authorized) but do still produce a Receipt-adjacent audit row (`CampaignEvent`-style log or a dedicated `RefundReceipt` if time allows) so the audit trail remains complete.

## 6. Idempotency (SHOULD HAVE, strongly recommended)

**[VERIFY]** whether Razorpay Orders API supports an idempotency key header in the current docs; if so, the adapter should pass `receipt_id` (already unique per Guardian decision) as the idempotency key so a network retry from `create_order` never creates two orders for one approved decision.

## 7. Test-Mode Specifics

- Test API keys (`rzp_test_...`) only, stored in `.env`, never committed (`19_ENVIRONMENT_SETUP.md`).
- Test card numbers/UPI IDs for demo payment success/failure — **[VERIFY]** current Razorpay test credentials list in docs (these are documented by Razorpay and change occasionally).
- No live webhook endpoint needed if testing locally without a public URL — **[VERIFY]** whether Razorpay's test-mode webhook delivery requires a public tunnel (e.g., ngrok) for local dev, and document the chosen approach in `19_ENVIRONMENT_SETUP.md`.

## 8. Explicit Non-Goals

- No live/production mode, ever, in this project.
- No support for non-Razorpay payment methods.
- No direct client-side order creation — amount is always server (Guardian)-determined, never trusted from the frontend, to prevent client-side amount tampering.
