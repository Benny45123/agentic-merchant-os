# AGENT_10_INTEGRATION

## Objective

Own full-system integration: resolve cross-module bugs, keep the import-graph lint and receipt-replay checks green, build and maintain the end-to-end demo scenario scripts, and sign off against `18_DEFINITION_OF_DONE.md` before demo rehearsal.

## Scope

- `scripts/run_scenarios.py` and the four scenario scripts: `scenario_happy_path.py`, `scenario_injection_attack.py`, `scenario_price_change.py`, `scenario_campaign_lifecycle.py` (per `14_TEST_PLAN.md` §7)
- Cross-module bugfixes (minimal, scoped changes inside other agents' packages when a genuine integration bug is found — not redesigns)
- Final `18_DEFINITION_OF_DONE.md` checklist verification
- Coordinating merge order per `17_MULTI_AGENT_WORKFLOW.md` §3

## Files/Directories Owned

`scripts/` (except `check_import_graph.py`, owned by AGENT_01 — coordinate changes), plus narrowly-scoped bugfix commits across `backend/app/*` as needed, clearly flagged in commit messages as `[INTEGRATION-FIX: <package>]`.

## Dependencies

All other agents' work must be substantially complete (per the Day 8 gate in `16_DEVELOPMENT_PLAN_10_DAYS.md`) before this task can fully complete, though scenario script scaffolding can begin earlier against stubs.

## Implementation Requirements

1. Build each scenario script as a sequence of real HTTP calls (via `httpx`) against a running local stack, asserting on responses at each step — not a narrative description.
2. `scenario_happy_path.py`: discover → upsell → checkout-intent → APPROVE → payment → receipt, all assertions passing.
3. `scenario_injection_attack.py`: reproduces `15_DEMO_SCENARIOS.md` Beat 5 exactly — malicious catalog content, Guardian BLOCK, receipt with `security.catalog_content_flagged: true`.
4. `scenario_price_change.py`: reproduces Beat 6 — price mutated mid-flow, Guardian `REQUIRE_CONFIRMATION`, both prices visible in the check detail.
5. `scenario_campaign_lifecycle.py`: propose → Guardian validate → activate → transact → verify budget/revenue numbers.
6. Any bugfix touching another agent's package must be minimal and scoped to the specific integration bug — do not refactor or redesign under this task.
7. Any change to `04_API_CONTRACTS.md`/`05_DATA_MODEL.md` discovered to be necessary must be flagged `[CONTRACT-CHANGE]` with a changelog entry, never made silently.

## Tests Required

All four scenario scripts, runnable via `python scripts/run_scenarios.py`, each independently and as a full suite against a freshly seeded DB.

## Acceptance Criteria

- [ ] All four scenario scripts pass in one run against a fresh seed
- [ ] `scripts/check_import_graph.py` passes
- [ ] Receipt replay passes for every receipt generated during a full scenario run
- [ ] Every checkbox in `18_DEFINITION_OF_DONE.md`'s project-level section is verified true (or explicitly reported as not-yet-true with a clear reason)
- [ ] Manual pre-demo checklist (`14_TEST_PLAN.md` §8) completed at least once

## Must NOT Modify

Any package's core design/architecture — only narrowly-scoped, clearly-flagged bugfixes are permitted outside `scripts/`.
