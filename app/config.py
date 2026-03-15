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
    provider: str = os.getenv("OPENCLAW_PROVIDER", "openai").lower()

    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    # Railway injects PORT; fall back to APP_PORT then 8000
    app_port: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
    app_title: str = os.getenv("APP_TITLE", "OpenClaw AI")

    telegram_bot_enabled: bool = _env_bool("TELEGRAM_BOT_ENABLED", False)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_poll_timeout: int = int(os.getenv("TELEGRAM_POLL_TIMEOUT", "20"))


settings = Settings()
