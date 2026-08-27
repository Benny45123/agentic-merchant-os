import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.ai_provider.base import AIProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    """
    Groq High-Speed LLM Provider (OpenAI compatible).
    Supports ultra-fast inference with free tier limits (e.g. qwen/qwen3.8-27b, llama-3.3-70b-versatile).
    """

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL or "qwen/qwen3.8-27b"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

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
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(self.base_url, json=payload, headers=headers)
                if res.status_code != 200:
                    logger.error(f"Groq API Error {res.status_code}: {res.text}")
                    # Fallback to secondary lightweight Groq model if specific preview model has issues
                    if "model_not_found" in res.text or res.status_code == 404:
                        logger.info("Falling back to llama-3.1-8b-instant on Groq...")
                        payload["model"] = "llama-3.1-8b-instant"
                        res = await client.post(self.base_url, json=payload, headers=headers)

                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq generate_text failed: {e}")
            return "I apologize, I am temporarily having trouble reaching the Groq service. Please try again."

    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {}

        sys_inst = f"{system_prompt}\n\nIMPORTANT: You must respond in valid pure JSON format only with no surrounding markdown or explanation."
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
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(self.base_url, json=payload, headers=headers)
                if res.status_code != 200:
                    logger.error(f"Groq JSON API Error {res.status_code}: {res.text}")
                    if "model_not_found" in res.text or res.status_code == 404:
                        payload["model"] = "llama-3.1-8b-instant"
                        res = await client.post(self.base_url, json=payload, headers=headers)

                data = res.json()
                raw_text = data["choices"][0]["message"]["content"]
                return json.loads(raw_text)
        except Exception as e:
            logger.error(f"Groq generate_structured_json failed: {e}")
            return {}
