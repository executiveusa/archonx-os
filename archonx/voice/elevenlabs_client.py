"""
BEAD: AX-MERGE-006 / BEAD-PROD-001
ElevenLabs Client
==================
Production-ready wrapper for the ElevenLabs REST API.
Supports TTS synthesis, voice listing, and voice info retrieval.
Mock mode active when ELEVEN_LABS_API is not set.
Falls back from httpx to urllib.request if httpx is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger("archonx.voice.elevenlabs_client")

# Attempt to import httpx; fall back to urllib if not installed
try:
    import httpx as _httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False
    import urllib.request as _urllib_request
    import urllib.error as _urllib_error

_TIMEOUT = 30.0


class ElevenLabsClient:
    """
    ElevenLabs TTS API client.

    Reads API key from ELEVEN_LABS_API env var.
    In mock mode (no key), synthesize() returns b"MOCK_AUDIO" and
    list operations return empty collections.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialise the client.

        Args:
            api_key: ElevenLabs API key. If None, reads from ELEVEN_LABS_API env var.
        """
        self.api_key: str | None = api_key or os.environ.get("ELEVEN_LABS_API")
        self.base_url: str = "https://api.elevenlabs.io/v1"
        self._mock: bool = not bool(self.api_key)

        if self._mock:
            logger.warning("ElevenLabsClient: ELEVEN_LABS_API not set — mock mode active")
        else:
            logger.info(
                "ElevenLabsClient initialised (key=...%s)",
                (self.api_key or "")[-4:],
            )

    def is_available(self) -> bool:
        """Return True when the client has a real API key configured."""
        return not self._mock

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    def _get(self, path: str) -> Any:
        """
        Perform a GET request against the ElevenLabs API.

        Args:
            path: URL path relative to base_url (e.g. "/voices").

        Returns:
            Parsed JSON response body (dict or list), or None on error.
        """
        url = self.base_url + path
        headers = {"xi-api-key": self.api_key or ""}

        if _HAS_HTTPX:
            try:
                with _httpx.Client(timeout=_TIMEOUT) as client:
                    resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                logger.error("ElevenLabs GET %s error %d: %s", path, resp.status_code, resp.text[:200])
                return None
            except Exception as exc:
                logger.exception("ElevenLabs GET %s failed: %s", path, exc)
                return None
        else:
            try:
                req = _urllib_request.Request(url, headers=headers)
                with _urllib_request.urlopen(req, timeout=_TIMEOUT) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception as exc:
                logger.exception("ElevenLabs GET %s failed (urllib): %s", path, exc)
                return None

    def _post_audio(self, path: str, payload: dict[str, Any]) -> bytes | None:
        """
        Perform a POST request and return raw audio bytes.

        Args:
            path: URL path relative to base_url.
            payload: JSON-serialisable request body.

        Returns:
            Raw audio bytes on success, None on error.
        """
        url = self.base_url + path
        headers = {
            "xi-api-key": self.api_key or "",
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        body = json.dumps(payload).encode("utf-8")

        if _HAS_HTTPX:
            try:
                with _httpx.Client(timeout=_TIMEOUT) as client:
                    resp = client.post(url, content=body, headers=headers)
                if resp.status_code == 200:
                    return resp.content
                logger.error("ElevenLabs POST %s error %d: %s", path, resp.status_code, resp.text[:200])
                return None
            except Exception as exc:
                logger.exception("ElevenLabs POST %s failed: %s", path, exc)
                return None
        else:
            try:
                req = _urllib_request.Request(url, data=body, headers=headers, method="POST")
                with _urllib_request.urlopen(req, timeout=_TIMEOUT) as resp:
                    return resp.read()
            except Exception as exc:
                logger.exception("ElevenLabs POST %s failed (urllib): %s", path, exc)
                return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
    ) -> bytes | None:
        """
        Synthesize text to audio bytes using the given voice.

        Args:
            text: Text to convert to speech.
            voice_id: ElevenLabs voice ID.
            model_id: ElevenLabs model ID (default: eleven_multilingual_v2).

        Returns:
            Raw MP3 audio bytes on success, b"MOCK_AUDIO" in mock mode,
            or None if the live request fails.
        """
        if self._mock:
            logger.warning("Mock synthesize: text='%.40s...'", text)
            return b"MOCK_AUDIO"

        payload: dict[str, Any] = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }
        return self._post_audio(f"/text-to-speech/{voice_id}", payload)

    def list_voices(self) -> list[dict[str, Any]]:
        """
        Retrieve available voices from ElevenLabs.

        Returns:
            List of voice dicts (voice_id, name, labels, etc.),
            or empty list in mock mode or on error.
        """
        if self._mock:
            logger.warning("Mock list_voices: ELEVEN_LABS_API not set")
            return []

        data = self._get("/voices")
        if isinstance(data, dict):
            return data.get("voices", [])
        return []

    def get_voice_info(self, voice_id: str) -> dict[str, Any]:
        """
        Retrieve metadata for a specific voice.

        Args:
            voice_id: ElevenLabs voice ID.

        Returns:
            Voice info dict, or empty dict in mock mode or on error.
        """
        if self._mock:
            logger.warning("Mock get_voice_info: ELEVEN_LABS_API not set")
            return {}

        data = self._get(f"/voices/{voice_id}")
        if isinstance(data, dict):
            return data
        return {}
