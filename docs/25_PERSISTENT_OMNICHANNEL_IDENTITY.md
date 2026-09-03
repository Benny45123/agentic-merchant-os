# 25. Persistent Omnichannel Identity Architecture

## 1. Vision & Core Philosophy

In traditional e-commerce, user identity requires high-friction authentication barriers: phone numbers, passwords, OAuth redirects, and SMS OTP verification. While acceptable for human shoppers, this model **completely breaks autonomous AI commerce**, where machines, swarms, and background mobile bots transact continuously.

**Agentic Merchant OS (AMOS)** implements **Zero-Friction Persistent Omnichannel Identity**:
1. **Zero Registration Walls**: Every client connecting via Web, Telegram, Claude MCP, LangChain, or UAP automatically receives a first-class, cryptographically isolated `buyer_id`.
2. **Deterministic Persistence**: Identity survives browser restarts, computer reboots, and network switches without requiring login credentials.
3. **Instant-On Financial Mandates**: New identities are auto-provisioned with an initial demo UPI AutoPay spending pool (default ₹50,000) and Google AP2 ES256 keypairs, allowing immediate zero-click headless purchases.
4. **Merchant Observability**: The store owner's dashboard visualizes every distinct device, smartphone, and AI agent as an independent customer card with live financial headroom and per-customer pause/revoke killswitches.

---

## 2. Channel Resolution Specifications

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       INCOMING COMMERCE TRAFFIC                             │
├────────────────────┬────────────────────┬─────────────────┬─────────────────┤
│ 📱 Telegram Mobile │ 💻 Web Browser     │ 🤖 Claude MCP   │ 🦜 Swarm / UAP  │
├────────────────────┼────────────────────┼─────────────────┼─────────────────┤
│ user_id:           │ localStorage &     │ getpass.getuser │ AMOS_BUYER_ID   │
│ 8554611903         │ 1-year cookie      │ + hostname hash │ or client cert  │
│                    │                    │                 │                 │
│ buyer_id:          │ buyer_id:          │ buyer_id:       │ buyer_id:       │
│ "tg_8554611903"    │ "b_dev_8f2a1b"     │ "mcp_alex_9c41" │ "langchain_01"  │
└─────────┬──────────┴─────────┬──────────┴────────┬────────┴────────┬────────┘
          │                    │                   │                 │
          └────────────────────┼───────────────────┴─────────────────┘
                               ▼
            ┌──────────────────────────────────────┐
            │   CORE IDENTITY SERVICE              │
            │   app.core.identity.get_or_create()  │
            ├──────────────────────────────────────┤
            │ 1. Check database for buyer_id       │
            │ 2. If exists: return buyer & mandate │
            │ 3. If new:                           │
            │    • Insert Buyer row with metadata  │
            │    • Seed ₹50k AutoPay Mandate       │
            │    • Derive Google AP2 ES256 Keypair │
            │    • Assign default VPA              │
            └──────────────────┬───────────────────┘
                               ▼
            ┌──────────────────────────────────────┐
            │   DETERMINISTIC COMMERCE GUARDIAN    │
            │   • Isolates spending pool           │
            │   • Enforces margin policy ≥ 15%     │
            │   • Verifies ES256 AP2 delegation    │
            └──────────────────────────────────────┘
