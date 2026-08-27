
# 18 — Definition of Done

A feature, component, or the whole project is "done" only when every applicable item below is checked. This file is the enforcement mechanism for the architectural rules in the original brief.

## Per-Component Definition of Done

- [ ] Matches its section in `03_COMPONENT_ARCHITECTURE.md` exactly (responsibilities, "must not" list respected)
- [ ] Public functions/endpoints match `04_API_CONTRACTS.md` / `05_DATA_MODEL.md` exactly (no undocumented fields, no missing fields)
- [ ] Import-graph lint passes with this component included
- [ ] All test cases listed for this component in `14_TEST_PLAN.md` pass
- [ ] No secrets, API keys, or credentials committed
- [ ] Only files inside the component's owned directory were modified (or any exception is flagged `[CONTRACT-CHANGE]`/`[SCHEMA-CHANGE]` per `17_MULTI_AGENT_WORKFLOW.md`)

## Guardian-Specific Definition of Done (highest bar — this is the trust boundary)

- [ ] Zero LLM calls anywhere in `app/guardian`
- [ ] Zero reads of any field marked UNTRUSTED in `09_CATALOG_SECURITY.md` §2
- [ ] Every one of the 22 test matrix cases in `14_TEST_PLAN.md` §4 passes
- [ ] Every decision (APPROVE, BLOCK, REQUIRE_CONFIRMATION) writes exactly one Receipt
- [ ] Receipt replay produces an identical decision for every seeded/generated receipt

## Project-Level Definition of Done (must all be true before Day 9 rehearsal)

- [ ] Rule 1: no code path allows LLM output to directly authorize a Razorpay call — verified by import-graph lint + manual code review of `app/guardian`
- [ ] Rule 2: catalog free-text fields are never read by `app/guardian`, `app/mandate`, or `app/policy` — verified by grep audit (`grep -rn "description" app/guardian app/mandate app/policy` should return zero decision-relevant hits)
- [ ] Rule 3: `git grep "razorpay_adapter"` shows imports only inside `app/guardian` and `app/razorpay_adapter` itself
- [ ] Rule 4: price/inventory revalidation test cases (11-14 in `14_TEST_PLAN.md` §4) pass
- [ ] Rule 5: campaign actions cannot apply without a Guardian `APPROVE`/confirmed decision — verified by test case 20-22
- [ ] Rule 6: `git grep` for hardcoded revenue numbers in frontend/dashboard code returns nothing outside of test fixtures — all dashboard values traced to a live SQL aggregation
- [ ] Rule 7: no Kubernetes/Kafka/Redis/event-bus/vector-DB dependency in `requirements.txt`/`package.json`
- [ ] Rule 8: every package listed in `03_COMPONENT_ARCHITECTURE.md` has a non-empty test directory with passing tests
- [ ] Rule 9: every `GuardianDecision` has a corresponding `Receipt` — verified by a SQL check (`COUNT(GuardianDecision) == COUNT(Receipt)` for money-relevant decisions)
- [ ] Rule 10: `docker-compose down && docker-compose up` (or equivalent local run) works with no AWS credentials configured
- [ ] All four `scenario_*.py` end-to-end scripts pass against a fresh seeded DB
- [ ] Both required failure demos (`15_DEMO_SCENARIOS.md` Beats 5-6) reproduce reliably, 3/3 rehearsal attempts
- [ ] `docs/ARCHITECTURE.pdf` exists, matches the current architecture, under ~10 pages
- [ ] `20_README.md` lets a stranger clone and run the project in under 15 minutes

## Explicit Anti-Patterns That Fail Review

- An endpoint that lets the frontend set the Razorpay order amount directly
- A Guardian check implemented as "ask the LLM if this looks okay"
- A dashboard number computed at seed time and never refreshed
- A campaign that applies an offer to the catalog before a Guardian `APPROVE`
- Any `try/except: pass` around a Guardian check (silent failures cannot occur in the money-decision path — a failed check must resolve to `BLOCK`, never a swallowed exception that defaults to APPROVE)
