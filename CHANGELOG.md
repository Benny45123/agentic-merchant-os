# Changelog

All notable changes to the Agentic Merchant OS platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and adheres to Semantic Versioning.

---

## [1.5.0] - 2026-09-02
### Added
- **Live Razorpay Test Mandate Verification Gate**:
  - Implemented `verify_mandate_token(customer_id, token_id)` in `RazorpayAdapter` (`app/razorpay_adapter/client.py`) to cryptographically verify recurring tokens directly against Razorpay's API sandbox (`api.razorpay.com`) prior to zero-click debit execution.
  - Integrated Live Mandate Verification Gate into the Commerce Guardian (`app/guardian/pipeline.py`), appending deterministic invariant check `mandate.razorpay_verified: PASSED` to signed Decision Receipts.
  - Added REST endpoint `GET /mandates/autopay/verify` in `app/razorpay_adapter/router.py` returning live token authorization status, customer ID, and verification metadata.
  - Enforced strict gate ordering: `setup_autopay_mandate` queries the Live Razorpay Mandate Verification Gate BEFORE writing activation state to the database, deterministically rejecting unverified tokens.
  - Positioned `RAZORPAY MANDATE VERIFICATION GATE: PASSED` on line 1 of Claude MCP setup card to ensure visibility before CLI message folding (`ctrl+o`).
  - Fixed mandate cycle spend calculation: `setup_autopay_mandate` resets `mandate.spent_amount = 0`, giving newly authorized mandate pools 100% available headroom rather than tallying historical lifetime orders.

- **Hosted Razorpay Test Mandate Verification & Authorization Portal**:
  - Built Hosted Mandate Portal (`GET /mandates/checkout/{identifier}`) with live token telemetry, spending ceiling (₹1,00,000.00), available headroom, and linked VPA (`b_001@okhdfcbank`).
  - Implemented True 2-Step Mandate Lifecycle: `setup_autopay_mandate` creates mandate in `PENDING_AUTH` state (`autopay_enabled = False`) with a live Razorpay authorization link; mandate only transitions to `ACTIVE` once the human shopper authorizes via the hosted Razorpay modal.
  - Added `POST /mandates/checkout/{identifier}/authorize` endpoint to finalize online mandate activation and record captured payment IDs.
  - Embedded official Razorpay `checkout.js` modal with real test `order_id` (₹1.00 NPCI test auth) via `adapter.create_order` and removed un-indexed `customer_id` from client-side modal options.
  - Added live Razorpay `handler` callback in `checkout.js` with instant celebration banner displaying the captured Razorpay Payment ID and real-time state transition to ACTIVE.
  - Streamlined portal UX to a single primary `[ ⚡ Authorize & Activate Mandate on Razorpay ]` button with 1-click test fallback.

- **Omnichannel Telegram Mobile Gateway 2-Step Verification**:
  - Integrated 2-Step Mandate Authorization Gate into Telegram Bot (`@agentic_merchant_store_bot`):
    - When shopper triggers `/autopay` or types "activate autopay", the bot presents an inline URL button `[ ⚡ Authorize Mandate on Razorpay ]` opening the hosted Razorpay checkout portal in the mobile in-app browser via the public HTTPS tunnel.
    - Verified live end-to-end mobile authorization directly from physical smartphone: opens Razorpay checkout, captures ₹1 test auth, and transitions mandate to `ACTIVE 🟢`.
    - Added real-time token state awareness in `/autopay` and `autopay:verify` callback handlers in `app/telegram/bot.py`, indicating `PENDING_AUTH` before authorization and `ACTIVE 🟢` with 100% available headroom afterward.
    - Extended Telegram natural language message router to recognize all AutoPay phrases (`activate`, `turn on`, `verify`, `check status`, `revoke`).

- **Claude MCP Server & Payment Discovery Upgrades**:
  - Maintained `MachinePurchaseResponse.status = "APPROVED"` contract in UAP gateway while exposing `headless_autopay: bool` for client-side payment link differentiation.
  - Added dedicated `check_payment_status` tool to Claude MCP server with real-time Razorpay payment verification, paid settlement confirmation, and pending checkout URL guidance.
  - Enabled single-command full catalog retrieval in `search_catalog` (accepts empty query, `*`, or `all`), returning all 27 products across mobiles, laptops, audio, wearables, and accessories.
  - Added `GET /payments/sync/{order_id}` and `GET /payments/order/{order_id}` route aliases with bidirectional receipt UUID and order ID lookup.
  - Enhanced catalog search engine (`search_products`) with multi-token smart matching across product name, SKU, category, and description (e.g. "samsung phone" reliably matches Samsung Galaxy S24).
  - Unified payment link routing for Claude MCP, UAP machine gateway, and Guardian escalation alerts to use `{BACKEND_PUBLIC_URL}/payments/checkout/{id}`, resolving Razorpay invalid hosted URL errors.
  - Updated `docs/23_HEADLESS_RAZORPAY_UPI_AUTOPAY.md` and `agent_tasks/agent_20_headless_autopay.md` with complete 3-layer mandate verification specs.
  - Added test coverage in `tests/test_headless_autopay.py` (`test_live_razorpay_mandate_verification_endpoint` and `test_telegram_autopay_verify_handler`).

