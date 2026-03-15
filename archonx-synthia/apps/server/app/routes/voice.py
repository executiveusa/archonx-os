"""Voice API — Twilio webhook for push-to-talk MVP."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Form
from fastapi.responses import Response

router = APIRouter()
logger = structlog.get_logger()


@router.post("/inbound")
async def twilio_inbound():
    """Twilio calls this when an inbound call arrives. Return TwiML to gather speech."""
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello, this is Synthia. What would you like me to do?</Say>
    <Gather input="speech" action="/api/voice/transcribed" method="POST"
            speechTimeout="3" language="en-US">
        <Say voice="alice">I'm listening.</Say>
    </Gather>
    <Say voice="alice">I didn't catch that. Goodbye.</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@router.post("/transcribed")
async def twilio_transcribed(SpeechResult: str = Form(""), Confidence: str = Form("0")):
    """Twilio posts transcription here. Create a task and respond."""
    logger.info("voice.transcribed", speech=SpeechResult, confidence=Confidence)
    # STUB — will create Notion task + trigger agent loop in P3
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Got it. I heard: {_escape_xml(SpeechResult)}. I'll work on that now. Goodbye.</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


def _escape_xml(text: str) -> str:
    """Escape XML special characters to prevent injection in TwiML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
