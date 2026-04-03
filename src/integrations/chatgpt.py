"""OpenAI / ChatGPT integration client."""

from __future__ import annotations

import logging
from typing import Any

import openai

from config.settings import get_settings

logger = logging.getLogger(__name__)


class ChatGPTClient:
    """Async wrapper around the OpenAI Chat Completions API.

    Usage::

        client = ChatGPTClient()
        reply = await client.chat("Write a tweet about AI automation.")
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def chat(
        self,
        prompt: str,
        system: str = "You are a helpful autonomous automation assistant.",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Send a single-turn chat message and return the assistant reply.

        Parameters
        ----------
        prompt:
            The user message.
        system:
            System instructions for the model.
        temperature:
            Sampling temperature (0–2).
        max_tokens:
            Maximum tokens in the response.

        Returns
        -------
        str
            The assistant's reply text.
        """
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        reply: str = response.choices[0].message.content or ""
        logger.debug("ChatGPT reply (%d chars)", len(reply))
        return reply

    async def generate_content(
        self,
        topic: str,
        content_type: str = "blog post",
        tone: str = "professional",
        word_count: int = 300,
    ) -> str:
        """High-level helper to generate marketing / affiliate content.

        Parameters
        ----------
        topic:
            Subject matter for the content.
        content_type:
            E.g. ``"tweet"``, ``"blog post"``, ``"email"``.
        tone:
            Writing tone, e.g. ``"casual"``, ``"professional"``.
        word_count:
            Approximate desired word count.

        Returns
        -------
        str
            Generated content.
        """
        prompt = (
            f"Write a {tone} {content_type} about '{topic}'. "
            f"Target approximately {word_count} words. "
            "Include a clear call-to-action."
        )
        return await self.chat(prompt, max_tokens=word_count * 2)