- **Google AP2 Specification & Architectural Task Planning**:
  - Authored Document 24 (`docs/24_GOOGLE_AP2_MANDATE_CHAINS.md`) establishing the formal Google Agent Payments Protocol (AP2) Open vs. Closed ES256 Mandate specification.
  - Authored Agent Task 21 (`agent_tasks/agent_21_google_ap2_mandates.md`) detailing the implementation roadmap for ECDSA P-256 delegation chains, canonical cart digests, Guardian dual-chain gate, and 4-leaf Merkle Tree integration.

- **Google AP2 Open vs. Closed Mandate Chains (ES256) Full Implementation**:
  - Built pure-Python cryptographic engine (`app/mandate/ap2_service.py`) generating NIST P-256 (secp256r1) keypairs, computing canonical cart digests (`SHA-256(canonical_json(items))`), and minting/verifying Open and Closed Mandate JWTs with sub-3ms evaluation latency.
  - Extended `Mandate` model (`app/models/mandate.py`) and schemas (`app/mandate/schemas.py`) with optional `open_mandate_jwt`, `user_public_key_pem`, and `agent_public_key_pem` fields with non-breaking backwards compatibility.
  - Added SQLite lifespan dynamic schema migration in `app/main.py` and created Alembic migration `003_add_google_ap2_mandate_fields.py`.
  - Added REST endpoints in `app/mandate/router.py`: `GET /mandate/ap2/open/{buyer_id}`, `POST /mandate/ap2/mint-closed`, and `POST /mandate/ap2/verify-chain`.
  - Integrated 6-point Google AP2 Dual-Chain Verification Gate directly into Commerce Guardian (`app/guardian/pipeline.py`), appending `ap2.open_mandate_signature`, `ap2.closed_mandate_signature`, `ap2.cart_digest_verified`, and `ap2.chain_linkage_verified` to invariant audits and blocking cart tampering deterministically.
  - Integrated AP2 cryptographic metadata into Decision Receipts (`app/receipts/service.py`) and expanded the Merkle Tree Proof visualizer (`frontend/src/components/MerkleTreeVisualizer.tsx`) to a 4-leaf balanced Merkle Tree incorporating Leaf D ($H_{\text{AP2}}$).
  - Added `get_ap2_mandate_chain` tool to Claude MCP server (`app/api/mcp_server.py`) and added the Google AP2 Cryptographic Chain badge to Telegram mobile gateway `/autopay` status messages (`app/telegram/handlers.py`).
  - Added 10-test automated verification suite in `backend/tests/test_google_ap2_mandates.py` covering key generation, canonical cart hashing, chain verification, SKU tampering detection, and price tampering defense.
  - Added Scenario 11 (`scripts/scenario_google_ap2_mandates.py`) and integrated it into the 11-scenario end-to-end test runner (`scripts/run_scenarios.py` and `bin/run_scenarios.sh`).


### Fixed
- **Razorpay Modal "The id provided does not exist" Error**: Removed non-existent client-side `customer_id` and provisioned a real Razorpay test order (`order_id`) for ₹1.00 NPCI test auth.
- **500 Internal Server Error in `/mandates/autopay/status`**: Initialized `settings = get_settings()` at module scope within router handler.
- **500 Internal Server Error in `/mandates/checkout/{token}`**: Imported missing `or_` from `sqlalchemy`.
- **Telegram Inline Keyboard Localhost Rejection**: Handled localhost URL restrictions with fallback callback buttons to prevent Telegram API 400 errors.
- **Pytest Schema Import in `test_google_ap2_mandates.py`**: Replaced incorrect `PolicyCreate` import with `MerchantPolicyUpdate` and wired `test_db_session` fixture and `seed_data` autouse fixture for clean in-memory database test isolation.
- **Scenario 11 Receipt Unpacking Fix**: Updated `scripts/scenario_google_ap2_mandates.py` to retrieve the decision receipt directly via `receipt_id` returned by the Commerce Guardian and safely handle the `ReceiptListResponse` schema dictionary.
- **Merchant Dashboard Store Revenue NaN & Missing Handlers**: Resolved `Store Revenue: ₹NaN` by reading `total_revenue` (and mapping `store_revenue` on both FastAPI backend and Next.js frontend), implemented missing `handleSetupMandate` and `handleToggleMandate` handlers, and clamped mandate utilization progress bar bounds between 0% and 100%.
- **Merchant Dashboard AutoPay Center Light Theme Alignment**: Redesigned the Headless AutoPay e-Mandate telemetry center, active shopper cards, and registration modal in `frontend/src/app/(merchant)/dashboard/page.tsx` from dark slate into the clean, modern white/indigo SaaS aesthetic matching the rest of the Merchant Dashboard.
- **Merchant Dashboard AutoPay Card Padding & Text Spacing**: Replaced non-existent `p-4.5` with generous `p-5 sm:p-6` padding, added responsive flex-wrapping with gap spacing to prevent title and badge squishing, and formatted VPA, Headroom balance, and action links with dedicated container borders to prevent text touching outer borders.

