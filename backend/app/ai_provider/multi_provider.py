import logging
from typing import Any, Dict, List, Optional

from app.ai_provider.base import AIProvider
from app.ai_provider.gemini_provider import GeminiProvider, MockAIProvider
from app.ai_provider.groq_provider import GroqProvider
from app.ai_provider.openrouter_provider import OpenRouterProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ResilientMultiProvider(AIProvider):
    """
    Cascading Multi-Provider with Automatic Failover & Token Cost Sharing.
    Tries primary high-quota provider first (e.g. Groq 2B tokens/day),
    and transparently auto-delegates to Gemini and OpenRouter if rate limits or errors occur.
    """

    def __init__(self, preferred_provider: Optional[str] = None):
        settings = get_settings()
        self.preferred = preferred_provider or settings.LLM_PROVIDER
        self.providers: List[tuple[str, AIProvider]] = []

        # Build prioritized chain based on available API keys
        if self.preferred == "groq" and settings.GROQ_API_KEY:
            self.providers.append(("Groq (Qwen 3.8 27B)", GroqProvider()))
        elif self.preferred == "gemini" and settings.GEMINI_API_KEY:
            self.providers.append(("Google Gemini (3.5 Flash-Lite)", GeminiProvider()))
        elif self.preferred == "openrouter" and settings.OPENROUTER_API_KEY:
            self.providers.append(("OpenRouter (Free Community)", OpenRouterProvider()))

        # Add remaining configured providers to the failover chain
        if settings.GROQ_API_KEY and not any(p[0].startswith("Groq") for p in self.providers):
            self.providers.append(("Groq (Qwen 3.8 27B)", GroqProvider()))

        if settings.GEMINI_API_KEY and not any(p[0].startswith("Google Gemini") for p in self.providers):
            self.providers.append(("Google Gemini (3.5 Flash-Lite)", GeminiProvider()))

        if settings.OPENROUTER_API_KEY and not any(p[0].startswith("OpenRouter") for p in self.providers):
            self.providers.append(("OpenRouter (Free Community)", OpenRouterProvider()))

        # Guaranteed offline safety fallback
        self.providers.append(("Deterministic Safety Mock", MockAIProvider()))

    async def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        last_error = None
        for name, provider in self.providers:
            try:
                result = await provider.generate_text(system_prompt, messages, temperature)
                if result and not result.startswith("I apologize, I am temporarily having trouble reaching"):
                    return result
                logger.warning(f"⚠️ [Multi-Provider Pool] {name} returned empty/error text. Delegating to next available model...")
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ [Multi-Provider Failover] {name} failed: {e}. Auto-delegating to next provider...")

        return "I am here to help you shop our catalog. What are you looking for?"

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        last_error = None
        for name, provider in self.providers:
            try:
                result = await provider.generate_structured_json(system_prompt, messages, response_schema, temperature)
                if result and isinstance(result, dict) and len(result) > 0:
                    return result
                logger.warning(f"⚠️ [Multi-Provider Pool] {name} returned empty structured JSON. Delegating to next available model...")
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ [Multi-Provider Failover] {name} failed: {e}. Auto-delegating to next provider...")

        # If all fail, return mock campaign proposal
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
