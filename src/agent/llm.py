"""LLM factory — returns the right chat model based on configuration."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from src.config import Settings


def build_llm(settings: Settings) -> BaseChatModel:
    """Instantiate the LLM for the configured provider.

    Supports ``anthropic`` and ``openai``. Raises ``ValueError`` for
    unknown providers.
    """
    provider = settings.llm_provider.lower()

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
            max_tokens=4096,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        kwargs: dict = {
            "model": settings.llm_model,
            "api_key": settings.openai_api_key,
            "temperature": 0,
        }
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url

        return ChatOpenAI(**kwargs)

    raise ValueError(
        f"Unsupported LLM provider: '{provider}'. Choose 'anthropic' or 'openai'."
    )