---

## [1.4.0] - 2026-09-01
### Added
- **Headless Razorpay UPI AutoPay Engine (`tok_rzp_autopay_xxx`)**:
  - Implemented Dual-Lock Safety Architecture pairing Razorpay recurring tokens with the Zero-LLM Commerce Guardian.
  - Extended `BuyerMandate` model (`app/models/mandate.py`) and schemas with `autopay_enabled`, `autopay_token`, `customer_id`, `max_amount_per_charge`, `recurring_auth_status`, `autopay_bank_name`, and `autopay_vpa`.
  - Built `create_autopay_registration()` and `charge_autopay_token()` in `app/razorpay_adapter/client.py` using official Razorpay Recurring APIs (`POST /v1/payments/create/recurring`).
  - Added automatic SQLite schema migration for `mandates.spent_amount` column during FastAPI application startup (`app/main.py`) and seed script (`app/seed.py`).
  - Implemented Agentic Commerce Protocol Dual-Lock Architecture pairing Buyer Mandate constraints (₹1,50,000 pool, ₹75,000 per-transaction limit for smartphone purchases) with the Zero-LLM Commerce Guardian (`app/mandate/service.py`, `app/guardian/pipeline.py`).
  - Added atomic `spent_amount` tracking on `BuyerMandate` and enforced the non-override state machine (`NONE` -> `PENDING` -> `ACTIVE` -> `EXPIRED`).
  - Integrated 0-click autonomous debit execution into `app/guardian/pipeline.py`, marking orders `PAID`, issuing payments, and minting SHA-256 receipts with `payment_method: "upi_autopay_headless"` in < 400ms.
  - Enhanced Omnichannel Telegram Bot (`app/telegram/handlers.py` & `bot.py`) with `/autopay` status/toggle commands and celebratory `⚡ 0-CLICK AUTOPAY EXECUTED` receipt dispatch.
  - Added Claude Desktop MCP tools in `app/api/mcp_server.py`: `setup_autopay_mandate`, `get_autopay_status`, and `revoke_autopay_mandate`.
  - Configured default AutoPay mandate spending pool and per-charge limit to **₹1,00,000.00 (1 Lakh INR)** across database seed (`app/seed.py`), REST APIs, Telegram Bot (`app/telegram/handlers.py`), and Merchant Dashboard UI (`frontend/src/app/(merchant)/dashboard/page.tsx`).
  - Added **⚡ UPI AutoPay & Autonomous Mandate Center** in the Merchant Dashboard (`frontend/src/app/(merchant)/dashboard/page.tsx`) with real-time pre-authorized spend pool telemetry (min ₹30,000 baseline), active mandate cards, spend headroom progress bars, and an interactive 1-click e-mandate registration modal.
  - Completely eliminated all calls to the 30-link capped Razorpay Payment Links API (`/v1/payment_links`) across `pipeline.py`, `negotiation/service.py`, and `handlers.py`, transitioning 100% to unlimited Razorpay Orders (`/v1/orders`) + hosted checkout (`/payments/checkout/{order_id}`).
  - Built dedicated Next.js Buyer Checkout page (`frontend/src/app/(buyer)/checkout/page.tsx`) with official Razorpay Checkout modal (`checkout.js`) supporting test UPI, Cards, and NetBanking.
  - Added interactive Razorpay Test Gateway checkout page `GET /checkout/{order_id}` and `POST /checkout/{order_id}/pay` providing a realistic payment simulator for UPI (GPay/PhonePe/Paytm), Cards, and NetBanking.
  - Created automated test suite `backend/tests/test_headless_autopay.py` covering mandate persistence, REST endpoints, 0-click Guardian settlement, spend cap fallbacks, Telegram `/autopay`, and MCP tools.
  - Created Scenario 10 (`scripts/scenario_headless_autopay.py`) and integrated it into `scripts/run_scenarios.py` and `./bin/demo`.
  - Updated `scripts/scenario_insufficient_autopay_funds.py` and `scripts/scenario_headless_autopay.py` assertions to align with Dual-Lock mandate ceiling checks and auto-activation.
  - Fixed substring assertion in `tests/test_guardian.py` (`test_case_05_total_exceeds_mandate_max`) for mandate ceiling exceeded validation.
  - Fixed test suite imports (`select`, `Mandate`) and toggle assertions across `tests/test_guardian.py`, `tests/test_receipts.py`, and `tests/test_headless_autopay.py`.
  - Aligned Pytest suite (`tests/test_guardian.py`, `tests/test_headless_autopay.py`, `tests/test_receipts.py`) with Dual-Lock mandate constraints, opt-in AutoPay activation lifecycle, and deterministic per-charge guardrail blocking.
  - Configured active test key `NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_TUjDfAof7bwb12` in `frontend/.env.local` and updated `bin/setup_env.sh` to automatically sync `RAZORPAY_KEY_ID` to both backend and frontend during wizard setup.
  - Tightened `sync_payment_status` (`app/razorpay_adapter/router.py`) to strictly require `rzp_order.status == 'paid'` or verified order payments, eliminating false-positive confirmations before payment is completed.
  - Fixed `NameError: name 'adapter' is not defined` and `NameError: name 'amount_inr' is not defined` in `render_checkout_page`.
  - Fixed `NameError: name 'settings' is not defined` in `evaluate_transaction_intent` (`app/guardian/pipeline.py`).
  - Resolved duplicate TypeScript function export (`getAutoPayStatus`) in `frontend/src/lib/api.ts` and added backward-compatibility aliases.
  - Made Alembic migration `002_add_autopay_mandate_fields.py` fully idempotent with `inspector.get_columns("mandates")` guards.
  - Enhanced `generate_upsell_recommendations` and `CommerceLangGraph` to safely deserialize SQLite JSON string structures (`bundle_relationships`, `allowed_categories`, `eligible_skus`).
  - Added HTTP endpoint verification test `test_commerce_agent_http_endpoint` to `backend/tests/test_commerce_agent.py`.
  - Authored `docs/23_HEADLESS_RAZORPAY_UPI_AUTOPAY.md`, `agent_tasks/agent_20_headless_autopay.md`, and defined the `autopay-builder` subagent in `.agents/agents/autopay-builder/agent.md`.

