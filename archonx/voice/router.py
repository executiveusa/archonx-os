"""
BEAD: AX-MERGE-006 / BEAD-PROD-001
Voice API Router
=================
FastAPI APIRouter for /api/voice/* endpoints.
Handles health, TTS synthesis, Twilio webhooks, and outbound calls.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from archonx.agents.archon_x_phone import ArchonXPhone
from archonx.agents.archon_x_router import ArchonXRouter
from archonx.agents.archon_x_voice_engine import ArchonXVoiceEngine
from archonx.voice.twilio_bridge import TwilioBridge

logger = logging.getLogger("archonx.voice.router")

router = APIRouter(prefix="/api/voice", tags=["voice"])

# Singleton instances (lazy-initialised per request in production — singletons here for simplicity)
_router_instance: ArchonXRouter | None = None
_voice_engine: ArchonXVoiceEngine | None = None
_phone: ArchonXPhone | None = None
_twilio_bridge: TwilioBridge | None = None


def _get_router() -> ArchonXRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ArchonXRouter()
    return _router_instance


def _get_voice_engine() -> ArchonXVoiceEngine:
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = ArchonXVoiceEngine()
    return _voice_engine


def _get_phone() -> ArchonXPhone:
    global _phone
    if _phone is None:
        _phone = ArchonXPhone()
    return _phone


def _get_twilio_bridge() -> TwilioBridge:
    global _twilio_bridge
    if _twilio_bridge is None:
        _twilio_bridge = TwilioBridge()
    return _twilio_bridge


# ---- Request models ----

class SpeakRequest(BaseModel):
    """Request body for /api/voice/speak."""

    text: str
    persona_id: str = "AX-SYNTHIA-001"
    language: str = "es-MX"


class OutboundCallRequest(BaseModel):
    """Request body for /api/voice/call/outbound."""

    to_number: str
    persona_id: str = "AX-SYNTHIA-001"
    message: str
    bead_id: str


# ---- Endpoints ----

@router.get("/status")
async def voice_status() -> dict[str, Any]:
    """
    Health check for the voice engine.

    Returns:
        JSON with active persona, voice engine availability, and upstream service status.
    """
    engine = _get_voice_engine()
    ax_router = _get_router()
    active_persona = os.environ.get("AX_ACTIVE_PERSONA", "AX-SYNTHIA-001")
    return {
        "status": "ok",
        "active_persona": active_persona,
        "voice_engine_available": engine.is_available(),
        "personas": ax_router.list_personas(),
        "twilio_configured": bool(os.environ.get("TWILIO_ACCOUNT_SID")),
        "livekit_configured": bool(os.environ.get("LIVEKIT_URL")),
        "gemini_configured": bool(os.environ.get("GOOGLE_API_KEY")),
    }


@router.post("/speak")
async def speak(req: SpeakRequest) -> Response:
    """
    Synthesize text to speech.

    Body: {text, persona_id, language}
    Returns: audio/mpeg bytes, or JSON with status in mock mode.
    """
    engine = _get_voice_engine()
    voice_id = engine.select_voice(req.persona_id, req.language)
    audio_bytes = engine.synthesize(req.text, voice_id, req.language)

    if audio_bytes:
        return Response(content=audio_bytes, media_type="audio/mpeg")

    # Mock mode — return status JSON
    return JSONResponse(
        status_code=200,
        content={
            "status": "mock",
            "voice_id": voice_id,
            "text": req.text,
            "note": "ELEVEN_LABS_API not set — mock mode",
        },
    )


@router.post("/twilio/inbound")
async def twilio_inbound(request: Request) -> Response:
    """
    Twilio inbound call webhook.

    Parses Twilio POST data and returns TwiML response.
    """
    phone = _get_phone()
    form = await request.form()
    call_sid = str(form.get("CallSid", "unknown"))
    from_number = str(form.get("From", "unknown"))

    active_persona = os.environ.get("AX_ACTIVE_PERSONA", "AX-SYNTHIA-001")
    twiml = phone.handle_inbound_call(call_sid, from_number, active_persona)

    return Response(content=twiml, media_type="text/xml")


@router.post("/twilio/gather")
async def twilio_gather(request: Request) -> Response:
    """Handle Twilio Gather callback - process caller speech input."""
    form = await request.form()
    call_sid = str(form.get("CallSid", "unknown"))
    speech_result = str(form.get("SpeechResult", ""))
    persona_id = str(form.get("persona_id", os.environ.get("AX_ACTIVE_PERSONA", "AX-SYNTHIA-001")))

    ax_router = _get_router()
    persona_id_resolved, persona = ax_router.route(speech_result or "hello", "gather-" + call_sid[:8])
    response_text = persona.get_system_prompt(persona.detect_language(speech_result))[:200] if speech_result else "No entendí. ¿Puede repetir?"

    voice = "Polly.Lupe-Neural" if persona_id_resolved == "AX-SYNTHIA-001" else "Polly.Giorgio"
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="{voice}">{response_text[:500]}</Say>
  <Gather input="speech" timeout="5" action="/api/voice/twilio/gather">
    <Say voice="{voice}">¿Algo más en que le pueda ayudar?</Say>
  </Gather>
  <Hangup/>
</Response>'''
    return Response(content=twiml, media_type="text/xml")


@router.post("/twilio/status")
async def twilio_status_callback(request: Request) -> dict[str, str]:
    """
    Twilio call status callback webhook.

    Logs the call status update from Twilio.
    """
    form = await request.form()
    call_sid = str(form.get("CallSid", "unknown"))
    call_status = str(form.get("CallStatus", "unknown"))
    logger.info("Twilio status callback: sid=%s, status=%s", call_sid, call_status)
    return {"received": "ok", "call_sid": call_sid, "call_status": call_status}


@router.get("/personas")
async def list_personas() -> dict[str, Any]:
    """
    List all available personas.

    Reads dynamically from archonx/config/archon_x_personas.yaml.
    Falls back to hardcoded list if config is unavailable.

    Returns:
        JSON with list of persona IDs and their display names.
    """
    import yaml
    import pathlib
    config_path = pathlib.Path(__file__).parent.parent / "config" / "archon_x_personas.yaml"
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        personas = [
            {"id": k, "name": v.get("name"), "lang": v.get("primary_language"), "org": v.get("company")}
            for k, v in config.get("personas", {}).items()
        ]
    except Exception:
        personas = [
            {"id": "AX-SYNTHIA-001", "name": "SYNTHIA", "lang": "es-MX", "org": "Kupuri Media"},
            {"id": "AX-PAULI-BRAIN-002", "name": "PAULI BRAIN", "lang": "en-US", "org": "The Pauli Effect"},
        ]
    return {"personas": personas}


@router.post("/call/outbound")
async def initiate_outbound_call(req: OutboundCallRequest) -> dict[str, Any]:
    """
    Initiate an outbound call via Twilio.

    Body: {to_number, persona_id, message, bead_id}
    Returns: {call_sid, status, to_number, persona_id, bead_id}
    """
    phone = _get_phone()
    try:
        result = phone.initiate_outbound_call(
            to_number=req.to_number,
            persona_id=req.persona_id,
            message=req.message,
            bead_id=req.bead_id,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Outbound call failed: %s", exc)
        raise HTTPException(status_code=500, detail="Call initiation failed") from exc
