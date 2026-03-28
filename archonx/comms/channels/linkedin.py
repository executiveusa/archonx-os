"""
BEAD-POPEBOT-001 — LinkedInChannel
======================================
Posts share updates to LinkedIn via UGC Posts API (v2).
Uses a single Popebot app token (shared account pattern).

Env / vault keys:
    LINKEDIN_POPEBOT_TOKEN       OAuth 2 access token with w_member_social scope
    LINKEDIN_POPEBOT_PERSON_URN  "urn:li:person:{id}" — the Popebot account URN
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from archonx.comms.models import Channel, CommMessage, CommResult

logger = logging.getLogger("archonx.comms.channels.linkedin")

_LI_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"


class LinkedInChannel:
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
        token = self._get_cred("LINKEDIN_POPEBOT_TOKEN")
        person_urn = self._get_cred("LINKEDIN_POPEBOT_PERSON_URN")

        if not token or not person_urn:
            logger.warning("LinkedInChannel: credentials not configured — skipping send")
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.LINKEDIN,
                error="LinkedIn credentials not configured",
            )

        # Agent-signed body for shared account
        signed_body = f"[{message.from_agent_id.upper()}]: {message.body}"

        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": signed_body},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(_LI_UGC_URL, json=payload, headers=headers)
                resp.raise_for_status()
                post_id = resp.headers.get("x-restli-id")

            logger.info("LinkedInChannel: posted %s (post_id=%s)", message.message_id, post_id)
            return CommResult(
                success=True,
                message_id=message.message_id,
                channel=Channel.LINKEDIN,
                external_id=post_id,
            )

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            retry_after: int | None = None
            if status == 429:
                retry_after = int(exc.response.headers.get("Retry-After", "600"))
            logger.error("LinkedInChannel: HTTP %s for %s", status, message.message_id)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.LINKEDIN,
                error=str(exc),
                retry_after=retry_after,
            )

        except Exception as exc:
            logger.error("LinkedInChannel: unexpected error for %s: %s", message.message_id, exc)
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.LINKEDIN,
                error=str(exc),
                retry_after=60,
            )
