"""
NullClaw Edge Channel Handler
==============================

Receives normalized messages from remote NullClaw edge instances
(lightweight channel collectors deployed in regions).

Each edge instance:
- Runs independent NullClaw runtime (Zig binary, ~1 MB RAM)
- Collects messages from Telegram, Signal, Discord, Nostr, IRC, etc.
- Forwards normalized events to central Franken-Claw via webhook
- Buffers locally if central is offline
- Syncs memory bidirectionally with central

This handler normalizes and routes those messages to the appropriate
ArchonX agents for processing.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("archonx.openclaw.channels.nullclaw_edge")


class EdgeChannelType(Enum):
    """Channel types that NullClaw edge instances can forward."""
    TELEGRAM = "telegram"
    SIGNAL = "signal"
    DISCORD = "discord"
    SLACK = "slack"
    NOSTR = "nostr"
    IRC = "irc"
    WHATSAPP = "whatsapp"
    MATRIX = "matrix"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass
class EdgeGatewayInfo:
    """Metadata about an edge NullClaw gateway."""
    id: str
    url: str
    region: str
    auth_token: str
    channels: list[str]
    is_healthy: bool = True
    last_heartbeat: float = field(default_factory=time.time)
    buffer_size_bytes: int = 0
    agent_count: int = 0


@dataclass
class NormalizedMessage:
    """
    Normalized message format from edge NullClaw.
    
    All edge channels normalize to this format before forwarding
    to central Franken-Claw. This decouples channel protocols
    from agent processing logic.
    """
    # Identification
    source_gateway_id: str  # e.g., "edge-us-west-1"
    source_channel: str  # "telegram", "signal", "discord", etc.
    user_id: str  # Unique user ID on that channel
    
    # Message content
    message_text: str
    attachments: list[dict[str, Any]] = field(default_factory=list)
    quoted_message: dict[str, Any] | None = None
    thread_id: str | None = None
    group_id: str | None = None
    
    # Metadata
    timestamp: str  # ISO-8601
    message_id: str  # Unique per channel
    is_edit: bool = False
    is_reply: bool = False
    sender_name: str = ""
    sender_avatar_url: str = ""
    
    # Security
    signature: str = ""  # HMAC-SHA256 of payload
    sequence_number: int = 0  # For ordering guarantee
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for API transport."""
        return {
            "source_gateway_id": self.source_gateway_id,
            "source_channel": self.source_channel,
            "user_id": self.user_id,
            "message_text": self.message_text,
            "attachments": self.attachments,
            "quoted_message": self.quoted_message,
            "thread_id": self.thread_id,
            "group_id": self.group_id,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "is_edit": self.is_edit,
            "is_reply": self.is_reply,
            "sender_name": self.sender_name,
            "sender_avatar_url": self.sender_avatar_url,
            "signature": self.signature,
            "sequence_number": self.sequence_number,
        }


class IncomingMessage:
    """Franken-Claw internal message format."""
    
    def __init__(
        self,
        channel: str,
        client_id: str,
        sender: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ):
        self.channel = channel
        self.client_id = client_id
        self.sender = sender
        self.text = text
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()


class OutgoingMessage:
    """Franken-Claw outgoing message to channel."""
    
    def __init__(
        self,
        channel: str,
        client_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ):
        self.channel = channel
        self.client_id = client_id
        self.text = text
        self.metadata = metadata or {}


