# Agent Task: Agent 20 — Headless Razorpay UPI AutoPay

## Context & Purpose
Transition Agentic Merchant OS from interactive checkout modals to **True Autonomous AI Agent Commerce**. Build the headless UPI AutoPay recurring token system (`tok_rzp_autopay_...`), allowing the Commerce Guardian to execute 0-click settlements across Telegram (`/autopay`), Claude MCP, Web UI, and UAP protocols in < 400ms without OTP prompts.

---

## Deliverables

### 1. Database & Models (`backend/app/models/` & `backend/app/mandate/`)
- Extend `BuyerMandate` model in `app/models/mandate.py` with:
  - `autopay_enabled: bool`
  - `autopay_token: Optional[str]`
  - `customer_id: Optional[str]`
  - `max_amount_per_charge: int`
  - `recurring_auth_status: str`
  - `autopay_bank_name: Optional[str]`
  - `autopay_vpa: Optional[str]`
- Update `MandateResponse` and `MandateCreate` schemas in `app/mandate/schemas.py`.

### 2. Razorpay Recurring Adapter (`backend/app/razorpay_adapter/`)
- Implement `create_autopay_registration(buyer_id, max_amount_paise)` in `app/razorpay_adapter/client.py`.
- Implement `charge_autopay_token(customer_id, token_id, amount_paise, order_id, receipt_id)` in `app/razorpay_adapter/client.py`.
- Add AutoPay router endpoints in `app/razorpay_adapter/router.py`:
  - `POST /mandates/autopay/setup`
  - `POST /mandates/autopay/revoke`

### 3. Commerce Guardian AutoPay Settlement (`backend/app/guardian/`)
- In `app/guardian/pipeline.py`:
  - On `APPROVE` decisions, check if buyer has active `autopay_token`.
  - If active, automatically invoke `charge_autopay_token()`, set `Order.status = OrderStatus.PAID`, and mint Decision Receipt with `payment_method: "upi_autopay_headless"`.

### 4. Omnichannel Telegram Bot Integration (`backend/app/telegram/`)
- In `app/telegram/handlers.py`:
  - Add `/autopay` command handler to toggle and register 1-click UPI AutoPay.
  - When AutoPay is enabled, all purchases/negotiations immediately execute with `⚡ 0-CLICK AUTOPAY EXECUTED` receipt messages.

### 5. Model Context Protocol (MCP) Server for Claude (`backend/app/api/mcp_server.py`)
- Add `setup_autopay_mandate` MCP tool.
- Enable `submit_machine_purchase` and `accept_negotiation_offer` to charge pre-approved AutoPay tokens headlessly.

### 6. Automated Pytest & Scenarios
- Add `backend/tests/test_headless_autopay.py`.
- Add Scenario 10 (`scripts/scenario_headless_autopay.py`) to the demo runner suite.

---

## Acceptance Criteria
- [ ] 1-Time mandate setup generates valid test recurring token (`tok_rzp_autopay_...`).
- [ ] Guardian validates 19 invariants and charges token headlessly in < 400ms.
- [ ] Zero OTP prompts / zero browser popups during autonomous purchases.
- [ ] Telegram Bot `/autopay` command enables 0-click checkout.
- [ ] Claude MCP tool executes headless purchases with `status: "PAID"`.
- [ ] Decision Receipts cryptographically record `upi_autopay_headless` payment method.
