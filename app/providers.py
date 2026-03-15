from __future__ import annotations

import asyncio

import httpx

from .config import settings


class ProviderError(Exception):
    pass


async def chat_with_provider(message: str, history: list[dict[str, str]]) -> str:
    provider = settings.provider

    if provider == "openai":
        return await _chat_openai_compatible(message, history)

    raise ProviderError(f"Unsupported provider: {provider}")


async def _chat_openai_compatible(message: str, history: list[dict[str, str]]) -> str:
    if not settings.openai_api_key:
        raise ProviderError("OPENAI_API_KEY is not set")

    payload_messages = [*history, {"role": "user", "content": message}]
    payload: dict[str, object] = {
        "model": settings.openai_model,
        "messages": payload_messages,
    }

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await _post_openai_with_retry(
                client=client,
                url=url,
                payload=payload,
                headers=headers,
            )
    except httpx.RequestError as error:
        raise ProviderError(
            "Failed to connect to OpenAI-compatible endpoint. "
            "Check OPENAI_BASE_URL and your internet connection."
        ) from error

    if response.status_code != 200:
        raise ProviderError(f"OpenAI-compatible error {response.status_code}: {response.text}")

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise ProviderError("Model response has no choices")

    reply: str = choices[0].get("message", {}).get("content", "")
    if not reply:
        raise ProviderError("Model response is empty")

    return reply


async def _post_openai_with_retry(
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, object],
    headers: dict[str, str],
) -> httpx.Response:
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 429:
            return response

        if attempt == max_attempts:
            break

        wait_seconds = _retry_wait_seconds(response, attempt)
        await asyncio.sleep(wait_seconds)

    raise ProviderError(
        "OpenAI-compatible error 429: too many requests. "
        "Please try again later, reduce chat frequency, or switch to another provider temporarily."
    )


def _retry_wait_seconds(response: httpx.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(1.0, float(retry_after))
        except ValueError:
            pass

    backoff_schedule = {1: 1.5, 2: 3.0}
    return backoff_schedule.get(attempt, 5.0)
