"""
BEAD-POPEBOT-001 — SlackChannel
=================================
Posts to Slack via an incoming-webhook URL stored in vault.

Env / vault key:
    SLACK_WEBHOOK_URL    https://hooks.slack.com/services/xxx/yyy/zzz
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from archonx.comms.models import Channel, CommMessage, CommResult

logger = logging.getLogger("archonx.comms.channels.slack")


class SlackChannel:
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
        webhook_url = self._get_cred("SLACK_WEBHOOK_URL")
        if not webhook_url:
            logger.warning("SlackChannel: SLACK_WEBHOOK_URL not configured — skipping send")
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.SLACK,
                error="SLACK_WEBHOOK_URL not configured",
            )

        # Agent-signed body
        signed_text = f"[{message.from_agent_id.upper()}]: {message.body}"
        if message.subject:
            signed_text = f"*{message.subject}*\n{signed_text}"

        payload: dict = {"text": signed_text}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(webhook_url, json=payload)
                resp.raise_for_status()

            logger.info("SlackChannel: sent message %s", message.message_id)
            return CommResult(
                success=True,
                message_id=message.message_id,
                channel=Channel.SLACK,
                external_id=resp.text,
            )

        except httpx.HTTPStatusError as exc:
            retry_after: int | None = None
            if exc.response.status_code == 429:
                retry_after = int(exc.response.headers.get("Retry-After", "60"))
            logger.error("SlackChannel: HTTP error %s for %s", exc.response.status_code, message.message_id)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.SLACK,
                error=str(exc),
                retry_after=retry_after,
            )

        except Exception as exc:
            logger.error("SlackChannel: unexpected error for %s: %s", message.message_id, exc)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.SLACK,
                error=str(exc),
                retry_after=30,
            )
