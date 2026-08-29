# Agentic Merchant OS

**Razorpay Buildathon — Track 01: AI Growth & Agentic Commerce**

> Grow the merchant's revenue, and make them sellable to AI buyers — with every money action explainable, bounded, and gated.

---

## 🌟 The Core Architecture Rule

```
AI Buyer Bot / Web Chat → Proposed Transaction Intent → Commerce Guardian (Deterministic) → APPROVE / BLOCK / REQUIRE_CONFIRMATION → Razorpay
```

- **The LLM NEVER calls Razorpay directly.** Only the deterministic Guardian authorizes order creation.
- **Catalog free-text is UNTRUSTED.** Catalog content cannot authorize discounts, payments, refunds, or policy overrides.
- **Autonomous A2A Dynamic Negotiation (Reverse Auction):** AI Buyer agents submit custom RFQs; the Merchant Pricing Agent formulates margin-safe counter-offers with companion bundle sweeteners (+Profit Lift).
- **Universal Protocol Compatibility:** Full support for **UAP-1.0, ACP-Draft, AP2, x402, and Anthropic Model Context Protocol (MCP)**.
- **Every Decision Writes an Immutable Decision Receipt:** 100% mathematical replay audit.
- **Zero Hardcoded Revenue Numbers:** All dashboard metrics are live SQL aggregations over actual database rows.

---

## ⚡ Quick Start Commands (`bin/`)

Executable scripts are provided in `bin/` for single-command operations on macOS / Linux:

| Command | Action |
| :--- | :--- |
| **`./bin/setup_env.sh`** | Auto-installs standalone Astral `uv` if missing, sets up Python 3.12 virtualenv, runs Alembic migrations, loads seed data, and installs frontend dependencies. |
| **`./bin/start.sh`** | **Starts full stack in background daemon mode** (FastAPI Backend on `:8000` + Next.js Frontend on `:3000`) and frees the terminal immediately. |
| **`./bin/logs.sh`** | **Streams live logs in real time** (supports `./bin/logs.sh combined`, `./bin/logs.sh backend`, `./bin/logs.sh frontend`). |
| **`./bin/simulate_ai_buyer.sh`** | **Runs Headless AI Buyer CLI Simulator** negotiating dynamic wholesale quotes over UAP-1.0 and settling autonomously with zero human UI. |
| **`./bin/stop.sh`** | **Stops all running background servers** and frees ports `:8000` & `:3000`. |
| **`./bin/test.sh`** | Runs the full **Pytest suite** (47/47 passing) + **Architecture Import Graph Linter**. |
| **`./bin/run_scenarios.sh`** | Runs all **8 Automated End-to-End Demo Scenarios** (Happy Path, Injection Attack, Price Drift, Underpayment Tampering, Campaign Lifecycle, UAP Machine Checkout, Autopay Breach, A2A Reverse Auction). |

---

## 🚀 Running the Platform

### 1. Launch Backend & Frontend in Background
```bash
./bin/start.sh
```
*Processes run detached in the background so your terminal is immediately ready for other work.*

### 2. View Live Logs Anytime
```bash
# Stream combined live backend & frontend logs:
./bin/logs.sh

# Or stream specific logs:
./bin/logs.sh backend
./bin/logs.sh frontend
```

