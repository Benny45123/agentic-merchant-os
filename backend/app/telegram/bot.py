"""
Async Telegram Bot Polling Daemon for Agentic Merchant OS.
Connects Telegram Bot API to the Commerce Agent and Guardian negotiation engine.
"""

import asyncio
import logging
import signal
import sys
import httpx
from typing import Optional

from app.core.config import get_settings
from app.telegram.handlers import TelegramHandlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("telegram_bot")


class TelegramBotService:
    def __init__(self, token: str, api_base: str = "http://localhost:8000"):
        self.token = token
        self.api_base = api_base
        self.tg_base_url = f"https://api.telegram.org/bot{token}"
        self.handlers = TelegramHandlers(api_base=api_base)
        self.offset = 0
        self.running = False

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[dict] = None) -> bool:
        """Sends an HTML formatted message to a Telegram chat with automatic fallback."""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup

            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(f"{self.tg_base_url}/sendMessage", json=payload)
                if res.status_code == 200:
                    return True
                
                # If HTML parsing fails, retry as plain text (strip tags)
                logger.warning(f"HTML send failed ({res.status_code}): {res.text}. Retrying as plain text...")
                import re
                clean_text = re.sub(r"<[^>]+>", "", text)
                payload["text"] = clean_text
                payload.pop("parse_mode", None)
                retry_res = await client.post(f"{self.tg_base_url}/sendMessage", json=payload)
                return retry_res.status_code == 200

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False


    async def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None):
        """Acknowledges a button click in Telegram."""
        try:
            payload = {"callback_query_id": callback_query_id}
            if text:
                payload["text"] = text
            async with httpx.AsyncClient(timeout=8.0) as client:
                await client.post(f"{self.tg_base_url}/answerCallbackQuery", json=payload)
        except Exception as e:
            logger.debug(f"Answer callback query warning: {e}")

    async def process_update(self, update: dict):
        """Processes an incoming Telegram update (Message or Callback Query)."""
        # Handle Callback Queries (Inline button clicks)
        if "callback_query" in update:
            cb = update["callback_query"]
            cb_id = cb["id"]
            chat_id = cb["message"]["chat"]["id"]
            data = cb.get("data", "")
            await self.answer_callback_query(cb_id, "Processing request...")

            if data.startswith("prod:"):
                sku = data.split(":", 1)[1]
                res = await self.handlers.handle_product_view(sku)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("rfq:"):
                parts = data.split(":")
                sku = parts[1]
                qty = int(parts[2]) if len(parts) > 2 else 1
                res = await self.handlers.handle_rfq_bargain(sku, qty)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("buy:"):
                parts = data.split(":")
                sku = parts[1]
                qty = int(parts[2]) if len(parts) > 2 else 1
                res = await self.handlers.handle_direct_buy(sku, qty)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("accept:"):
                parts = data.split(":")
                session_id = parts[1]
                option_id = parts[2]
                res = await self.handlers.handle_accept_offer(session_id, option_id)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("openrzp:"):
                order_id = data.split(":", 1)[1]
                res = await self.handlers.handle_open_razorpay_gateway(order_id)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("rzpm:"):
                parts = data.split(":")
                order_id = parts[1]
                method = parts[2] if len(parts) > 2 else "upi"
                res = await self.handlers.handle_razorpay_test_prompt(order_id, method)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("rzpok:"):
                order_id = data.split(":", 1)[1]
                res = await self.handlers.handle_pay_now(order_id, "upi")
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("rzpno:"):
                order_id = data.split(":", 1)[1]
                res = await self.handlers.handle_razorpay_failure(order_id)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("paynow:"):

                parts = data.split(":")
                order_id = parts[1]
                pay_method = parts[2] if len(parts) > 2 else "upi"
                res = await self.handlers.handle_pay_now(order_id, pay_method)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("chkpay:"):
                parts = data.split(":")
                order_id = parts[1]
                receipt_id = parts[2] if len(parts) > 2 else ""
                res = await self.handlers.handle_check_payment(order_id, receipt_id)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("rcpt:"):
                receipt_id = data.split(":", 1)[1]
                res = await self.handlers.handle_receipt_view(receipt_id)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("autopay:setup:"):

                amount_inr = int(data.split(":", 2)[2])
                res = await self.handlers.handle_autopay_setup_amount(amount_inr)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data.startswith("autopay:toggle:"):
                toggle_action = data.split(":", 2)[2]
                enable = toggle_action == "on"
                res = await self.handlers.handle_autopay_toggle(enable)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data == "cmd:autopay":
                res = await self.handlers.handle_autopay_status()
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data == "autopay:verify":
                res = await self.handlers.handle_autopay_verify()
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))



            elif data == "cmd:catalog":
                res = await self.handlers.handle_catalog()
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif data == "cmd:start":
                user_name = cb.get("from", {}).get("first_name", "Shopper")
                res = await self.handlers.handle_start(user_name)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            return

        # Handle Standard Messages
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_name = msg.get("from", {}).get("first_name", "Shopper")
            text = msg.get("text", "").strip()

            if not text:
                return

            if text.startswith("/start"):
                res = await self.handlers.handle_start(user_name)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif text.startswith("/catalog"):
                res = await self.handlers.handle_catalog()
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            elif text.startswith("/autopay"):
                lower = text.lower()
                if any(w in lower for w in ["on", "enable", "setup", "activate", "start"]):
                    res = await self.handlers.handle_autopay_toggle(True)
                elif any(w in lower for w in ["off", "disable", "pause", "revoke", "stop"]):
                    res = await self.handlers.handle_autopay_toggle(False)
                elif any(w in lower for w in ["verify", "check", "status"]):
                    res = await self.handlers.handle_autopay_verify()
                else:
                    res = await self.handlers.handle_autopay_status()
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))


            elif text.startswith("/help"):
                res = await self.handlers.handle_start(user_name)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))

            else:
                res = await self.handlers.handle_text_message(text)
                await self.send_message(chat_id, res["text"], res.get("reply_markup"))


    async def start_polling(self):
        """Starts the long-polling loop against Telegram Bot API."""
        self.running = True
        logger.info(f"🤖 Telegram Bot Gateway listening on @agentic_merchant_store_bot...")
        logger.info(f"🔗 Backend API Connected: {self.api_base}")

        async with httpx.AsyncClient(timeout=40.0) as client:
            while self.running:
                try:
                    payload = {"offset": self.offset, "timeout": 25}
                    res = await client.post(f"{self.tg_base_url}/getUpdates", json=payload)

                    if res.status_code == 200:
                        data = res.json()
                        updates = data.get("result", [])
                        for update in updates:
                            self.offset = update["update_id"] + 1
                            asyncio.create_task(self.process_update(update))
                    elif res.status_code == 409:
                        logger.warning("⏳ 409 Conflict: Previous Telegram session is closing. Reconnecting in 3s...")
                        await asyncio.sleep(3)
                    elif res.status_code == 401:
                        logger.error("❌ Invalid TELEGRAM_BOT_TOKEN provided. Please check .env")
                        break
                    else:
                        logger.warning(f"Telegram API returned status: {res.status_code}")
                        await asyncio.sleep(2)


                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Polling connection retry: {e}")
                    await asyncio.sleep(2)

        logger.info("🛑 Telegram Bot Service Stopped Cleanly.")


async def run_telegram_bot():
    """Entrypoint to initialize and launch Telegram bot service."""
    settings = get_settings()
    token = settings.TELEGRAM_BOT_TOKEN

    if not token or token.startswith("placeholder") or len(token) < 15:
        logger.info("ℹ️ TELEGRAM_BOT_TOKEN not configured in .env — skipping Telegram Bot startup.")
        return

    bot = TelegramBotService(token=token, api_base=settings.MERCHANT_API_BASE)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: setattr(bot, "running", False))
        except NotImplementedError:
            pass

    await bot.start_polling()


if __name__ == "__main__":
    try:
        asyncio.run(run_telegram_bot())
    except KeyboardInterrupt:
        pass