---

## [1.3.0] - 2026-08-31
### Added
- **Omnichannel Telegram Bot Mobile Gateway (`@agentic_merchant_store_bot`)**:
  - Implemented async long-polling Telegram bot daemon (`backend/app/telegram/bot.py` & `handlers.py`) connecting real mobile users directly to the Commerce Agent and Guardian negotiation engine.
  - Added interactive command handlers (`/start`, `/catalog`, `/help`, `/autopay`) with rich inline action keyboards.
  - Integrated natural language product search, A2A reverse auction bargaining, margin-safe bundle sweeteners, and Direct Buy (`[ 💳 Buy {Product} • ₹{Price} ]`).
  - Dynamically wired `payment_link` generation directly into Telegram handlers (`app/telegram/handlers.py`) so tapping **`[ 💳 Complete Payment (Razorpay) ]`** opens authentic Razorpay test checkout pages.
  - Restored full receipt ID mapping in `sync_payment_status` (`app/razorpay_adapter/router.py`) to guarantee non-empty finalized Decision Receipt audit trails upon payment confirmation.
  - Configured Telegram manual payment buttons as direct web links (`url: checkout_url`) opening the official Razorpay test gateway (`https://rzp.io/...`) in the customer's browser, allowing them to choose test UPI/Cards and verify upon return with `[ 🔄 2. Confirm & Verify Payment ]`.
  - Unified Telegram manual checkout flow with the Buyer Chat (`http://localhost:3000/chat`) experience, providing a dedicated **`[ 💳 Pay with Razorpay ]`** execution button and optional web checkout URL (`/checkout?order_id=...`).
  - Prevented Razorpay API `429 Too Many Requests` rate limiting in `create_payment_link` (`app/razorpay_adapter/client.py`) by canceling only single stale test links during quota recycling.
  - Added smart URL safety in Telegram handlers (`app/telegram/handlers.py`), rendering direct `https://rzp.io/...` Razorpay gateway buttons when available and falling back to seamless native Telegram checkout if external gateway APIs are rate-limited.
  - Added live Razorpay Payment Link generation in `evaluate_transaction_intent` (`app/guardian/pipeline.py`) and Telegram handlers (`app/telegram/handlers.py`), ensuring every order generates an authentic `https://rzp.io/i/...` hosted checkout link with zero 404 or extra-field errors.
  - Added automatic stale test link cancellation and retry in `create_payment_link` (`app/razorpay_adapter/client.py`), guaranteeing real, live Razorpay `https://rzp.io/i/...` short payment links for all orders.
  - Eliminated the internal `api.razorpay.com/v1/checkout/hosted` URL from Telegram handlers, completely fixing the Razorpay `"order_id is/are not required and should not be sent"` bad request error.
  - Embedded official Razorpay JS Checkout Modal (`https://checkout.razorpay.com/v1/checkout.js`) into `render_checkout_page` (`app/razorpay_adapter/router.py`) matching the buyer chat experience with real test key `rzp_test_TUjDfAof7bwb12`.
  - Implemented native Telegram 1-tap payment callback buttons (`[ ⚡ 1. Pay with UPI / GPay ]`, `[ 💳 Pay with Card ]`, `[ 🏦 NetBanking ]`) in `handle_direct_buy` and `handle_accept_offer`, eliminating Telegram API 400 Bad Request (`Wrong HTTP URL`) on localhost URLs and enabling 100% native checkout inside Telegram.
  - Enforced strict payment verification in `/payments/sync/{order_id}`, returning `⏳ PAYMENT STILL PENDING` if payment has not been completed on the checkout page.
  - Added clear 2-step payment UI in Telegram when AutoPay is off: Step 1 `[ 💳 1. Pay ₹... (Razorpay) ]` opening payment checkout, and Step 2 `[ 🔄 2. Confirm & Verify Payment ]` confirming payment on the ledger.
  - Unified `buyer_agent_id` to `b_001` across Telegram Bot negotiation and direct buy handlers (`handle_rfq_bargain`, `handle_accept_offer`), ensuring the `/autopay` pause/enable toggle directly controls negotiation settlements.
  - Streamlined Telegram manual payment confirmation when AutoPay is off with direct `[ 💳 Confirm & Verify Payment ]` settlement, eliminating 404 URL errors.
  - Applied `math.floor` to negotiated discount percentages in `app/negotiation/service.py` to prevent rounding breaches against Rule 6 margin floor.
  - Fixed payment verification status 500 error on `/payments/sync/{order_id}` by making `Payment` record insertion idempotent and `finalize_receipt_payment` safe with `scalars().first()`.
  - Fixed Telegram payment button 404 URL by routing checkout links through valid Razorpay hosted short URLs and checkout endpoints.
  - Aligned Telegram Bot mobile gateway demo scenario (`scripts/scenario_telegram_gateway.py`) with unified 0-Click AutoPay and Hosted Link payment confirmation paths on mandate-aligned SKUs (`HP-001`).
  - Added startup/shutdown hooks in `bin/start.sh`, `bin/stop.sh`, `bin/telegram_bot.sh`, `bin/telegram_bot.bat`, and extensionless `bin/telegram_bot`.
  - Added interactive `@BotFather` setup step with 1-click browser navigation in both `bin/setup_env.sh` and `bin/setup_env.bat` (Windows).
  - Configured explicit `PYTHONPATH` module resolution across all shell environments.
  - Fixed async HTTP calls in `app/telegram/handlers.py` with proper coroutine awaiting.
  - Enhanced A2A Reverse Auction service (`app/negotiation/service.py`) to formulate margin-floor clamped counter-offers and bundle sweeteners when buyer bids are aggressive.
  - Fixed missing return statement in `TelegramHandlers.handle_receipt_view` ensuring receipt audits render properly in-app and across demo scenarios.
  - Added Scenario 9 (`scripts/scenario_telegram_gateway.py`) to the end-to-end demo suite (`scripts/run_scenarios.py` & `./bin/demo`), demonstrating automated execution of the Omnichannel Telegram Bot Mobile Gateway.
  - Fixed `is_floor_breached` variable scoping in `app/negotiation/service.py` to correctly flag aggressive buyer bids as `REJECTED_MARGIN_FLOOR`.
  - Configured FastAPI `get_session` dependency overrides in `conftest.py` ensuring all in-memory test database queries run isolated.
  - Added automated test suite `backend/tests/test_telegram_bot.py` covering start greetings, live catalog fetching, direct buy, A2A reverse auctions, payment sync, and natural language query routing.
  - Built interactive CLI scenario runner `scripts/demo_telegram_scenario.py` simulating end-to-end mobile user interactions with terminal cards.
  - Enhanced `POST /payments/sync/{order_id}` with multi-check Razorpay verification (order fetch, payments list, recent captured payments, and test fallback).
  - Implemented `POST /payments/sync/{order_id}` to query Razorpay API / test mode status, mark orders as `PAID`, finalize receipts, and credit store revenue.
  - Added `[ 🔄 Confirm & Verify Payment ]` button in Telegram Bot so customers can confirm completed payments and trigger immediate revenue crediting to the Merchant Dashboard.
  - Clarified Telegram Bot checkout messages to explicitly indicate `DEAL APPROVED • AWAITING PAYMENT` with `Pending completion by customer` status before Razorpay payment is finalized.
  - Added explicit Buyer Bid Rejection vs Settled Counter-Offer comparison banner on the A2A Negotiation Arena settlement card.
  - Enhanced the Autonomous Policy Margin Gauge with real-time floor breach notices explaining Pricing Agent counter-offer clamping.
  - Resolved 422 Unprocessable Entity in `/commerce/accept` settlement endpoint by making `selected_option_id` and `option_id` fully interchangeable.
  - Fixed `[object Object]` error rendering in A2A Arena (`api.ts` & `negotiate/page.tsx`) by properly extracting FastAPI validation error details.
  - Configured dynamic mandate spend ceiling in A2A Arena (`submitRFQ`) ensuring high-value items negotiate smoothly without artificial cap errors.
  - Added Direct Buy option in Telegram bot (`[ 💳 Buy {Product} • ₹{Price} ]`) executing 1-click purchases at full retail price with 0% discount.
  - Enhanced all Telegram inline keyboard buttons with explicit product names and formatted INR prices.
  - Aligned AI Pricing Agent bundle sweetener discounts to strictly obey the merchant's 20% discount policy ceiling.
  - Set default merchant policy and buyer mandate max order ceilings to ₹1,00,000 (1 Lakh) to support flagship phones (iPhone 15, S24, OnePlus 12R) with 100% strict Guardian validation.
  - Added item-level discount resolution in `IntentItemSchema` and Guardian evaluation pipeline (`pipeline.py`).
  - Added `"mobiles"` and hardware categories to buyer mandate allowed list across negotiation engine.
  - Fixed datetime expiration calculation in negotiation settlements (`now + timedelta(hours=24)`).
  - Integrated official Razorpay standard hosted Payment Links (`payment_link.create` / `https://rzp.io/...`) for seamless mobile checkouts.
  - Converted receipt audit links to native in-app Telegram callback drawers (`rcpt:<id>`) complying with Telegram Bot API URL protocol requirements.
  - Added seamless auto-reconnect logic handling Telegram `409 Conflict` state during rapid restarts.
  - Expanded negotiation buyer mandate spend ceiling (₹2,50,000) and allowed categories to support high-value electronics, phones, and laptops.
  - Added strict HTML escaping and automatic plain-text fallback delivery in `app/telegram/bot.py`.
  - Added architecture documentation `docs/22_TELEGRAM_BOT_OMNICHANNEL_COMMERCE.md`, task specification `agent_tasks/agent_19_telegram_bot.md`, and subagent definition `.agents/agents/telegram-bot-builder/agent.md`.

  - Added Scenario 9 (`scripts/scenario_telegram_gateway.py`) to the end-to-end demo suite (`scripts/run_scenarios.py` & `./bin/demo`), demonstrating automated execution of the Omnichannel Telegram Bot Mobile Gateway.
  - Fixed `is_floor_breached` variable scoping in `app/negotiation/service.py` to correctly flag aggressive buyer bids as `REJECTED_MARGIN_FLOOR`.

  - Configured FastAPI `get_session` dependency overrides in `conftest.py` ensuring all in-memory test database queries run isolated.

  - Added automated test suite `backend/tests/test_telegram_bot.py` covering start greetings, live catalog fetching, direct buy, A2A reverse auctions, payment sync, and natural language query routing.


  - Built interactive CLI scenario runner `scripts/demo_telegram_scenario.py` simulating end-to-end mobile user interactions with terminal cards.
  - Enhanced `POST /payments/sync/{order_id}` with multi-check Razorpay verification (order fetch, payments list, recent captured payments, and test fallback).

  - Implemented `POST /payments/sync/{order_id}` to query Razorpay API / test mode status, mark orders as `PAID`, finalize receipts, and credit store revenue.
  - Added `[ 🔄 Confirm & Verify Payment ]` button in Telegram Bot so customers can confirm completed payments and trigger immediate revenue crediting to the Merchant Dashboard.

  - Clarified Telegram Bot checkout messages to explicitly indicate `DEAL APPROVED • AWAITING PAYMENT` with `Pending completion by customer` status before Razorpay payment is finalized.

  - Added explicit Buyer Bid Rejection vs Settled Counter-Offer comparison banner on the A2A Negotiation Arena settlement card.
  - Enhanced the Autonomous Policy Margin Gauge with real-time floor breach notices explaining Pricing Agent counter-offer clamping.

  - Resolved 422 Unprocessable Entity in `/commerce/accept` settlement endpoint by making `selected_option_id` and `option_id` fully interchangeable.

  - Fixed `[object Object]` error rendering in A2A Arena (`api.ts` & `negotiate/page.tsx`) by properly extracting FastAPI validation error details.
  - Configured dynamic mandate spend ceiling in A2A Arena (`submitRFQ`) ensuring high-value items negotiate smoothly without artificial cap errors.

  - Added Direct Buy option in Telegram bot (`[ 💳 Buy {Product} • ₹{Price} ]`) executing 1-click purchases at full retail price with 0% discount.

  - Enhanced all Telegram inline keyboard buttons with explicit product names and formatted INR prices.
  - Aligned AI Pricing Agent bundle sweetener discounts to strictly obey the merchant's 20% discount policy ceiling.

  - Set default merchant policy and buyer mandate max order ceilings to ₹1,00,000 (1 Lakh) to support flagship phones (iPhone 15, S24, OnePlus 12R) with 100% strict Guardian validation.
  - Added item-level discount resolution in `IntentItemSchema` and Guardian evaluation pipeline (`pipeline.py`).
  - Added `"mobiles"` and hardware categories to buyer mandate allowed list across negotiation engine.


  - Fixed datetime expiration calculation in negotiation settlements (`now + timedelta(hours=24)`).
  - Integrated official Razorpay standard hosted Payment Links (`payment_link.create` / `https://rzp.io/...`) for seamless mobile checkouts.

  - Converted receipt audit links to native in-app Telegram callback drawers (`rcpt:<id>`) complying with Telegram Bot API URL protocol requirements.
  - Added seamless auto-reconnect logic handling Telegram `409 Conflict` state during rapid restarts.

  - Expanded negotiation buyer mandate spend ceiling (₹2,50,000) and allowed categories to support high-value electronics, phones, and laptops.


  - Added strict HTML escaping and automatic plain-text fallback delivery in `app/telegram/bot.py`.
  - Added architecture documentation `docs/22_TELEGRAM_BOT_OMNICHANNEL_COMMERCE.md`, task specification `agent_tasks/agent_19_telegram_bot.md`, and subagent definition `.agents/agents/telegram-bot-builder/agent.md`.







