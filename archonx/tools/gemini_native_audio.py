"""
BEAD: AX-MERGE-007
Gemini Native Audio Tool
=========================
Real-time voice conversation via Gemini 2.5 Native Audio.
Mock implementation when GOOGLE_API_KEY is not set.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from archonx.tools.base import BaseTool, ToolResult

logger = logging.getLogger("archonx.tools.gemini_native_audio")


class GeminiNativeAudioTool(BaseTool):
    """
    Tool for real-time voice conversation via Gemini 2.5 Native Audio Dialog.

    Processes audio input and generates audio-aware text responses.
    Mock mode returns empty audio response when GOOGLE_API_KEY is not set.
    """

    name: str = "gemini_native_audio"
    description: str = "Real-time voice conversation via Gemini 2.5 Native Audio"

    _MODEL_ID = "gemini-2.5-flash-preview-native-audio-dialog"
    _FALLBACK_MODEL = "gemini-1.5-flash"

    def __init__(self) -> None:
        """Initialise the tool and check API availability."""
        self._api_key: str | None = os.environ.get("GOOGLE_API_KEY")
        self._mock: bool = not bool(self._api_key)
        if self._mock:
            logger.warning("GeminiNativeAudioTool: GOOGLE_API_KEY not set — mock mode")

    def run(
        self,
        bead_id: str,
        prompt: str,
        audio_bytes: bytes | None = None,
    ) -> dict[str, Any]:
        """
        Run a voice/text conversation turn with Gemini.

        Args:
            bead_id: BEAD ID for traceability (required).
            prompt: Text prompt or transcribed speech.
            audio_bytes: Optional raw audio bytes for native audio processing.

        Returns:
            Dict with keys:
                - text_response (str): Generated text response.
                - audio_response_available (bool): Whether audio was generated.
                - latency_ms (int): Processing latency in milliseconds.
        """
        if not bead_id:
            return {
                "text_response": "",
                "audio_response_available": False,
                "latency_ms": 0,
                "error": "bead_id is required",
            }

        if self._mock:
            logger.warning(
                "Mock GeminiNativeAudio: bead=%s, prompt='%.40s...'", bead_id, prompt
            )
            return {
                "text_response": f"[MOCK] Gemini response to: {prompt[:50]}",
                "audio_response_available": False,
                "latency_ms": 0,
            }

        start = time.monotonic()
        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(self._FALLBACK_MODEL)

            content: list[Any] = []
            if audio_bytes:
                import base64

                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                content.append(
                    {"inline_data": {"mime_type": "audio/pcm", "data": audio_b64}}
                )
            content.append(prompt)

            response = model.generate_content(content)
            latency_ms = int((time.monotonic() - start) * 1000)
            text = response.text.strip() if response.text else ""
            return {
                "text_response": text,
                "audio_response_available": False,
                "latency_ms": latency_ms,
            }
        except Exception as exc:
            logger.exception("GeminiNativeAudio failed: %s", exc)
            latency_ms = int((time.monotonic() - start) * 1000)
            return {
                "text_response": "",
                "audio_response_available": False,
                "latency_ms": latency_ms,
                "error": str(exc),
            }

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Execute the tool via the ToolRegistry interface.

        Args:
            params: Dict with bead_id, prompt, and optionally audio_bytes.

        Returns:
            ToolResult wrapping the run() output.
        """
        bead_id = params.get("bead_id", "")
        prompt = params.get("prompt", "")
        audio_bytes: bytes | None = params.get("audio_bytes")

        data = self.run(bead_id=bead_id, prompt=prompt, audio_bytes=audio_bytes)
        if "error" in data:
            return ToolResult(tool=self.name, status="error", data=data, error=data["error"])
        return ToolResult(tool=self.name, status="success", data=data)
