"""
BEAD: AX-MERGE-006
Gemini Audio Stream
====================
STT and LLM response via Google Gemini API.
Mock mode when GOOGLE_API_KEY is not set.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("archonx.voice.gemini_stream")

_MODEL_ID = "gemini-2.5-flash-preview-native-audio-dialog"
_FALLBACK_MODEL = "gemini-1.5-flash"


class GeminiAudioStream:
    """
    Google Gemini audio streaming client.

    Provides STT via Gemini streaming and LLM response generation.
    Mock mode active when GOOGLE_API_KEY is not configured.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialise Gemini client.

        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
        """
        self._api_key: str | None = api_key or os.environ.get("GOOGLE_API_KEY")
        self._mock: bool = not bool(self._api_key)
        self._client: Any = None

        if self._mock:
            logger.warning("GeminiAudioStream: GOOGLE_API_KEY not set — mock mode")
        else:
            self._init_client()

    def _init_client(self) -> None:
        """Initialise the Google Generative AI client."""
        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(_FALLBACK_MODEL)
            logger.info("GeminiAudioStream initialised with model %s", _FALLBACK_MODEL)
        except ImportError:
            logger.error(
                "google-generativeai not installed. "
                "Run: pip install google-generativeai>=0.8"
            )
            self._mock = True

    def is_available(self) -> bool:
        """
        Check whether Gemini API is available.

        Returns:
            True if GOOGLE_API_KEY is set.
        """
        return not self._mock

    def transcribe_stream(self, audio_chunk: bytes) -> str:
        """
        Transcribe an audio chunk to text using Gemini STT.

        Args:
            audio_chunk: Raw PCM audio bytes.

        Returns:
            Transcribed text string, or empty string in mock mode.
        """
        if self._mock or not audio_chunk:
            if self._mock:
                logger.warning("Mock transcribe_stream: GOOGLE_API_KEY not set")
            return ""

        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            # Use the audio bytes via multimodal content
            model = genai.GenerativeModel(_FALLBACK_MODEL)
            # Encode as base64 for the API
            import base64

            audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
            response = model.generate_content(
                [
                    {"inline_data": {"mime_type": "audio/pcm", "data": audio_b64}},
                    "Transcribe the audio to text. Return only the transcription.",
                ]
            )
            return response.text.strip() if response.text else ""
        except Exception as exc:
            logger.exception("Gemini transcribe_stream failed: %s", exc)
            return ""

    def generate_voice_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> str:
        """
        Generate a text response for voice TTS using Gemini.

        Args:
            prompt: User input text.
            context: List of prior conversation turns as {role, content} dicts.

        Returns:
            Generated response text, or empty string in mock mode.
        """
        if self._mock:
            logger.warning("Mock generate_voice_response: GOOGLE_API_KEY not set")
            return ""

        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            model = genai.GenerativeModel(_FALLBACK_MODEL)
            # Build conversation history
            history = []
            for turn in context:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                history.append({"role": role, "parts": [content]})

            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            return response.text.strip() if response.text else ""
        except Exception as exc:
            logger.exception("Gemini generate_voice_response failed: %s", exc)
            return ""
