"""
BEAD: AX-MERGE-006
ElevenLabs Client
==================
Wraps the ElevenLabs REST API for TTS synthesis.
Mock mode when ELEVEN_LABS_API is not set.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("archonx.voice.elevenlabs_client")

_BASE_URL = "https://api.elevenlabs.io/v1"
_TIMEOUT = 30.0


class ElevenLabsClient:
    """
    ElevenLabs TTS API client.

    Reads API key from ELEVEN_LABS_API env var by default.
    Returns empty bytes in mock mode (no key set).
    """

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialise client.

        Args:
            api_key: ElevenLabs API key. If None, reads from ELEVEN_LABS_API env var.
        """
        self._api_key: str | None = api_key or os.environ.get("ELEVEN_LABS_API")
        if not self._api_key:
            logger.warning("ElevenLabsClient: no API key — mock mode active")

    def is_available(self) -> bool:
        """
        Check whether the client is configured and reachable.

        Returns:
            True if API key is set.
        """
        return bool(self._api_key)

    def synthesize(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Synthesize text to audio bytes.

        Args:
            text: Text to convert to speech.
            voice_id: ElevenLabs voice ID.
            model_id: ElevenLabs model ID.
            voice_settings: Optional dict with stability, similarity_boost, style.

        Returns:
            Raw audio bytes (MP3), or empty bytes in mock mode.
        """
        if not self._api_key:
            logger.warning("Mock synthesize: text='%.40s...'", text)
            return b""

        settings: dict[str, Any] = voice_settings or {
            "stability": 0.75,
            "similarity_boost": 0.85,
        }
        url = f"{_BASE_URL}/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload: dict[str, Any] = {
            "text": text,
            "model_id": model_id,
            "voice_settings": settings,
        }

        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                resp = client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                return resp.content
            logger.error(
                "ElevenLabs synthesize error %d: %s",
                resp.status_code,
                resp.text[:200],
            )
            return b""
        except Exception as exc:
            logger.exception("ElevenLabs synthesize failed: %s", exc)
            return b""

    def list_voices(self) -> list[dict[str, Any]]:
        """
        Retrieve available voices from ElevenLabs.

        Returns:
            List of voice dicts (id, name, labels), or empty list in mock mode.
        """
        if not self._api_key:
            logger.warning("Mock list_voices: ELEVEN_LABS_API not set")
            return []

        url = f"{_BASE_URL}/voices"
        headers = {"xi-api-key": self._api_key}
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                data: dict[str, Any] = resp.json()
                return data.get("voices", [])
            logger.error("ElevenLabs list_voices error %d", resp.status_code)
            return []
        except Exception as exc:
            logger.exception("ElevenLabs list_voices failed: %s", exc)
            return []
