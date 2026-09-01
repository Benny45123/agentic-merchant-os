# Document 23: True Headless Razorpay UPI AutoPay Specification

## 1. Executive Summary

**Headless Razorpay UPI AutoPay** transitions Agentic Merchant OS from interactive checkout modals to **True Autonomous AI Agent Commerce**. By binding pre-authorized, user-bounded UPI e-mandates (`tok_rzp_autopay_...`) with the **Deterministic Zero-LLM Commerce Guardian**, AI agents across Telegram, Web Chat, Claude MCP, and UAP Machine Protocols can negotiate and execute real-time settlements in **< 400ms with 0 OTP prompts**.

---

## 2. Dual-Lock Safety Architecture

Autonomous payment execution without deterministic guardrails creates existential financial risk. The platform implements a **Dual-Lock Verification Model**:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           LOCK 1: THE BUYER MANDATE                               │
│  • Human owner authorizes maximum spend ceiling (e.g. ₹50,000 / month).           │
│  • Bounded by product categories, max item quantities, and expiration date.       │
│  • Registered ONCE via official UPI app (PhonePe / GPay) ➔ Razorpay issues token. │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    LOCK 2: DETERMINISTIC COMMERCE GUARDIAN                        │
│  • Mathematically evaluates 19 safety invariants in Python (< 1ms, Zero-LLM).    │
│  • Enforces Rule 6 gross margin floor (≥ 15.0%) and merchant policy ceiling (20%).│
│  • Verifies SKU availability, price match, and zero prompt injection.             │
│  • Mints immutable SHA-256 Decision Receipt.                                      │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼ (Only if 19/19 Invariants PASS)
┌───────────────────────────────────────────────────────────────────────────────────┐
│                  HEADLESS RAZORPAY RECURRING EXECUTION                            │
│  • Guardian dispatches `client.payment.createRecurring(...)` with `tok_rzp_...`.  │
│  • Bank debits UPI account silently in sub-second test execution.                 │
│  • Automatically marks `Order.status = PAID` and updates Merchant Dashboard.      │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model Extensions

### 3.1 Database Schema (`app/models/mandate.py`)
```python
class BuyerMandate(Base):
    ...
    autopay_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    autopay_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True) # e.g. "tok_rzp_autopay_..."
    customer_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)   # e.g. "cust_..."
    max_amount_per_charge: Mapped[int] = mapped_column(BigInteger, default=10000000) # In paise (₹1,00,000)
    recurring_auth_status: Mapped[str] = mapped_column(String(32), default="NONE") # NONE | PENDING | ACTIVE
    autopay_bank_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    autopay_vpa: Mapped[Optional[str]] = mapped_column(String(64), nullable=True) # e.g. "user@okhdfcbank"
```

### 3.2 Decision Receipt Schema (`app/models/receipt.py`)
```python
# Receipt payload records execution method:
{
    "payment_method": "upi_autopay_headless",
    "token_id": "tok_rzp_autopay_98fa...",
    "customer_id": "cust_87bc...",
    "zero_click_settlement": True,
    "execution_latency_ms": 340
}
```

---

## 4. Razorpay Recurring Adapter Contracts

### 4.1 1-Time Mandate Registration (`app/razorpay_adapter/client.py`)
```python
def create_autopay_registration(
    self,
    buyer_id: str,
    max_amount_paise: int,
    description: str = "Agentic Merchant OS Autonomous Procurement Mandate"
) -> Dict[str, Any]:
    """
    Creates a Razorpay customer and generates a ₹0 or ₹1 authorization order
    to establish the recurring UPI e-mandate.
    """
```

### 4.2 Headless Charge Dispatch (`app/razorpay_adapter/client.py`)
```python
def charge_autopay_token(
    self,
    customer_id: str,
    token_id: str,
    amount_paise: int,
    order_id: str,
    receipt_id: str
) -> Dict[str, Any]:
    """
    Executes an autonomous headless recurring charge via Razorpay's Recurring API:
    POST /v1/payments/create/recurring
    Returns captured payment details with zero OTP prompts.
    """
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
