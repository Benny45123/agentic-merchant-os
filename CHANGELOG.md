# Changelog

All notable changes to the Agentic Merchant OS platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and adheres to Semantic Versioning.

---

## [1.3.0] - 2026-08-31
### Added
- **Real Mobile Telegram Bot Gateway (`@agentic_merchant_store_bot`)**:
  - Implemented async long-polling Telegram bot daemon (`backend/app/telegram/bot.py` & `handlers.py`) connecting real mobile users directly to the Commerce Agent and Guardian negotiation engine.
  - Added interactive command handlers (`/start`, `/catalog`, `/help`) with rich inline action keyboards.
  - Integrated natural language product search, A2A reverse auction bargaining, margin-safe bundle sweeteners, and 1-click Razorpay test payment links directly in Telegram.
  - Added startup/shutdown hooks in `bin/start.sh`, `bin/stop.sh`, `bin/telegram_bot.sh`, `bin/telegram_bot.bat`, and extensionless `bin/telegram_bot`.
  - Added interactive `@BotFather` setup step with 1-click browser navigation in both `bin/setup_env.sh` and `bin/setup_env.bat` (Windows).
  - Configured explicit `PYTHONPATH` module resolution across all shell environments.
  - Fixed async HTTP calls in `app/telegram/handlers.py` with proper coroutine awaiting.
  - Enhanced A2A Reverse Auction service (`app/negotiation/service.py`) to formulate margin-floor clamped counter-offers and bundle sweeteners when buyer bids are aggressive.
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