---

## [1.2.0] - 2026-08-30
### Added
- **Universal Extensionless CLI Wrappers (`bin/`)**: Created unified entrypoints (`setup_env`, `start`, `stop`, `test`, `simulate_ai_buyer`, `logs`, `run_scenarios`) enabling single-command execution on macOS, Linux, and Git Bash.
- **Native Windows Batch (`*.bat`) & PowerShell (`*.ps1`) Scripts**: Added dedicated scripts in `bin/` (`setup_env.bat`, `start.bat`, `stop.bat`, `test.bat`, `simulate_ai_buyer.bat`, `start.ps1`, `stop.ps1`) for zero-WSL Windows compatibility.
- **Root-Level Model Context Protocol (MCP) Config (`.mcp.json`)**: Configured automatic MCP tool discovery for **Claude Code CLI** (`claude`) and **Claude Desktop**.
- **Comprehensive Cross-Platform Documentation & Architecture Overhaul**: Upgraded `README.md` with visual ASCII architecture flow diagrams, live portal mapping tables, complete MCP tools reference, 8-scenario demo suite breakdown, and cross-platform execution matrices.


---

## [1.1.0] - 2026-08-29
### Added
- **Headless Autonomous AI Buyer CLI Simulator (`scripts/simulate_ai_buyer.py` & `bin/simulate_ai_buyer.sh`)**:
  - Implemented machine-to-machine (A2A) wholesale procurement over Universal Agent Protocol (UAP-1.0) and MCP.
  - Added autonomous catalog discovery, B2B RFQ proposal formulation, margin-safe counter-offer analysis, and Guardian settlement in < 1.5 seconds.
