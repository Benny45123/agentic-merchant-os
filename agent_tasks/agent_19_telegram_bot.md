# Agent Task: Agent 19 — Telegram Bot Mobile Gateway

## Context & Purpose
Provide an omnichannel conversational shopping gateway over Telegram (`@agentic_merchant_store_bot`), allowing judges and mobile users to search catalog products, negotiate wholesale reverse auction bargains, receive margin-safe bundle sweeteners (+₹298.50 lift), and execute 1-click Razorpay test checkouts directly on their phone.

---

## Deliverables
1. `backend/app/telegram/`:
   - `bot.py`: Async long-polling daemon connecting to Telegram Bot API.
   - `handlers.py`: Command routing (`/start`, `/catalog`, `/cart`, bargaining, inline buttons, Razorpay checkout links).
2. `backend/app/core/config.py`:
   - Add `TELEGRAM_BOT_TOKEN: Optional[str] = None` setting.
3. `.env.example` & `backend/.env`:
   - Add `TELEGRAM_BOT_TOKEN` variable.
4. `bin/start.sh` & `bin/stop.sh`:
   - Automatically launch Telegram bot daemon in background if `TELEGRAM_BOT_TOKEN` is present.
5. `README.md` & `CHANGELOG.md`:
   - Document the live `@agentic_merchant_store_bot` integration.

---

## Acceptance Criteria
- [x] `/start` returns rich interactive welcome card with inline buttons.
- [x] Natural language queries (e.g. "iPhone 15", "bargain") return authoritative pricing.
- [x] Reverse auction bargaining triggers Rule 6 Margin Guardian and returns bundle sweetener options.
- [x] 1-Click Razorpay test checkout button is dispatched to the user.
- [x] Gracefully handles missing `TELEGRAM_BOT_TOKEN` with zero errors.
