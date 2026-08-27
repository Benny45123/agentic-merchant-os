
# 01 — Product Spec: Agentic Merchant OS

**Track:** Razorpay Buildathon Track 01 — AI Growth & Agentic Commerce
**Objective:** Grow merchant revenue AND make the merchant transactable by an AI buyer, end to end, with every money action explainable, bounded, and gated.

This document is the single source of truth for **what** we are building and **why**. All other documents describe **how**. If any other document conflicts with this one, this document wins unless explicitly superseded by `02_SYSTEM_ARCHITECTURE.md`.

---

## 1. One-Line Pitch

A merchant catalog that an AI buyer can shop, backed by a deterministic **Commerce Guardian** that gates every money action against buyer mandates and merchant policy — plus a **Campaign Orchestrator** that uses the same Guardian to safely grow revenue through AI-generated, policy-bounded promotions.

## 2. Problem Statement

Two converging trends create Track 01's problem:

1. Agent-to-agent commerce (NPCI UAP, ACP, AP2, x402) means merchants will increasingly be shopped by AI agents, not humans clicking buttons. Merchants need to be **agent-readable and agent-transactable**.
2. Merchants adopting agentic checkout need assurance that an LLM cannot be tricked — via prompt injection, hallucination, or stale data — into authorizing a transaction it shouldn't. Trust requires a **deterministic control plane**, not "the LLM promises to behave."

Agentic Merchant OS solves both: it makes a merchant transactable by an AI buyer, and it uses AI to grow revenue (upsell/cross-sell + campaigns), while keeping every rupee movement behind a non-LLM gate.

## 3. Both Sides of Track 01

**Side A — Merchant transactable by an AI buyer:**

- Agent-readable catalog (structured, machine-consumable)
- Conversational commerce agent that discovers, compares, and carts products
- Guardian-gated checkout against an explicit buyer mandate
- Razorpay test-mode payment completion
- Full decision receipt per transaction

**Side B — AI grows merchant revenue:**

- Contextual upsell/cross-sell during cart construction (Guardian-gated, margin-safe)
- Campaign Orchestrator: merchant states an objective in natural language, AI proposes a bounded campaign, Guardian/Policy Engine validates it, and real transactions during the campaign are measured from actual receipt data

Both sides run through **one Guardian**, **one policy model**, **one receipt system**. This is not two demos glued together.

## 4. Core Non-Negotiable Principle

> The LLM proposes. The Guardian decides. The Guardian is deterministic. Nothing reaches Razorpay without passing the Guardian.

Catalog content (descriptions, reviews, marketing copy) is **data**, never **authorization**. A buyer's mandate and a merchant's policy are the only sources of authorization, and both are structured, non-LLM-authored records.

## 5. Primary User Roles

| Role                            | Description                                                                                                                                                             |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Buyer**                 | A human or an AI shopping agent acting on a human's behalf, operating under a declared Mandate.                                                                         |
| **Merchant**              | The store owner. Defines catalog, policies, and campaign objectives.                                                                                                    |
| **Commerce Agent**        | The LLM-backed assistant that talks to the Buyer, searches the catalog, builds carts, proposes upsells, and proposes Transaction Intents. Never touches money directly. |
| **Campaign Orchestrator** | The LLM-backed assistant that talks to the Merchant, proposes bounded campaigns from an objective. Never touches money directly.                                        |
| **Commerce Guardian**     | Deterministic policy engine. The only component allowed to authorize a path to Razorpay.                                                                                |

## 6. Scope Tiers

### MUST HAVE (demo depends on these)

- Agent-readable catalog with trusted/untrusted field separation
- Conversational discovery → cart → checkout intent (Commerce Agent)
- Mandate Engine (structured buyer authorization)
- Merchant Policy Engine (structured merchant constraints)
- Commerce Guardian with deterministic APPROVE / BLOCK / REQUIRE_CONFIRMATION
- Price & inventory revalidation before payment
- Razorpay test-mode order creation, checkout, payment verification, webhook handling
- Decision Receipt generated for every money action (approved or blocked)
- Catalog prompt-injection defense (architectural: catalog text cannot become an authorization input) + at least one working attack demo
- One working upsell/cross-sell flow
- Campaign Orchestrator: objective → proposal → Guardian/Policy validation → bounded campaign applied to catalog → real transactions measured
- Two failure demos (malicious catalog content; price-change mid-flow)
- Revenue dashboard sourced from real Order/Receipt rows (no hardcoded numbers)

### SHOULD HAVE (build if time allows after MUST HAVE is solid)

- Refund flow (test-mode)
- Multiple concurrent campaigns with shared budget pool
- Bundle-aware recommendations (not just single-item upsell)
- Campaign auto-pause on budget/margin breach mid-flight
- Admin UI for merchant policy editing
- Idempotency key handling on all Razorpay calls
- Structured suspicious-content flag surfaced in merchant dashboard

### STRETCH (only after all MUST HAVE + SHOULD HAVE are demo-solid)

- Signed/cryptographic mandates (Ed25519) — data model must not preclude this later
- Multi-merchant marketplace view
- Real AP2/ACP-style external agent protocol adapter
- A/B testing of campaign offers
- PostgreSQL migration
- AWS deployment

## 7. Explicit "Do Not Build" (see `18_DEFINITION_OF_DONE.md` for enforcement)

- No Kubernetes, Kafka, Redis, event buses, or vector DB
- No microservice split — one backend service, modular internally
- No live/production Razorpay mode
- No autonomous unbounded campaign loop — every campaign action is proposed, validated, then applied as bounded static config
- No LLM call in the Guardian's decision path
- No fake/hardcoded revenue metrics anywhere in the UI

## 8. Success Criteria (Demo-Level)

1. A judge can watch an AI buyer discover a product, get upsold, checkout, and pay via Razorpay test mode — with a receipt shown at the end.
2. A judge can watch a catalog-injection attack fail with a clear Guardian explanation.
3. A judge can watch a price change get caught before payment.
4. A judge can watch a merchant type a campaign objective and see a bounded, policy-checked campaign go live and affect real transactions.
5. Every number on the "revenue impact" screen is traceable to a real Receipt row.

## 9. Glossary

See `05_DATA_MODEL.md` for full field-level definitions. Key terms:

- **Transaction Intent**: structured proposal from Commerce Agent to Guardian, never a payment itself.
- **Mandate**: buyer's structured spending authorization.
- **Policy**: merchant's structured commerce constraints.
- **Decision Receipt**: immutable, replayable record of a Guardian decision and its outcome.
- **Catalog Snapshot**: versioned, timestamped product state used to detect drift between discovery and payment.
