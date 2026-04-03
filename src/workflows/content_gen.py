"""Content-generation workflow: ChatGPT + Grok → draft + review cycle."""

from __future__ import annotations

import logging
from typing import Any

from src.core.workflow import Step, Workflow, WorkflowEngine
from src.integrations.chatgpt import ChatGPTClient
from src.integrations.grok import GrokClient

logger = logging.getLogger(__name__)


class ContentGenerationWorkflow:
    """Generate, refine, and optionally review content using AI models.

    Steps
    -----
    1. **generate** — ChatGPT writes a first draft based on the topic.
    2. **review**   — Grok reviews the draft and suggests improvements.
    3. **refine**   — ChatGPT applies Grok's suggestions to produce the final copy.

    Usage::

        wf = ContentGenerationWorkflow()
        result = await wf.run(topic="AI automation tools", content_type="tweet")
        print(result["final_content"])
    """

    def __init__(self) -> None:
        self._chatgpt = ChatGPTClient()
        self._grok = GrokClient()
        self._engine = WorkflowEngine()

    async def run(
        self,
        topic: str,
        content_type: str = "blog post",
        tone: str = "professional",
        word_count: int = 300,
    ) -> dict[str, Any]:
        """Execute the full content generation pipeline.

        Parameters
        ----------
        topic:
            Subject of the content.
        content_type:
            E.g. ``"tweet"``, ``"email"``, ``"blog post"``.
        tone:
            Writing tone.
        word_count:
            Target word count for the draft.

        Returns
        -------
        dict[str, Any]
            Context dict with keys ``draft``, ``review``, and ``final_content``.
        """

        async def generate(ctx: dict[str, Any]) -> dict[str, Any]:
            draft = await self._chatgpt.generate_content(
                topic=topic,
                content_type=content_type,
                tone=tone,
                word_count=word_count,
            )
            logger.info("Draft generated (%d chars)", len(draft))
            return {"draft": draft}

        async def review(ctx: dict[str, Any]) -> dict[str, Any]:
            prompt = (
                f"Review the following {content_type} and provide concise, "
                "actionable improvement suggestions (3 bullet points max):\n\n"
                f"{ctx['draft']}"
            )
            feedback = await self._grok.chat(prompt)
            logger.info("Grok review received")
            return {"review": feedback}

        async def refine(ctx: dict[str, Any]) -> dict[str, Any]:
            prompt = (
                f"Improve the following {content_type} based on this feedback:\n\n"
                f"FEEDBACK:\n{ctx['review']}\n\n"
                f"ORIGINAL DRAFT:\n{ctx['draft']}\n\n"
                "Return only the improved version."
            )
            final = await self._chatgpt.chat(prompt, max_tokens=word_count * 2)
            logger.info("Final content produced (%d chars)", len(final))
            return {"final_content": final}

        workflow = Workflow(
            name="content_generation",
            steps=[
                Step(name="generate", fn=generate),
                Step(name="review", fn=review, skip_on_error=True),
                Step(name="refine", fn=refine, skip_on_error=True),
            ],
        )
        return await self._engine.run(workflow, {"topic": topic})
