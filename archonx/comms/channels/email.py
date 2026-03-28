"""
BEAD-POPEBOT-001 — EmailChannel
=================================
SMTP email via smtplib. All credentials from vault/env — ZERO hardcoded.

Env vars / Infisical keys:
    SMTP_HOST         e.g. smtp.gmail.com
    SMTP_PORT         e.g. 587
    SMTP_USER         sender address
    SMTP_PASSWORD     app password / OAuth token
    SMTP_FROM_NAME    display name, default "Popebot — ArchonX OS"
"""
from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from archonx.comms.models import Channel, CommMessage, CommResult

logger = logging.getLogger("archonx.comms.channels.email")


class EmailChannel:
    """Sends email via SMTP. One connection per send (stateless for safety)."""

    def __init__(self, vault: Any | None = None) -> None:
        self._vault = vault

    def _get_cred(self, key: str, default: str = "") -> str:
        """Try vault first, then env, then default."""
        if self._vault is not None:
            try:
                val = self._vault.get_secret(key)
                if val:
                    return val
            except Exception:
                pass
        return os.getenv(key, default)

    async def send(self, message: CommMessage) -> CommResult:
        host = self._get_cred("SMTP_HOST", "smtp.gmail.com")
        port = int(self._get_cred("SMTP_PORT", "587"))
        user = self._get_cred("SMTP_USER")
        password = self._get_cred("SMTP_PASSWORD")
        from_name = self._get_cred("SMTP_FROM_NAME", "Popebot — ArchonX OS")

        if not user or not password:
            logger.warning("EmailChannel: SMTP_USER or SMTP_PASSWORD not configured — skipping send")
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.EMAIL,
                error="SMTP credentials not configured",
            )

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject or f"[ArchonX] Message from {message.from_agent_id}"
            msg["From"] = f"{from_name} <{user}>"
            msg["To"] = message.to
            msg["X-Agent-ID"] = message.from_agent_id

            # Sign body with agent identifier
            signed_body = f"{message.body}\n\n— {message.from_agent_id.upper()}, ArchonX OS"
            msg.attach(MIMEText(signed_body, "plain"))

            with smtplib.SMTP(host, port) as server:
                server.ehlo()
                server.starttls()
                server.login(user, password)
                server.sendmail(user, message.to, msg.as_string())

            logger.info(
                "EmailChannel: sent message %s from %s to %s",
                message.message_id, message.from_agent_id, message.to,
            )
            return CommResult(
                success=True,
                message_id=message.message_id,
                channel=Channel.EMAIL,
                external_id=msg["Message-ID"],
            )

        except Exception as exc:
            logger.error("EmailChannel: send failed for %s: %s", message.message_id, exc)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.EMAIL,
                error=str(exc),
                retry_after=60,
            )
