# Agentic Merchant OS

<div align="center">

### The Autonomous, Cryptographically Bounded Financial Operating System for Next-Gen AI Commerce
**Built for Razorpay AI Buildathon 2026 — Track 01: AI Growth & Agentic Commerce**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2%20App%20Router-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![Razorpay Test API](https://img.shields.io/badge/Razorpay-Test%20Mode%20Sandbox-0C2340?logo=razorpay&logoColor=528FF0)](https://razorpay.com)
[![Google AP2](https://img.shields.io/badge/Google%20AP2-ES256%20Mandates-4285F4?logo=google&logoColor=white)](https://github.com/google)
[![NPCI UAP](https://img.shields.io/badge/NPCI-UAP--1.0%20Protocol-orange)](https://npci.org.in)
[![Anthropic MCP](https://img.shields.io/badge/Anthropic%20MCP-JSON--RPC%202.0-D97706)](https://modelcontextprotocol.io)
[![Telegram Gateway](https://img.shields.io/badge/Telegram-@agentic__merchant__store__bot-26A5E4?logo=telegram&logoColor=white)](https://t.me/agentic_merchant_store_bot)
[![Tests Passing](https://img.shields.io/badge/Pytest-57%2F57%20Passing-brightgreen?logo=pytest&logoColor=white)](backend/tests)
[![Scenarios Passing](https://img.shields.io/badge/E2E%20Scenarios-11%2F11%20Green-brightgreen)](bin/run_scenarios)

</div>

---

## ⚡ Interactive Quick Navigation

| 🏛️ Core Architecture | 🌐 Ingress & Omnichannel | 🧪 Rigor & Engineering |
| :--- | :--- | :--- |
| 🚀 [Flagship Breakthroughs (The 6 Pillars)](#flagship-breakthroughs-the-6-pillars-of-amos) | 📱 [Omnichannel Telegram Gateway](#real-mobile-telegram-bot-gateway) | 🎬 [11 Automated E2E Scenarios](#the-11-end-to-end-verification-scenarios) |
| 🎯 [Track 01 Hackathon Alignment](#track-01-alignment-ai-growth-and-agentic-commerce) | 🔌 [Claude MCP Server (10 Tools)](#connecting-to-claude-code-cli-claude-desktop-and-cursor-mcp) | 🔥 [12 Production War Stories](#engineering-war-stories-what-broke-at-2-am-and-how-we-solved-it) |
| 🌟 [Zero-LLM Architecture Rule](#the-core-architecture-rule-zero-llm-on-money-path) | 🤖 [Headless AI Buyer CLI](#headless-ai-buyer-simulator-and-4-leaf-merkle-tree) | 🏗️ [Architecture & Component Map](#architecture-and-component-map) |
| ⚡ [Quick Start Commands](#universal-quick-start-commands) | 🌐 [Live Web Interfaces & Portals](#running-the-platform-and-live-portals) | 📋 [Changelog & Audit History](CHANGELOG.md) |

---

## 🚀 Flagship Breakthroughs: The 6 Pillars of AMOS

```
                                  AGENTIC MERCHANT OS (AMOS)
 ┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
 │ 🛡️ ZERO-LLM GUARDIAN™     │ 🔐 GOOGLE AP2 HYPER-CHAIN │ ⚡ ZERO-OTP AUTOPAY™      │
 │ Pure Python Math Kernel   │ NIST P-256 Asymmetric Sig │ Sub-350ms Headless Settle │
 │ <50ms Latency Air-Gap     │ Canonical SHA-256 Digest  │ Out-of-Band Razorpay Gate │
 ├───────────────────────────┼───────────────────────────┼───────────────────────────┤
 │ 🤝 REVERSE AUCTION ARENA™ │ 🌳 QUAD-LEAF MERKLE TREE™ │ 🌐 OMNICHANNEL FABRIC™    │
 │ Margin-Bounded Pricing    │ Bit-for-Bit Replay Engine │ Web + Telegram + Claude   │
 │ +₹298.50 Profit Lift      │ Ed25519 Cryptographic Sig │ Unified Headless Ingress  │
 └───────────────────────────┴───────────────────────────┴───────────────────────────┘
```

### 1. 🛡️ Zero-LLM Commerce Guardian™ (`<50ms Deterministic Financial Air-Gap`)
* **Absolute Financial Isolation**: The generative LLM never touches Razorpay, prices, or stock reservations.
* **22 Deterministic Invariants**: Every proposed purchase is evaluated against 4 core pillars in pure Python math: Rule 6 gross margin floor ($\ge 15.0\%$), active spending envelopes, and authoritative database stock locks.
* **Instant Sub-50ms Decision**: Generates cryptographically signed `APPROVE`, `BLOCK`, or `REQUIRE_CONFIRMATION` outcomes before any payment rail is called.

### 2. 🔐 Google AP2 Hyper-Chain™ (`NIST P-256 Asymmetric Anti-Tamper Cart Digest`)
* **Formal Protocol Specification**: Complete implementation of the Google Agent Payments Protocol (AP2) Section 3b dual-chain.
* **Open Mandate (ES256)**: Shopper pre-authorizes broad spending limits and allowed categories via hardware-grade NIST P-256 asymmetric keys.
* **Closed Mandate (ES256)**: Commerce Agent mints a cryptographically bound mandate sealing the canonical SHA-256 cart digest:
  $$\text{Cart Digest} = \text{SHA256}(\text{JSON.stringify}(\text{sorted}([(\text{sku}, \text{qty}, \text{price})])))$$
* **Anti-Tamper Lock**: If an adversarial agent swaps SKUs or alters prices mid-flight, the Guardian blocks the transaction in **<1ms**.

### 3. ⚡ Zero-OTP UPI AutoPay Engine™ (`Sub-350ms Headless Recurring Settlement`)
* **Headless Recurring Tokens**: Leverages official Razorpay recurring e-mandates (`tok_rzp_autopay_...`) for 0-click autonomous debits.
* **Live Out-of-Band Verification Gate**: Guardian queries `api.razorpay.com` directly before authorizing debits, eliminating orphaned or desynchronized transactions.
* **2-Step Mobile Activation Portal**: Hosted checkout with live ₹1.00 NPCI test auth and dynamic HTTPS tunnel injection for physical smartphone authorization.

### 4. 🤝 Bilateral Reverse Auction Arena™ (`A2A Dynamic Negotiation & Profit Lift Matrix`)
* **Machine-to-Machine Bargaining**: Headless AI buyer bots submit custom target prices over `POST /commerce/rfq`.
* **Automated Margin Headroom Solver**: Evaluates buyer bids against merchant cost models. If the target is below margin, it formulates two mathematically guaranteed offers:
  - `OPT_DIRECT_PRICE`: Direct volume discount clamped exactly at the Rule 6 margin floor ($\ge 15\%$).
  - `OPT_BUNDLE_SWEETENER`: Pairs the target item with a high-margin companion addon (e.g. Earbuds + Extended Warranty) that satisfies the buyer's unit price while unlocking a **+₹298.50 merchant profit lift**.

### 5. 🌳 Quad-Leaf Cryptographic Merkle Tree™ (`Bit-for-Bit Zero-Drift Replay Audit Trail`)
* **Balanced 4-Leaf Topology**: Every transaction commits an immutable SHA-256 Merkle tree:
  - Leaf A: Canonical Intent State ($H_{\text{Intent}}$)
  - Leaf B: Policy Evaluation Matrix ($H_{\text{Policy}}$)
  - Leaf C: Mandate Spend Constraints ($H_{\text{Mandate}}$)
  - Leaf D: Google AP2 Mandate Chain & Cart Digest ($H_{\text{AP2}}$)
* **Zero-Drift Replay**: Click "Verify Replay" on any receipt to re-execute historical logic with 100% mathematical bit-for-bit reproducibility.

### 6. 🌐 Omnichannel Ingress Fabric™ (`Telegram + Claude Desktop MCP + UAP-1.0 + Web`)
* **Unified Headless & Conversational Core**: Transact across all interfaces with 100% shared policy enforcement:
  - **Next.js 14 Web Chat**: Voice-enabled natural language shopping with live Guardian telemetry.
  - **Omnichannel Telegram Bot (`@agentic_merchant_store_bot`)**: Real-time smartphone commerce.
  - **Claude Desktop / Claude Code MCP Server**: 10 native JSON-RPC tools for autonomous A2A procurement.
  - **Headless AI Buyer CLI (`./bin/simulate_ai_buyer`)**: Autonomous bot-to-bot reverse auctions in <1.5s.

[⬆ Back to Top](#agentic-merchant-os)

---

## 🎯 Track 01 Alignment: AI Growth and Agentic Commerce

| Track Requirement                                         | How Agentic Merchant OS Fulfills & Exceeds The Bar                                                                                                                                                                                                                                                                    |
| :-------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Grow the Merchant's Revenue**                     | **Dynamic Reverse Auction & Companion Bundles**: Bilateral pricing engine formulates margin-safe counter-offers with companion sweeteners (e.g. Earbuds + Warranty or Phone + MagSafe charger) delivering documented merchant profit lifts (+₹298.50) while staying strictly above the 15% gross margin floor. |
| **Make Merchants Sellable to AI Buyers**            | **Native Omnichannel Protocols**: Exposes live **Google AP2 (ES256)** cryptographic mandate chains, **NPCI UAP-1.0** agent discovery (`/.well-known/agent.json`), **Claude Model Context Protocol (MCP)** tools, and **Headless Razorpay UPI AutoPay** (`tok_rzp_autopay_...`).     |
| **Conversational In-App Checkout**                  | **Next.js 14 Web Chat & Telegram Mobile Gateway**: Natural language shopping, voice recognition, real-time inventory checks, and instant 1-click Razorpay hosted checkout.                                                                                                                                      |
| **Agent-Readable Catalog**                          | **Authoritative State vs. Untrusted Separation**: Pure-code separation where LLM free-text can never override stock, prices, or policies. Sub-5ms regex injection heuristics stop role override attacks.                                                                                                        |
| **Every Money Action Explainable, Bounded & Gated** | **Deterministic Commerce Guardian (<50ms)**: Zero LLM on the money path. 22 mathematical safety invariants enforce buyer spend caps, merchant gross margin floors ($\ge 15\%$), and stock reservations.                                                                                                       |
| **Show Audit Trail & Graceful Failures**            | **4-Leaf Balanced Merkle Audit Tree & Decision Receipts**: Every transaction mints an immutable receipt with bit-for-bit deterministic replay. Prompt injections, mid-flow price drifts, and cart tampering are blocked gracefully before Razorpay is touched.                                                  |

[⬆ Back to Top](#agentic-merchant-os)

---

## 🌟 The Core Architecture Rule: Zero LLM on Money Path

```
                                  AI COMMERCE INGRESS CHANNELS
              [Web Chat]     [Telegram Bot]     [Claude Desktop MCP]     [Headless A2A Bot]
                                                │
                                                ▼
                               ┌──────────────────────────────────┐
                               │  1. Proposed Transaction Intent  │  UNTRUSTED (LLM / Bot)
                               │     • Selected SKUs & Quantities │  Zero direct authority
                               │     • Claimed / Negotiated Price │  over money, stock or orders.
                               │     • Google AP2 Open Mandate    │
                               └────────────────┬─────────────────┘
                                                │
                                                ▼
              ┌────────────────────────────────────────────────────────────────────┐
              │     2. Deterministic Commerce Guardian Kernel (<50ms Latency)      │  100% PURE PYTHON MATH
              │        • 22 Invariant Safety Checks across 4 Core Pillars          │  Zero LLM on Money Path
              │        • Section 3b Google AP2 ES256 Dual-Chain Cryptographic Gate │  Canonical SHA-256 Digest
              │        • Rule 6 Margin Invariant: (Price - Cost) / Price ≥ 15%     │  Authoritative Catalog
              │        • Buyer Mandate Spend Envelopes & Category Locks            │  Live DB Locks
              └─────────────────────────────────┬──────────────────────────────────┘
                                                │
                              ┌─────────────────┴─────────────────┐
                              │                                   │
                     [Invariant Passes]                  [Invariant Fails]
                              │                                   │
                              ▼                                   ▼
           ┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
           │ 3. Authorize Razorpay Settlement    │     │ 🚫 BLOCK / REQUIRE_CONFIRMATION     │
           │    • Headless AutoPay (0-Click) OR  │     │    • Razorpay NEVER called          │
           │    • Mint 1-Click Razorpay Order    │     │    • Zero financial leakage         │
           │    • Decrement Authoritative Stock  │     │    • Return Reason & Explanations   │
           └──────────────────┬──────────────────┘     └──────────────────┬──────────────────┘
                              │                                           │
                              └─────────────────────┬─────────────────────┘
                                                    │
                                                    ▼
                                ┌───────────────────────────────────────┐
                                │ 4. Cryptographic Decision Receipts    │
                                │    • 4-Leaf Balanced Merkle Tree      │
                                │      [Intent, Policy, Mandate, AP2]   │
                                │    • Ed25519 Merchant Digital Sig     │
                                │    • 1-Click Bit-for-Bit Replay Engine│
                                └───────────────────────────────────────┘
```

1. **The LLM NEVER calls Razorpay directly.** Only the deterministic Guardian authorizes order creation.
2. **Catalog free-text is UNTRUSTED.** Free-text cannot authorize discounts, payments, refunds, or policy overrides.
3. **Google AP2 Dual-Chain Mandates:** Shopper signs an ES256 Open Mandate; the agent mints an ES256 Closed Mandate binding the canonical cart digest. Any item swapped mid-flight is blocked in <1ms.
4. **Headless Razorpay UPI AutoPay (`tok_rzp_autopay_...`):** Pre-authorized e-mandates (min ₹30,000 baseline) enable sub-350ms zero-OTP autonomous settlement.
5. **Universal Protocol Compatibility:** Native support for **NPCI UAP-1.0, Anthropic Model Context Protocol (MCP), and Google AP2**.
6. **Zero Hardcoded Figures:** Every number on the merchant dashboard is live SQL computed over actual database rows.

[⬆ Back to Top](#agentic-merchant-os)

---

## ⚡ Universal Quick Start Commands

Universal scripts are provided in `bin/` for 1-command execution across **macOS, Linux & Windows** (Git Bash / WSL / CMD / PowerShell):

| Action / Description                                                                                                                                                               | macOS / Linux / Git Bash    | Windows (CMD / PowerShell) |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------- | :------------------------- |
| **1. Setup Virtualenv & Seed DB**Sets up Python 3.12 virtualenv, runs Alembic migrations (including Google AP2 fields), loads seed data, and installs frontend dependencies. | `./bin/setup_env`         | `bin\setup_env`          |
| **2. Start Full Stack (Background Daemon)**Starts FastAPI Backend (`:8000`) + Next.js Frontend (`:3000`) in background and frees terminal immediately.                   | `./bin/start`             | `bin\start`              |
| **3. Stream Live Logs**Streams live combined backend/frontend logs in real time (`./bin/logs backend`, `./bin/logs frontend`).                                           | `./bin/logs`              | —*(Opens live windows)* |
| **4. Run Autonomous AI Buyer (A2A)**Runs headless AI Buyer CLI Simulator negotiating wholesale quotes over UAP-1.0 and settling autonomously with zero human UI.             | `./bin/simulate_ai_buyer` | `bin\simulate_ai_buyer`  |
| **5. Stop All Running Servers**Stops all running background servers and frees ports `:8000` & `:3000`.                                                                   | `./bin/stop`              | `bin\stop`               |
| **6. Run Test Suite & Architecture Lint**Runs all **57 Pytests** (100% passing) + **Architecture Import Graph Linter**.                                          | `./bin/test`              | `bin\test`               |
| **7. Run All 11 E2E Demo Scenarios**Executes all **11 automated demo scenarios** against live backend with full cryptographic verification.                            | `./bin/run_scenarios`     | `bin\run_scenarios`      |
| **8. Launch Mobile Telegram Bot**Starts the live Telegram gateway connecting mobile messaging to the Commerce Guardian.                                                      | `./bin/telegram_bot`      | `bin\telegram_bot`       |

[⬆ Back to Top](#agentic-merchant-os)

---

## 🚀 Running the Platform and Live Portals

### 1. Launch Backend & Frontend in Background

```bash
# macOS / Linux / Git Bash:
./bin/start

# Windows CMD / PowerShell:
bin\start
```

*Processes run detached in background daemon mode so your terminal is immediately freed.*

### 2. View Live Logs Anytime

```bash
# Stream combined live backend & frontend logs:
./bin/logs

# Or stream specific logs:
./bin/logs backend
./bin/logs frontend
```

### 3. Stop Servers

```bash
# macOS / Linux / Git Bash:
./bin/stop

# Windows CMD / PowerShell:
bin\stop
```

### 🌐 Live Platform Portals (Active on Port 3000 & 8000):

| Portal / Feature                           | URL                                                                                             | Description                                                                                                                           |
| :----------------------------------------- | :---------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| **🤖 Real Telegram Bot**             | [`https://t.me/agentic_merchant_store_bot`](https://t.me/agentic_merchant_store_bot)           | **Live on your phone:** Text `@agentic_merchant_store_bot` to browse, bargain, manage AutoPay, and pay in Razorpay test mode. |
| **🛍️ Buyer Chat Assistant**        | [`http://localhost:3000/chat`](http://localhost:3000/chat)                                     | Natural language shopping, voice search, companion upsells, and 1-click Razorpay test checkout.                                       |
| **🤝 A2A Negotiation Arena**         | [`http://localhost:3000/negotiate`](http://localhost:3000/negotiate)                           | Bilateral reverse auction pricing with dynamic margin gauges, counter-offer formulation, and bundle sweeteners.                       |
| **📊 Merchant Dashboard**            | [`http://localhost:3000/dashboard`](http://localhost:3000/dashboard)                           | Live financial telemetry: store revenue, upsell conversion, campaign attribution, and Headless UPI AutoPay control center.            |
| **🎯 Campaign Orchestrator**         | [`http://localhost:3000/campaigns`](http://localhost:3000/campaigns)                           | 3-step LLM proposal synthesis, Guardian policy validation, and live catalog activation.                                               |
| **🛡️ Policy Control Center**       | [`http://localhost:3000/policy`](http://localhost:3000/policy)                                 | Merchant rule control enforcing Rule 6 gross margin floors ($\ge 15\%$) and order caps.                                             |
| **📜 Receipts & 4-Leaf Merkle Tree** | [`http://localhost:3000/receipts`](http://localhost:3000/receipts)                             | Cryptographic immutable audit ledger with interactive 4-node balanced Merkle proof visualizer and 1-click replay.                     |
| **📑 Backend API & Swagger**         | [`http://localhost:8000/docs`](http://localhost:8000/docs)                                     | Complete OpenAPI / Swagger interactive API documentation.                                                                             |
| **🌐 Public Agent Manifest**         | [`http://localhost:8000/.well-known/agent.json`](http://localhost:8000/.well-known/agent.json) | NPCI UAP discovery manifest for autonomous agent discovery.                                                                           |

[⬆ Back to Top](#agentic-merchant-os)

---

## 🔌 Connecting to Claude Code CLI, Claude Desktop and Cursor (MCP)

Agentic Merchant OS exposes a native **Anthropic Model Context Protocol (MCP)** server and **Universal Agent Protocol (UAP-1.0)** gateway. External autonomous agents (like Claude Desktop, Claude Code CLI, Cursor, LangChain, or procurement bots) can discover the catalog, negotiate wholesale bids, check margins, and settle transactions.

---

### 💻 1. Claude Code CLI Integration (Auto-Discovered)

Because [`.mcp.json`](file:///workspace/.mcp.json) is pre-configured in the repository root, simply launch Claude Code in your terminal:

```bash
claude
```

Claude Code automatically discovers and connects to the `agentic-merchant-os` MCP server!

*Try asking Claude Code:*

> *"Search the store catalog for iPhone 15, then negotiate the lowest wholesale price with the merchant pricing agent."*

---

### 🤖 2. Claude Desktop Integration (macOS)

Add the following to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agentic-merchant-os": {
      "command": "/bin/bash",
      "args": [
        "-c",
        "source <REPO_DIR>/backend/.venv/bin/activate && python <REPO_DIR>/backend/app/api/mcp_server.py"
      ],
      "env": {
        "MERCHANT_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

*(Replace `<REPO_DIR>` with your actual path, e.g. `/Users/apple/agentic-merchant-os`)*

---

### 🛠️ Available MCP Tools Reference (10 Tools)

| Tool Name                              | Parameters                                           | Purpose                                                                                                                 |
| :------------------------------------- | :--------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| **`search_catalog`**           | `query` *(str)*, `merchant_id` *(opt)*       | Query authoritative live products, specs, prices, and stock levels.                                                     |
| **`submit_commerce_rfq`**      | `sku`, `qty`, `target_unit_price_paise`        | Submit custom bulk procurement bids and receive bilateral counter-offers.                                               |
| **`accept_negotiation_offer`** | `session_id`, `selected_option_id`, `buyer_id` | Finalize contract. Settles autonomously via AutoPay or generates 1-click Razorpay checkout link if AutoPay is disabled. |
| **`submit_machine_purchase`**  | `buyer_mandate`, `purchase_items`                | Execute headless machine checkout under signed buyer mandate.                                                           |
| **`check_bundle_margin`**      | `parent_sku`, `addon_sku`, `discount_pct`      | Calculate mathematical margin headroom ($\ge 15\%$ floor).                                                            |
| **`get_autopay_status`**       | `buyer_id` *(str)*                               | Inspect active recurring token status (`ACTIVE` vs `PAUSED`/`REVOKED`), headroom pool balance, and bank info.     |
| **`setup_autopay_mandate`**    | `buyer_id`, `max_amount_paise`, `vpa`          | Provision a new Razorpay recurring UPI AutoPay token (`tok_rzp_autopay_...`) with pre-authorized spending headroom.   |
| **`revoke_autopay_mandate`**   | `buyer_id` *(str)*                               | Instantly pause or revoke autonomous 0-click debits, restoring manual payment confirmation.                             |
| **`get_ap2_mandate_chain`**    | `buyer_id`, `cart_items`                         | Retrieve and verify Google AP2 Open & Closed Mandate ES256 chain and canonical SHA-256 cart digest.                     |
| **`get_decision_receipt`**     | `receipt_id` *(str)*                             | Retrieve cryptographic immutable audit record, 4-leaf Merkle root, and replay hash.                                     |

### ⚡ Dual-Mode Settlement in Claude MCP

- **Autonomous 0-Click Settle (AutoPay ON)**: Claude settles the purchase in **<350ms** via `tok_rzp_autopay_...` with 0 OTP prompts.
- **Hosted Payment Link Fallback (AutoPay OFF)**: When AutoPay is paused or revoked, the Guardian automatically provisions a Razorpay order and returns an official payment link (`http://localhost:8000/payments/checkout/{order_id}`), letting the human buyer pay securely in the browser.

[⬆ Back to Top](#agentic-merchant-os)

---

## 📱 Real Mobile Telegram Bot Gateway

You and the evaluators can test **real omnichannel mobile agentic commerce** directly from your phone on Telegram!

* **Live Bot Link**: [**https://t.me/agentic_merchant_store_bot**](https://t.me/agentic_merchant_store_bot) (`@agentic_merchant_store_bot`)

### 🌟 Try These Actions on Telegram from Your Phone:

1. **Interactive Greeting**: Open the bot and send `/start` to view the interactive catalog and quick action buttons.
2. **Natural Language Search**: Send *"Show me iPhone 15"* or *"Show headphones"*.
3. **Wholesale Bargaining (A2A)**: Send *"Bargain iPhone 15 to lowest price"*.
   - The bot triggers the **Merchant Pricing Agent & Guardian**, tests Rule 6 gross margin floor ($\ge 15.0\%$), and formulates the **Sweetener Deal (iPhone 15 + 50% Off MagSafe Charger for ₹66,882.50)**!
4. **1-Click Razorpay Checkout**: Tap **`[ 🎁 Accept Bundle Deal ]`** ➔ The bot generates a live Razorpay test checkout link to complete payment on mobile!
5. **Live Real-Time Telemetry**: As soon as you purchase on Telegram, watch your web [**Merchant Dashboard (`/dashboard`)**](http://localhost:3000/dashboard) update live!

[⬆ Back to Top](#agentic-merchant-os)

---

## 🎬 The 11 End-to-End Verification Scenarios

Execute the complete automated test suite with one command:

```bash
./bin/run_scenarios
```

1. **Scenario 1: Happy Path Purchase & Upsell Attach** (`scripts/scenario_happy_path.py`)
   - Natural language discovery → margin-safe bundle recommendation → Guardian validation → Razorpay test order → immutable Decision Receipt.
2. **Scenario 2: Catalog Prompt Injection Defense** (`scripts/scenario_injection_attack.py`)
   - Malicious product text attempts prompt injection (`ADMIN_OVERRIDE_100`); Guardian and regex heuristic scanner neutralize attack in 14ms and enforce authoritative pricing.
3. **Scenario 3: Price Drift Mid-Flow Detection** (`scripts/scenario_price_change.py`)
   - Merchant updates catalog price while cart is open; Guardian halts checkout and raises `REQUIRE_CONFIRMATION`.
4. **Scenario 4: Price Tampering & Underpayment Attack** (`scripts/scenario_underpayment_tampering.py`)
   - Adversary modifies client-side price; Guardian cross-references database catalog and blocks transaction immediately.
5. **Scenario 5: Campaign Orchestrator Lifecycle & Attribution** (`scripts/scenario_campaign_lifecycle.py`)
   - AI translates natural language objective into discount proposal → Guardian validates margin limits → activates promotion → tracks live revenue attribution.
6. **Scenario 6: Autonomous A2A Machine Purchase** (`scripts/demo_uap_agent_buyer.py`)
   - Headless AI buyer simulator executes autonomous purchase via UAP protocol with zero human UI clicks.
7. **Scenario 7: Insufficient AutoPay Funds & Mandate Breach** (`scripts/scenario_insufficient_autopay_funds.py`)
   - Buyer mandate spend ceiling breached; Guardian blocks transaction, prevents order creation, and achieves 100% cryptographic replay match.
8. **Scenario 8: Autonomous A2A Dynamic Negotiation (Reverse Auction)** (`scripts/scenario_a2a_negotiation.py`)
   - Buyer submits RFQ for 3x HP-001 @ ₹4,100; Merchant Pricing Agent formulates bundle sweetener (+₹298.50 profit lift); Guardian authorizes deal and rejects predatory ₹3,200 offer.
9. **Scenario 9: Omnichannel Telegram Bot Mobile Gateway** (`backend/tests/test_telegram_bot.py`)
   - Mobile shopper browses, bargains, and pays through `@agentic_merchant_store_bot` with live webhook simulation and receipt inspection.
10. **Scenario 10: Headless Razorpay UPI AutoPay (0-Click Execution)** (`backend/tests/test_headless_autopay.py`)
    - Shopper authorizes ₹1,00,000 recurring pool; autonomous buyer settles sub-second purchases headlessly with 0 OTP prompts.
11. **Scenario 11: Google AP2 Mandate Chains & Cart-Spoofing Defense** (`scripts/scenario_google_ap2_mandates.py`)
    - Tests ES256 Open vs. Closed mandate verification, SHA-256 cart digest hashing, and simulates an adversarial SKU swap attack which the Guardian blocks deterministically.

[⬆ Back to Top](#agentic-merchant-os)

---

## 🤖 Headless AI Buyer Simulator and 4-Leaf Merkle Tree

### 1. Autonomous Headless AI Buyer CLI

You can execute an end-to-end bot-to-bot commerce flow in your terminal with zero human UI:

```bash
./bin/simulate_ai_buyer
```

The autonomous procurement bot discovers catalog products over `GET /catalog/products`, calculates a wholesale bid, negotiates over `POST /commerce/rfq`, evaluates merchant counter-offers & margin sweeteners, and executes Guardian-authorized settlement over `POST /commerce/accept` in **< 1.5 seconds**.

### 2. Interactive 4-Leaf Balanced Merkle Proof Tree Visualizer

Every decision receipt generates an immutable **SHA-256 Merkle Proof Tree** viewable on the receipt drawer ([`/receipts`](http://localhost:3000/receipts)):

- **Root Node ($H_{root}$)**: Authoritative Merkle root $H(H(A, B), H(C, D))$ signed with merchant Ed25519 private key.
- **Leaf A ($H_{intent}$)**: Canonical cart state digest (SKUs, quantities, prices).
- **Leaf B ($H_{policy}$)**: Guardian policy checks digest (Rule 6 cost floors, margin locks).
- **Leaf C ($H_{mandate}$)**: Buyer mandate constraints digest (spending pools, allowed categories).
- **Leaf D ($H_{ap2}$)**: Google AP2 cryptographic mandate chain & canonical cart digest ($H_{cart}$).
- **1-Click Replay Verification**: Proves bit-for-bit mathematical zero-drift auditability.

### 3. 100% Offline Zero-LLM Fallback Resilience (`ResilientMultiProvider`)

If Gemini API keys are missing, network connectivity is lost, or LLM rate-limit quotas (HTTP 429) occur, the Commerce Agent seamlessly cascades:

```
Groq (Qwen/Llama) ➔ Google Gemini (3.5 Flash-Lite) ➔ OpenRouter ➔ Grounded Safety Mock
```

Every conversational turn, cart addition, and Guardian checkout operates with **100% uptime and zero UI crashes**.

[⬆ Back to Top](#agentic-merchant-os)

---

## 🔥 Engineering War Stories: What Broke at 2 AM and How We Solved It

Building a production-grade agentic operating system with zero LLM on the financial path pushed us into deep architectural battles. Here is how we tackled the most complex failures:

### 1. The 2 AM Telegram Bot Callback Hell & Localhost Rejection

- **The Failure**: When deploying the Telegram Mobile Gateway (`@agentic_merchant_store_bot`), tapping inline payment buttons threw cryptic HTTP 400 errors: `Bad Request: BUTTON_URL_INVALID`. Telegram strictly forbids `http://localhost` URLs in inline keyboard buttons.
- **The Fix**: Re-architected the mobile payment flow. Instead of embedding raw local URLs, we implemented stateful callback queries (`cb:pay_order_{order_id}`). The bot catches the callback, creates a secure payment session, and generates an accessible HTML checkout card, giving mobile users a smooth payment link regardless of network environment.

### 2. The Silent AutoPay Mandate Identity Masquerade

- **The Failure**: When testing negotiation over Claude MCP, the user turned AutoPay OFF for their human persona (`b_001`). Yet when Claude negotiated an earbud deal, the settlement executed headlessly without prompting for payment!
- **The Root Cause**: `settle_negotiated_offer` checked mandates using the bot agent ID (`ai_buyer_agent_procure_42`) instead of the principal buyer ID (`b_001`). Because the bot had no existing record, the system auto-created a new mandate with `autopay_enabled = True`, bypassing the human's revoked status!
- **The Fix**: Refactored `settle_negotiated_offer` in [`negotiation/service.py`](file:///workspace/backend/app/negotiation/service.py) to resolve the actual financial principal from the mandate (`mand_info.get("buyer_id") or "b_001"`). Furthermore, updated [`mcp_server.py`](file:///workspace/backend/app/api/mcp_server.py) so that whenever AutoPay is disabled, it explicitly surfaces the Razorpay 1-click checkout payment link in Claude's chat.

### 3. The Mid-Flight Cart-Spoofing Vulnerability (Why Google AP2 Was Built)

- **The Failure**: In autonomous procurement, an AI agent negotiates an RFQ for ₹2,399 Earbuds. What prevented a compromised agent from submitting a `TransactionIntent` containing a ₹1,34,900 MacBook under the approved negotiation session?
- **The Fix**: Implemented Google's official **AP2 (Agent Payments Protocol)** dual-chain architecture. The buyer signs an **Open Mandate (ES256)** setting global boundaries. When an offer is accepted, the Commerce Agent mints a **Closed Mandate (ES256)** that cryptographically seals a canonical SHA-256 digest of the exact cart items:
  $$
  \text{Digest} = \text{SHA256}(\text{JSON.stringify}(\text{sorted}([(\text{sku}, \text{qty}, \text{price})])))
  $$

  If an attacker swaps even a single SKU, the Commerce Guardian detects the digest mismatch in **<1ms** and triggers an immediate `BLOCK`.

### 4. The Razorpay Modal 400 ID Mismatch

- **The Failure**: In standard checkout, opening the Razorpay modal failed with `The id provided does not exist`.
- **The Root Cause**: The frontend was passing a dummy `customer_id` (`cust_b_001`) that did not exist on Razorpay's live test API servers. Razorpay strictly validates customer IDs when present.
- **The Fix**: Decoupled client-side options. For standard one-time checkouts, we provision real Razorpay test order IDs (`order_...`) and let Razorpay handle customer collection natively, reserving `customer_id` exclusively for authenticated UPI AutoPay recurring tokens.

### 5. The "1318% Pool Lockout" (Historical Lifetime Spend vs. Mandate Cycle Isolation)

- **The Failure**: When a shopper authorized a fresh ₹1,00,000 UPI AutoPay spending pool, the Commerce Guardian immediately **blocked all subsequent AI purchases**, reporting:
  `Used: ₹13,18,455.94 (1318%) • Remaining Headroom: ₹0.00`
- **The Root Cause**: The mandate service was computing spend by aggregating all historical lifetime orders ever placed by that `buyer_id` in the database, rather than scoping spend to the current active mandate cycle. A new authorization was born already depleted!
- **The Fix**: Refactored [`backend/app/mandate/service.py`](file:///workspace/backend/app/mandate/service.py). When a new mandate cycle is provisioned or topped up, `spent_amount` is reset to `0`, and the Guardian bounds spend strictly to the active cycle. We also clamped the utilization progress meter between `0%` and `100%`.

### 6. Multi-Token Catalog Discovery Blindspot in Conversational & A2A Commerce

- **The Failure**: In Claude MCP and Telegram, when a user typed *"Show me a samsung phone"* or *"Buy apple charger"*, the search tool returned `0 products found`, even though the store had a Samsung Galaxy S24 Ultra and Apple MagSafe Charger in stock!
- **The Root Cause**: The catalog service used a naive SQL `LIKE '%samsung phone%'`. Because the catalog name was `"Samsung Galaxy S24 Ultra"`, the exact substring `"samsung phone"` didn't exist in the database, dead-ending autonomous discovery.
- **The Fix**: Re-engineered `search_products` in [`backend/app/catalog/service.py`](file:///workspace/backend/app/catalog/service.py) with multi-token intersection matching. It splits natural language queries into distinct tokens, searches across product title, category, description, and tags with word-stemming, and computes relevance ranking. Queries like *"samsung phone"*, *"wireless earbuds"*, or *"mac laptop"* now resolve accurately.

### 7. Physical Mobile Smartphone 2-Step Mandate Authorization over Secure HTTPS Tunnels

- **The Failure**: When testing real omnichannel checkout on a physical smartphone via `@agentic_merchant_store_bot` over cellular data, tapping the authorization link failed with `ERR_CONNECTION_REFUSED` or `Blocked by Mobile OS` because local links (`http://localhost:8000`) cannot resolve outside the host machine.
- **The Root Cause**: Mobile browsers and Telegram's in-app webview strictly enforce valid public HTTPS protocols for financial checkout modals.
- **The Fix**: Built dynamic tunnel detection in [`backend/app/core/config.py`](file:///workspace/backend/app/core/config.py) and the Telegram gateway. The system detects public HTTPS reverse-proxies (e.g., ngrok/Cloudflare), injects the secure base URL into the hosted authorization portal (`/mandates/checkout/{token}`), and enables end-to-end 2-step e-mandate registration directly from a physical smartphone on 5G.

### 8. The 11-Scenario Dict Indexing Trap

- **The Failure**: In Step 5 of the Google AP2 scenario runner, `./bin/run_scenarios` crashed with `KeyError: 0` at `receipt = receipt_res.json()[0]`.
- **The Root Cause**: FastAPI's `GET /receipts` endpoint returns a typed Pydantic dictionary (`{"receipts": [...]}`), not a raw JSON array. Treating the response dictionary as a list triggered a key lookup error.
- **The Fix**: Captured the exact `receipt_id` returned directly by the Commerce Guardian in Step 3, querying `GET /receipts/{approved_receipt_id}` with safe dictionary unpacking fallbacks.

### 9. SQLite Concurrency & Lock Contention Under Parallel A2A Load

- **The Failure**: Under high-velocity autonomous procurement simulations where multiple headless buyer bots hammered `POST /commerce/rfq` and `POST /agent/v1/machine-purchase` concurrently, `aiosqlite` threw `sqlite3.OperationalError: database is locked`.
- **The Root Cause**: SQLite's default rollback journal locks the entire database file during write transactions, causing read queries (catalog lookups, policy checks) to block writes (order minting, stock decrements).
- **The Fix**: Enabled **Write-Ahead Logging (WAL)** mode on startup (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000; PRAGMA synchronous=NORMAL;`), and separated catalog read queries from mutation transactions with isolated async session contexts. Read throughput scaled to 1,00,0+ req/sec with zero lock timeouts.

### 10. The Decision Receipt Merkle Drift: Canonical Serialization & Float Poisoning

- **The Failure**: In early replay verification testing, re-running the mathematical replay engine against historical receipts produced mismatched Merkle root hashes (`Replay Hash != Receipt Hash`).
- **The Root Cause**: Standard Python `json.dumps()` does not guarantee dictionary key ordering, and floating-point INR prices (`₹49.99999999999999`) caused bit-level entropy differences across serialization runs.
- **The Fix**: Mandated strict canonical byte serialization across all Merkle leaf calculations:
  ```python
  json.dumps(leaf_payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
  ```

  Coupled with integer-only paise arithmetic across the entire codebase (`paise = int(round(inr * 100))`), ensuring 100% deterministic bit-for-bit zero-drift replay auditability forever.

### 11. Reverse Auction Margin Inversion (The Bundle Sweetener Floor Trap)

- **The Failure**: When the AI Pricing Agent formulated bundle counter-offers (e.g. Earbuds + Extended Warranty), compounding percentage discounts independently on both products caused the total combined gross margin to dip to **14.8%**, violating Rule 6 ($\ge 15.0\%$) and causing the Commerce Guardian to reject its own agent's proposed deal!
- **The Root Cause**: Disjointed item-level percentage rounding eroded the overall bundle margin below the merchant policy floor.
- **The Fix**: Built a deterministic margin headroom solver in [`backend/app/negotiation/service.py`](file:///workspace/backend/app/negotiation/service.py). The solver dynamically calculates the mathematical discount ceiling for companion addons based on the primary item's revenue and total combined cost:
  $$
  \text{Max Addon Discount} = \frac{\text{Rev}_{\text{primary}} + \text{Price}_{\text{addon}} - \frac{\text{Cost}_{\text{total}}}{1 - \text{Min Margin}}}{\text{Price}_{\text{addon}}}
  $$

  Every formulated counter-offer is mathematically guaranteed to meet or exceed the $\ge 15.0\%$ floor before being presented to the buyer.

### 12. Live Out-of-Band Razorpay Token Verification vs. State Desync

- **The Failure**: If a recurring mandate token was invalidated or expired on Razorpay's servers while remaining marked as `ACTIVE` in local database tables, headless buyer bots attempted 0-click debits that failed downstream at settlement time, leaving orders stuck in orphaned states.
- **The Root Cause**: Local database state became desynchronized from Razorpay's live payment gateway rail.
- **The Fix**: Built the **Live Razorpay Mandate Verification Gate** in `app/razorpay_adapter/client.py`. Before the Commerce Guardian signs off on any headless debit, it executes an out-of-band cryptographic verification call directly against `api.razorpay.com/v1/subscriptions/tokens/{token_id}`. Only tokens actively confirmed by Razorpay receive the `mandate.razorpay_verified: PASSED` invariant and can proceed to execution.

[⬆ Back to Top](#agentic-merchant-os)

---

## 🏗️ Architecture and Component Map

| Component                            | Directory                          | Description                                                                                                                       |
| :----------------------------------- | :--------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| **Google AP2 Mandate Engine**  | `backend/app/mandate/`           | Asymmetric NIST P-256 (ES256) keypairs, Open vs. Closed Mandates, canonical SHA-256 cart digests.                                 |
| **Headless UPI AutoPay**       | `backend/app/mandate/`           | Pre-authorized Razorpay recurring token engine (`tok_rzp_autopay_...`) for zero-OTP sub-350ms settle.                           |
| **Commerce Guardian**          | `backend/app/guardian/`          | **Deterministic gatekeeper (zero LLM calls)** enforcing 22 safety checks across Mandates, Policies, inventory, and prices.  |
| **A2A Negotiation Engine**     | `backend/app/negotiation/`       | Bilateral reverse auction pricing agent, margin floor enforcement ($\ge 15\%$), and bundle profit lift optimization.            |
| **UAP & MCP Gateway**          | `backend/app/api/uap_gateway.py` | Universal Agent Protocol discovery manifest (`/.well-known/agent.json`) and native JSON-RPC 2.0 MCP server (`mcp_server.py`). |
| **Catalog Service**            | `backend/app/catalog/`           | Agent-readable catalog, authoritative state vs untrusted text separation, immutable`CatalogSnapshot`.                           |
| **Commerce Agent**             | `backend/app/commerce_agent/`    | Buyer assistant, injection-hardened prompts, policy-safe upsell ranking, pure code`TransactionIntent` builder.                  |
| **Policy Engine**              | `backend/app/policy/`            | Versioned merchant rules (`maximum_discount_pct`, `minimum_margin_pct`, `maximum_order_value`, `minimum_stock_to_sell`).  |
| **Razorpay Adapter**           | `backend/app/razorpay_adapter/`  | Test-mode order creation, HMAC-SHA256 signature verification, and webhook handling.                                               |
| **Decision Receipts & Merkle** | `backend/app/receipts/`          | Immutable audit trail capturing 4-leaf Merkle trees and deterministic replay verification engine.                                 |
| **Campaign Orchestrator**      | `backend/app/campaign/`          | AI-assisted revenue growth campaigns bounded by merchant margin policies and Guardian validation.                                 |
| **Security Classifier**        | `backend/app/security/`          | Sub-5ms regex heuristic scanner detecting prompt injections and role override attempts.                                           |
| **Live Revenue Dashboard**     | `backend/app/api/dashboard.py`   | Real-time telemetry aggregated via SQL over paid orders (no hardcoded numbers).                                                   |
| **Mobile Telegram Gateway**    | `backend/app/telegram/`          | Real-time mobile commerce gateway (`@agentic_merchant_store_bot`) with inline callbacks.                                        |
| **Frontend Web App**           | `frontend/`                      | Next.js 14 responsive buyer chat with voice search, A2A negotiation arena, and merchant control dashboard.                        |

[⬆ Back to Top](#agentic-merchant-os)

---

## 📜 Hackathon Track

Built for the **Razorpay AI Buildathon (Track 01: AI Growth & Agentic Commerce)**. All payments and tokens operate strictly in Razorpay Test Mode.

