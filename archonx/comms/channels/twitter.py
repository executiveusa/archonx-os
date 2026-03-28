"""
BEAD-POPEBOT-001 — TwitterChannel
====================================
Posts tweets via Tweepy v4 using a SHARED Popebot account (not per-agent OAuth).
Agents sign messages: "[AGENT_NAME]: {body}"

Env / vault keys:
    TWITTER_POPEBOT_API_KEY
    TWITTER_POPEBOT_API_SECRET
    TWITTER_POPEBOT_ACCESS_TOKEN
    TWITTER_POPEBOT_ACCESS_SECRET
    TWITTER_POPEBOT_BEARER_TOKEN
"""
from __future__ import annotations

import logging
import os
from typing import Any

from archonx.comms.models import Channel, CommMessage, CommResult

logger = logging.getLogger("archonx.comms.channels.twitter")

_TWEET_MAX_CHARS = 280


class TwitterChannel:
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
        api_key = self._get_cred("TWITTER_POPEBOT_API_KEY")
        api_secret = self._get_cred("TWITTER_POPEBOT_API_SECRET")
        access_token = self._get_cred("TWITTER_POPEBOT_ACCESS_TOKEN")
        access_secret = self._get_cred("TWITTER_POPEBOT_ACCESS_SECRET")

        if not all([api_key, api_secret, access_token, access_secret]):
            logger.warning("TwitterChannel: credentials not configured — skipping send")
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.TWITTER,
                error="Twitter credentials not configured",
            )

        try:
            import tweepy  # soft import — not required if Twitter unused
        except ImportError:
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.TWITTER,
                error="tweepy not installed: pip install tweepy",
            )

        # Agent signature (shared account, agent identity in body)
        signed_text = f"[{message.from_agent_id.upper()}]: {message.body}"
        if len(signed_text) > _TWEET_MAX_CHARS:
            # Truncate body, keep signature prefix intact
            prefix = f"[{message.from_agent_id.upper()}]: "
            max_body = _TWEET_MAX_CHARS - len(prefix) - 3
            signed_text = f"{prefix}{message.body[:max_body]}..."

        try:
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
            )
            response = client.create_tweet(text=signed_text)
            tweet_id = str(response.data["id"]) if response.data else None

            logger.info("TwitterChannel: posted tweet %s (tweet_id=%s)", message.message_id, tweet_id)
            return CommResult(
                success=True,
                message_id=message.message_id,
                channel=Channel.TWITTER,
                external_id=tweet_id,
            )

        except Exception as exc:
            logger.error("TwitterChannel: post failed for %s: %s", message.message_id, exc)
            retry_after: int | None = None
            err_str = str(exc)
            if "429" in err_str or "Too Many Requests" in err_str:
                retry_after = 900  # 15-minute Twitter window
            return CommResult(
                success=False,
                message_id=message.message_id,
                channel=Channel.TWITTER,
                error=err_str,
                retry_after=retry_after,
            )