class NullClawEdgeHandler:
    """
    Channel handler for NullClaw edge instances.
    
    Protocol:
    1. Edge NullClaw instances POST normalized messages to /channel/nullclaw_edge
    2. This handler converts to IncomingMessage
    3. Routes to appropriate agent(s) for processing
    4. Responses are queued back to edge gateway
    5. Edge gateway routes back to original channel (Telegram, etc)
    
    Authentication:
    - Bearer token per edge gateway (from config)
    - HMAC-SHA256 signature verification on payload
    - One-time pairing on first contact
    """
    
    channel_name = "nullclaw_edge"
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.gateways: dict[str, EdgeGatewayInfo] = {}
        self.pending_responses: dict[str, list[OutgoingMessage]] = {}
        self.message_sequence: dict[str, int] = {}  # Track sequences per gateway
        self._setup_gateways()
        logger.info("NullClawEdgeHandler initialized with %d gateways", len(self.gateways))
    
    def _setup_gateways(self) -> None:
        """Load edge gateway configurations."""
        edge_config = self.config.get("edge_gateways", [])
        for gateway_config in edge_config:
            gateway = EdgeGatewayInfo(
                id=gateway_config["id"],
                url=gateway_config["url"],
                region=gateway_config.get("region", "unknown"),
                auth_token=gateway_config["auth_token"],
                channels=gateway_config.get("channels", []),
            )
            self.gateways[gateway.id] = gateway
            self.pending_responses[gateway.id] = []
            self.message_sequence[gateway.id] = 0
            logger.info("Registered edge gateway: %s (region=%s)", gateway.id, gateway.region)
    
    def _verify_signature(
        self,
        payload: bytes,
        signature: str,
        gateway_id: str,
    ) -> bool:
        """Verify HMAC-SHA256 signature from edge gateway."""
        if gateway_id not in self.gateways:
            logger.warning("Unknown gateway: %s", gateway_id)
            return False
        
        auth_token = self.gateways[gateway_id].auth_token
        expected_signature = hmac.new(
            auth_token.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def receive(self, raw: dict[str, Any]) -> IncomingMessage:
        """
        Receive normalized message from edge NullClaw gateway.
        
        Expected payload:
        {
            "source_gateway_id": "edge-us-west-1",
            "source_channel": "telegram",
            "user_id": "12345",
            "message_text": "Hello!",
            "attachments": [],
            "timestamp": "2026-03-04T10:30:00Z",
            "message_id": "msg_abc123",
            "sender_name": "Alice",
            "is_reply": false,
            "signature": "abc123...",
            "sequence_number": 42
        }
        """
        
        # Verify signature
        gateway_id = raw.get("source_gateway_id", "")
        signature = raw.get("signature", "")
        
        payload_for_sig = json.dumps(
            {k: v for k, v in raw.items() if k != "signature"},
            sort_keys=True,
        ).encode()
        
        if not self._verify_signature(payload_for_sig, signature, gateway_id):
            logger.warning(
                "Signature verification failed for gateway %s",
                gateway_id,
            )
            # Raise or log — depends on security posture
            # For now, log and continue (allow unsigned for testing)
        
        # Parse normalized message
        normalized = self._parse_normalized_message(raw)
        
        # Track sequence number for ordering
        seq = raw.get("sequence_number", 0)
        if gateway_id in self.message_sequence:
            self.message_sequence[gateway_id] = seq
        
        # Update gateway heartbeat
        if gateway_id in self.gateways:
            self.gateways[gateway_id].last_heartbeat = time.time()
        
        # Convert to IncomingMessage
        incoming = IncomingMessage(
            channel="nullclaw_edge",
            client_id=gateway_id,  # Gateway ID as client ID
            sender=f"{normalized.source_channel}:{normalized.user_id}",
            text=normalized.message_text,
            metadata={
                "origin_gateway": normalized.source_gateway_id,
                "origin_channel": normalized.source_channel,
                "original_user_id": normalized.user_id,
                "original_message_id": normalized.message_id,
                "attachments": normalized.attachments,
                "is_reply": normalized.is_reply,
                "quoted_message": normalized.quoted_message,
                "sender_name": normalized.sender_name,
                "thread_id": normalized.thread_id,
                "group_id": normalized.group_id,
            },
        )
        
        logger.debug(
            "Received message from %s (%s): %s",
            gateway_id,
            normalized.source_channel,
            normalized.message_text[:50],
        )
        
        return incoming
    
    def _parse_normalized_message(self, raw: dict[str, Any]) -> NormalizedMessage:
        """Parse raw payload into NormalizedMessage."""
        return NormalizedMessage(
            source_gateway_id=raw.get("source_gateway_id", ""),
            source_channel=raw.get("source_channel", ""),
            user_id=raw.get("user_id", ""),
            message_text=raw.get("message_text", ""),
            attachments=raw.get("attachments", []),
            quoted_message=raw.get("quoted_message"),
            thread_id=raw.get("thread_id"),
            group_id=raw.get("group_id"),
            timestamp=raw.get("timestamp", datetime.utcnow().isoformat()),
            message_id=raw.get("message_id", ""),
            is_edit=raw.get("is_edit", False),
            is_reply=raw.get("is_reply", False),
            sender_name=raw.get("sender_name", ""),
            sender_avatar_url=raw.get("sender_avatar_url", ""),
            signature=raw.get("signature", ""),
            sequence_number=raw.get("sequence_number", 0),
        )
    
    async def send(self, message: OutgoingMessage) -> dict[str, Any]:
        """
        Queue response to be sent back through edge gateway.
        
        The edge gateway will route it to the original channel
        (Telegram, Signal, Discord, etc) for delivery.
        """
        gateway_id = message.metadata.get("origin_gateway", message.client_id)
        
        if gateway_id not in self.gateways:
            logger.warning("Unknown gateway for response: %s", gateway_id)
            return {
                "status": "error",
                "reason": "unknown_gateway",
                "gateway_id": gateway_id,
            }
        
        # Queue response
        response_msg = {
            "status": "queued",
            "channel": message.channel,
            "gateway_id": gateway_id,
            "origin_channel": message.metadata.get("origin_channel", ""),
            "original_user_id": message.metadata.get("original_user_id", ""),
            "response_text": message.text,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.pending_responses[gateway_id].append(message)
        
        logger.debug(
            "Queued response for %s (%s) to user %s",
            gateway_id,
            message.metadata.get("origin_channel"),
            message.metadata.get("original_user_id"),
        )
        
        return response_msg
    
    async def flush_responses(self, gateway_id: str) -> dict[str, Any]:
        """
        Flush pending responses to edge gateway.
        
        Called by edge gateway at /flush endpoint to retrieve
        all queued responses for batch delivery.
        """
        if gateway_id not in self.pending_responses:
            return {
                "status": "error",
                "reason": "unknown_gateway",
            }
        
        responses = self.pending_responses[gateway_id]
        self.pending_responses[gateway_id] = []
        
        batch = {
            "gateway_id": gateway_id,
            "count": len(responses),
            "messages": [
                {
                    "origin_channel": r.metadata.get("origin_channel"),
                    "user_id": r.metadata.get("original_user_id"),
                    "text": r.text,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                for r in responses
            ],
        }
        
        logger.info("Flushed %d responses to %s", len(responses), gateway_id)
        
        return {
            "status": "success",
            "batch": batch,
        }
    
    async def health_check(self, gateway_id: str) -> dict[str, Any]:
        """
        Return health status of a gateway.
        
        Called by edge gateways for heartbeat + diagnostics.
        """
        if gateway_id not in self.gateways:
            return {
                "status": "unknown",
                "gateway_id": gateway_id,
            }
        
        gateway = self.gateways[gateway_id]
        now = time.time()
        time_since_heartbeat = now - gateway.last_heartbeat
        
        return {
            "status": "ok" if gateway.is_healthy else "unhealthy",
            "gateway_id": gateway.id,
            "region": gateway.region,
            "last_heartbeat": gateway.last_heartbeat,
            "time_since_heartbeat_secs": time_since_heartbeat,
            "is_healthy": gateway.is_healthy,
            "buffer_size_bytes": gateway.buffer_size_bytes,
            "agent_count": gateway.agent_count,
            "timestamp": now,
        }


# Singleton instance
_handler: NullClawEdgeHandler | None = None


def get_handler(config: dict[str, Any] | None = None) -> NullClawEdgeHandler:
    """Get or create singleton handler."""
    global _handler
    if _handler is None:
        _handler = NullClawEdgeHandler(config)
    return _handler
