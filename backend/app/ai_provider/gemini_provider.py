import json
import logging
import re
from typing import Any, Dict, List, Optional
from app.ai_provider.base import AIProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _generate_grounded_offline_fallback(user_msg: str) -> str:
    """Generates rich, grounded category responses when LLM is offline or unconfigured."""
    msg = user_msg.lower()

    if "iphone" in msg or "apple phone" in msg:
        return "Here are the details for **Apple iPhone 15 (128GB)** (SKU: `PHN-APL-15`) priced at **₹69,900.00**.\n\n• 48MP Camera & A16 Bionic\n• Super Retina XDR OLED Display\n• MagSafe Wireless Fast Charging Support\n\nWould you like me to add this to your cart?"
    elif "galaxy" in msg or "s24" in msg or "samsung" in msg:
        return "I found the **Samsung Galaxy S24 5G (256GB)** (SKU: `PHN-SAM-S24`) for **₹74,999.00** with Galaxy AI features and Dynamic AMOLED 2X. Would you like to add it to your cart?"
    elif "macbook" in msg or "laptop" in msg or "m3" in msg:
        return "We have the **Apple MacBook Air M3 (16GB, 512GB)** (SKU: `LAP-APL-M3`) for **₹1,14,900.00** and the **Dell XPS 13 Plus** (SKU: `LAP-DEL-XPS`) for **₹1,29,999.00**. Which one would you like to explore?"
    elif "headphone" in msg or "aerosound" in msg or "hp-001" in msg or "audio" in msg:
        return "I found the **AeroSound Wireless Headphones (HP-001)** for **₹4,499.00** featuring Active Noise Cancellation and 40-hour battery life. Would you like me to add it to your cart?"
    elif "cable" in msg or "usb-c" in msg:
        return "We have the **Braided USB-C Fast Charging Cable (2m)** (SKU: `CBL-USB-C`) for **₹399.00** in stock. Would you like to add it?"
    elif "magsafe" in msg or "charger" in msg:
        return "We have the **15W MagSafe Magnetic Wireless Fast Charger** (SKU: `ACC-MAG-CHG`) for **₹1,999.00**. Would you like to add it?"
    elif "watch" in msg or "smartwatch" in msg:
        return "We have the **Apple Watch Series 9 (45mm)** (SKU: `WCH-APL-S9`) for **₹38,900.00** and the **Galaxy Watch6 Classic** (SKU: `WCH-SAM-W6`) for **₹31,999.00**."
    elif "warranty" in msg or "shield" in msg:
        return "We offer the **2-Year Complete Mobile Shield** (SKU: `WRNTY-PHN-2Y`) for **₹2,499.00** and **1-Year Extended Care** (SKU: `WRNTY-1Y`) for **₹499.00**."
    elif "campaign" in msg or "discount" in msg or "promo" in msg or "sale" in msg:
        return "🎉 **Active Promotion Available!** Our Weekend Campaign applies up to 15% discount on catalog purchases with margin-safe bundle sweeteners. Add any item to view your verified discount!"
    elif "checkout" in msg or "pay" in msg or "order" in msg:
        return "To complete your purchase, click **'🛡️ Check Out via Commerce Guardian'** on the right panel to execute sub-50ms deterministic validation and launch the Razorpay payment gateway."
    elif "undo" in msg or "rollback" in msg:
        return "🔄 You can revert your cart to any previous state by typing 'undo'!"
    
    return "Hello! I am your AI Shopping Assistant for the store. You can search for smartphones (iPhone 15, Galaxy S24), laptops (MacBook Air, Dell XPS), smartwatches, or active promotional discounts. How can I help you today?"


class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI Client: {e}")

    async def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        last_user_msg = messages[-1].get("content", "") if messages else ""

        if not self._client:
            return _generate_grounded_offline_fallback(last_user_msg)

        try:
            contents = []
            for msg in messages:
                contents.append(f"{msg.get('role', 'user')}: {msg.get('content', '')}")
            
            prompt_str = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nCONVERSATION:\n" + "\n".join(contents)
            
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt_str,
                config={"temperature": temperature}
            )
            return response.text or _generate_grounded_offline_fallback(last_user_msg)
        except Exception as e:
            logger.warning(f"Gemini API unavailable or quota limit reached, seamlessly using deterministic grounded fallback: {e}")
            return _generate_grounded_offline_fallback(last_user_msg)

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        last_user_msg = messages[-1].get("content", "") if messages else ""

        default_campaign_proposal = {
            "eligible_skus": ["HP-001", "PHN-APL-15", "LAP-APL-M3"],
            "discount_pct": 10,
            "bundle_offer": {
                "trigger_sku": "PHN-APL-15",
                "addon_sku": "ACC-MAG-CHG",
                "addon_discount_pct": 50
            },
            "budget": 5000000,
            "duration_days": 7,
            "rationale": "High margin headroom on flagship lines with high companion accessory attach rate."
        }

        if not self._client:
            return default_campaign_proposal

        try:
            contents = []
            for msg in messages:
                contents.append(f"{msg.get('role', 'user')}: {msg.get('content', '')}")
            
            prompt_str = f"SYSTEM INSTRUCTIONS (Respond in pure JSON only):\n{system_prompt}\n\nDATA:\n" + "\n".join(contents)
            
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt_str,
                config={
                    "temperature": temperature,
                    "response_mime_type": "application/json"
                }
            )
            raw_text = response.text or "{}"
            return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"Gemini structured JSON unavailable, using deterministic rule fallback: {e}")
            return default_campaign_proposal


class MockAIProvider(AIProvider):
    """Deterministic mock provider for offline development & tests."""

    async def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        last_user_msg = messages[-1].get("content", "") if messages else ""
        return _generate_grounded_offline_fallback(last_user_msg)

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        return {
            "eligible_skus": ["HP-001", "PHN-APL-15"],
            "discount_pct": 10,
            "bundle_offer": {
                "trigger_sku": "PHN-APL-15",
                "addon_sku": "ACC-MAG-CHG",
                "addon_discount_pct": 50
            },
            "budget": 5000000,
            "duration_days": 7,
            "rationale": "High margin headroom on flagship lines with high companion attach rate."
        }


def get_ai_provider() -> AIProvider:
    from app.ai_provider.multi_provider import ResilientMultiProvider
    return ResilientMultiProvider()
