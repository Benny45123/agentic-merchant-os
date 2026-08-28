# 🤝 Specification 20: Autonomous A2A Dynamic Negotiation & Model Context Protocol (MCP)

**Track 01: AI Growth & Agentic Commerce**

---

## 1. Overview & Motivation

Traditional e-commerce is built around static "take-it-or-leave-it" pricing. In an **Agentic Commerce** paradigm, autonomous AI Buyer Bots (e.g., procurement agents, personal AI shoppers) interact directly with the **Merchant's Pricing Agent** via machine protocols.

**Agentic Merchant OS** introduces the **Bilateral Reverse Auction Engine**:
1. **Buyer Agent RFQ**: Buyer proposes a custom volume and target unit price backed by a cryptographic spending mandate.
2. **Merchant Pricing Agent**: Evaluates product costs, current inventory velocity, and strict policy margin floors ($\ge 15\%$), and formulates bilateral counter-offers.
3. **Margin-Maximizing Bundle Sweetener**: Converts buyer discount requests into profit-lifting bundles (+₹298.50 profit lift by bundling high-margin accessories at 50% off).
4. **Deterministic Guardian Settlement**: Zero-LLM mathematical verification guarantees no hallucinated prices or mandate breaches, issuing a Razorpay test order in **sub-50ms**.

---

## 2. Mathematical Margin & Headroom Formulas

### 2.1 Absolute Margin Floor
For a product with unit price $P$, unit cost $C$, and merchant minimum gross margin floor $M_{min} = 15\%$:

$$\text{Unit Margin} = \frac{\text{Target Price} - C}{\text{Target Price}} \ge M_{min}$$

$$\text{Minimum Allowed Price Floor} = \frac{C}{1 - M_{min}}$$

*Example for AeroSound Headphones (`HP-001`):*
* Catalog Price: $P = ₹4,499.00$ ($449,900\text{ paise}$)
* Unit Cost: $C = ₹3,000.00$ ($300,000\text{ paise}$)
* Minimum Gross Margin: $M_{min} = 15\%$

$$\text{Price Floor} = \frac{3000}{1 - 0.15} = \frac{3000}{0.85} \approx ₹3,529.41$$

If a predatory buyer agent proposes $₹3,200.00$ (Margin: $\frac{3200-3000}{3200} = 6.25\% < 15\%$), the Pricing Agent immediately returns `REJECTED_MARGIN_FLOOR`.

---

### 2.2 Bilateral Counter-Offer Generation

When a valid proposal arrives (e.g., 3x `HP-001` @ $₹4,100.00$, margin $26.8\% \ge 15\%$):

#### Strategy A: Direct Price Compromise
Splits the gap between catalog price ($₹4,499$) and buyer target ($₹4,100$):
$$\text{Compromise Price} = ₹4,100 + (4,499 - 4,100) \times 0.35 = ₹4,239.65/\text{unit}$$
* Total Deal: $3 \times ₹4,239.65 = ₹12,718.95$ ($29.2\%$ Gross Margin).
* Merchant Profit Lift: $+₹418.95$.

#### Strategy B: Bundle Sweetener (Value Maximizer)
Accepts buyer's target price ($₹4,100.00$) for the main item, and bundles companion accessories (e.g., 3x `CASE-HP` Travel Cases @ 50% discount = $₹499.50$):
* Total Bundle Revenue: $3 \times 4,100 + 3 \times 499.50 = ₹13,798.50$.
* Total Bundle Cost: $3 \times 3,000 + 3 \times 400 = ₹10,200.00$.
* Combined Gross Margin: $\frac{13,798.50 - 10,200}{13,798.50} = 26.1\% \ge 15.0\%$ Floor.
* **Merchant Profit Lift**: $+₹298.50$ additional profit over the standalone buyer offer!

---

## 3. Protocol Endpoints & Payloads

### 3.1 Request for Quote: `POST /commerce/rfq`

