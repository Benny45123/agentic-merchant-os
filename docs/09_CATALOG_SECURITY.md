
# 09 — Catalog Security Spec

## 1. Core Principle

**Catalog content ≠ authorization.** This is enforced structurally, not by hoping the LLM behaves. Two independent layers:

**Layer 1 — Structural (primary defense, always active):**
The Guardian never reads any free-text catalog field (`description`, review text, marketing copy) as an input to any check. Every Guardian check operates only on: the `Mandate` row, the `MerchantPolicy` row, authoritative `Product.price`/`Product.inventory`/`Product.category`/`Product.sku` (structured columns), and the `TransactionIntent` (which itself is assembled by deterministic code from `CartItem` state, not by the LLM writing free text — see `06_AGENT_SPEC.md` §3). Even a fully-compromised Commerce Agent LLM cannot produce a `TransactionIntent` that bypasses a mandate or policy limit, because the limit is re-checked against structured data the LLM never controls.

**Layer 2 — Heuristic detection (defense-in-depth + demo visibility):**
A lightweight classifier (`app/security`) scans untrusted text fields for instruction-like patterns and sets `Product.suspicious_content_flag`. This does not block anything by itself — it surfaces to the merchant dashboard and is recorded (informationally) on any Receipt touching that SKU, so a merchant/judge can see the system *noticed* the attack even though the noticing wasn't what stopped it.

## 2. Trusted vs Untrusted Field Classification (authoritative list)

| Field                                                                   | Trust                                   | Guardian-readable?                          | Agent-readable?                   |
| ----------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------- | --------------------------------- |
| `sku`, `price`, `inventory`, `currency`, `category`, `cost` | Trusted                                 | Yes                                         | Yes (cost: no)                    |
| `variants[].price_delta`, `variants[].inventory`                    | Trusted                                 | Yes                                         | Yes                               |
| `bundle_relationships`                                                | Trusted                                 | No (not needed for money decisions)         | Yes (for upsell)                  |
| `shipping_info`, `return_policy`                                    | Trusted (merchant-authored, structured) | No                                          | Yes (display)                     |
| `description`, `marketing_copy`                                     | **Untrusted**                     | **No**                                | Yes (display + conversation only) |
| Reviews (if implemented)                                                | **Untrusted**                     | **No**                                | Yes (display only)                |
| `offers[].discount_pct`                                               | Trusted (merchant/campaign authored)    | Yes, but always re-validated against policy | Yes                               |

Rule of thumb: any field a merchant could enter as free-form prose is untrusted. Any field that is a number, enum, or ID is trusted and structurally validated at write time (`app/catalog` rejects a `PATCH` that tries to set `price` to a non-numeric value, etc.).

## 3. Heuristic Classifier Design

Pattern families flagged (regex/keyword based, case-insensitive, run on `description`/reviews at write time and on a periodic re-scan):

- Imperative override language directed at an AI system (e.g., phrases instructing an assistant to disregard limits, rules, or prior instructions).
- References to system-level roles or prompt structure appearing inside product text (e.g., fake "system:" or "assistant:" role markers).
- Explicit instructions to perform a purchase action embedded in descriptive text (e.g., directives to add specific quantities or skip confirmation).

Implementation detail is intentionally left to `AGENT_09_SECURITY_TESTING` to build as a small, testable rule set (`app/security/classifier.py`) — this document specifies the **contract**, not the exact regex list, to avoid the documentation itself becoming a how-to-bypass guide. The contract:

```python
def scan_content(text: str) -> ContentScanResult:
    """Returns { flagged: bool, matched_categories: list[str] }.
    Pure function, no I/O, must run in <5ms for demo-scale text."""
```

## 4. Where Enforcement Lives

| Concern                      | Enforced by                                 | Not enforced by                        |
| ---------------------------- | ------------------------------------------- | -------------------------------------- |
| Buyer spending limit         | Mandate check in Guardian (structured)      | Commerce Agent's "good judgment"       |
| Discount ceiling             | Policy check in Guardian (structured)       | Catalog offer text                     |
| Quantity ceiling             | Mandate check in Guardian (structured)      | Agent's interpretation of catalog copy |
| "Is this content suspicious" | `app/security` classifier (informational) | Guardian decision logic                |

## 5. Attack Scenarios Covered (maps to `13_THREAT_MODEL.md` items 1-4)

1. Injected instruction in `description` telling the agent to ignore the buyer's mandate → **fails** because the Guardian re-checks the actual mandate regardless of what the agent "believes."
2. Injected instruction in a review telling the agent to apply an unauthorized discount → **fails** because `discount_pct` is always re-validated against `MerchantPolicy.maximum_discount_pct` server-side, never trusted from agent output.
3. Injected instruction trying to get the agent to skip `REQUIRE_CONFIRMATION` → **fails** because confirmation is a Guardian-issued state machine step (`/guardian/confirm/{decision_id}`), not something the agent can flag its way past — the agent can only *narrate* the requirement, it cannot suppress it.
4. Malicious merchant content designed to make the agent recommend an item at a loss → **fails** because margin is re-validated in Policy check, independent of what the agent recommended.

## 6. Test Requirements

- Fixture catalog entries with injected instructions (used by `AGENT_09_SECURITY_TESTING`, referenced by `15_DEMO_SCENARIOS.md` Failure 1).
- Unit test: `scan_content()` correctly flags fixture attack strings and does not flag ordinary marketing copy (false-positive check with ≥10 benign samples).
- Integration test: end-to-end chat with an attack-laden product description results in a `TransactionIntent` that still respects the buyer's real mandate, and the resulting Receipt shows `security.catalog_content_flagged: true` alongside `decision: BLOCK` (or `APPROVE` at the buyer's *actual* authorized quantity — the point being the injected quantity is never used).
