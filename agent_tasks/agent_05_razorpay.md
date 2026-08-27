
# AGENT_05_RAZORPAY

## Objective

Implement the Razorpay Adapter: test-mode order creation, payment verification, webhook handling, and refunds — with zero business logic, called only by the Guardian.

## Scope

- `app/razorpay_adapter/client.py`: thin wrapper around the official Razorpay Python SDK
- `app/razorpay_adapter/router.py`: `POST /webhooks/razorpay`, `POST /payments/verify` per `04_API_CONTRACTS.md` §5

## Files/Directories Owned

`backend/app/razorpay_adapter/`

## Dependencies

`app/core` (AGENT_01) for config (`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`).

## Interfaces/Contracts

```python
def create_order(amount: int, currency: str, receipt_id: str) -> RazorpayOrder: ...
def verify_payment(order_id: str, payment_id: str, signature: str) -> bool: ...
def handle_webhook(payload: bytes, signature_header: str) -> WebhookEvent: ...
def refund(payment_id: str, amount: int) -> RazorpayRefund: ...
```

## Implementation Requirements — READ FIRST

Every item below marked **[VERIFY]** in `12_RAZORPAY_INTEGRATION.md` must be checked against current official Razorpay documentation (razorpay.com/docs) before implementation. Do not implement signature verification, webhook event names, or field shapes from memory — Razorpay's exact API surface can change and an incorrect signature check is a real security hole, not a formality.

1. `create_order` — **[VERIFY]** Orders API request/response shape; pass `receipt_id` as the idempotency key if the current API supports it.
2. `verify_payment` — **[VERIFY]** current HMAC-SHA256 signature verification algorithm exactly.
3. `handle_webhook` — **[VERIFY]** current webhook event names and `X-Razorpay-Signature` verification method; must be idempotent against Razorpay's own retries (dedupe on event id); must reject invalid signatures before parsing payload.
4. `refund` — **[VERIFY]** Refunds API shape (SHOULD HAVE, implement if time allows after core flow is solid).
5. This package must contain zero policy/business logic — no mandate checks, no discount logic, nothing beyond translating Guardian decisions into Razorpay calls and Razorpay responses into internal types.
6. Test mode only — reject/refuse to initialize with a non-`rzp_test_` key.

## Tests Required

- Mocked SDK test: `create_order` returns the correct internal type from a mocked Razorpay response
- Real test-mode smoke test (manual, run once against a real Razorpay test account, documented in a script, not required in CI): full order→payment→verify flow
- Invalid webhook signature → rejected with no state change
- Duplicate webhook event (same event id) → processed once, no double-write

## Acceptance Criteria

- [ ] `create_order`/`verify_payment` work against a real Razorpay test-mode account
- [ ] Webhook signature verification correctly rejects a forged payload
- [ ] Duplicate webhook delivery does not double-write `Order`/`Payment`
- [ ] No business logic exists in this package (spot-check: no references to `Mandate`, `MerchantPolicy`, or `discount` anywhere in `app/razorpay_adapter`)
- [ ] All **[VERIFY]** items were actually checked against current docs, not assumed

## Must NOT Modify

`app/guardian`, `app/catalog`, `app/commerce_agent`, `app/campaign`, `app/receipts`, `app/mandate`, `app/policy`.
