"""Tests for configuration."""

from src.config import Settings


def test_defaults():
    s = Settings()
    assert s.llm_provider == "anthropic"
    assert s.database_url.startswith("sqlite:///")
    assert s.allow_write_queries is False


def test_model_resolution():
    s = Settings(llm_provider="openai")
    assert s.llm_model == "gpt-4o"
