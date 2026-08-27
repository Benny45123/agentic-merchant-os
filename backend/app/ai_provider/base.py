from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AIProvider(ABC):
    """Abstract interface for LLM provider."""

    @abstractmethod
    async def generate_text(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        """Generate conversational text response."""
        pass

    @abstractmethod
    async def generate_structured_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """Generate schema-validated structured JSON output."""
        pass
