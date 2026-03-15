from __future__ import annotations

import asyncio
from typing import Any

import httpx

from .config import settings
from .providers import ProviderError, chat_with_provider


class TelegramBotError(Exception):
    pass


def _telegram_api_url(method: str) -> str:
    if not settings.telegram_bot_token:
        raise TelegramBotError("TELEGRAM_BOT_TOKEN belum diset")
    return f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"


async def _get_updates(offset: int | None) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "timeout": settings.telegram_poll_timeout,
        "allowed_updates": ["message"],
    }
    if offset is not None:
        payload["offset"] = offset

    async with httpx.AsyncClient(timeout=settings.telegram_poll_timeout + 10) as client:
        response = await client.post(_telegram_api_url("getUpdates"), json=payload)

    if response.status_code != 200:
        raise TelegramBotError(f"getUpdates gagal {response.status_code}: {response.text}")

    data = response.json()
    if not data.get("ok"):
        raise TelegramBotError(f"getUpdates error: {data}")

    result: list[dict[str, Any]] = data.get("result", [])
    return result


async def _send_message(chat_id: int, text: str) -> None:
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(_telegram_api_url("sendMessage"), json=payload)

    if response.status_code != 200:
        raise TelegramBotError(f"sendMessage gagal {response.status_code}: {response.text}")


def _extract_user_message(update: dict[str, Any]) -> tuple[int, str] | None:
    message = update.get("message")
    if not message:
        return None

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if chat_id is None or not text:
        return None

    return chat_id, text


async def _handle_message(chat_id: int, text: str) -> None:
    if text == "/start":
        await _send_message(chat_id, "OpenClaw AI aktif. Kirim pesan apa saja untuk mulai chat.")
        return

    if text == "/help":
        await _send_message(chat_id, "Perintah: /start, /help. Selain itu langsung chat biasa.")
        return

    try:
        reply = await chat_with_provider(text, history=[])
    except ProviderError as error:
        reply = f"Provider error: {error}"
    except Exception as error:
        reply = f"Internal error: {error}"

    await _send_message(chat_id, reply)


async def run_telegram_bot() -> None:
    if not settings.telegram_bot_enabled:
        raise TelegramBotError(
            "Telegram bot belum aktif. Set TELEGRAM_BOT_ENABLED=true di file .env"
        )

    if not settings.telegram_bot_token:
        raise TelegramBotError("TELEGRAM_BOT_TOKEN belum diset")

    offset: int | None = None
    print("[telegram] bot polling started")

    while True:
        try:
            updates = await _get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                extracted = _extract_user_message(update)
                if not extracted:
                    continue

                chat_id, text = extracted
                await _handle_message(chat_id, text)
        except TelegramBotError as error:
            print(f"[telegram] warning: {error}")
            await asyncio.sleep(2)
        except Exception as error:
            print(f"[telegram] unexpected error: {error}")
            await asyncio.sleep(2)


def main() -> None:
    asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
