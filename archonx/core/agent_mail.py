"""
Agent Mail
==========
Internal messaging system for inter-agent communication.

Agents can send messages to each other, broadcast to crews, or post to
channels. Messages are typed (request, response, broadcast, alert) and
carry structured payloads.

Inspired by BrennerBot protocol patterns — structured async message
passing that compounds through the flywheel.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable

logger = logging.getLogger("archonx.core.agent_mail")


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ALERT = "alert"
    FLYWHEEL = "flywheel"  # Improvement notifications


@dataclass
class AgentMessage:
    id: str
    sender: str          # agent_id
    recipient: str       # agent_id or "crew:white" or "broadcast"
    message_type: MessageType
    subject: str
    payload: dict[str, Any] = field(default_factory=dict)
    reply_to: str | None = None  # message id this replies to
    timestamp: float = field(default_factory=time.time)
    read: bool = False


class AgentMailbox:
    """
    Central mail exchange for all 64 agents.

    Features:
    - Direct agent-to-agent messaging
    - Crew-wide broadcasts (crew:white, crew:black)
    - Global broadcasts
    - Subscription-based handlers for reactive patterns
    """

    def __init__(self) -> None:
        self._inbox: dict[str, list[AgentMessage]] = defaultdict(list)
        self._counter = 0
        self._handlers: dict[str, list[Callable[[AgentMessage], Awaitable[None]]]] = defaultdict(list)

    def send(
        self,
        sender: str,
        recipient: str,
        message_type: MessageType,
        subject: str,
        payload: dict[str, Any] | None = None,
        reply_to: str | None = None,
    ) -> AgentMessage:
        """Send a message. Returns the message object."""
        self._counter += 1
        msg = AgentMessage(
            id=f"mail-{self._counter:06d}",
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            subject=subject,
            payload=payload or {},
            reply_to=reply_to,
        )

        if recipient == "broadcast":
            # Deliver to all inboxes
            for box in self._inbox.values():
                box.append(msg)
        elif recipient.startswith("crew:"):
            # We'll let the kernel resolve crew membership
            self._inbox[recipient].append(msg)
        else:
            self._inbox[recipient].append(msg)

        logger.debug("Mail: %s → %s [%s] %s", sender, recipient, message_type.value, subject)
        return msg

    def read(self, agent_id: str, unread_only: bool = True) -> list[AgentMessage]:
        """Read messages for an agent."""
        msgs = self._inbox.get(agent_id, [])
        if unread_only:
            msgs = [m for m in msgs if not m.read]
        for m in msgs:
            m.read = True
        return msgs

    def subscribe(self, agent_id: str, handler: Callable[[AgentMessage], Awaitable[None]]) -> None:
        """Register an async handler that fires on new messages."""
        self._handlers[agent_id].append(handler)

    async def deliver_and_notify(self, msg: AgentMessage) -> None:
        """Send message and fire subscription handlers."""
        handlers = self._handlers.get(msg.recipient, [])
        for handler in handlers:
            try:
                await handler(msg)
            except Exception:
                logger.exception("Handler error for %s on message %s", msg.recipient, msg.id)

    @property
    def stats(self) -> dict[str, Any]:
        total = sum(len(msgs) for msgs in self._inbox.values())
        unread = sum(1 for msgs in self._inbox.values() for m in msgs if not m.read)
        return {
            "total_messages": self._counter,
            "inbox_total": total,
            "unread": unread,
            "active_inboxes": len(self._inbox),
        }
