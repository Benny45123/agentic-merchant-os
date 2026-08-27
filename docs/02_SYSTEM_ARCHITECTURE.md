
# 02 — System Architecture

## 1. Architectural Style

One deployable **backend service** (FastAPI/Python), modular internally by domain package. One **frontend** (Next.js/React/TypeScript). One **SQLite** database (SQLAlchemy ORM, migration-ready for Postgres). No microservices, no message bus. Modules communicate via in-process function calls behind interfaces — not network calls — for the MVP. This keeps the system debuggable by one developer and buildable by parallel coding agents against stable contracts.

## 2. Monorepo Layout

```
/frontend                     # Next.js app (buyer + merchant UI)
/backend
  /app
    /core                     # config, db session, shared enums, base models, auth
    /catalog                  # Product, CatalogSnapshot, offers, bundles
    /mandate                  # Mandate model + validation
    /policy                   # MerchantPolicy model + validation
    /guardian                 # Deterministic decision engine (the ONLY path to razorpay_adapter)
    /commerce_agent           # LLM orchestration for buyer-facing chat/cart/checkout-intent
    /campaign                 # Campaign Orchestrator (LLM proposal) + CampaignPolicy validation
    /razorpay_adapter         # Thin wrapper around Razorpay SDK/API
    /receipts                 # Decision Receipt generation, storage, replay
    /security                 # Catalog content sanitizer / injection heuristics
    /api                      # FastAPI routers — the ONLY layer other modules are called from over HTTP
    /ai_provider               # LLM provider abstraction (Gemini/Groq/OpenRouter)
  /tests
/docs
  ARCHITECTURE.pdf
/AGENT_TASKS
  ...
```

## 3. Component Map

```
                         ┌────────────────────┐
                         │      FRONTEND       │
                         │  (Buyer + Merchant) │
                         └──────────┬──────────┘
                                    │ HTTPS/JSON
                                    ▼
                         ┌────────────────────┐
                         │     API LAYER       │  (FastAPI routers)
                         └──────────┬──────────┘
              ┌─────────────────────┼──────────────────────┐
              ▼                     ▼                       ▼
   ┌────────────────────┐ ┌────────────────────┐  ┌─────────────────────┐
   │   COMMERCE AGENT    │ │ CAMPAIGN ORCHESTR.  │  │   CATALOG SERVICE    │
   │ (LLM, proposes only)│ │ (LLM, proposes only)│  │ (trusted+untrusted)  │
   └──────────┬──────────┘ └──────────┬──────────┘  └───────────┬──────────┘
              │  Transaction Intent    │  Campaign Proposal                  │ reads
              └───────────┬────────────┘                                    │
                          ▼                                                 │
                ┌────────────────────┐        reads current state ─────────┘
                │  COMMERCE GUARDIAN  │◄───────────────────┐
                │  (deterministic)    │                     │
                │  - Mandate check    │           ┌────────────────────┐
                │  - Policy check     │           │   MANDATE ENGINE    │
                │  - Price/state      │           └────────────────────┘
                │    revalidation     │           ┌────────────────────┐
                │  - Decision         │◄──────────┤   POLICY ENGINE     │
                └──────────┬──────────┘           └────────────────────┘
                           │ APPROVE
                           ▼
                ┌────────────────────┐
                │  RAZORPAY ADAPTER   │──► Razorpay Test-Mode API
                └──────────┬──────────┘
                           ▼
                ┌────────────────────┐
                │  RECEIPTS / AUDIT   │
                └────────────────────┘
```

## 4. The Golden Rule (enforced structurally, not by convention)

`commerce_agent` and `campaign` packages **must not import** `razorpay_adapter`. Only `guardian` may call `razorpay_adapter`. This is enforced by:

1. Code review checklist in `18_DEFINITION_OF_DONE.md`.
2. A CI lint step (import-graph check, see `14_TEST_PLAN.md`) that fails the build if `commerce_agent` or `campaign` import `razorpay_adapter` directly.

## 5. Data Flow — Buyer Purchase (happy path)

