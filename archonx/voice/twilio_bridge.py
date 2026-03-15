"""
BEAD: AX-MERGE-006
Twilio Bridge
==============
Wraps Twilio REST client for TwiML generation and WebSocket streaming.
Mock mode when TWILIO_ACCOUNT_SID is not set.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("archonx.voice.twilio_bridge")


class TwilioBridge:
    """
    Twilio REST client wrapper for Archon-X voice calls.

    Generates TwiML responses and manages WebSocket streaming setup.
    Mock mode active when TWILIO_ACCOUNT_SID is not configured.
    """

    def __init__(self) -> None:
        """Initialise from environment variables."""
        self._account_sid: str | None = os.environ.get("TWILIO_ACCOUNT_SID")
        self._auth_token: str | None = os.environ.get("TWILIO_SECRET")
        self._mock: bool = not bool(self._account_sid)

        if self._mock:
            logger.warning("TwilioBridge: TWILIO_ACCOUNT_SID not set — mock mode")
        else:
            logger.info("TwilioBridge initialised")

    def generate_twiml_response(
        self,
        message: str,
        voice: str = "Polly.Lupe-Neural",
    ) -> str:
        """
        Generate a TwiML <Say> response.

        Args:
            message: The text for Twilio to speak.
            voice: Twilio voice identifier (default: Polly.Lupe-Neural for Spanish).

        Returns:
            TwiML XML string.
        """
        # Escape XML special characters
        safe_message = (
            message.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f'  <Say voice="{voice}">{safe_message}</Say>\n'
            "</Response>"
        )

    def stream_to_websocket(self, call_sid: str, websocket_url: str) -> str:
        """
        Generate TwiML to connect a call to a Media Streams WebSocket.

        Args:
            call_sid: Twilio Call SID.
            websocket_url: WebSocket URL for media streaming (wss://...).

        Returns:
            TwiML XML string with <Start><Stream> directives.
        """
        logger.info(
            "Generating stream TwiML: call_sid=%s, ws=%s", call_sid, websocket_url
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            "  <Start>\n"
            f'    <Stream url="{websocket_url}" />\n'
            "  </Start>\n"
            "  <Pause length=\"30\" />\n"
            "</Response>"
        )

    def is_available(self) -> bool:
        """
        Check whether Twilio credentials are configured.

        Returns:
            True if TWILIO_ACCOUNT_SID is set.
        """
        return not self._mock
