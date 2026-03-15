"""
Shared fixtures untuk semua tests.
"""

import os

import pytest

# Set env vars SEBELUM import app modules
os.environ.setdefault("OPENCLAW_PROVIDER", "ollama")
os.environ.setdefault("OPENAI_API_KEY", "test-key-123")


@pytest.fixture
def anyio_backend():
    return "asyncio"
