"""ManyChat REST API integration client."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)

MANYCHAT_BASE = "https://api.manychat.com"


class ManyChatClient:
    """Async HTTP client for the ManyChat REST API.

    Supports sending messages and triggering flows for subscribers.

    Usage::

        client = ManyChatClient()
        await client.send_text(subscriber_id="123", text="Hello from ClawBase!")
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.manychat_api_key
        self._bot_id = settings.manychat_bot_id
        self._http = httpx.AsyncClient(
            base_url=MANYCHAT_BASE,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def send_text(self, subscriber_id: str, text: str) -> dict[str, Any]:
        """Send a plain-text message to a ManyChat subscriber.

        Parameters
        ----------
        subscriber_id:
            The ManyChat subscriber's unique ID.
        text:
            Message body.

        Returns
        -------
        dict[str, Any]
            Raw API response payload.
        """
        payload = {
            "subscriber_id": subscriber_id,
            "data": {"version": "v2", "content": {"type": "text", "text": text}},
        }
        response = await self._http.post("/fb/sending/sendContent", json=payload)
        response.raise_for_status()
        logger.debug("Sent text to subscriber %s", subscriber_id)
        return response.json()

    async def trigger_flow(self, subscriber_id: str, flow_ns: str) -> dict[str, Any]:
        """Trigger a ManyChat automation flow for a subscriber.

        Parameters
        ----------
        subscriber_id:
            The ManyChat subscriber's unique ID.
        flow_ns:
            The namespace / ID of the flow to trigger.

        Returns
        -------
        dict[str, Any]
            Raw API response payload.
        """
        payload = {"subscriber_id": subscriber_id, "flow_ns": flow_ns}
        response = await self._http.post("/fb/sending/sendFlow", json=payload)
        response.raise_for_status()
        logger.debug("Triggered flow '%s' for subscriber %s", flow_ns, subscriber_id)
        return response.json()

    async def get_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        """Fetch subscriber information by ID."""
        response = await self._http.get(f"/fb/subscriber/getInfo?subscriber_id={subscriber_id}")
        response.raise_for_status()
        return response.json()

    async def broadcast(self, flow_ns: str, tag: str | None = None) -> dict[str, Any]:
        """Send a broadcast to all (or tagged) subscribers.

        Parameters
        ----------
        flow_ns:
            The flow to broadcast.
        tag:
            Optional audience tag to target a segment.

        Returns
        -------
        dict[str, Any]
            Raw API response payload.
        """
        payload: dict[str, Any] = {"flow_ns": flow_ns}
        if tag:
            payload["tag"] = tag
        response = await self._http.post("/fb/sending/sendFlowToSubscribers", json=payload)
        response.raise_for_status()
        logger.info("Broadcast flow '%s' (tag=%s) sent", flow_ns, tag)
        return response.json()

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.aclose()