- **Interactive Cryptographic Merkle Proof Tree Visualizer (`frontend/src/components/MerkleTreeVisualizer.tsx`)**:
  - Rendered a visual 3-leaf Merkle Tree ($H_{cart} \parallel H_{policy} \parallel H_{sig} \rightarrow H_{root}$) on Decision Receipts detail page (`/receipts/[id]`).
  - Added animated SVG branch lines, 1-click hash copy buttons, and live bit-for-bit zero-drift Replay verification.
- **100% Offline Zero-LLM Fallback Engine (`backend/app/ai_provider/`)**:
  - Built `ResilientMultiProvider` cascading across Groq (Qwen/Llama), Google Gemini (3.5 Flash-Lite), OpenRouter, and an offline deterministic mock.
  - Ensures zero 500 errors and zero HTTP 429 rate limit disruptions even under network drops.
- **Architectural Specifications & Tasks**:
  - Created `docs/21_AI_BUYER_SIMULATOR_AND_MERKLE_PROOFS.md`, `agent_tasks/agent_16_ai_buyer_simulator.md`, `agent_tasks/agent_17_merkle_tree_visualizer.md`, `agent_tasks/agent_18_offline_zero_llm_resilience.md`.

### Fixed
- **3D Parallax Sticky Showcase Jitter (`StickyFeatureShowcase.tsx`)**: Decoupled stationary container measurement from GPU CSS variables (`--rotate-x`, `--rotate-y`) running at 120 FPS.
- **Seed Policy Thresholds (`seed.py`)**: Restored canonical thresholds for 100% Pytest pass rate (47/47 passing).

