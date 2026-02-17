"""Centralised configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Defaults ────────────────────────────────────────────────────────────────

_DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
}


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application settings derived from env vars."""

    # LLM
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "anthropic"))
    llm_model: str = ""  # resolved in __post_init__
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # Database
    database_path: str = field(
        default_factory=lambda: os.getenv("DATABASE_PATH", "data/sample.db")
    )

    # Safety
    allow_write_queries: bool = field(
        default_factory=lambda: os.getenv("ALLOW_WRITE_QUERIES", "false").lower() == "true"
    )

    def __post_init__(self) -> None:
        # Resolve model name (frozen dataclass requires object.__setattr__)
        model = os.getenv("LLM_MODEL", "") or _DEFAULT_MODELS.get(self.llm_provider, "")
        object.__setattr__(self, "llm_model", model)

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path}"

    @property
    def db_path(self) -> Path:
        return Path(self.database_path)


def get_settings() -> Settings:
    """Factory that returns a fresh Settings instance."""
    return Settings()
