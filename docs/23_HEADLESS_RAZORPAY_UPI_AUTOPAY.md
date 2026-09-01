# Document 23: Agentic Commerce Protocol & Autonomous Mandate Specification

## 1. Executive Summary

The **Agentic Commerce Protocol** enables autonomous machine-to-machine procurement while maintaining mathematical financial safety. Rather than treating payment tokens as unrestricted debit keys, the platform establishes the **Buyer Mandate as the Primary Authorization Lock**, with Razorpay as the underlying execution rail.

When Claude MCP, A2A Machine Buyers, or Telegram users initiate procurement, the **Deterministic Zero-LLM Commerce Guardian** evaluates all mandate constraints (spending ceiling, per-transaction limits, valid window, margin floors) before dispatching any payment.

---

## 2. The Core Architecture

```text
ONE-TIME HUMAN AUTHORIZATION
        │
        ▼ (Razorpay recurring registration / test mandate)
BUYER MANDATE = THE LOCK
        │
        ├── Max Total Pool: ₹1,50,000
        ├── Per-Transaction Limit: ₹75,000 (Mobile cost ceiling)
        ├── Duration: 90 Days
        └── Status: ACTIVE
        │
Claude MCP / A2A Buyer Agent
        │
        │ Negotiates purchase: iPhone 15 @ ₹64,500
        ▼
DETERMINISTIC COMMERCE GUARDIAN
        │
        ├── 1. Mandate Status == ACTIVE?                  ✓ PASS
        ├── 2. Expiration > Current Time?                 ✓ PASS
        ├── 3. Txn (₹64,500) ≤ Max Txn (₹75,000)?         ✓ PASS
        ├── 4. Cumulative Spend (₹64.5k) ≤ Pool (₹150k)?  ✓ PASS
        ├── 5. Merchant Margin Floor ≥ 15%?              ✓ PASS
        └── 6. Zero Prompt Injection?                     ✓ PASS
        │
        ▼ (Only if 100% Invariants PASS)
PAYMENT EXECUTION RAIL (Razorpay)
        │
        ├── client.payment.createRecurring(...)
        └── Order.status = PAID (Instant Settlement)
        │
        ▼
TELEGRAM NOTIFICATION + DECISION RECEIPT
        │
        ├── Signed with Merchant RSA/Ed25519 Key
        └── Updated in Autonomous Commerce Dashboard
```

---

## 3. Mandate Lifecycle State Machine

```text
                 ┌──────────────┐
                 │     NONE     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │    PENDING   │
                 └──────┬───────┘
                        │
                 User authorizes
                        │
                        ▼
                 ┌──────────────┐
                 │    ACTIVE    │◄─────────┐
                 └──────┬───────┘          │
                        │                   │
                expiration/revoke          │
                        │                   │
                        ▼                   │
                 ┌──────────────┐           │
                 │ EXPIRED      │           │
                 └──────┬───────┘           │
                        │                   │
                   re-authorize ────────────┘
```

> [!IMPORTANT]
> **Anti-Reactivation Guarantee:** An AI agent is mathematically incapable of transitioning `EXPIRED -> ACTIVE` by itself. Only a direct human authorization verified by the payment provider can activate or renew a mandate.

---

## 4. Deterministic Guardian Mandate Locks

```python
def can_autopay(mandate: Mandate, amount: int, now: datetime) -> tuple[bool, str]:
    if not mandate or not mandate.active:
        return False, "Mandate is not active"

    if mandate.expires_at <= now:
        return False, "Mandate expired"

    if mandate.recurring_auth_status != "ACTIVE":
        return False, "AutoPay recurring status requires human authorization"

    if amount > mandate.max_amount_per_charge:
        return False, f"Transaction ₹{amount/100:.2f} exceeds per-charge limit ₹{mandate.max_amount_per_charge/100:.2f}"

    if mandate.spent_amount + amount > mandate.max_amount:
        remaining = max(0, mandate.max_amount - mandate.spent_amount)
        return False, f"Transaction exceeds remaining pool ₹{remaining/100:.2f} (Total: ₹{mandate.max_amount/100:.2f})"

    return True, "Mandate constraints satisfied for autonomous execution"
```

---

## 5. Mobile-Optimized Limits

| Parameter | Value (INR) | Value (Paise) | Description |
| :--- | :--- | :--- | :--- |
| `max_amount` (Total Pool) | **₹1,50,000.00** | `15000000` | Total allowable spend over mandate validity window. |
| `max_amount_per_charge` | **₹75,000.00** | `7500000` | Sized to accommodate flagship smartphones (e.g. iPhone 15 ₹69,900, Galaxy S24 ₹74,999). |
| `valid_days` | **90 Days** | - | Expiration window before requiring human re-authorization. |
| `spent_amount` | Dynamic | Dynamic | Tracks cumulative debits atomically on the immutable ledger. |

---

## 6. Claude MCP & A2A Machine Protocol

Agents interact exclusively through gated tools:
* `commerce_execute_purchase`: Requests purchase for specific SKU & quantity.
* `commerce_negotiate_purchase`: Initiates multi-turn margin-safe price bargaining.

If an agent attempts to spend ₹80,000 on a ₹75,000 per-transaction mandate, the Guardian returns `BLOCKED` with a Decision Receipt explaining the exact constraint violation. **Zero calls are made to Razorpay.**

```

---

## 5. Omnichannel Touchpoints

| Channel | Autonomous AutoPay Experience |
| :--- | :--- |
| **📱 Telegram Bot** | `/autopay` command allows 1-click mandate setup. Subsequent queries like *"Buy iPhone 15"* execute in **0-clicks** with instant `⚡ AUTOPAY EXECUTED` receipt message. |
| **🤖 Claude Desktop / MCP** | Exposes `setup_autopay_mandate` and enables Claude to negotiate wholesale deals and settle orders headlessly over stdio JSON-RPC. |
| **💻 Web Buyer Chat** | Toggle switch `[ ⚡ Enable Headless UPI AutoPay ]` enables zero-modal instant checkout. |
| **📊 Merchant Dashboard** | Visualizes live AutoPay adoption metrics, zero-click revenue streams, and sub-second settlement telemetry. |

---

## 6. Security & Invariant Non-Negotiables
1. **Zero LLM in AutoPay Triggering**: No LLM may directly call Razorpay recurring APIs; only the Guardian pipeline can invoke `charge_autopay_token()`.
2. **Strict Cap Enforcement**: Any transaction exceeding `max_amount_per_charge` is blocked deterministically before Razorpay is touched.
3. **Mandate Revocation**: Customers can revoke or pause their AutoPay token instantly at any time via `/autopay off`.
