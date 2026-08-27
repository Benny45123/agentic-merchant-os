
# AGENT_09_SECURITY_TESTING

## Objective

Build the catalog content security scanner (defense-in-depth heuristic) and the full injection/threat-model test fixture set. This is a **builder** role — implementing defenses and their tests. (Adversarial red-teaming of the finished system is a separate exercise; see `.gemini/agents/security-auditor.md` / `.agents/agents/security-auditor/agent.md`, which attacks what this task builds — it must not be run as a substitute for this task.)

## Scope

- `app/security/classifier.py`: `scan_content(text: str) -> ContentScanResult` per `09_CATALOG_SECURITY.md` §3
- Fixture catalog entries with injected instructions (description injection, review injection, discount-instruction injection) for use across the test suite
- ≥10 benign catalog copy samples proving no false-positives
- Test cases for `13_THREAT_MODEL.md` items 1, 2, 3, 8, 14 (the injection/hallucination/malicious-content family)

## Files/Directories Owned

`backend/app/security/`, plus shared test fixtures (coordinate location with existing per-package test directories rather than duplicating — e.g. a `tests/fixtures/malicious_catalog.py` importable by `commerce_agent`, `guardian`, and `catalog` test suites).

## Dependencies

`app/core` (AGENT_01), `app/catalog` (AGENT_02, to attach `suspicious_content_flag` to seeded fixture products).

## Interfaces/Contracts

```python
def scan_content(text: str) -> ContentScanResult:  # {flagged: bool, matched_categories: list[str]}
    """Pure function, no I/O, must run in <5ms for demo-scale text."""
```

## Implementation Requirements

1. This scanner is **informational only** — it must never be wired into any Guardian APPROVE/BLOCK decision as an authoritative signal. It sets `Product.suspicious_content_flag` and surfaces to the merchant dashboard and Receipt display; the real defense is structural (Guardian never reads untrusted fields), documented in `09_CATALOG_SECURITY.md` §1.
2. Build the exact fixture set demonstrated in `15_DEMO_SCENARIOS.md` Beat 5 — this fixture is load-bearing for the live demo, not just for CI.
3. Do not publish the exact bypass-enabling regex/keyword list in prose documentation — keep detection logic in code/tests only, so this documentation package doesn't double as an evasion guide.
4. Coordinate with AGENT_03 (Commerce Agent) and AGENT_04 (Guardian) to prove, via integration test, that the fixture's injected instructions never influence a `TransactionIntent` or a Guardian decision.

## Tests Required

- `scan_content()` flags each fixture attack string, does not flag any of the ≥10 benign samples
- Integration test: full chat with the malicious-content product results in a decision that respects the buyer's real request/mandate, with `security.catalog_content_flagged: true` present in the Receipt
- Performance test: `scan_content()` completes in <5ms on realistic description-length text

## Acceptance Criteria

- [ ] Full injection test matrix from `14_TEST_PLAN.md` §5 passes
- [ ] Malicious fixture product exists in seed data and is queryable
- [ ] Zero false positives on the benign sample set
- [ ] `suspicious_content_flag` correctly appears in `GET /catalog/products/{sku}` responses and in Receipts touching that SKU

## Must NOT Modify

`app/guardian`'s decision logic (only the informational flag field it reads), `app/catalog` core CRUD, `app/commerce_agent`, `app/campaign`, `app/razorpay_adapter`, `app/receipts`.
