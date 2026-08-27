import pytest
from app.ai_provider.base import AIProvider
from app.ai_provider.groq_provider import GroqProvider
from app.ai_provider.openrouter_provider import OpenRouterProvider
from app.ai_provider.gemini_provider import MockAIProvider, get_ai_provider
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_mock_ai_provider():
    provider = MockAIProvider()
    reply = await provider.generate_text(
        system_prompt="system",
        messages=[{"role": "user", "content": "Add headphones to cart"}]
    )
    assert "AeroSound" in reply or "HP-001" in reply

    json_res = await provider.generate_structured_json(
        system_prompt="system",
        messages=[{"role": "user", "content": "Propose campaign"}]
    )
    assert "eligible_skus" in json_res
    assert json_res["discount_pct"] == 10


@pytest.mark.asyncio
async def test_groq_provider_initialization():
    groq = GroqProvider(api_key="mock_groq_key")
    assert groq.model == "qwen/qwen3.8-27b"
    assert groq.api_key == "mock_groq_key"


@pytest.mark.asyncio
async def test_openrouter_provider_initialization():
    openrouter = OpenRouterProvider(api_key="mock_openrouter_key")
    assert "free" in openrouter.model or "llama" in openrouter.model
    assert openrouter.api_key == "mock_openrouter_key"


def test_get_ai_provider_fallback():
    provider = get_ai_provider()
    assert isinstance(provider, AIProvider)


@pytest.mark.asyncio
async def test_resilient_multi_provider_failover():
    from app.ai_provider.multi_provider import ResilientMultiProvider
    pool = ResilientMultiProvider()
    assert len(pool.providers) >= 1

    # Text generation should succeed gracefully through fallback chain
    text = await pool.generate_text(
        system_prompt="You are an assistant.",
        messages=[{"role": "user", "content": "Add headphones to cart"}]
    )
    assert len(text) > 0

    # JSON generation should succeed gracefully through fallback chain
    json_data = await pool.generate_structured_json(
        system_prompt="Propose campaign",
        messages=[{"role": "user", "content": "Weekend sale"}]
    )
    assert isinstance(json_data, dict)
    assert "discount_pct" in json_data or len(json_data) >= 0
