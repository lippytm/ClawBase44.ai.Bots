"""Social-media automation workflow: generate content → broadcast via ManyChat."""

from __future__ import annotations

import logging
from typing import Any

from src.core.workflow import Step, Workflow, WorkflowEngine
from src.integrations.chatgpt import ChatGPTClient
from src.integrations.manychat import ManyChatClient

logger = logging.getLogger(__name__)


class SocialMediaWorkflow:
    """Automate social-media messaging via ManyChat.

    Steps
    -----
    1. **generate** — ChatGPT writes a short social-media post.
    2. **broadcast** — Pushes the post to ManyChat subscribers.

    Usage::

        wf = SocialMediaWorkflow()
        result = await wf.run(
            topic="New AI tool launch",
            flow_ns="content20240101120000_post0",
            audience_tag="subscribers",
        )
    """

    def __init__(self) -> None:
        self._chatgpt = ChatGPTClient()
        self._manychat = ManyChatClient()
        self._engine = WorkflowEngine()

    async def run(
        self,
        topic: str,
        flow_ns: str,
        audience_tag: str | None = None,
    ) -> dict[str, Any]:
        """Generate a social post and broadcast it through ManyChat.

        Parameters
        ----------
        topic:
            Subject of the social-media post.
        flow_ns:
            ManyChat flow namespace to trigger for the broadcast.
        audience_tag:
            Optional ManyChat subscriber tag to target a segment.

        Returns
        -------
        dict[str, Any]
            Context dict with keys ``post`` and ``broadcast_result``.
        """

        async def generate(ctx: dict[str, Any]) -> dict[str, Any]:
            post = await self._chatgpt.generate_content(
                topic=topic,
                content_type="social media post",
                tone="engaging",
                word_count=50,
            )
            logger.info("Social post generated: %s…", post[:60])
            return {"post": post}

        async def broadcast(ctx: dict[str, Any]) -> dict[str, Any]:
            result = await self._manychat.broadcast(flow_ns=flow_ns, tag=audience_tag)
            logger.info("ManyChat broadcast result: %s", result)
            return {"broadcast_result": result}

        workflow = Workflow(
            name="social_media",
            steps=[
                Step(name="generate", fn=generate),
                Step(name="broadcast", fn=broadcast, skip_on_error=True),
            ],
        )
        return await self._engine.run(workflow, {"topic": topic})
