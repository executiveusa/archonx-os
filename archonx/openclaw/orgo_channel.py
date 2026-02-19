"""
Orgo Channel Handler
====================
OpenClaw channel that routes tasks to Orgo computer-use VMs.

When a message arrives on the "orgo" channel, it launches a VM session
and translates the task into browser actions.
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.openclaw.channels import ChannelHandler, IncomingMessage, OutgoingMessage
from archonx.openclaw.orgo import OrgoClient

logger = logging.getLogger("archonx.openclaw.orgo_channel")


class OrgoChannelHandler(ChannelHandler):
    """Channel handler for Orgo computer-use tasks."""

    channel_name = "orgo"

    def __init__(self, orgo_client: OrgoClient | None = None) -> None:
        self._orgo = orgo_client or OrgoClient()

    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        """Receive a task request destined for Orgo."""
        return IncomingMessage(
            channel="orgo",
            client_id=raw.get("client_id", ""),
            sender=raw.get("sender", "kernel"),
            text=raw.get("task", ""),
            metadata=raw,
        )

    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        """
        Send a task to Orgo — launches a VM session and starts execution.
        """
        session = await self._orgo.create_session(
            task=message.text,
            config=message.metadata.get("config"),
        )
        logger.info(
            "Orgo channel: launched session %s for: %s",
            session.session_id,
            message.text[:80],
        )
        return {
            "status": "launched",
            "channel": "orgo",
            "session_id": session.session_id,
            "vm_url": session.vm_url,
        }
