"""
Channel Handlers
================
WhatsApp, Telegram, and Slack message routing.

Security (BEAD-019 / Sprint 2):
- Webhook signature verification per channel
- Message sanitization through SafetyLayer
- Per-channel rate limiting
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
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

    def verify_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> bool:
        """Default HMAC-SHA256 webhook verification. Override per channel."""
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


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
        return {"status": "sent", "channel": "whatsapp"}

    def verify_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> bool:
        """WhatsApp uses HMAC-SHA256."""
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)


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
        return {"status": "sent", "channel": "telegram"}

    def verify_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> bool:
        """Telegram uses secret_token header (simple equality)."""
        return hmac.compare_digest(signature, secret)


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
        return {"status": "sent", "channel": "slack"}

    def verify_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> bool:
        """Slack signing secret v0 verification."""
        # Slack sends timestamp:body, signs with v0=hmac
        expected = "v0=" + hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


# ---------------------------------------------------------------------------
# Per-channel rate limiter
# ---------------------------------------------------------------------------

class ChannelRateLimiter:
    """Simple sliding-window rate limiter per channel + sender."""

    def __init__(self, max_per_minute: int = 30) -> None:
        self.max_per_minute = max_per_minute
        self._windows: dict[str, list[float]] = defaultdict(list)

    def allow(self, channel: str, sender: str) -> bool:
        key = f"{channel}:{sender}"
        now = time.time()
        cutoff = now - 60.0
        window = [t for t in self._windows[key] if t > cutoff]
        if len(window) >= self.max_per_minute:
            logger.warning("Rate limit hit for %s", key)
            return False
        window.append(now)
        self._windows[key] = window
        return True


# ---------------------------------------------------------------------------
# Channel Router (upgraded)
# ---------------------------------------------------------------------------

class ChannelRouter:
    """Routes messages to the correct channel handler with security layers."""

    def __init__(self, rate_limit_per_min: int = 30) -> None:
        self._handlers: dict[str, ChannelHandler] = {}
        self._secrets: dict[str, str] = {}
        self._rate_limiter = ChannelRateLimiter(max_per_minute=rate_limit_per_min)
        self._sanitizer: Any = None

    @property
    def sanitizer(self) -> Any:
        if self._sanitizer is None:
            from archonx.security.safety_layer import Sanitizer
            self._sanitizer = Sanitizer()
        return self._sanitizer

    def register(self, handler: ChannelHandler, webhook_secret: str = "") -> None:
        self._handlers[handler.channel_name] = handler
        if webhook_secret:
            self._secrets[handler.channel_name] = webhook_secret

    def register_defaults(self) -> None:
        self.register(WhatsAppHandler())
        self.register(TelegramHandler())
        self.register(SlackHandler())

    def register_orgo(self) -> None:
        """Register the Orgo computer-use channel."""
        from archonx.openclaw.orgo_channel import OrgoChannelHandler
        self.register(OrgoChannelHandler())

    def verify_webhook(
        self, channel: str, payload: bytes, signature: str
    ) -> bool:
        """Verify webhook signature for a channel."""
        handler = self._handlers.get(channel)
        secret = self._secrets.get(channel, "")
        if not handler or not secret:
            return not secret  # No secret configured = pass
        return handler.verify_signature(payload, signature, secret)

    async def route_incoming(
        self, channel: str, raw: dict[str, Any]
    ) -> IncomingMessage:
        handler = self._handlers.get(channel)
        if not handler:
            raise ValueError(f"No handler for channel: {channel}")
        msg = await handler.receive(raw)
        # Sanitize incoming text
        msg.text = self.sanitizer.sanitize(msg.text)
        return msg

    async def route_outgoing(self, message: OutgoingMessage) -> dict[str, Any]:
        handler = self._handlers.get(message.channel)
        if not handler:
            raise ValueError(f"No handler for channel: {message.channel}")
        # Rate limit on outgoing
        if not self._rate_limiter.allow(message.channel, message.recipient):
            return {"status": "rate_limited", "channel": message.channel}
        return await handler.send(message)
