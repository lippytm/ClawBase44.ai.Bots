"""Tests for the WorkflowEngine."""

from __future__ import annotations

import pytest

from src.core.workflow import Step, Workflow, WorkflowEngine


@pytest.mark.asyncio
async def test_workflow_runs_steps_in_order() -> None:
    order: list[str] = []

    async def step_a(ctx: dict) -> dict:
        order.append("a")
        return {"a": 1}

    async def step_b(ctx: dict) -> dict:
        order.append("b")
        assert ctx["a"] == 1
        return {"b": 2}

    workflow = Workflow(name="test", steps=[Step("a", step_a), Step("b", step_b)])
    engine = WorkflowEngine()
    result = await engine.run(workflow)

    assert order == ["a", "b"]
    assert result == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_workflow_propagates_initial_context() -> None:
    async def step(ctx: dict) -> dict:
        return {"seen": ctx.get("seed")}

    workflow = Workflow(name="test", steps=[Step("s", step)])
    engine = WorkflowEngine()
    result = await engine.run(workflow, initial_context={"seed": "hello"})

    assert result["seen"] == "hello"


@pytest.mark.asyncio
async def test_workflow_skip_on_error() -> None:
    async def bad_step(ctx: dict) -> dict:
        raise RuntimeError("boom")

    async def good_step(ctx: dict) -> dict:
        return {"ok": True}

    workflow = Workflow(
        name="test",
        steps=[
            Step("bad", bad_step, skip_on_error=True),
            Step("good", good_step),
        ],
    )
    engine = WorkflowEngine()
    result = await engine.run(workflow)

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_workflow_raises_on_error_when_not_skipped() -> None:
    async def bad_step(ctx: dict) -> dict:
        raise ValueError("intentional")

    workflow = Workflow(name="test", steps=[Step("bad", bad_step, skip_on_error=False)])
    engine = WorkflowEngine()

    with pytest.raises(ValueError, match="intentional"):
        await engine.run(workflow)
