"""Global application settings loaded from environment / .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI / ChatGPT
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Grok / xAI
    grok_api_key: str = ""
    grok_base_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-beta"

    # ManyChat
    manychat_api_key: str = ""
    manychat_bot_id: str = ""

    # Web3
    web3_rpc_url: str = "http://localhost:8545"
    web3_chain_id: int = 1
    web3_wallet_address: str = ""
    web3_private_key: str = ""

    # Affiliate
    affiliate_default_tag: str = "clawbase44-20"

    # Scheduler
    scheduler_timezone: str = "UTC"


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
