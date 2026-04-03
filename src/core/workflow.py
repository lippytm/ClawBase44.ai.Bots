"""Workflow engine — chains Steps into an ordered pipeline."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

StepFn = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]


@dataclass
class Step:
    """A single unit of work inside a :class:`Workflow`.

    Parameters
    ----------
    name:
        Human-readable label shown in logs.
    fn:
        Async callable that accepts and returns a context dict.
    skip_on_error:
        When *True* exceptions are logged but the pipeline continues.
    """

    name: str
    fn: StepFn
    skip_on_error: bool = False


@dataclass
class Workflow:
    """An ordered collection of :class:`Step` objects."""

    name: str
    steps: list[Step] = field(default_factory=list)

    def add_step(self, step: Step) -> Workflow:
        """Append a step and return *self* for chaining."""
        self.steps.append(step)
        return self


class WorkflowEngine:
    """Executes :class:`Workflow` instances sequentially.

    Each step receives the accumulated context dict produced by all
    preceding steps and may return additional or updated keys.
    """

    async def run(
        self,
        workflow: Workflow,
        initial_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run all steps in *workflow* and return the final context.

        Parameters
        ----------
        workflow:
            The workflow to execute.
        initial_context:
            Seed data made available to the first step.

        Returns
        -------
        dict[str, Any]
            Accumulated context after all steps have run.
        """
        context: dict[str, Any] = initial_context or {}
        logger.info("▶  Workflow '%s' started (%d steps)", workflow.name, len(workflow.steps))

        for idx, step in enumerate(workflow.steps, start=1):
            logger.info("  [%d/%d] Running step: %s", idx, len(workflow.steps), step.name)
            try:
                result = await step.fn(context)
                context.update(result or {})
            except Exception:
                if step.skip_on_error:
                    logger.exception("  Step '%s' failed — skipping", step.name)
                else:
                    logger.exception("  Step '%s' failed — aborting workflow", step.name)
                    raise

        logger.info("✓  Workflow '%s' completed", workflow.name)
        return context