```

### Channel 1: 📱 Telegram Mobile Gateway
* **Extraction**: `update["message"]["from"]["id"]` or `update["callback_query"]["from"]["id"]`.
* **Format**: `tg_{telegram_user_id}` (e.g. `tg_8554611903`).
* **Display Name**: `{first_name} (@{username})` or `{first_name} (Telegram)`.
* **Persistence**: Guaranteed forever by Telegram's distributed platform infrastructure.

### Channel 2: 💻 Web Browser (Chat & Checkout)
* **Extraction**: `localStorage.getItem("amos_shopper_identity")` with fallback to `document.cookie` (`amos_buyer_id`).
* **Format**: `b_dev_{random_hex_6}` (e.g. `b_dev_a8f29c`).
* **Device Telemetry**: Automatically records user-agent platform, e.g. `Shopper (Chrome • macOS)` or `Shopper (Safari • iPhone)`.
* **Persistence**: 1-year expiration cookie (`Max-Age: 31536000; SameSite=Lax`). Survives page refreshes, tab closures, and laptop reboots.
* **Customization**: Shopper can click "Edit Name" in the chat header to set a human alias (e.g. "Alex").

### Channel 3: 🤖 Claude Desktop & Claude Code (MCP)
* **Extraction**:
  ```python
  username = getpass.getuser()
  host_hash = hashlib.md5(socket.gethostname().encode()).hexdigest()[:4]
  buyer_id = f"claude_{username}_{host_hash}"
  ```
* **Format**: `claude_{username}_{host_hash}` (e.g. `claude_alex_e4a1`).
* **Persistence**: Bound to the user's workstation and OS login. Persists across all Claude Desktop restarts.

### Channel 4: 🦜 LangChain, Hermes, and Custom Swarms
* **Extraction**: Environment variable `AMOS_BUYER_ID` or request header `X-Buyer-ID`.
* **Format**: `langchain_{agent_name}` or `hermes_local_{hash}`.
* **Persistence**: Managed by the calling agent harness or automation script.

---

## 3. Financial & Cryptographic Isolation

Each resolved identity maintains strictly segregated financial boundaries:

1. **Headroom Segregation**: Deductions against `tg_8554611903`'s mandate pool never decrement `b_dev_a8f29c`'s balance.
2. **Google AP2 ES256 Keypair Segregation**: 
   `app.mandate.ap2_service.get_or_create_buyer_keypair(buyer_id)` derives a dedicated elliptic curve keypair per identity:
   * Key identifier: `urn:buyer:{buyer_id}`
   * Private key used to sign Open Mandates (`mnd_open_...`).
   * Public key stored in mandate snapshot for independent receipt verification.
3. **Razorpay Token Rails**:
   * Token ID: `tok_rzp_autopay_{buyer_id}`
   * Customer ID: `cust_{buyer_id}`
   * Simulated VPA: `{buyer_id}@okhdfcbank`

---

## 4. Merchant Dashboard Telemetry

The Merchant Dashboard (`/dashboard`) surfaces all registered omnichannel buyers in real time:
* **Channel Badges**: Color-coded badges indicating source (`TELEGRAM 📱`, `WEB BROWSER 💻`, `CLAUDE MCP 🤖`, `SEED ⚡`).
* **Active Spending Meters**: Visual headroom progress bars showing remaining balance out of total authorized pool.
* **Individual Killswitch**: Per-buyer toggle to immediately pause zero-click headless debits and revert to hosted Razorpay payment links.

---

## 5. Live Agentic Transaction Stream (Decentralized Mempool Ledger)

To provide the merchant with real-time operational awareness without duplicating the deep cryptographic replay engine (which lives on its dedicated `/receipts` page), the Merchant Dashboard features the **Live Agentic Transaction Stream**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📡 LIVE AGENTIC TRANSACTION STREAM (Decentralized Mempool Ledger)           │
│ ● LIVE STREAMING (Auto-Sync: 10s) • 4 Connected Ingress Channels           │
│ Filters: [ All Events ] [ 📱 Telegram ] [ 🤖 Claude MCP ] [ 💻 Web ] [ 🛑 Blocked ] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🟢 APPROVED • ₹6,990.00                               12s ago • Latency <35ms│
│ 👤 USER: tg_855***903 (Telegram Shopper)   📱 Channel: Telegram Mobile     │
│ 🎯 ACTION: 0-Click Autonomous UPI AutoPay   💳 Rail: HDFC AutoPay Token     │
│ 📦 ITEMS: AeroSound HP-001 (x1)             🛡️ GUARDIAN: Margin 32.4% (≥15%)│
│ 🔐 RECEIPT: rcpt_62b7c15f... ➔ [ 🔍 Inspect Merkle Proof & Replay ]         │
│                                                                             │
│ ─────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│ 🛑 BLOCKED • ₹0.00                                   2m ago • Latency <3ms  │
│ 👤 USER: b_dev_8f2a... (Web Browser)        💻 Channel: Web Store           │
│ 🚨 ACTION: Malicious Prompt Injection       🛡️ GUARDIAN: Rule 1 Triggered   │
│ ⚠️ DETAIL: Security scanner heuristic flagged prompt injection payload      │
│ 🔒 FINANCIAL LEAKAGE: ZERO (Razorpay API was NOT called)                    │
│ 🔐 RECEIPT: rcpt_e49b1a02... ➔ [ 🔍 Inspect Merkle Proof & Replay ]         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Privacy-Preserving Identity Masking
In strict alignment with the **India Digital Personal Data Protection (DPDP) Act 2023** and **GDPR Article 25 (Privacy by Design)**:
1. **Masked Telemetry Identifiers**:
   * Raw Telegram 64-bit IDs are masked before rendering: `tg_855***903`
   * Browser device UUIDs are truncated: `b_dev_8f2a...`
   * Claude MCP identifiers are truncated: `claude_alex...`
2. **Zero PII Exposure**:
   * No phone numbers, passwords, OTPs, or real bank account numbers are ever collected, stored, or rendered.
   * All payment rails use simulated virtual payment handles (e.g. `b_001@okhdfcbank`) and tokenized recurring references (`tok_rzp_autopay_...`).
3. **Separation of Concerns**:
   * **`/dashboard`**: Real-time operational command plane displaying revenue metrics, mandate headroom, and live stream telemetry.
   * **`/receipts`**: Comprehensive audit vault housing the Quad-Leaf Merkle Tree visualizer and bit-for-bit replay verifier. Each live stream transaction card contains a 1-click direct link to its corresponding cryptographic audit receipt.

---

## 6. AutoPay Opt-In Lifecycle & Authorization Gate

To prevent unexpected zero-click charges, AutoPay follows a strict **Opt-In by Design** lifecycle across all channels:

1. **Baseline Ingress (AutoPay: OFF)**:
   * When a buyer interacts for the first time via Telegram, Claude MCP, or Web, they are provisioned with an active baseline shopping profile (`active=True`) ensuring Guardian Rule 17 passes.
   * **AutoPay is disabled by default** (`autopay_enabled=False`, `recurring_auth_status="INACTIVE"`).
   * Initial purchases return an official Razorpay payment link (`APPROVE` with `payment_link`) requiring manual payment (UPI / Card).

2. **Explicit User Activation**:
   * **Telegram Mobile**: Shopper runs `/autopay` or taps `⚡ Setup AutoPay Mandate (₹1 Lakh)`.
   * **Claude Desktop**: Shopper instructs Claude to `setup autopay mandate`.
   * The system generates a Razorpay Mandate Authorization link (`/mandates/checkout/{token_id}`).
   * The shopper authorizes their recurring e-mandate on Razorpay.

3. **Subsequent Purchases (0-Click Active)**:
   * Once authorized (`autopay_enabled=True`, `recurring_auth_status="ACTIVE"`), future purchases within spending limits execute headlessly in < 400ms with zero OTP prompts.


