"""
BEAD-POPEBOT-001 — Popebot orchestrator
=========================================
Routes CommMessage objects to the correct channel handler.
Enforces rate limits. Agent-signs all outgoing messages.

Usage:
    popebot = Popebot(vault=vault)
    result = await popebot.send(CommMessage(
        from_agent_id="pauli_king",
        to="admin@archonx.io",
        channel=Channel.EMAIL,
        body="Kernel boot complete.",
        priority=MessagePriority.NORMAL,
    ))
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from typing import Any

from archonx.comms.channels.email import EmailChannel
from archonx.comms.channels.linkedin import LinkedInChannel
from archonx.comms.channels.slack import SlackChannel
from archonx.comms.channels.sms import SMSChannel
from archonx.comms.channels.twitter import TwitterChannel
from archonx.comms.models import (
    Channel,
    CommMessage,
    CommResult,
    MessagePriority,
    MessageStatus,
)
from archonx.comms.rate_limiter import RateLimiter

logger = logging.getLogger("archonx.comms.popebot")

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class Popebot:
    """Unified communication dispatcher for ArchonX OS agents."""

    def __init__(self, vault: Any | None = None, rate_limiter: RateLimiter | None = None) -> None:
        self._vault = vault
        self._rate = rate_limiter or RateLimiter()
        self._channels: dict[Channel, Any] = {
            Channel.EMAIL: EmailChannel(vault=vault),
            Channel.SLACK: SlackChannel(vault=vault),
            Channel.SMS: SMSChannel(vault=vault),
            Channel.TWITTER: TwitterChannel(vault=vault),
            Channel.LINKEDIN: LinkedInChannel(vault=vault),
        }

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def channels(self) -> dict:
        return self._channels

    @property
    def rate_limiter(self) -> "RateLimiter":
        return self._rate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def send(self, message: CommMessage) -> CommResult:
        """Route a single CommMessage to its channel handler."""
        # Stamp message_id if absent
        if not message.message_id:
            message.message_id = str(uuid.uuid4())

        is_critical = message.priority == MessagePriority.CRITICAL

        # Rate-limit check
        if not await self._rate.consume(message.channel, bypass_for_critical=is_critical):
            logger.warning(
                "Popebot: rate limit exceeded for channel %s (message %s)",
                message.channel.value,
                message.message_id,
            )
            message.status = MessageStatus.QUEUED
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=message.channel,
                error="rate_limit_exceeded",
                retry_after=self._rate.retry_after(message.channel),
            )

        handler = self._channels.get(message.channel)
        if handler is None:
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=message.channel,
                error=f"No handler for channel {message.channel.value}",
            )

        message.status = MessageStatus.PENDING
        result = await handler.send(message)

        message.status = MessageStatus.SENT if result.success else MessageStatus.FAILED
        message.sent_at = datetime.now(timezone.utc)

        if result.success:
            logger.info(
                "Popebot: ✓ %s → %s (%s)",
                message.from_agent_id, message.channel.value, message.message_id,
            )
        else:
            logger.error(
                "Popebot: ✗ %s → %s (%s): %s",
                message.from_agent_id, message.channel.value, message.message_id, result.error,
            )

        return result

    async def send_template(
        self,
        template_id: str,
        channel: Channel,
        from_agent_id: str,
        to: str,
        variables: dict[str, str] | None = None,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> CommResult:
        """Render a template from comms/templates/ and send it."""
        template_path = _TEMPLATES_DIR / f"{template_id}.txt"
        if not template_path.exists():
            return CommResult(
                success=False,
                message_id=str(uuid.uuid4()),
                channel=channel,
                error=f"Template not found: {template_id}",
            )

        raw = template_path.read_text(encoding="utf-8")
        body = Template(raw).safe_substitute(variables or {})

        # First line that starts with "SUBJECT:" is used as email subject
        subject: str | None = None
        lines = body.splitlines()
        if lines and lines[0].upper().startswith("SUBJECT:"):
            subject = lines[0][8:].strip()
            body = "\n".join(lines[1:]).strip()

        message = CommMessage(
            from_agent_id=from_agent_id,
            to=to,
            channel=channel,
            body=body,
            subject=subject,
            template_id=template_id,
            priority=priority,
        )
        return await self.send(message)

    async def broadcast(
        self,
        from_agent_id: str,
        body: str,
        channels: list[Channel],
        to_map: dict[Channel, str],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> dict[Channel, CommResult]:
        """Send the same message on multiple channels simultaneously."""
        import asyncio

        tasks = []
        for channel in channels:
            if channel not in to_map:
                continue
            msg = CommMessage(
                from_agent_id=from_agent_id,
                to=to_map[channel],
                channel=channel,
                body=body,
                priority=priority,
            )
            tasks.append((channel, self.send(msg)))

        results: dict[Channel, CommResult] = {}
        for channel, coro in tasks:
            results[channel] = await coro  # sequential to respect rate limits

        return results
