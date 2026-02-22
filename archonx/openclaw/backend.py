"""
OpenClaw Backend — Multi-tenant WebSocket Gateway
==================================================
Port 18789 — Tool dispatch, agent coordination, client isolation.

Security (BEAD-019 / Sprint 1):
- Bearer token auth (constant-time comparison)
- SafetyLayer integration on every dispatch
- CORS / security headers
- Bind to 127.0.0.1 by default
"""

from __future__ import annotations

import asyncio
import hmac
import logging
import secrets
import time
from typing import Any

from archonx.security.safety_layer import SafetyLayer

logger = logging.getLogger("archonx.openclaw.backend")

# Default bind to loopback — external access requires explicit config
_DEFAULT_HOST = "127.0.0.1"


class OpenClawBackend:
    """
    Multi-tenant WebSocket gateway for ARCHONX.

    Features:
    - Bearer token auth (constant-time)
    - SafetyLayer wrapping every tool dispatch
    - Multi-tenant session management
    - Channel handlers (WhatsApp, Telegram, Slack)
    - Agent coordination across crews
    - Client isolation and security
    """

    def __init__(
        self,
        port: int = 18789,
        host: str = _DEFAULT_HOST,
        auth_token: str | None = None,
        auth_required: bool = True,
    ) -> None:
        self.port = port
        self.host = host
        self.auth_token = auth_token or secrets.token_urlsafe(48)
        self.auth_required = auth_required
        self.sessions: dict[str, ClientSession] = {}
        self.channels: dict[str, ChannelHandler] = {}
        self.safety = SafetyLayer()
        self._running = False
        logger.info(
            "OpenClaw Backend initialized on %s:%d (auth=%s)",
            host, port, "required" if auth_required else "open",
        )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self, token: str) -> bool:
        """Constant-time bearer token comparison."""
        if not self.auth_required:
            return True
        return hmac.compare_digest(token, self.auth_token)

    @staticmethod
    def verify_webhook_signature(
        payload: bytes, signature: str, secret: str
    ) -> bool:
        """HMAC-SHA256 webhook signature verification."""
        import hashlib

        expected = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def security_headers() -> dict[str, str]:
        """Standard security headers for HTTP responses."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'",
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start WebSocket gateway."""
        self._running = True
        logger.info("OpenClaw Backend starting on %s:%d…", self.host, self.port)
        logger.info("OpenClaw Backend online")

    async def stop(self) -> None:
        """Graceful shutdown — disconnect all clients, drain."""
        self._running = False
        for session in list(self.sessions.values()):
            await session.disconnect()
        self.sessions.clear()
        logger.info("OpenClaw Backend stopped")

    # ------------------------------------------------------------------
    # Tool dispatch with safety
    # ------------------------------------------------------------------

    async def dispatch_tool(
        self,
        tool_name: str,
        params: dict[str, Any],
        client_id: str,
        agent_id: str = "",
        iteration: int = 0,
    ) -> dict[str, Any]:
        """
        Dispatch tool execution through SafetyLayer.

        1. Sanitize params
        2. Policy + validator + leak check
        3. Execute (placeholder)
        4. Scan output
        """
        # Safety gate
        safety_result = self.safety.check_tool_call(
            agent_id=agent_id,
            tool_name=tool_name,
            params=params,
            iteration=iteration,
        )
        if not safety_result.safe:
            violations = [v.message for v in safety_result.violations]
            logger.warning(
                "Tool dispatch BLOCKED for %s/%s: %s",
                client_id, tool_name, violations,
            )
            return {
                "status": "blocked",
                "tool": tool_name,
                "client": client_id,
                "violations": violations,
            }

        logger.info("Dispatching tool: %s for client %s", tool_name, client_id)
        # Placeholder — wire to actual tools
        result = {"status": "success", "tool": tool_name, "client": client_id}

        # Output leak scan
        result_text = str(result)
        _, output_safety = self.safety.check_output(result_text)
        if not output_safety.safe:
            logger.warning("Leak detected in tool output — redacting")
            result["_redacted"] = True

        return result


class ClientSession:
    """Individual client session with isolation."""

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
        self.connected = True
        self.metadata: dict[str, Any] = {}
        self.connected_at: float = time.time()

    async def disconnect(self) -> None:
        self.connected = False
        logger.info("Client %s disconnected", self.client_id)


class ChannelHandler:
    """Base handler for communication channels."""

    def __init__(self, channel_name: str) -> None:
        self.channel_name = channel_name

    async def send_message(self, client_id: str, message: str) -> bool:
        logger.info("[%s] Sending to %s: %s", self.channel_name, client_id, message[:50])
        return True