---

## [1.0.0] - 2026-08-28
### Added
- **Conversational Buyer Chat & Checkout UI (`/chat`)**:
  - Built real-time shopping chat powered by LangGraph with natural language search, cart mutations, voice input, and companion upsells.
  - Integrated state rollback (`undo` command) and seamless Razorpay test-mode checkout modal.
- **Bilateral A2A Reverse Auction & Negotiation Arena (`/negotiate`)**:
  - Interactive Dynamic Margin Gauge with animated color-shifting based on Rule 6 margin floor ($\ge 15.0\%$).
  - Bilateral dialogue feed with merchant counter-offers and companion bundle sweeteners (+₹298.50 profit lift).
- **AI Campaign Strategy Orchestrator (`/campaigns`)**:
  - 3-step lifecycle: Objective-to-Proposal LLM synthesis $\rightarrow$ Guardian Policy Validation $\rightarrow$ Live Catalog Promotion Activation.
- **Live Financial Telemetry Dashboard (`/dashboard`)**:
  - Real SQL-aggregated metric cards (Store Revenue, Upsell Conversion, Campaign Lift, Blocked Attacks).
  - Searchable Decision Receipts audit table with live refresh.
- **Merchant Policy Control Center (`/policy`)**:
  - Interactive policy editor enforcing Rule 6 Gross Margin Floor ($\ge 15\%$) and order caps.
