# Agent 22 Task: Persistent Omnichannel Identity System

## Objective
Implement zero-friction, persistent identity resolution across all channels (Telegram, Web Browser, Claude MCP, External Swarms) with automatic buyer provisioning, instant-on ₹50,000 AutoPay test pools, and Google AP2 ES256 keypair derivation without requiring user login or registration screens.

---

## Deliverables

### 1. Backend Core Identity Service (`backend/app/core/identity.py`)
* `ensure_buyer_and_mandate(session, buyer_id, display_name=None, channel="web", initial_pool_paise=5000000)`:
  * Looks up `Buyer` by `buyer_id`.
  * If missing, creates `Buyer(buyer_id=buyer_id, name=display_name)`.
  * Checks if active `Mandate` exists for `buyer_id`.
  * If missing, creates `Mandate` with:
    * `max_amount = initial_pool_paise` (₹50,000 default; ₹1,00,000 for Telegram)
    * `autopay_enabled = True`, `recurring_auth_status = "ACTIVE"`
    * `autopay_token = f"tok_rzp_autopay_{buyer_id}"`
    * `autopay_vpa = f"{buyer_id}@okhdfcbank"`
    * `autopay_bank_name = "HDFC Bank (UPI AutoPay)"`
  * Generates Google AP2 ES256 keypair via `get_or_create_buyer_keypair(buyer_id)`.
* Expose API endpoint in `backend/app/api/` or `auth/`:
  * `POST /auth/identity/resolve`: Accepts client fingerprint/channel, returns active buyer profile and mandate.

### 2. Telegram Bot Gateway (`backend/app/telegram/`)
* In `bot.py`:
  * Extract `from_user.id` and `from_user.first_name` + `username`.
  * Construct dynamic `buyer_id = f"tg_{from_user.id}"`.
  * Pass `buyer_id` and `user_name` to all handler methods.
* In `handlers.py`:
  * Update `handle_direct_buy`, `handle_bargain_start`, `handle_accept_offer`, `handle_autopay_status`, `handle_autopay_setup_amount`, `handle_autopay_toggle`, `handle_pay_now` to accept and utilize dynamic `buyer_id`.
  * Call `ensure_buyer_and_mandate` on initial `/start` and purchase events.

### 3. Frontend Web Identity Service (`frontend/src/lib/identity.ts`)
* `getOrCreateShopperIdentity()`:
  * Checks `localStorage.getItem("amos_shopper_id")` and cookie `amos_buyer_id`.
  * If not found, detects user agent (e.g. "Chrome (Mac)", "Safari (iPhone)"), generates `b_dev_{random_hex}`, sets 1-year persistent cookie and `localStorage`.
  * Returns `{ buyerId: string, displayName: string }`.
  * `updateShopperName(newName: string)`: Updates local storage and informs backend.
* Update `frontend/src/app/(buyer)/chat/page.tsx`:
  * Use `getOrCreateShopperIdentity()`.
  * Render an identity pill badge in the chat navigation with quick edit modal.
* Update `frontend/src/app/(merchant)/negotiate/page.tsx`:
  * Use dynamic shopper identity.

### 4. Claude Desktop & MCP Integration (`backend/app/api/mcp_server.py`)
* Derive persistent identity:
  ```python
  def get_persistent_mcp_buyer_id() -> Tuple[str, str]:
      env_id = os.environ.get("AMOS_BUYER_ID")
      if env_id:
          return env_id, os.environ.get("AMOS_BUYER_NAME", f"Agent ({env_id})")
      user = getpass.getuser()
      host_hash = hashlib.md5(socket.gethostname().encode()).hexdigest()[:4]
      return f"claude_{user}_{host_hash}", f"Claude Desktop ({user})"
  ```
* Fall back to this dynamic identity whenever `buyer_id` is omitted in tool calls.
* Auto-provision on first tool execution.

### 5. Merchant Dashboard Enhancement (`frontend/src/app/(merchant)/dashboard/page.tsx`)
* Categorize buyers in the AutoPay Mandates section:
  * Detect channel from ID prefix (`tg_` ➔ Telegram, `b_dev_` ➔ Web Browser, `claude_` / `mcp_` ➔ Claude MCP, `b_001` ➔ Seed Benchmark).
  * Display channel badges with icons.
  * Allow filtering mandates by channel.

---

## Acceptance Criteria
1. When a new Telegram user interacts with `@agentic_merchant_store_bot`, a new buyer `tg_{user_id}` is automatically provisioned and appears as an active card on `/dashboard`.
2. When visiting the Web Store from Chrome and Safari simultaneously, two separate `b_dev_...` cards appear with separate headroom meters.
3. When Claude Desktop calls MCP tools without arguments, it transacts under `claude_{username}_{hash}`.
4. Core functionality (Guardian policy verification, margin floors, AP2 cryptographic signatures, Razorpay payment links) remains 100% green and unchanged.
5. `CHANGELOG.md` updated with Version 1.7.0.
