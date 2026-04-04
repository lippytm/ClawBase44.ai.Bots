"""Abstract base class for all ClawBase bots."""

from __future__ import annotations

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseBot(abc.ABC):
    """All autonomous bots inherit from this class.

    Subclasses must implement :meth:`run` which performs the bot's primary
    action.  The optional :meth:`setup` / :meth:`teardown` hooks are called
    before and after :meth:`run` respectively.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._logger = logging.getLogger(f"bot.{name}")

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Called once before the first :meth:`run` invocation."""

    def teardown(self) -> None:
        """Called once after the last :meth:`run` invocation."""

    @abc.abstractmethod
    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the bot's primary action.

        Parameters
        ----------
        context:
            Arbitrary key/value data passed into the bot (e.g. from a
            preceding workflow step).

        Returns
        -------
        dict[str, Any]
            Output data that will be merged into the workflow context.
        """

    # ------------------------------------------------------------------
    # Convenience wrapper
    # ------------------------------------------------------------------

    async def execute(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the full lifecycle: setup → run → teardown."""
        ctx = context or {}
        self.setup()
        try:
            result = await self.run(ctx)
        finally:
            self.teardown()
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
