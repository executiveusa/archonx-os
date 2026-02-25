"""
BEAD: AX-MERGE-006
LiveKit Bridge
===============
Manages LiveKit room creation and access token generation.
Mock mode when LIVEKIT_URL is not set.
"""

from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger("archonx.voice.livekit_bridge")


class LiveKitBridge:
    """
    LiveKit room and token management for Archon-X voice agents.

    Generates access tokens for real-time voice rooms.
    Mock mode active when LIVEKIT_URL is not configured.
    """

    def __init__(self) -> None:
        """Initialise from environment variables."""
        self._url: str | None = os.environ.get("LIVEKIT_URL")
        self._api_key: str | None = os.environ.get("LIVEKIT_API_KEY")
        self._api_secret: str | None = os.environ.get("LIVEKIT_API_SECRET")
        self._mock: bool = not bool(self._url)

        if self._mock:
            logger.warning("LiveKitBridge: LIVEKIT_URL not set — mock mode")
        else:
            logger.info("LiveKitBridge initialised: %s", self._url)

    def is_available(self) -> bool:
        """
        Check whether LiveKit is configured.

        Returns:
            True if LIVEKIT_URL is set.
        """
        return not self._mock

    def create_room(self, room_name: str) -> str:
        """
        Create or join a LiveKit room and return an access token.

        In mock mode, returns a dummy token string for testing.

        Args:
            room_name: Name of the LiveKit room to create or join.

        Returns:
            Access token string for the room.
        """
        if self._mock:
            mock_token = f"mock_livekit_token_{room_name}_{int(time.time())}"
            logger.info("Mock LiveKit token for room '%s': %s", room_name, mock_token)
            return mock_token

        try:
            from livekit import api  # type: ignore[import-untyped]

            token = (
                api.AccessToken(self._api_key, self._api_secret)
                .with_identity("archon-x-agent")
                .with_name("Archon-X")
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=room_name,
                    )
                )
                .to_jwt()
            )
            logger.info("LiveKit token created for room '%s'", room_name)
            return token
        except ImportError:
            logger.error(
                "livekit-agents not installed. Run: pip install livekit-agents>=0.10"
            )
            return f"error_livekit_not_installed_{room_name}"
        except Exception as exc:
            logger.exception("LiveKit create_room failed: %s", exc)
            return f"error_{room_name}_{int(time.time())}"
