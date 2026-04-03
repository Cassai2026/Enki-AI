"""Configuration for Enki AI loaded from environment / .env file."""
from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ENKI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider selection
    provider: Literal["openai", "anthropic"] = "openai"

    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o"

    # Anthropic
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Generation
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = (
        "You are Enki, a universal AI assistant named after the Sumerian god of"
        " wisdom and knowledge. You are helpful, accurate, and thoughtful. You"
        " leverage tools when available to give the best possible answer."
    )

    # Memory
    memory_window: int = 20  # 0 = unlimited

    # API server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @field_validator("memory_window")
    @classmethod
    def _non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("memory_window must be >= 0")
        return v


# Singleton — import this everywhere
settings = Settings()
