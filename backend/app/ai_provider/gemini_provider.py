import json
import logging
from typing import Any, Dict, List, Optional
from app.ai_provider.base import AIProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)


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
        if not self._client:
            return "I am your shopping assistant. How may I help you today?"

        try:
            # Combine system prompt and user history
            contents = []
            for msg in messages:
                contents.append(f"{msg.get('role', 'user')}: {msg.get('content', '')}")
            
            prompt_str = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nCONVERSATION:\n" + "\n".join(contents)
            
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt_str,
                config={"temperature": temperature}
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generate_text failed: {e}")
            return "I apologize, I am temporarily having trouble reaching the LLM service. Please try again."

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        if not self._client:
            return {}

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
            logger.error(f"Gemini generate_structured_json failed: {e}")
            return {}


class MockAIProvider(AIProvider):
    """Deterministic mock provider for offline development & tests."""

    async def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        user_msg = messages[-1].get("content", "").lower() if messages else ""
        if "headphone" in user_msg or "wireless" in user_msg:
            return "I found the AeroSound Wireless Headphones (HP-001) for ₹4,499. Would you like to add it to your cart?"
        elif "warranty" in user_msg:
            return "I can add the 1-Year Extended Care Warranty (WRNTY-1Y) for ₹499. Would you like to proceed?"
        return "I am here to help you shop our catalog. What are you looking for?"

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        return {
            "eligible_skus": ["HP-001", "HP-002"],
            "discount_pct": 10,
            "bundle_offer": {
                "trigger_sku": "HP-001",
                "addon_sku": "CASE-HP",
                "addon_discount_pct": 50
            },
            "budget": 5000000,
            "duration_days": 7,
            "rationale": "High margin headroom on HP-001 audio line with high historical attach rate."
        }


def get_ai_provider() -> AIProvider:
    from app.ai_provider.multi_provider import ResilientMultiProvider
    return ResilientMultiProvider()
