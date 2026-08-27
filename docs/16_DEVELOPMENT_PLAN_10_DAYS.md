
# 16 — 10-Day Development Plan

Assumes ~1 solo developer directing multiple Gemini CLI coding agents in parallel per day, roughly 6-8 focused hours/day. Each day lists: goal, agents active, deliverable, and the gate that must pass before the next day's dependent work starts.

## Day 0 — Foundation & Contracts Freeze

**Goal:** repo skeleton, DB models, seed data, import-graph lint, `.env` template, all contracts in `04_API_CONTRACTS.md`/`05_DATA_MODEL.md` locked.
**Agent:** AGENT_01_FOUNDATION only (others should not start substantial business logic yet, but may scaffold their package + stub tests against the frozen contracts).
**Deliverable:** `alembic`/SQLAlchemy models migrate cleanly, seed script loads default policy + demo catalog + demo buyer/mandate, `pytest` runs (even if mostly empty), import-graph lint script exists and passes on the skeleton.
**Gate:** contracts frozen — any change after this point goes through the Contract Changelog process (`17_MULTI_AGENT_WORKFLOW.md`).

## Day 1 — Catalog + Mandate/Policy Data Layer

**Goal:** working Catalog CRUD + read API; Mandate and Policy models with pure validation functions and full unit test coverage from `14_TEST_PLAN.md` §4 (cases 2-10, 17-18).
**Agents:** AGENT_02_CATALOG, AGENT_04_GUARDIAN (mandate/policy sub-scope only, guardian orchestration comes Day 2-3).
**Deliverable:** `GET/POST/PATCH /catalog/products` working against SQLite; `check_mandate()`/`check_policy()` fully unit tested.
**Gate:** catalog seed data (including the Failure-1 malicious-content product) exists and is queryable.

## Day 2 — Guardian Core + Razorpay Adapter (parallel)

**Goal:** full Guardian pipeline (`07_GUARDIAN_SPEC.md` §2) wired end-to-end against mocked Razorpay; Razorpay Adapter built and smoke-tested against real test-mode API for order creation.
**Agents:** AGENT_04_GUARDIAN, AGENT_05_RAZORPAY (independent — Guardian depends on the adapter's *interface*, defined Day 0, not its finished implementation).
**Deliverable:** `/guardian/evaluate` returns correct decisions for test matrix cases 1, 11-16; `create_order`/`verify_payment` working against real Razorpay test mode.
**Gate:** Guardian → Adapter integration test passes with a real (test-mode) order id.

## Day 3 — Receipts + Commerce Agent (parallel)

**Goal:** Receipt generation wired into every Guardian decision path; Commerce Agent chat loop with catalog search + cart tools functioning (LLM calls working, tool-calling architecture in place).
**Agents:** AGENT_06_RECEIPTS, AGENT_03_COMMERCE_AGENT.
**Deliverable:** every Guardian decision produces a Receipt (including BLOCK); `/agent/chat` can discover products and build a cart via real tool calls.
**Gate:** Receipt replay test passes for at least the happy-path and one BLOCK case.

## Day 4 — Agent→Guardian Integration + Upsell Logic

**Goal:** `/agent/checkout-intent` fully wired (Agent builds intent from real cart → Guardian → decision returned and narrated); upsell/cross-sell recommendation logic implemented and policy-safe.
**Agent:** AGENT_03_COMMERCE_AGENT (leads), AGENT_04_GUARDIAN (support).
**Deliverable:** full buyer happy path works via API calls (no frontend needed yet) — discover → upsell → checkout-intent → APPROVE → order id.
**Gate:** `scenario_happy_path.py` (from `14_TEST_PLAN.md` §7) passes.

## Day 5 — Frontend Buyer Flow + Security Scanner

**Goal:** Next.js buyer chat UI, cart UI, Razorpay Checkout embed, Receipt viewer; catalog security heuristic scanner implemented and unit tested.
**Agents:** AGENT_08_FRONTEND, AGENT_09_SECURITY_TESTING.
**Deliverable:** a human can complete a real purchase end-to-end in the browser; `scan_content()` correctly flags the seeded malicious product.
**Gate:** one full manual browser purchase completes with a real Razorpay test payment.

## Day 6 — Campaign Orchestrator

**Goal:** full campaign propose → Guardian validate → activate → offer application pipeline.
**Agent:** AGENT_07_CAMPAIGN.
**Deliverable:** `scenario_campaign_lifecycle.py` passes; campaign offers are visible in the normal catalog/checkout flow.
**Gate:** a seeded campaign scenario shows budget decrementing correctly across multiple transactions.

## Day 7 — Merchant Frontend + Injection/Failure Demo Hardening

**Goal:** merchant dashboard (policy editor, campaign composer, revenue view, receipt list); both failure scenarios (`15_DEMO_SCENARIOS.md` Beats 5-6) working reliably in the UI, not just via API.
**Agents:** AGENT_08_FRONTEND, AGENT_09_SECURITY_TESTING, AGENT_04_GUARDIAN (bugfix support).
**Deliverable:** merchant can see and act on everything the demo needs; both failure demos reproducible on demand.
**Gate:** `scenario_injection_attack.py` and `scenario_price_change.py` pass, and are also demonstrable manually in the browser.

## Day 8 — Integration Pass + Bug Bash

**Goal:** full system integration test, fix cross-module bugs, verify import-graph lint is still clean, verify Receipt replay passes on all accumulated receipts.
**Agent:** AGENT_10_INTEGRATION (leads), all others on bugfix call.
**Deliverable:** all four `scenario_*.py` scripts green in one run against a fresh seed.
**Gate:** zero known P0/P1 bugs remaining.

## Day 9 — Demo Rehearsal + Real Razorpay Verification + PDF/Docs Polish

**Goal:** run the full `15_DEMO_SCENARIOS.md` script live at least 3 times, complete the manual pre-demo checklist (`14_TEST_PLAN.md` §8), finalize `docs/ARCHITECTURE.pdf`, polish README.
**Agent:** AGENT_10_INTEGRATION + solo developer presenting.
**Deliverable:** demo timing under 6 minutes, backup recording made.
**Gate:** ready to submit.

## Day 10 — Buffer / Submission

**Goal:** absorb any Day 9 surprises, final submission packaging (repo, README, PDF, demo video/recording), rest before presenting.

## Dependency Graph (build order)

```
Day0 Foundation (contracts+db+seed)
   │
   ├──► Day1 Catalog ─────────────┐
   ├──► Day1 Mandate/Policy ──────┤
   │                              ▼
   │                    Day2 Guardian Core ◄──── Day2 Razorpay Adapter
   │                              │
   │                              ▼
   │                    Day3 Receipts
   │                              │
   ├──────────────► Day3 Commerce Agent (needs Catalog)
   │                              │
   │                              ▼
   │                Day4 Agent↔Guardian Integration
   │                              │
   │              ┌───────────────┼───────────────┐
   │              ▼               ▼               ▼
   │      Day5 Frontend    Day5 Security    Day6 Campaign
   │              │               │               │
   │              └───────────────┴───────┬───────┘
   │                                      ▼
   │                       Day7 Merchant UI + Failure Hardening
   │                                      ▼
   │                       Day8 Integration + Bug Bash
   │                                      ▼
   │                       Day9 Rehearsal + PDF
   │                                      ▼
   │                       Day10 Submit
```
