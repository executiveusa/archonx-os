"""
BEAD-POPEBOT-001 — Comms data models.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Channel(str, Enum):
    EMAIL    = "EMAIL"
    SLACK    = "SLACK"
    SMS      = "SMS"
    TWITTER  = "TWITTER"
    LINKEDIN = "LINKEDIN"


class MessagePriority(str, Enum):
    CRITICAL = "CRITICAL"   # Send immediately, bypass rate limit
    HIGH     = "HIGH"       # Send within 60s
    NORMAL   = "NORMAL"     # Batch in 5 min window
    LOW      = "LOW"        # Queue for daily digest


class MessageStatus(str, Enum):
    PENDING = "PENDING"
    SENT    = "SENT"
    FAILED  = "FAILED"
    QUEUED  = "QUEUED"


@dataclass
class CommMessage:
    from_agent_id: str
    to: str
    channel: Channel
    body: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subject: str | None = None
    template_id: str | None = None
    template_vars: dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: dict[str, Any] = field(default_factory=dict)
    scheduled_at: str | None = None
    sent_at: str | None = None
    status: MessageStatus = MessageStatus.PENDING


@dataclass
class CommResult:
    success: bool
    message_id: str
    channel: Channel
    external_id: str | None = None
    error: str | None = None
    retry_after: int | None = None   # seconds
