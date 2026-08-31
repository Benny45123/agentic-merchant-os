# 22. Telegram Bot Omnichannel Commerce Architecture

## 1. Executive Summary & Objective

In **Razorpay Buildathon Track 01 (AI Growth & Agentic Commerce)**, agentic commerce must not be confined to a single browser tab. The **Telegram Bot Gateway** (`@agentic_merchant_store_bot`) turns Agentic Merchant OS into a truly **ubiquitous omnichannel merchant** capable of transacting directly on mobile devices over Telegram.

Judges, evaluators, and shoppers can message the bot from their personal smartphones to:
1. Discover catalog items through natural language (`/catalog` or search).
2. Execute **A2A Bilateral Reverse Auctions** against the Merchant Pricing Agent to bargain wholesale discounts.
3. Receive **Margin-Safe Bundle Sweeteners** (+₹298.50 profit lift) bounded by the Guardian Rule 6 Invariant ($\ge 15.0\%$).
4. Receive a 1-click **Razorpay Test-Mode Checkout Link** and cryptographic **Decision Receipt ID**.
5. Trigger live financial telemetry updates in the web dashboard ([`/dashboard`](http://localhost:3000/dashboard)) in real time.

---

## 2. Architecture & Data Flow

```
┌──────────────────────────────────────────────────────────┐
│              Judge's Real Mobile Phone                   │
│      (Telegram App: @agentic_merchant_store_bot)         │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼  HTTPS Telegram Bot API
┌──────────────────────────────────────────────────────────┐
│        Telegram Gateway Daemon (app/telegram/bot.py)     │
│         Async Long-Polling / Webhook Listener            │
└────────────────────────────┬─────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
         ▼ (Conversational Inquiries)            ▼ (Bilateral Bargains)
┌───────────────────────────────┐       ┌───────────────────────────────┐
│     LangGraph Commerce Agent  │       │  A2A Reverse Auction Engine   │
│     (/agent/chat Service)     │       │  (/commerce/rfq & accept)     │
└───────────────┬───────────────┘       └───────────────┬───────────────┘
                │                                       │
                └───────────────────┬───────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────┐
│             Deterministic Commerce Guardian              │
│       • Rule 6 Margin Floor Check (≥ 15.0%)              │
│       • Razorpay Test Order Minter                       │
│       • Cryptographic Decision Receipt Generator         │
└────────────────────────────┬─────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
         ▼                                       ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐
│ 📲 Instant Telegram Response  │       │ 📊 Live Web Telemetry Stream  │
│ • Sweetener Deal Card         │       │ • http://localhost:3000/      │
│ • 💳 1-Click Razorpay Button  │       │   dashboard updates live!     │
│ • 📜 Signed Receipt Link      │       │                               │
└───────────────────────────────┘       └───────────────────────────────┘
```

---

## 3. Supported Telegram Commands & Actions

| Command / Trigger | Action | Backend System |
| :--- | :--- | :--- |
| **`/start`** | Sends interactive welcome banner with quick-action inline buttons (`iPhone 15`, `Headphones`, `MacBook`, `Bargain Deals`). | `app/telegram/handlers.py` |
| **`/catalog`** | Lists live authoritative catalog items with formatted prices and stock levels. | `app/catalog/` |
| **`"Show iPhone 15"`** | Returns product specs, price (₹69,900.00), and inline action buttons to Buy or Bargain. | `app/commerce_agent/` |
| **`"Bargain iPhone 15"`** | Submits RFQ to `POST /commerce/rfq`, evaluates Rule 6 margin floor, and returns the **₹66,882.50 MagSafe Sweetener Deal**. | `app/negotiation/` + `app/guardian/` |
| **`[ 🎁 Buy Sweetener Bundle ]`** | Executes settlement over `POST /commerce/accept`, creates Razorpay test order, and returns payment link. | `app/razorpay_adapter/` |
| **`/cart`** | Displays user's active mobile cart state and total checkout amount. | `app/commerce_agent/` |

---

## 4. Security & Isolation Guarantee

1. **Zero LLM on Money Path**: The Telegram bot formatting and responses cannot bypass the **Deterministic Commerce Guardian**.
2. **Authoritative Pricing**: All item prices and discounts displayed in Telegram are pulled directly from SQLite `CatalogSnapshot`.
3. **Graceful Degradation**: If `TELEGRAM_BOT_TOKEN` is not configured in `.env`, the Telegram worker disables silently with zero CPU or memory footprint.
