"""
Tests untuk provider module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.providers import (
    ProviderError,
    _chat_openai_compatible,
    _retry_wait_seconds,
    chat_with_provider,
)


# ════════════════════════════════════════════
# _chat_openai_compatible
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_chat_openai_success():
    """OpenAI compatible should return reply."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Hello from OpenAI!"}}]}

    with patch("app.providers.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await _chat_openai_compatible("hi", [])

    assert result == "Hello from OpenAI!"


@pytest.mark.anyio
async def test_chat_openai_no_api_key():
    """Missing API key should raise ProviderError."""
    with patch("app.providers.settings") as mock_settings:
        mock_settings.openai_api_key = ""
        mock_settings.openai_model = "gpt-4o-mini"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with pytest.raises(ProviderError, match="OPENAI_API_KEY"):
            await _chat_openai_compatible("hi", [])


# ════════════════════════════════════════════
# _retry_wait_seconds
# ════════════════════════════════════════════
def test_retry_wait_with_retry_after_header():
    """Should use Retry-After header value."""
    response = MagicMock()
    response.headers = {"Retry-After": "5"}
    assert _retry_wait_seconds(response, 1) == 5.0


def test_retry_wait_without_header():
    """Should use backoff schedule."""
    response = MagicMock()
    response.headers = {}
    assert _retry_wait_seconds(response, 1) == 1.5
    assert _retry_wait_seconds(response, 2) == 3.0


# ════════════════════════════════════════════
# chat_with_provider (unsupported provider)
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_unsupported_provider():
    """Unsupported provider should raise ProviderError."""
    with patch("app.providers.settings") as mock_settings:
        mock_settings.provider = "unknown_provider"

        with pytest.raises(ProviderError, match="tidak didukung"):
            await chat_with_provider("hi", [])
