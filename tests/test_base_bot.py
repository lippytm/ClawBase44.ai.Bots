"""Tests for BaseBot lifecycle."""

from __future__ import annotations

import pytest

from src.core.base_bot import BaseBot


class _ConcreteBot(BaseBot):
    def __init__(self) -> None:
        super().__init__(name="test-bot")
        self.setup_called = False
        self.teardown_called = False

    def setup(self) -> None:
        self.setup_called = True

    def teardown(self) -> None:
        self.teardown_called = True

    async def run(self, context: dict) -> dict:
        return {"result": "ok", **context}


@pytest.mark.asyncio
async def test_execute_calls_lifecycle_hooks() -> None:
    bot = _ConcreteBot()
    result = await bot.execute({"input": 42})

    assert bot.setup_called
    assert bot.teardown_called
    assert result["result"] == "ok"
    assert result["input"] == 42


@pytest.mark.asyncio
async def test_execute_with_no_context() -> None:
    bot = _ConcreteBot()
    result = await bot.execute()
    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_teardown_called_even_after_error() -> None:
    class _ErrorBot(BaseBot):
        def __init__(self) -> None:
            super().__init__(name="error-bot")
            self.teardown_called = False

        def teardown(self) -> None:
            self.teardown_called = True

        async def run(self, context: dict) -> dict:
            raise RuntimeError("crash")

    bot = _ErrorBot()
    with pytest.raises(RuntimeError):
        await bot.execute()

    assert bot.teardown_called
