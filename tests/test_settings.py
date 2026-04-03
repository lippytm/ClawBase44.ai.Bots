"""Tests for the Settings model."""

from __future__ import annotations

import pytest

from config.settings import Settings, get_settings


def test_settings_defaults() -> None:
    s = Settings()
    assert s.openai_model == "gpt-4o"
    assert s.grok_model == "grok-beta"
    assert s.scheduler_timezone == "UTC"
    assert s.affiliate_default_tag == "clawbase44-20"


def test_settings_override_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4-turbo")
    monkeypatch.setenv("AFFILIATE_DEFAULT_TAG", "test-99")
    s = Settings()
    assert s.openai_model == "gpt-4-turbo"
    assert s.affiliate_default_tag == "test-99"


def test_get_settings_returns_singleton() -> None:
    import config.settings as cs

    cs._settings = None  # reset singleton
    a = get_settings()
    b = get_settings()
    assert a is b