### 3. Stop Servers
```bash
./bin/stop.sh
```
- **🛍️ Buyer Chat & Shopping Assistant:** [`http://localhost:3000/chat`](http://localhost:3000/chat)
- **🤝 A2A Dynamic Negotiation Arena:** [`http://localhost:3000/negotiate`](http://localhost:3000/negotiate)
- **📊 Merchant Control Plane & Revenue:** [`http://localhost:3000/dashboard`](http://localhost:3000/dashboard)
- **🎯 Campaign Strategy Orchestrator:** [`http://localhost:3000/campaigns`](http://localhost:3000/campaigns)
- **🛡️ Merchant Policy Editor:** [`http://localhost:3000/policy`](http://localhost:3000/policy)
- **📑 Backend API & Swagger Docs:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **🌐 Public Agent Discovery Manifest:** [`http://localhost:8000/.well-known/agent.json`](http://localhost:8000/.well-known/agent.json)

---

## 🔌 Connecting to Claude Desktop, Cursor & External AI Agents

Agentic Merchant OS exposes a native **Model Context Protocol (MCP)** server and **Universal Agent Protocol (UAP-1.0)** gateway. This allows external autonomous agents (like Claude Desktop, Cursor, LangChain, or custom procurement bots) to discover the catalog, negotiate quotes, check margins, and trigger settlements.

---

### 🤖 1. Claude Desktop Integration (1-Click Setup)

To allow **Claude Desktop** to browse your store, negotiate prices, and execute transactions:

#### **macOS Configuration**:
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
*(Replace `<REPO_DIR>` with your actual project path, e.g. `/Users/apple/agentic-merchant-os`)*

#### **Test it in Claude Desktop**:
Ask Claude:
> *"Search for wireless headphones in the store, then submit a bulk procurement RFQ for 3 units at ₹4,100 each."*

---

### 💻 2. Cursor IDE / Windsurf Integration

Add the server to your project's `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agentic-merchant-os": {
      "command": "python",
      "args": ["backend/app/api/mcp_server.py"],
      "env": {
        "MERCHANT_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

---

### 🌐 3. Connecting Custom Python / LangChain / CrewAI Agents

Any autonomous agent can interact over standard HTTP or JSON-RPC 2.0:

#### **A. Zero-Config Manifest Discovery**:
External agents query `/.well-known/agent.json` to auto-discover tools, catalog versions, and protocols:
```python
import httpx

res = httpx.get("http://localhost:8000/.well-known/agent.json")
manifest = res.json()
print("Store Manifest:", manifest["store_name"])
print("Supported Tools:", [t["name"] for t in manifest["tools"]])
```

#### **B. Direct MCP JSON-RPC 2.0 Over HTTP (`POST /mcp`)**:
```python
import httpx

# Example: Search Catalog via MCP JSON-RPC
mcp_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "search_catalog",
        "arguments": {
            "query": "headphones",
            "merchant_id": "m_001"
        }
    }
}
res = httpx.post("http://localhost:8000/mcp", json=mcp_payload)
print("MCP Tool Output:", res.json()["result"]["content"][0]["text"])
```

#### **C. Programmatic A2A RFQ Negotiation**:
```python
# External AI Buyer Agent negotiates volume price
rfq_payload = {
    "buyer_agent_id": "ai_buyer_agent_procure_007",
    "merchant_id": "m_001",
    "buyer_mandate": {
        "buyer_id": "b_001",
        "max_amount": 2000000,
        "max_quantity_per_item": 10,
        "currency": "INR"
    },
    "items": [
        {"sku": "HP-001", "qty": 3, "target_unit_price_paise": 410000}
    ]
}
res = httpx.post("http://localhost:8000/commerce/rfq", json=rfq_payload)
print("Counter-Offers Formulated:", res.json()["counter_offers"])
```

---

### 🛠️ Available MCP Tools Reference

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| **`search_catalog`** | `query` *(str)*, `category` *(opt)* | Query authoritative live products, specs, prices, and available stock. |
| **`submit_commerce_rfq`** | `sku`, `qty`, `target_unit_price_paise` | Submit custom bulk procurement bids and receive bilateral counter-offers. |
| **`accept_negotiation_offer`** | `session_id`, `selected_option_id` | Accept counter-offers and trigger sub-50ms Guardian authorization. |
| **`submit_machine_purchase`** | `buyer_mandate`, `purchase_items` | Execute headless machine-to-machine checkout under signed buyer mandate. |
| **`check_bundle_margin`** | `parent_sku`, `addon_sku`, `discount_pct` | Calculate mathematical margin headroom ($\ge 15\%$ floor). |
| **`get_decision_receipt`** | `receipt_id` *(str)* | Retrieve cryptographic immutable audit record and replay hash. |

---

## 🎬 7 Automated End-to-End Demo Scenarios

Execute the complete automated test suite with one command:
```bash
./bin/run_scenarios.sh
```

1. **Scenario 1: Happy Path Purchase** (`scenario_happy_path.py`) — Conversational discovery → margin-safe bundle upsell → Guardian approval → Razorpay order → Decision Receipt.
2. **Scenario 2: Catalog Prompt Injection Defense** (`scenario_injection_attack.py`) — Catalog text attempts role override and 90% discount bypass; Guardian and security scanner neutralize attack and enforce authoritative pricing.
3. **Scenario 3: Price Drift Mid-Flow** (`scenario_price_change.py`) — Merchant updates catalog price while cart is open; Guardian halts and returns `REQUIRE_CONFIRMATION`.
4. **Scenario 4: Campaign Orchestrator Lifecycle** (`scenario_campaign_lifecycle.py`) — Natural language objective → multi-provider LLM proposal → Guardian policy validation → activation → live SQL revenue attribution.
5. **Scenario 5: Autonomous A2A Machine Purchase** (`demo_uap_agent_buyer.py`) — Headless AI buyer bot executes purchase via UAP protocol with zero human clicks.
6. **Scenario 6: Insufficient Autopay Funds & Mandate Cap Breach** (`scenario_insufficient_autopay_funds.py`) — Buyer mandate spend ceiling breached; Guardian issues `BLOCK`, prevents order creation, and achieves 100% cryptographic replay match.
7. **Scenario 7: Autonomous A2A Dynamic Negotiation (Reverse Auction)** (`scenario_a2a_negotiation.py`) — Buyer submits RFQ for 3x HP-001 @ ₹4,100; Merchant Pricing Agent formulates bundle sweetener (+₹298.50 profit lift); Guardian authorizes deal and rejects predatory ₹3,200 offer.

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

## 🤖 Headless AI Buyer Simulator & Merkle Cryptographic Proofs

### 1. Autonomous Headless AI Buyer CLI
You can execute an end-to-end bot-to-bot commerce flow in your terminal with zero human UI:
```bash
./bin/simulate_ai_buyer.sh
```
The autonomous procurement bot discovers catalog products over `GET /api/uap/catalog`, calculates a wholesale bid, negotiates over `POST /commerce/rfq`, evaluates merchant counter-offers & margin sweeteners, and executes Guardian-authorized settlement over `POST /commerce/accept` in **< 1.5 seconds**.

### 2. Interactive Merkle Proof Tree Visualizer
Every decision receipt generates an immutable **SHA-256 Merkle Proof Tree** viewable on the receipt drawer:
- **Root Node ($H_{root}$)**: Authoritative Merkle root signed with merchant Ed25519 private key.
- **Leaf A ($H_{cart}$)**: Canonical cart state digest (SKUs, quantities, prices).
- **Leaf B ($H_{policy}$)**: Guardian policy checks digest (Rule 6 cost floors, margin locks).
- **Leaf C ($H_{sig}$)**: Digital signature digest.
- **1-Click Replay Verification**: Proves bit-for-bit mathematical zero-drift auditability.

### 3. 100% Offline Zero-LLM Fallback Resilience
If Gemini API keys are missing, network connectivity is lost, or LLM rate-limit quotas (HTTP 429) occur, the Commerce Agent seamlessly degrades to a deterministic, catalog-grounded fallback. Every conversational turn, cart addition, and Guardian checkout operates with **100% reliability and zero UI crashes**.

---

## 📜 Hackathon Track
Built for the **Razorpay AI Buildathon (Track 01: AI Growth & Agentic Commerce)**. Test-mode only.
