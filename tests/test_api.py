"""
Tests untuk FastAPI endpoints.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def async_client():
    """Create test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ════════════════════════════════════════════
# GET /health
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_health_endpoint(async_client):
    async with async_client as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "provider" in data


# ════════════════════════════════════════════
# GET / (index page)
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_index_returns_html(async_client):
    async with async_client as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# ════════════════════════════════════════════
# POST /api/chat - validation
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_chat_empty_message_returns_422(async_client):
    """Empty message should fail validation."""
    async with async_client as client:
        response = await client.post("/api/chat", json={"message": ""})

    assert response.status_code == 422


@pytest.mark.anyio
async def test_chat_missing_message_returns_422(async_client):
    """Missing message field should fail validation."""
    async with async_client as client:
        response = await client.post("/api/chat", json={})

    assert response.status_code == 422


# ════════════════════════════════════════════
# POST /api/chat - success (mocked provider)
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_chat_success(async_client, monkeypatch):
    """Chat endpoint should return reply from provider."""

    async def mock_provider(message, history):
        return f"Echo: {message}"

    monkeypatch.setattr("app.main.chat_with_provider", mock_provider)

    async with async_client as client:
        response = await client.post(
            "/api/chat",
            json={"message": "hello", "history": []},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Echo: hello"


@pytest.mark.anyio
async def test_chat_with_history(async_client, monkeypatch):
    """Chat endpoint should pass history to provider."""
    received_history = []

    async def mock_provider(message, history):
        received_history.extend(history)
        return "ok"

    monkeypatch.setattr("app.main.chat_with_provider", mock_provider)

    history = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]

    async with async_client as client:
        response = await client.post(
            "/api/chat",
            json={"message": "how are you?", "history": history},
        )

    assert response.status_code == 200
    assert len(received_history) == 2


# ════════════════════════════════════════════
# POST /api/chat - error handling
# ════════════════════════════════════════════
@pytest.mark.anyio
async def test_chat_provider_error_returns_400(async_client, monkeypatch):
    """ProviderError should return 400."""
    from app.providers import ProviderError

    async def mock_provider(message, history):
        raise ProviderError("Model not found")

    monkeypatch.setattr("app.main.chat_with_provider", mock_provider)

    async with async_client as client:
        response = await client.post(
            "/api/chat",
            json={"message": "test"},
        )

    assert response.status_code == 400
    assert "Model not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_chat_internal_error_returns_500(async_client, monkeypatch):
    """Unexpected error should return 500."""

    async def mock_provider(message, history):
        raise RuntimeError("unexpected")

    monkeypatch.setattr("app.main.chat_with_provider", mock_provider)

    async with async_client as client:
        response = await client.post(
            "/api/chat",
            json={"message": "test"},
        )

    assert response.status_code == 500