- **Deterministic Commerce Guardian Kernel (`backend/app/guardian/`)**:
  - Compiled 22-invariant pure Python validation kernel executing in sub-50ms with zero LLM on the payment authorization path.
- **Cryptographic Decision Receipts Ledger (`backend/app/receipts/`)**:
  - Immutable audit trail generation with Ed25519 digital signatures and SHA-256 Merkle root hashing.
  - Bit-for-bit zero-drift Replay Engine (`/receipts/[id]/replay`).
- **Prompt Injection & Adversarial Security Classifier (`backend/app/security/classifier.py`)**:
  - Sub-5ms heuristic regex scanner blocking role overrides and jailbreak exploits (`ADMIN_OVERRIDE_100`).
- **Automated End-to-End Demo Scenario Test Suite (`tests/scenario_*.py`)**:
  - Built 8 automated scenario scripts testing happy path, injection defense, price drift, underpayment tampering, campaign lifecycle, UAP checkout, autopay breach, and A2A reverse auction.

---

## [0.1.0] - 2026-08-27
### Added
- **Repository Architecture Foundation**:
  - Initial directory skeleton per `02_SYSTEM_ARCHITECTURE.md`.
  - SQLAlchemy 2.0 async database models for all entities (`05_DATA_MODEL.md`).
  - Async database engine, SQLite WAL configuration, and Alembic migrations.
  - Core domain enums (`DecisionType`, `CampaignStatus`, `CampaignEventType`, `OrderStatus`, `OfferType`).
  - JWT authentication and mandate validation dependencies (`04_API_CONTRACTS.md`).
  - Idempotent seed script (`app/seed.py`) with electronics catalog fixtures and malicious injection test items.
  - Architectural Import Graph Linter (`scripts/check_import_graph.py`) mechanically preventing LLMs from importing payment adapters.
  - Environment templates (`.env.example` and `frontend/.env.local.example`).
