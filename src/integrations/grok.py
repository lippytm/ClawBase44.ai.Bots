"""Grok / xAI integration client.

Grok exposes an OpenAI-compatible endpoint, so we reuse the ``openai``
SDK pointed at the xAI base URL.
"""

from __future__ import annotations

import logging
from typing import Any

import openai

from config.settings import get_settings

logger = logging.getLogger(__name__)


class GrokClient:
    """Async wrapper around the Grok (xAI) Chat Completions API.

    Usage::

        client = GrokClient()
        reply = await client.chat("Summarise today's crypto news.")
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._client = openai.AsyncOpenAI(
            api_key=settings.grok_api_key,
            base_url=settings.grok_base_url,
        )
        self._model = settings.grok_model

    async def chat(
        self,
        prompt: str,
        system: str = "You are Grok, an autonomous AI assistant built by xAI.",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Send a single-turn chat message to Grok.

        Parameters
        ----------
        prompt:
            The user message.
        system:
            System instructions.
        temperature:
            Sampling temperature (0–2).
        max_tokens:
            Maximum tokens in the response.

        Returns
        -------
        str
            The model's reply text.
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
        logger.debug("Grok reply (%d chars)", len(reply))
        return reply

    async def analyze_market(self, asset: str) -> str:
        """Quick helper to request a market / trend analysis for *asset*.

        Parameters
        ----------
        asset:
            Token symbol or asset name (e.g. ``"Bitcoin"``).

        Returns
        -------
        str
            Analysis text.
        """
        prompt = (
            f"Provide a concise market analysis for {asset}: "
            "recent price action, key support/resistance levels, and near-term outlook."
        )
        return await self.chat(prompt)
