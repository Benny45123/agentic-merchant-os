# Agentic Merchant OS

**Razorpay Buildathon — Track 01: AI Growth & Agentic Commerce**

> Grow the merchant's revenue, and make them sellable to AI buyers — with every money action explainable, bounded, and gated.

---

## 🌟 The Core Architecture Rule

```
AI Agent → Proposed Transaction Intent → Commerce Guardian (Deterministic) → APPROVE / BLOCK / REQUIRE_CONFIRMATION → Razorpay
```

- **The LLM NEVER calls Razorpay directly.** Only the deterministic Guardian authorizes order creation.
- **Catalog free-text is UNTRUSTED.** Catalog content cannot authorize discounts, payments, refunds, or policy overrides.
- **Every Decision Writes a Decision Receipt.** Immutable, replayable cryptographic audit trail.
- **Zero Hardcoded Revenue Numbers.** All dashboard metrics are live SQL aggregations over actual database rows.

---

## ⚡ Quick Start Commands (`bin/`)

Executable scripts are provided in `bin/` for single-command operations on macOS / Linux:

| Command | Action |
| :--- | :--- |
| **`./bin/setup_env.sh`** | Sets up Python virtualenv (`uv` prioritized with manual fallback), runs Alembic migrations, loads seed data, and installs npm dependencies. |
| **`./bin/start.sh`** | **Starts full stack** (FastAPI Backend on `:8000` + Next.js Frontend on `:3000`) with graceful Ctrl+C shutdown. |
| **`./bin/start_backend.sh`** | Starts FastAPI backend server only (`http://localhost:8000`). |
| **`./bin/start_frontend.sh`** | Starts Next.js dev server only (`http://localhost:3000`). |
| **`./bin/test.sh`** | Runs the full **Pytest suite** (Guardian 22-Matrix, Catalog, Receipts, Security, Agent) + **Architecture Import Linter**. |
| **`./bin/run_scenarios.sh`** | Runs all **4 Automated End-to-End Demo Scenarios** (Happy Path, Prompt Injection Defense, Price Drift, Campaign Lifecycle). |

---

## 🚀 Running the Platform

### 1. Launch Backend & Frontend Together
```bash
./bin/start.sh
```
- **Buyer Chat & Shopping Assistant:** [`http://localhost:3000/chat`](http://localhost:3000/chat)
- **Merchant Control Plane & Revenue:** [`http://localhost:3000/dashboard`](http://localhost:3000/dashboard)
- **Campaign Strategy Orchestrator:** [`http://localhost:3000/campaigns`](http://localhost:3000/campaigns)
- **Merchant Policy Editor:** [`http://localhost:3000/policy`](http://localhost:3000/policy)
- **Backend API & Swagger Docs:** [`http://localhost:8000/docs`](http://localhost:8000/docs)

### 2. Run Automated Verification & Architecture Lint
```bash
./bin/test.sh
```

### 3. Run the 4 End-to-End Demo Scenarios
```bash
./bin/run_scenarios.sh
```

---

## 🏗️ Architecture & Component Map

| Component | Directory | Description |
| :--- | :--- | :--- |
| **Catalog Service** | `backend/app/catalog/` | Agent-readable catalog, authoritative state vs untrusted text separation, immutable `CatalogSnapshot`. |
| **Commerce Agent** | `backend/app/commerce_agent/` | Buyer assistant, injection-hardened prompts, policy-safe upsell ranking, pure code `TransactionIntent` builder. |
| **Commerce Guardian** | `backend/app/guardian/` | **Deterministic gatekeeper (zero LLM calls)** enforcing Mandate limits, Policy ceilings, reserve inventory, and price consistency. |
| **Mandate Engine** | `backend/app/mandate/` | Buyer spending constraints, allowed categories, max qty per item. |
| **Policy Engine** | `backend/app/policy/` | Versioned merchant rules (`max_discount_pct`, `min_margin_pct`, `max_order_value`, `minimum_stock_to_sell`). |
| **Razorpay Adapter** | `backend/app/razorpay_adapter/` | Test-mode order creation, HMAC-SHA256 signature verification, and webhook handling. |
| **Decision Receipts** | `backend/app/receipts/` | Immutable audit trail capturing snapshots and deterministic replay verification engine. |
| **Campaign Orchestrator** | `backend/app/campaign/` | AI-assisted revenue growth campaigns bounded by merchant margin policies and Guardian validation. |
| **Security Classifier** | `backend/app/security/` | Sub-5ms regex heuristic scanner detecting prompt injections and role override attempts. |
| **Live Revenue Dashboard** | `backend/app/api/dashboard.py` | Real-time telemetry aggregated via SQL over paid orders (no hardcoded numbers). |
| **Frontend Web App** | `frontend/` | Next.js 14 responsive buyer chat, cart, live check breakdown, and merchant dashboard. |

---

## 📜 License / Hackathon Notice
Built for the **Razorpay Buildathon (Track 01: AI Growth & Agentic Commerce)**. Test-mode only.
