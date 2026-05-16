import pytest

from enki_ai.core import config


def test_require_env_returns_value(monkeypatch):
    monkeypatch.setenv("ENKI_TEST_ENV", "value123")
    assert config.require_env("ENKI_TEST_ENV") == "value123"


def test_require_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("ENKI_TEST_ENV_MISSING", raising=False)
    with pytest.raises(config.ConfigValidationError):
        config.require_env("ENKI_TEST_ENV_MISSING")
