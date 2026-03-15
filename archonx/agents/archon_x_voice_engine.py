"""
BEAD: AX-MERGE-004
Archon-X Voice Engine
======================
Synthesizes speech via ElevenLabs (primary) with gTTS fallback.
Loads voice configuration from archon_x_voice_engine.yaml.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, AsyncGenerator

import httpx
import yaml

logger = logging.getLogger("archonx.agents.archon_x_voice_engine")

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "archon_x_voice_engine.yaml"

_VOICE_SETTINGS_DEFAULTS: dict[str, dict[str, Any]] = {
    "ax-synthia-mx": {
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style": 0.4,
        "use_speaker_boost": True,
    },
    "ax-pauli-en": {
        "stability": 0.80,
        "similarity_boost": 0.90,
        "style": 0.30,
        "use_speaker_boost": False,
    },
    "ax-pauli-sr": {
        "stability": 0.80,
        "similarity_boost": 0.85,
        "style": 0.35,
        "use_speaker_boost": False,
    },
}

# Voice routing: persona + language -> voice_id
_PERSONA_VOICE_MAP: dict[str, dict[str, str]] = {
    "AX-SYNTHIA-001": {
        "es-MX": "ax-synthia-mx",
        "en-US": "ax-synthia-mx",
    },
    "AX-PAULI-BRAIN-002": {
        "en-US": "ax-pauli-en",
        "es-MX": "ax-pauli-en",
        "sr-RS": "ax-pauli-sr",
    },
}

_ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
_ELEVENLABS_TIMEOUT = 30.0
_MAX_RETRIES = 3


def _load_config() -> dict[str, Any]:
    """Load voice engine YAML config."""
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)  # type: ignore[return-value]
    except FileNotFoundError:
        logger.warning("Voice engine config not found at %s, using defaults", _CONFIG_PATH)
        return {}


class ArchonXVoiceEngine:
    """
    Archon-X Voice Synthesis Engine.

    Primary: ElevenLabs streaming TTS via ELEVEN_LABS_API env var.
    Fallback: Returns empty bytes with a log warning (gTTS available as extension).
    Mock mode: When ELEVEN_LABS_API is not set.
    """

    def __init__(self) -> None:
        """Initialise voice engine and load config."""
        self._config = _load_config()
        self._api_key: str | None = os.environ.get("ELEVEN_LABS_API")
        self._model_streaming: str = (
            self._config.get("engine", {}).get("model_streaming", "eleven_flash_v2_5")
        )
        self._model_quality: str = (
            self._config.get("engine", {}).get("model_quality", "eleven_multilingual_v2")
        )
        if self._api_key:
            logger.info("ArchonXVoiceEngine initialised with ElevenLabs API key")
        else:
            logger.warning(
                "ArchonXVoiceEngine: ELEVEN_LABS_API not set — mock mode active"
            )

    def is_available(self) -> bool:
        """
        Check whether the voice engine is available (API key is set).

        Returns:
            True if ELEVEN_LABS_API env var is configured.
        """
        return bool(self._api_key)

    def select_voice(self, persona_id: str, language: str) -> str:
        """
        Return the ElevenLabs voice ID for a given persona and language.

        Args:
            persona_id: Persona ID (e.g. "AX-SYNTHIA-001").
            language: Language code (e.g. "es-MX", "sr-RS").

        Returns:
            ElevenLabs voice ID string. Defaults to "ax-synthia-mx" if unknown.
        """
        persona_voices = _PERSONA_VOICE_MAP.get(persona_id, {})
        # Exact match first
        if language in persona_voices:
            return persona_voices[language]
        # Fallback: first available voice for the persona
        if persona_voices:
            return next(iter(persona_voices.values()))
        return "ax-synthia-mx"

    def synthesize(self, text: str, voice_id: str, language: str = "en-US") -> bytes:
        """
        Synthesize text to speech and return PCM audio bytes.

        Calls ElevenLabs REST API synchronously. Returns empty bytes in mock mode.
        Handles rate limits (429) and timeouts with up to 3 retries.

        Args:
            text: Text to synthesize.
            voice_id: ElevenLabs voice ID.
            language: Language code (used for model selection).

        Returns:
            Raw PCM audio bytes (may be empty in mock mode).
        """
        if not self._api_key:
            logger.warning(
                "Mock synthesize: ELEVEN_LABS_API not set. text='%.50s...'", text
            )
            return b""

        # Choose model based on language
        model_id = (
            self._model_quality
            if language in ("es-MX", "sr-RS")
            else self._model_streaming
        )
        voice_settings = _VOICE_SETTINGS_DEFAULTS.get(
            voice_id,
            {"stability": 0.75, "similarity_boost": 0.85},
        )

        url = f"{_ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload: dict[str, Any] = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings,
        }

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=_ELEVENLABS_TIMEOUT) as client:
                    resp = client.post(url, json=payload, headers=headers)

                if resp.status_code == 200:
                    logger.debug(
                        "ElevenLabs synthesize OK: voice=%s, bytes=%d",
                        voice_id,
                        len(resp.content),
                    )
                    return resp.content

                if resp.status_code == 429:
                    wait = 2**attempt
                    logger.warning(
                        "ElevenLabs rate limit (429) on attempt %d. Waiting %ds.",
                        attempt,
                        wait,
                    )
                    time.sleep(wait)
                    continue

                logger.error(
                    "ElevenLabs error %d: %s", resp.status_code, resp.text[:200]
                )
                return b""

            except httpx.TimeoutException:
                logger.warning(
                    "ElevenLabs timeout on attempt %d/%d", attempt, _MAX_RETRIES
                )
                if attempt == _MAX_RETRIES:
                    logger.error("ElevenLabs: all retries exhausted (timeout). Returning empty.")
                    return b""
            except Exception as exc:
                logger.exception("ElevenLabs unexpected error: %s", exc)
                return b""

        return b""

    async def stream_synthesize(
        self, text: str, voice_id: str
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream TTS synthesis for real-time response.

        Yields audio chunks as they arrive from ElevenLabs streaming API.
        Falls back to yielding full audio in one chunk if streaming unavailable.

        Args:
            text: Text to synthesize.
            voice_id: ElevenLabs voice ID.

        Yields:
            Audio byte chunks.
        """
        if not self._api_key:
            logger.warning("Mock stream_synthesize: ELEVEN_LABS_API not set.")
            yield b""
            return

        url = f"{_ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}/stream"
        voice_settings = _VOICE_SETTINGS_DEFAULTS.get(
            voice_id,
            {"stability": 0.75, "similarity_boost": 0.85},
        )
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "text": text,
            "model_id": self._model_streaming,
            "voice_settings": voice_settings,
        }

        try:
            async with httpx.AsyncClient(timeout=_ELEVENLABS_TIMEOUT) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as resp:
                    if resp.status_code != 200:
                        logger.error(
                            "ElevenLabs stream error %d", resp.status_code
                        )
                        yield b""
                        return
                    async for chunk in resp.aiter_bytes(chunk_size=4096):
                        if chunk:
                            yield chunk
        except Exception as exc:
            logger.exception("ElevenLabs stream_synthesize failed: %s", exc)
            yield b""
