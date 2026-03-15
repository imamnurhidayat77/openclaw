"""
Tests untuk config module.
"""

import os
from unittest.mock import patch

from app.config import _env_bool


def test_env_bool_true_values():
    """Should return True for truthy values."""
    with patch.dict(os.environ, {"TEST_VAR": "true"}):
        assert _env_bool("TEST_VAR") is True

    with patch.dict(os.environ, {"TEST_VAR": "1"}):
        assert _env_bool("TEST_VAR") is True

    with patch.dict(os.environ, {"TEST_VAR": "yes"}):
        assert _env_bool("TEST_VAR") is True

    with patch.dict(os.environ, {"TEST_VAR": "on"}):
        assert _env_bool("TEST_VAR") is True


def test_env_bool_false_values():
    """Should return False for falsy values."""
    with patch.dict(os.environ, {"TEST_VAR": "false"}):
        assert _env_bool("TEST_VAR") is False

    with patch.dict(os.environ, {"TEST_VAR": "0"}):
        assert _env_bool("TEST_VAR") is False


def test_env_bool_default():
    """Should return default when env var not set."""
    assert _env_bool("NONEXISTENT_VAR", False) is False
    assert _env_bool("NONEXISTENT_VAR", True) is True
