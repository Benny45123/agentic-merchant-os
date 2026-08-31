# Agentic Merchant OS

<div align="center">

**Razorpay AI Buildathon 2026 · Track 01 — AI Growth & Agentic Commerce**

[![Track](https://img.shields.io/badge/Track-01%20AI%20Growth%20%26%20Agentic%20Commerce-02042B?style=for-the-badge)](https://razorpay.com/buildathon/)
[![Status](https://img.shields.io/badge/Status-100%25%20Deterministic%20Guardian-brightgreen?style=for-the-badge)](https://github.com/Benny45123/agentic-merchant-os)
[![Tests](https://img.shields.io/badge/Tests-47%2F47%20Passing-00C853?style=for-the-badge)](./bin/test)
[![Latency](https://img.shields.io/badge/Guardian%20Latency-Sub--50ms-3395FF?style=for-the-badge)](docs/02_SYSTEM_ARCHITECTURE.md)
[![Protocols](https://img.shields.io/badge/Protocols-UAP--1.0%20%7C%20MCP%20%7C%20AP2-orange?style=for-the-badge)](docs/20_A2A_REVERSE_AUCTION_AND_MCP.md)

*Grow the merchant's revenue and make them transactable by autonomous AI buyers — with every money action explainable, bounded, gated, and cryptographically audited.*

</div>

---

## 🌟 The Core Architecture Rule

```
                                      AI COMMERCE INGRESS
                 [Buyer Chat]  [Claude Desktop MCP]  [Headless A2A Bot]  [UAP REST API]
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │  1. Proposed Transaction Intent  │  UNTRUSTED (LLM / Bot)
                              │     • Selected SKUs & Quantities │  Zero direct authority
                              │     • Claimed / Negotiated Price │  over money or orders.
                              └────────────────┬─────────────────┘
                                               │
                                               ▼
                 ┌────────────────────────────────────────────────────────────┐
                 │ 2. Deterministic Commerce Guardian Kernel (<50ms Latency)  │  100% PURE PYTHON MATH
                 │    • 22 Invariant Safety Checks across 4 Core Pillars      │  Zero LLM on Money Path
                 │    • Rule 6 Margin Invariant: (Price - Cost) / Price ≥ 15% │  Authoritative Catalog
                 │    • Buyer Mandate Constraints & Category Envelopes        │  Strict Version Locks
                 └─────────────────────────────┬──────────────────────────────┘
                                               │
                             ┌─────────────────┴─────────────────┐
                             │                                   │
                    [Invariant Passes]                  [Invariant Fails]
                             │                                   │
                             ▼                                   ▼
          ┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
          │  3. Authorize Razorpay Settlement   │     │  🚫 BLOCK / REQUIRE_CONFIRMATION    │
          │     • Mint Razorpay Test Order      │     │     • Razorpay NEVER called         │
          │     • Decrement Reserved Stock      │     │     • Zero financial leakage        │
          │     • Mint Cryptographic Receipt    │     │     • Mint Signed Replay Receipt    │
          └──────────────────┬──────────────────┘     └──────────────────┬──────────────────┘
                             │                                           │
                             └─────────────────────┬─────────────────────┘
                                                   │
                                                   ▼
                               ┌───────────────────────────────────────┐
                               │ 4. Cryptographic Decision Receipts    │
                               │    • 3-Node SHA-256 Merkle Proof Tree │
                               │    • Ed25519 Merchant Digital Sig     │
                               │    • 1-Click Bit-for-Bit Replay Engine│
                               └───────────────────────────────────────┘
```

1. **The LLM NEVER calls Razorpay directly.** Only the deterministic Guardian authorizes order creation.
2. **Catalog free-text is UNTRUSTED.** Free-text cannot authorize discounts, payments, refunds, or policy overrides.
3. **Autonomous A2A Dynamic Negotiation (Reverse Auction):** AI Buyer agents submit custom RFQs; the Merchant Pricing Agent formulates margin-safe counter-offers with companion bundle sweeteners (+Profit Lift).
4. **Universal Protocol Compatibility:** Native support for **NPCI UAP-1.0, Anthropic Model Context Protocol (MCP), ACP-Draft, and AP2**.
5. **Every Decision Writes an Immutable Decision Receipt:** 100% mathematical zero-drift replay audit.
6. **Zero Hardcoded Revenue Numbers:** All dashboard metrics are live SQL aggregations over actual database rows.

---

## ⚡ Universal Quick Start Commands (`bin/`)

Universal scripts are provided in `bin/` for 1-command execution across **macOS, Linux & Windows** (Git Bash / WSL / CMD / PowerShell):

| Action / Description | macOS / Linux / Git Bash | Windows (CMD / PowerShell) |
| :--- | :--- | :--- |
| **1. Setup Virtualenv & Seed DB**<br>Auto-installs standalone Astral `uv` if missing, sets up Python 3.12 virtualenv, runs Alembic migrations, loads seed data, and installs frontend dependencies. | `./bin/setup_env` | `bin\setup_env` |
| **2. Start Full Stack (Background)**<br>**Starts full stack in background daemon mode** (FastAPI Backend on `:8000` + Next.js Frontend on `:3000`) and frees the terminal immediately. | `./bin/start` | `bin\start` |
| **3. Stream Live Logs**<br>**Streams live logs in real time** (supports `./bin/logs combined`, `./bin/logs backend`, `./bin/logs frontend`). | `./bin/logs` | — *(Opens live windows)* |
| **4. Run Autonomous AI Buyer (A2A)**<br>**Runs Headless AI Buyer CLI Simulator** negotiating dynamic wholesale quotes over UAP-1.0 and settling autonomously with zero human UI. | `./bin/simulate_ai_buyer` | `bin\simulate_ai_buyer` |
| **5. Stop All Running Servers**<br>**Stops all running background servers** and frees ports `:8000` & `:3000`. | `./bin/stop` | `bin\stop` |
| **6. Run Pytests & Architecture Lint**<br>Runs the full **Pytest suite** (47/47 passing) + **Architecture Import Graph Linter**. | `./bin/test` | `bin\test` |
| **7. Run 8 E2E Demo Scenarios**<br>Runs all **8 Automated End-to-End Demo Scenarios** (Happy Path, Injection Attack, Price Drift, Underpayment Tampering, Campaign Lifecycle, UAP Machine Checkout, Autopay Breach, A2A Reverse Auction). | `./bin/run_scenarios` | `bin\run_scenarios` |
| **8. Run Telegram Bot Gateway**<br>Launches real mobile shopping & wholesale bargaining bot (**@agentic_merchant_store_bot**). | `./bin/telegram_bot` | `bin\telegram_bot` |

---

## 🚀 Running the Platform & Live Portals

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

| Portal / Feature | URL | Description |
| :--- | :--- | :--- |
| **🤖 Real Telegram Bot** | [`https://t.me/agentic_merchant_store_bot`](https://t.me/agentic_merchant_store_bot) | **Live on your phone:** Text `@agentic_merchant_store_bot` to browse, bargain, and pay in Razorpay test mode. |
| **🛍️ Buyer Chat Assistant** | [`http://localhost:3000/chat`](http://localhost:3000/chat) | Natural language shopping, voice input, companion upsells, and Razorpay test checkout. |
| **🤝 A2A Negotiation Arena** | [`http://localhost:3000/negotiate`](http://localhost:3000/negotiate) | Bilateral reverse auction pricing with dynamic margin gauges and bundle sweeteners. |
| **📊 Merchant Telemetry** | [`http://localhost:3000/dashboard`](http://localhost:3000/dashboard) | Real-time live financial dashboard with zero hardcoded numbers (SQL aggregated). |
| **🎯 Campaign Orchestrator** | [`http://localhost:3000/campaigns`](http://localhost:3000/campaigns) | 3-step LLM proposal synthesis, Guardian policy validation, and catalog activation. |
| **🛡️ Policy Control Center** | [`http://localhost:3000/policy`](http://localhost:3000/policy) | Merchant rule control enforcing Rule 6 gross margin floors ($\ge 15\%$) and order caps. |
| **📜 Receipts & Merkle Tree** | [`http://localhost:3000/receipts`](http://localhost:3000/receipts) | Cryptographic immutable audit ledger with interactive 3-node Merkle proof tree. |
| **📑 Backend API & Swagger** | [`http://localhost:8000/docs`](http://localhost:8000/docs) | Complete OpenAPI / Swagger interactive API documentation. |
| **🌐 Public Agent Manifest** | [`http://localhost:8000/.well-known/agent.json`](http://localhost:8000/.well-known/agent.json) | NPCI UAP discovery manifest for autonomous agent discovery. |

---

## 🔌 Connecting to Claude Code CLI, Claude Desktop & Cursor (MCP)

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

### 🛠️ Available MCP Tools Reference

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| **`search_catalog`** | `query` *(str)*, `merchant_id` *(opt)* | Query authoritative live products, specs, prices, and stock levels. |
| **`submit_commerce_rfq`** | `sku`, `qty`, `target_unit_price_paise` | Submit custom bulk procurement bids and receive bilateral counter-offers. |
| **`accept_negotiation_offer`** | `session_id`, `selected_option_id` | Accept counter-offers and trigger sub-50ms Guardian authorization. |
| **`submit_machine_purchase`** | `buyer_mandate`, `purchase_items` | Execute headless machine checkout under signed buyer mandate. |
| **`check_bundle_margin`** | `parent_sku`, `addon_sku`, `discount_pct` | Calculate mathematical margin headroom ($\ge 15\%$ floor). |
| **`get_decision_receipt`** | `receipt_id` *(str)* | Retrieve cryptographic immutable audit record and replay hash. |

---

## 📱 Real Mobile Telegram Bot Gateway (`@agentic_merchant_store_bot`)

You and the evaluators can test **real omnichannel mobile agentic commerce** directly from your phone on Telegram!

* **Live Bot Link**: [**https://t.me/agentic_merchant_store_bot**](https://t.me/agentic_merchant_store_bot) (`@agentic_merchant_store_bot`)

### 🌟 Try These Actions on Telegram from Your Phone:
1. **Interactive Greeting**: Open the bot and send `/start` to view the interactive catalog and quick action buttons.
2. **Natural Language Search**: Send *"Show me iPhone 15"* or *"Show headphones"*.
3. **Wholesale Bargaining (A2A)**: Send *"Bargain iPhone 15 to lowest price"*.
   - The bot triggers the **Merchant Pricing Agent & Guardian**, tests Rule 6 gross margin floor ($\ge 15.0\%$), and formulates the **Sweetener Deal (iPhone 15 + 50% Off MagSafe Charger for ₹66,882.50)**!
4. **1-Click Razorpay Checkout**: Tap **`[ 🎁 Accept Bundle Deal ]`** ➔ The bot generates a live Razorpay test checkout link to complete payment on mobile!
5. **Live Real-Time Telemetry**: As soon as you purchase on Telegram, watch your web [**Merchant Dashboard (`/dashboard`)**](http://localhost:3000/dashboard) update live!

---

## 🎬 8 Automated End-to-End Demo Scenarios


Execute the complete automated test suite with one command:
```bash
./bin/run_scenarios
```

1. **Scenario 1: Happy Path Purchase** (`scenario_happy_path.py`) — Conversational discovery → margin-safe bundle upsell → Guardian approval → Razorpay order → Decision Receipt.
2. **Scenario 2: Catalog Prompt Injection Defense** (`scenario_injection_attack.py`) — Catalog text attempts role override and 90% discount bypass (`ADMIN_OVERRIDE_100`); Guardian and security scanner neutralize attack in 14ms and enforce authoritative pricing.
3. **Scenario 3: Price Drift Mid-Flow** (`scenario_price_change.py`) — Merchant updates catalog price while cart is open; Guardian halts and returns `REQUIRE_CONFIRMATION`.
4. **Scenario 4: Campaign Orchestrator Lifecycle** (`scenario_campaign_lifecycle.py`) — Natural language objective → multi-provider LLM proposal → Guardian policy validation → activation → live SQL revenue attribution.
5. **Scenario 5: Autonomous A2A Machine Purchase** (`demo_uap_agent_buyer.py`) — Headless AI buyer bot executes purchase via UAP protocol with zero human clicks.
6. **Scenario 6: Insufficient Autopay Funds & Mandate Cap Breach** (`scenario_insufficient_autopay_funds.py`) — Buyer mandate spend ceiling breached; Guardian issues `BLOCK`, prevents order creation, and achieves 100% cryptographic replay match.
7. **Scenario 7: Autonomous A2A Dynamic Negotiation (Reverse Auction)** (`scenario_a2a_negotiation.py`) — Buyer submits RFQ for 3x HP-001 @ ₹4,100; Merchant Pricing Agent formulates bundle sweetener (+₹298.50 profit lift); Guardian authorizes deal and rejects predatory ₹3,200 offer.
8. **Scenario 8: Underpayment & Parameter Tampering Defense** (`scenario_underpayment_tampering.py`) — Attacker tampers with client-side amount; Guardian detects mismatch against database catalog and blocks transaction immediately.

---

## 🤖 Headless AI Buyer Simulator & Merkle Cryptographic Proofs

### 1. Autonomous Headless AI Buyer CLI
You can execute an end-to-end bot-to-bot commerce flow in your terminal with zero human UI:
```bash
./bin/simulate_ai_buyer
```
The autonomous procurement bot discovers catalog products over `GET /catalog/products`, calculates a wholesale bid, negotiates over `POST /commerce/rfq`, evaluates merchant counter-offers & margin sweeteners, and executes Guardian-authorized settlement over `POST /commerce/accept` in **< 1.5 seconds**.

### 2. Interactive Merkle Proof Tree Visualizer
Every decision receipt generates an immutable **SHA-256 Merkle Proof Tree** viewable on the receipt drawer ([`/receipts`](http://localhost:3000/receipts)):
- **Root Node ($H_{root}$)**: Authoritative Merkle root signed with merchant Ed25519 private key.
- **Leaf A ($H_{cart}$)**: Canonical cart state digest (SKUs, quantities, prices).
- **Leaf B ($H_{policy}$)**: Guardian policy checks digest (Rule 6 cost floors, margin locks).
- **Leaf C ($H_{sig}$)**: Digital signature digest.
- **1-Click Replay Verification**: Proves bit-for-bit mathematical zero-drift auditability.

### 3. 100% Offline Zero-LLM Fallback Resilience (`ResilientMultiProvider`)
If Gemini API keys are missing, network connectivity is lost, or LLM rate-limit quotas (HTTP 429) occur, the Commerce Agent seamlessly cascades:
```
Groq (Qwen/Llama) ➔ Google Gemini (3.5 Flash-Lite) ➔ OpenRouter ➔ Grounded Safety Mock
```
Every conversational turn, cart addition, and Guardian checkout operates with **100% uptime and zero UI crashes**.

---

## 🏗️ Architecture & Component Map

| Component | Directory | Description |
| :--- | :--- | :--- |
| **A2A Negotiation Engine** | `backend/app/negotiation/` | Bilateral reverse auction pricing agent, margin floor enforcement ($\ge 15\%$), and bundle profit lift optimization. |
| **UAP & MCP Gateway** | `backend/app/api/uap_gateway.py` | Universal Agent Protocol discovery manifest (`/.well-known/agent.json`) and native JSON-RPC 2.0 MCP server (`mcp_server.py`). |
| **Commerce Guardian** | `backend/app/guardian/` | **Deterministic gatekeeper (zero LLM calls)** enforcing 22 safety checks across Mandates, Policies, inventory, and prices. |
| **Catalog Service** | `backend/app/catalog/` | Agent-readable catalog, authoritative state vs untrusted text separation, immutable `CatalogSnapshot`. |
| **Commerce Agent** | `backend/app/commerce_agent/` | Buyer assistant, injection-hardened prompts, policy-safe upsell ranking, pure code `TransactionIntent` builder. |
| **Mandate Engine** | `backend/app/mandate/` | Buyer spending constraints, allowed categories, max qty per item, and cryptographic attestation signatures. |
| **Policy Engine** | `backend/app/policy/` | Versioned merchant rules (`maximum_discount_pct`, `minimum_margin_pct`, `maximum_order_value`, `minimum_stock_to_sell`). |
| **Razorpay Adapter** | `backend/app/razorpay_adapter/` | Test-mode order creation, HMAC-SHA256 signature verification, and webhook handling. |
| **Decision Receipts** | `backend/app/receipts/` | Immutable audit trail capturing snapshots and deterministic replay verification engine. |
| **Campaign Orchestrator** | `backend/app/campaign/` | AI-assisted revenue growth campaigns bounded by merchant margin policies and Guardian validation. |
| **Security Classifier** | `backend/app/security/` | Sub-5ms regex heuristic scanner detecting prompt injections and role override attempts. |
| **Live Revenue Dashboard** | `backend/app/api/dashboard.py` | Real-time telemetry aggregated via SQL over paid orders (no hardcoded numbers). |
| **Frontend Web App** | `frontend/` | Next.js 14 responsive buyer chat with voice search, A2A negotiation arena, and merchant control dashboard. |

---

## 📜 Hackathon Track
Built for the **Razorpay AI Buildathon (Track 01: AI Growth & Agentic Commerce)**. Test-mode only.