1. Buyer chats with Commerce Agent → Agent calls Catalog Service (read-only) to discover products.
2. Agent proposes a cart; Buyer confirms.
3. Agent constructs a **Transaction Intent** (SKU list, quantities, observed prices, catalog snapshot ids, buyer id, intent id, timestamp) and calls `POST /guardian/evaluate`.
4. Guardian loads the Buyer's active **Mandate**, the **Merchant Policy**, and **re-reads authoritative Catalog state** (ignoring what the Agent observed).
5. Guardian runs deterministic checks (see `07_GUARDIAN_SPEC.md`) and returns `APPROVE | BLOCK | REQUIRE_CONFIRMATION` + reasons.
6. If `APPROVE`: Guardian calls Razorpay Adapter to create an order; frontend opens Razorpay Checkout; on payment success, webhook/verification confirms payment; Guardian finalizes and Receipts module writes the Decision Receipt.
7. If `BLOCK` or `REQUIRE_CONFIRMATION`: no Razorpay call is made; a Decision Receipt is still written (blocked transactions are audited too); UI shows the reason.

## 6. Data Flow — Campaign

1. Merchant states an objective ("increase headphone sales this weekend") to the Campaign Orchestrator.
2. Orchestrator reads Catalog + historical Receipts (read-only) and proposes a **Campaign Proposal** (eligible SKUs, discount %, bundle offers, budget, duration).
3. Proposal is sent to `POST /guardian/evaluate_campaign`, validated against `MerchantPolicy` (max discount, min margin, campaign budget, allowed products, min stock).
4. If approved (or merchant explicitly confirms on `REQUIRE_CONFIRMATION`), the Orchestrator writes bounded, static `CampaignOffer` rows to the Catalog — these are just data, not code.
5. Normal buyer checkout flow picks up `CampaignOffer` rows exactly like any merchant-defined offer — **every individual transaction still goes through the Guardian** and decrements the campaign's remaining budget.
6. A lightweight monitor (invoked on each transaction, no background loop required for MVP) checks remaining campaign budget/margin; if breached, the campaign is flagged `PAUSED` and offers stop applying. A `CampaignEvent` row records the pause and reason.

## 7. Technology Stack

| Layer       | Choice                                                                                                                   | Rationale                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Frontend    | Next.js 14 (App Router), TypeScript, Tailwind                                                                            | Fast to build, good for chat UI + dashboards                                       |
| Backend     | FastAPI (Python 3.11+)                                                                                                   | Async, typed, fast for a solo dev + agents                                         |
| DB          | SQLite + SQLAlchemy 2.0 (async)                                                                                          | Zero infra; ORM abstracts SQL so Postgres swap later is a connection-string change |
| AI Provider | Abstraction interface (`ai_provider/base.py`) with Gemini implementation by default; Groq/OpenRouter adapters optional | Buildathon judges may ask "what if Gemini is down" — swap-ready                   |
| Payments    | Razorpay Python SDK,**test mode only**                                                                             | Official SDK; see`12_RAZORPAY_INTEGRATION.md`                                    |
| Auth        | Simple bearer/session token (buyer_id, merchant_id in JWT)                                                               | Not the focus of the buildathon; minimal but real                                  |
| Testing     | pytest (backend), Playwright or manual script (frontend smoke)                                                           | See`14_TEST_PLAN.md`                                                             |

## 8. Deployment (MVP vs. Future)

**MVP (required):** runs entirely on `localhost` — `uvicorn` for backend, `next dev`/`next start` for frontend, SQLite file on disk. No cloud dependency except Razorpay test-mode API and the chosen LLM API.

**Future (documented, not built):** containerize backend + frontend, deploy to AWS (ECS Fargate or App Runner), swap SQLite → RDS Postgres, add a real cron/scheduler for campaign monitoring, add secrets manager for API keys. This is described in `docs/ARCHITECTURE.pdf` §Deployment but is explicitly out of scope for the 10-day build (see `01_PRODUCT_SPEC.md` §7).

## 9. Environment / Config Boundaries

All secrets (Razorpay key/secret, LLM API key, JWT signing key) live in `.env`, loaded via `core/config.py`, never hardcoded, never logged. `19_ENVIRONMENT_SETUP.md` is authoritative for required variables.

## 10. Why Not Microservices

A single FastAPI service with strict internal module boundaries gives the same "clear ownership per Gemini CLI agent" benefit as microservices (each agent owns a package + its router + its tests) without network latency, service discovery, or deployment complexity that a solo 10-day build cannot absorb. Module boundaries are enforced by directory ownership (`17_MULTI_AGENT_WORKFLOW.md`) and the import-graph lint, not by network isolation.
