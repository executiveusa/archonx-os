"""
Channel Handlers
================
WhatsApp, Telegram, and Slack message routing.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("archonx.openclaw.channels")


@dataclass
class IncomingMessage:
    channel: str
    client_id: str
    sender: str
    text: str
    metadata: dict[str, Any] | None = None


@dataclass
class OutgoingMessage:
    channel: str
    client_id: str
    recipient: str
    text: str
    metadata: dict[str, Any] | None = None


class ChannelHandler(ABC):
    """Base class for channel integrations."""

    channel_name: str

    @abstractmethod
    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        """Parse an incoming webhook payload."""

    @abstractmethod
    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        """Send a message through this channel."""


class WhatsAppHandler(ChannelHandler):
    channel_name = "whatsapp"

    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        return IncomingMessage(
            channel="whatsapp",
            client_id=raw.get("client_id", ""),
            sender=raw.get("from", ""),
            text=raw.get("text", ""),
            metadata=raw,
        )

    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        logger.info("WhatsApp → %s: %s", message.recipient, message.text[:80])
        # In prod: call WhatsApp Business API
        return {"status": "sent", "channel": "whatsapp"}


class TelegramHandler(ChannelHandler):
    channel_name = "telegram"

    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        msg = raw.get("message", {})
        return IncomingMessage(
            channel="telegram",
            client_id=raw.get("client_id", ""),
            sender=str(msg.get("from", {}).get("id", "")),
            text=msg.get("text", ""),
            metadata=raw,
        )

    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        logger.info("Telegram → %s: %s", message.recipient, message.text[:80])
        # In prod: call Telegram Bot API
        return {"status": "sent", "channel": "telegram"}


class SlackHandler(ChannelHandler):
    channel_name = "slack"

    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        return IncomingMessage(
            channel="slack",
            client_id=raw.get("client_id", ""),
            sender=raw.get("user", ""),
            text=raw.get("text", ""),
            metadata=raw,
        )

    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        logger.info("Slack → %s: %s", message.recipient, message.text[:80])
        # In prod: call Slack Web API
        return {"status": "sent", "channel": "slack"}


class ChannelRouter:
    """Routes messages to the correct channel handler."""

    def __init__(self) -> None:
        self._handlers: dict[str, ChannelHandler] = {}

    def register(self, handler: ChannelHandler) -> None:
        self._handlers[handler.channel_name] = handler

    def register_defaults(self) -> None:
        self.register(WhatsAppHandler())
        self.register(TelegramHandler())
        self.register(SlackHandler())

    def register_orgo(self) -> None:
        """Register the Orgo computer-use channel."""
        from archonx.openclaw.orgo_channel import OrgoChannelHandler
        self.register(OrgoChannelHandler())

    async def route_incoming(self, channel: str, raw: dict[str, Any]) -> IncomingMessage:
        handler = self._handlers.get(channel)
        if not handler:
            raise ValueError(f"No handler for channel: {channel}")
        return await handler.receive(raw)

    async def route_outgoing(self, message: OutgoingMessage) -> dict[str, Any]:
        handler = self._handlers.get(message.channel)
        if not handler:
            raise ValueError(f"No handler for channel: {message.channel}")
        return await handler.send(message)
