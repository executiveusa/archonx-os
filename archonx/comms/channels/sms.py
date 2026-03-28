"""
BEAD-POPEBOT-001 — SMSChannel
=================================
Sends SMS via Twilio Messages REST API. All credentials from vault/env.

Env / vault keys:
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_FROM_NUMBER    "+1XXXXXXXXXX"
"""
from __future__ import annotations

import base64
import logging
import os
from typing import Any

import httpx

from archonx.comms.models import Channel, CommMessage, CommResult

logger = logging.getLogger("archonx.comms.channels.sms")

_TWILIO_API_URL = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"


class SMSChannel:
    def __init__(self, vault: Any | None = None) -> None:
        self._vault = vault

    def _get_cred(self, key: str) -> str:
        if self._vault is not None:
            try:
                val = self._vault.get_secret(key)
                if val:
                    return val
            except Exception:
                pass
        return os.getenv(key, "")

    async def send(self, message: CommMessage) -> CommResult:
        sid = self._get_cred("TWILIO_ACCOUNT_SID")
        token = self._get_cred("TWILIO_AUTH_TOKEN")
        from_number = self._get_cred("TWILIO_FROM_NUMBER")

        if not sid or not token or not from_number:
            logger.warning("SMSChannel: Twilio credentials not configured — skipping send")
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.SMS,
                error="Twilio credentials not configured",
            )

        # Agent-signed body; SMS has 160-char limit per segment
        signed_body = f"[{message.from_agent_id.upper()}]: {message.body}"
        if len(signed_body) > 1600:
            signed_body = signed_body[:1597] + "..."

        credentials = base64.b64encode(f"{sid}:{token}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        url = _TWILIO_API_URL.format(sid=sid)

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    data={"From": from_number, "To": message.to, "Body": signed_body},
                )
                resp.raise_for_status()
                data = resp.json()

            logger.info("SMSChannel: sent message %s to %s (Twilio SID: %s)",
                        message.message_id, message.to, data.get("sid"))
            return CommResult(
                success=True,
                message_id=message.message_id,
                channel=Channel.SMS,
                external_id=data.get("sid"),
            )

        except httpx.HTTPStatusError as exc:
            retry_after: int | None = None
            if exc.response.status_code == 429:
                retry_after = 60
            logger.error("SMSChannel: HTTP error %s for %s", exc.response.status_code, message.message_id)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.SMS,
                error=str(exc),
                retry_after=retry_after,
            )

        except Exception as exc:
            logger.error("SMSChannel: unexpected error for %s: %s", message.message_id, exc)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.SMS,
                error=str(exc),
                retry_after=30,
            )
