"""APScheduler-backed cron/interval scheduler for autonomous bots."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import get_settings

logger = logging.getLogger(__name__)

AsyncJobFn = Callable[[], Coroutine[Any, Any, None]]


class BotScheduler:
    """Thin wrapper around :class:`AsyncIOScheduler` with convenience helpers.

    Usage::

        scheduler = BotScheduler()
        scheduler.add_cron_job(my_bot_fn, hour=9, minute=0)
        scheduler.add_interval_job(my_poll_fn, minutes=30)
        await scheduler.start()
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)

    # ------------------------------------------------------------------
    # Job registration
    # ------------------------------------------------------------------

    def add_cron_job(self, fn: AsyncJobFn, job_id: str | None = None, **cron_kwargs: Any) -> None:
        """Schedule *fn* with a cron expression.

        Extra keyword arguments are forwarded to :class:`CronTrigger` (e.g.
        ``hour=9``, ``minute=0``, ``day_of_week="mon-fri"``).
        """
        trigger = CronTrigger(**cron_kwargs)
        jid = job_id or fn.__name__
        self._scheduler.add_job(fn, trigger=trigger, id=jid, replace_existing=True)
        logger.info("Scheduled cron job '%s': %s", jid, cron_kwargs)

    def add_interval_job(
        self, fn: AsyncJobFn, job_id: str | None = None, **interval_kwargs: Any
    ) -> None:
        """Schedule *fn* at a fixed interval.

        Extra keyword arguments are forwarded to :class:`IntervalTrigger` (e.g.
        ``minutes=30``, ``hours=1``).
        """
        trigger = IntervalTrigger(**interval_kwargs)
        jid = job_id or fn.__name__
        self._scheduler.add_job(fn, trigger=trigger, id=jid, replace_existing=True)
        logger.info("Scheduled interval job '%s': %s", jid, interval_kwargs)

    def remove_job(self, job_id: str) -> None:
        """Remove a previously registered job by its ID."""
        self._scheduler.remove_job(job_id)
        logger.info("Removed job '%s'", job_id)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the scheduler (non-blocking)."""
        self._scheduler.start()
        logger.info("BotScheduler started")

    async def stop(self) -> None:
        """Gracefully shut down the scheduler."""
        self._scheduler.shutdown(wait=True)
        logger.info("BotScheduler stopped")

    @property
    def jobs(self) -> list[Any]:
        """Return all currently scheduled jobs."""
        return self._scheduler.get_jobs()