```json
{
  "buyer_agent_id": "ai_buyer_agent_procure_42",
  "merchant_id": "m_001",
  "buyer_mandate": {
    "buyer_id": "b_001",
    "max_amount": 2000000,
    "max_quantity_per_item": 10,
    "currency": "INR",
    "signature": "sig_ed25519_procurement_mandate"
  },
  "items": [
    {
      "sku": "HP-001",
      "qty": 3,
      "target_unit_price_paise": 410000
    }
  ]
}
```

### 3.2 RFQ Response with Counter-Offers

```json
{
  "status": "OFFERS_PROPOSED",
  "session_id": "neg_sess_9a8c17ef3012",
  "round_index": 1,
  "merchant_id": "m_001",
  "catalog_total_paise": 1349700,
  "buyer_target_total_paise": 1230000,
  "minimum_margin_floor_pct": 15.0,
  "counter_offers": [
    {
      "option_id": "OPT_DIRECT_PRICE",
      "option_type": "DIRECT_PRICE_COUNTER",
      "title": "Direct Unit Price Counter: ₹4239.65/unit",
      "total_amount_paise": 1271895,
      "projected_gross_margin_pct": 29.2,
      "margin_floor_satisfied": true,
      "merchant_profit_lift_paise": 41895
    },
    {
      "option_id": "OPT_BUNDLE_SWEETENER",
      "option_type": "BUNDLE_SWEETENER",
      "title": "Target Price Accepted (₹4100.00) + 3x Travel Case @ 50% Off",
      "total_amount_paise": 1379850,
      "projected_gross_margin_pct": 26.1,
      "margin_floor_satisfied": true,
      "merchant_profit_lift_paise": 29850
    }
  ]
}
```

### 3.3 Deal Acceptance & Settlement: `POST /commerce/accept`

```json
{
  "session_id": "neg_sess_9a8c17ef3012",
  "buyer_agent_id": "ai_buyer_agent_procure_42",
  "merchant_id": "m_001",
  "selected_option_id": "OPT_BUNDLE_SWEETENER",
  "buyer_signature": "sig_ed25519_contract_accepted"
}
```

---

## 4. Model Context Protocol (MCP) Server

The native MCP stdio server (`backend/app/api/mcp_server.py`) enables Claude Desktop, Cursor, and Antigravity to transact over standard JSON-RPC 2.0 stdio.

### 4.1 MCP Server Tool Registry

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| **`search_catalog`** | `query`, `merchant_id` | Search live product catalog with authoritative prices & stock. |
| **`submit_commerce_rfq`** | `sku`, `quantity`, `target_unit_price_paise` | Submit bilateral RFQ and receive counter-offers. |
| **`accept_negotiation_offer`** | `session_id`, `selected_option_id` | Accept offer and trigger deterministic Guardian settlement. |
| **`submit_machine_purchase`** | `sku`, `quantity`, `max_budget_paise` | Submit standard headless autonomous machine purchase. |
| **`check_bundle_margin`** | `parent_sku`, `addon_sku`, `discount_pct` | Verify margin floor ($\ge 15\%$) for proposed bundle discounts. |
| **`get_decision_receipt`** | `receipt_id` | Retrieve cryptographic audit trail and replay proof. |

---

## 5. Security & Threat Mitigation

1. **Predatory Reverse Auctions**: Buyer agents attempting to manipulate prices below cost are bounded by hardcoded database policies.
2. **Replay & Hallucination Defense**: Every negotiated deal issues a cryptographic `DecisionReceipt` with a unique hash `sha256_...`. The receipt can be replayed at any time via `POST /receipts/{id}/replay` to verify that the Guardian produces the identical deterministic outcome.
3. **No Direct Gateway Access**: Neither the buyer agent nor the pricing LLM can touch Razorpay. Only the Commerce Guardian is permitted to invoke the Razorpay test API.
