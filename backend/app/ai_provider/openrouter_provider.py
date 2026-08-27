import json
import logging
import re
from typing import Any, Dict, List, Optional
import httpx

from app.ai_provider.base import AIProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenRouterProvider(AIProvider):
    """
    OpenRouter Free Tier Provider (OpenAI compatible).
    Supports free community models (e.g. meta-llama/llama-3.3-70b-instruct:free, deepseek/deepseek-r1:free, qwen/qwen-2.5-72b-instruct:free).
    """

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL or "meta-llama/llama-3.3-70b-instruct:free"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        if not self.api_key:
            return "I am your shopping assistant. How may I help you today?"

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/agentic-merchant-os",
            "X-Title": "Agentic Merchant OS",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(self.base_url, json=payload, headers=headers)
                if res.status_code != 200:
                    logger.error(f"OpenRouter Error {res.status_code}: {res.text}")
                    # Fallback to secondary free model if primary free model is busy
                    if res.status_code in [404, 429]:
                        payload["model"] = "qwen/qwen-2.5-72b-instruct:free"
                        res = await client.post(self.base_url, json=payload, headers=headers)

                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter generate_text failed: {e}")
            return "I apologize, I am temporarily having trouble reaching OpenRouter. Please try again."

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {}

        sys_inst = f"{system_prompt}\n\nCRITICAL: You must return valid raw JSON only. Do not wrap in markdown quotes or extra text."
        formatted_messages = [{"role": "system", "content": sys_inst}]
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/agentic-merchant-os",
            "X-Title": "Agentic Merchant OS",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(self.base_url, json=payload, headers=headers)
                data = res.json()
                raw_text = data["choices"][0]["message"]["content"]
                
                # Clean potential markdown fence if returned by model
                clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
                return json.loads(clean_json)
        except Exception as e:
            logger.error(f"OpenRouter generate_structured_json failed: {e}")
            return {}
