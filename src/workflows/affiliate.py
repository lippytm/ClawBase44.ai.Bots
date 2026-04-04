"""Affiliate-content workflow: generate SEO copy with embedded affiliate tags."""

from __future__ import annotations

import logging
import re
from typing import Any

from config.settings import get_settings
from src.core.workflow import Step, Workflow, WorkflowEngine
from src.integrations.chatgpt import ChatGPTClient

logger = logging.getLogger(__name__)


class AffiliateWorkflow:
    """Generate affiliate-optimised content and inject tracking links.

    Steps
    -----
    1. **generate** — ChatGPT writes product-review / comparison content.
    2. **inject_tag** — Appends the affiliate tag to every bare URL found in
       the copy (simple URL pattern; swap for your link-shortener if needed).

    Usage::

        wf = AffiliateWorkflow()
        result = await wf.run(
            product="AI writing tools",
            affiliate_tag="clawbase44-20",
        )
        print(result["affiliate_content"])
    """

    _URL_RE = re.compile(r"https?://[^\s\"'<>]+(?<![.,;:!?)])")

    def __init__(self) -> None:
        self._chatgpt = ChatGPTClient()
        self._engine = WorkflowEngine()
        self._default_tag = get_settings().affiliate_default_tag

    async def run(
        self,
        product: str,
        affiliate_tag: str | None = None,
        content_type: str = "product review",
        word_count: int = 400,
    ) -> dict[str, Any]:
        """Generate affiliate content for *product*.

        Parameters
        ----------
        product:
            Product or service to review / promote.
        affiliate_tag:
            Affiliate tracking tag.  Falls back to the value from settings.
        content_type:
            E.g. ``"product review"``, ``"comparison"``, ``"listicle"``.
        word_count:
            Target word count.

        Returns
        -------
        dict[str, Any]
            Context dict with keys ``raw_content`` and ``affiliate_content``.
        """
        tag = affiliate_tag or self._default_tag

        async def generate(ctx: dict[str, Any]) -> dict[str, Any]:
            prompt = (
                f"Write a {word_count}-word {content_type} for '{product}'. "
                "Include realistic product URLs as examples. "
                "End with a persuasive call-to-action that encourages the reader to buy."
            )
            raw = await self._chatgpt.chat(prompt, max_tokens=word_count * 2)
            logger.info("Affiliate draft generated (%d chars)", len(raw))
            return {"raw_content": raw}

        async def inject_tag(ctx: dict[str, Any]) -> dict[str, Any]:
            def _append_tag(match: re.Match[str]) -> str:
                url = match.group(0)
                separator = "&" if "?" in url else "?"
                return f"{url}{separator}tag={tag}"

            tagged = self._URL_RE.sub(_append_tag, ctx["raw_content"])
            logger.info("Affiliate tags injected (tag=%s)", tag)
            return {"affiliate_content": tagged}

        workflow = Workflow(
            name="affiliate",
            steps=[
                Step(name="generate", fn=generate),
                Step(name="inject_tag", fn=inject_tag),
            ],
        )
        return await self._engine.run(workflow, {"product": product, "tag": tag})
