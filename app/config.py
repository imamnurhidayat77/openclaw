import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    provider: str = os.getenv("OPENCLAW_PROVIDER", "ollama").lower()

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    fallback_to_openai_on_ollama_error: bool = _env_bool(
        "OPENCLAW_FALLBACK_TO_OPENAI_ON_OLLAMA_ERROR", False
    )

    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_title: str = os.getenv("APP_TITLE", "OpenClaw AI")

    telegram_bot_enabled: bool = _env_bool("TELEGRAM_BOT_ENABLED", False)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_poll_timeout: int = int(os.getenv("TELEGRAM_POLL_TIMEOUT", "20"))


settings = Settings()
