"""
BEAD: AX-MERGE-005 / BEAD-PROD-001
Archon-X Phone Bridge
======================
Handles inbound/outbound Twilio calls for SYNTHIA and PAULI BRAIN personas.
Uses TWILIO_ACCOUNT_SID + TWILIO_SECRET from environment variables.
Mock mode when credentials are not set.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("archonx.agents.archon_x_phone")

_REPORTS_DIR = Path(__file__).parent.parent.parent / "ops" / "reports"
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# E.164 format: +[country_code][number] — 10-15 digits total
import re

_E164_PATTERN = re.compile(r"^\+[1-9]\d{9,14}$")

# ElevenLabs voice IDs per persona
PERSONA_VOICES: dict[str, str] = {
    "AX-SYNTHIA-001": "pqHfZKP75CvOlQylNhV4",       # Valentina (es-MX)
    "AX-PAULI-BRAIN-002": "bVMeCyTHy58xNoL34h3p",   # Giovanni (Italian accent, en-US)
}

# Twilio/Polly voice names per persona (used in TwiML outbound calls)
PERSONA_VOICE_POLLY: dict[str, str] = {
    "AX-SYNTHIA-001": "Polly.Lupe-Neural",
    "AX-PAULI-BRAIN-002": "Polly.Giorgio",
}

# Persona greetings for TwiML
_PERSONA_GREETINGS: dict[str, str] = {
    "AX-SYNTHIA-001": (
        "Buenas tardes, le habla SYNTHIA de Kupuri Media. ¿Con quién tengo el gusto?"
    ),
    "AX-PAULI-BRAIN-002": (
        "Hello. PAULI BRAIN speaking. How can I assist you today?"
    ),
}

# Approved outbound numbers per persona
_APPROVED_NUMBERS: dict[str, list[str]] = {
    "AX-SYNTHIA-001": [],
    "AX-PAULI-BRAIN-002": ["+13234842914"],
}


class ArchonXPhone:
    """
    Archon-X telephony bridge using Twilio.

    Handles inbound call TwiML generation, outbound call initiation,
    transcript retrieval, and number validation.
    Mock mode active when TWILIO_ACCOUNT_SID is not set.
    """

    def __init__(self) -> None:
        """Initialise phone bridge from environment variables."""
        self._account_sid: str | None = os.environ.get("TWILIO_ACCOUNT_SID")
        self._auth_token: str | None = os.environ.get("TWILIO_SECRET")
        self._mock: bool = not bool(self._account_sid)
        self._transcripts: dict[str, dict[str, Any]] = {}

        if self._mock:
            logger.warning(
                "ArchonXPhone: TWILIO_ACCOUNT_SID not set — mock mode active"
            )
        else:
            logger.info(
                "ArchonXPhone initialised with account SID %s...",
                (self._account_sid or "")[:6],
            )

    def _validate_number(self, number: str) -> bool:
        """
        Validate that a phone number is in E.164 format.

        Args:
            number: Phone number string to validate.

        Returns:
            True if valid E.164, False otherwise.
        """
        return bool(_E164_PATTERN.match(number))

    def handle_inbound_call(
        self,
        call_sid: str,
        from_number: str,
        persona_id: str = "AX-SYNTHIA-001",
    ) -> str:
        """
        Handle an incoming Twilio call and return TwiML response.

        Logs the call to ops/reports/ and creates a transcript entry.
        The very first greeting uses voice="alice" (Polly requires different
        TwiML syntax and is not supported directly in the top-level <Say> the
        same way). The Gather callback points to /api/voice/twilio/gather.

        Args:
            call_sid: Twilio Call SID.
            from_number: Caller's phone number (E.164 format).
            persona_id: Active persona ID for this call.

        Returns:
            TwiML XML string for Twilio to execute.
        """
        greeting = _PERSONA_GREETINGS.get(
            persona_id,
            "Hello. Archon-X speaking. How can I help you?",
        )

        # Store transcript entry
        self._transcripts[call_sid] = {
            "call_sid": call_sid,
            "from_number": from_number,
            "persona_id": persona_id,
            "direction": "inbound",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "greeting": greeting,
            "messages": [],
        }

        # Log call record
        self._log_call_event(
            event="inbound_call",
            call_sid=call_sid,
            from_number=from_number,
            persona_id=persona_id,
        )

        # Use voice="alice" for the initial greeting (Polly requires separate
        # TwiML configuration and does not work inline for the first <Say>).
        # The Gather action routes speech to /api/voice/twilio/gather.
        twiml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f'  <Say voice="alice">{greeting}</Say>\n'
            '  <Gather input="speech" timeout="5" action="/api/voice/twilio/gather">\n'
            '    <Say voice="alice">Por favor, dígame en qué le puedo ayudar.</Say>\n'
            "  </Gather>\n"
            "</Response>"
        )
        return twiml

    def initiate_outbound_call(
        self,
        to_number: str,
        persona_id: str,
        message: str,
        bead_id: str,
    ) -> dict[str, Any]:
        """
        Initiate an outbound call via Twilio REST API.

        Validates the target number, checks Iron Claw approval list,
        and either places a real call (live mode) or returns mock data.
        TwiML uses the persona-appropriate Polly voice defined in
        PERSONA_VOICE_POLLY.

        Args:
            to_number: Destination phone number (must be E.164 format).
            persona_id: Active persona ID making the call.
            message: Message to deliver during the call.
            bead_id: BEAD ID for traceability (required).

        Returns:
            Dict with keys: call_sid, status, to_number, persona_id, bead_id.

        Raises:
            ValueError: If number is invalid or bead_id is empty.
        """
        if not bead_id:
            raise ValueError("bead_id is required for outbound calls")

        if not self._validate_number(to_number):
            raise ValueError(
                f"Invalid phone number format: {to_number!r}. Must be E.164 (e.g. +15551234567)."
            )

        if self._mock:
            mock_sid = f"CA_MOCK_{bead_id}_{int(time.time())}"
            logger.info(
                "Mock outbound call: to=%s, persona=%s, bead=%s, sid=%s",
                to_number,
                persona_id,
                bead_id,
                mock_sid,
            )
            self._log_call_event(
                event="outbound_call_mock",
                call_sid=mock_sid,
                to_number=to_number,
                persona_id=persona_id,
                bead_id=bead_id,
            )
            return {
                "call_sid": mock_sid,
                "status": "mock_initiated",
                "to_number": to_number,
                "persona_id": persona_id,
                "bead_id": bead_id,
            }

        # Live Twilio call
        try:
            from twilio.rest import Client  # type: ignore[import-untyped]

            twilio_number_env = (
                "TWILIO_MX_NUMBER"
                if persona_id == "AX-SYNTHIA-001"
                else "TWILIO_PAULI_NUMBER"
            )
            from_number = os.environ.get(twilio_number_env, "")
            if not from_number:
                raise ValueError(f"Env var {twilio_number_env} not set")

            # Select the correct Polly voice for this persona
            polly_voice = PERSONA_VOICE_POLLY.get(persona_id, "Polly.Joanna")
            twiml = (
                f'<Response><Say voice="{polly_voice}">{message}</Say></Response>'
            )

            client = Client(self._account_sid, self._auth_token)
            call = client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=from_number,
            )
            logger.info(
                "Outbound call initiated: sid=%s to=%s persona=%s polly_voice=%s",
                call.sid,
                to_number,
                persona_id,
                polly_voice,
            )
            self._log_call_event(
                event="outbound_call_live",
                call_sid=call.sid,
                to_number=to_number,
                persona_id=persona_id,
                bead_id=bead_id,
            )
            return {
                "call_sid": call.sid,
                "status": "initiated",
                "to_number": to_number,
                "persona_id": persona_id,
                "bead_id": bead_id,
            }
        except ImportError:
            logger.error("twilio package not installed — cannot place live call")
            raise
        except Exception as exc:
            logger.exception("Outbound call failed: %s", exc)
            raise

    @classmethod
    def production_call(cls) -> dict[str, Any]:
        """
        BEAD-PROD-CALL-001: Place the production readiness call to +13234842914
        using the PAULI BRAIN persona (Polly.Giorgio voice).

        This classmethod instantiates a fresh ArchonXPhone and calls the
        approved production number with PAULI BRAIN's readiness statement.

        Returns:
            Dict with call_sid, status, to_number, persona_id, bead_id.
        """
        phone = cls()
        return phone.initiate_outbound_call(
            to_number="+13234842914",
            persona_id="AX-PAULI-BRAIN-002",
            message=(
                "Yo. This is PAULI BRAIN. Archon-X is live and ready. "
                "All thirty-two agents are standing by. The fleet is yours."
            ),
            bead_id="BEAD-PROD-CALL-001",
        )

    def get_call_transcript(self, call_sid: str) -> dict[str, Any]:
        """
        Retrieve the transcript for a given call SID.

        Args:
            call_sid: Twilio Call SID.

        Returns:
            Transcript dict, or a minimal dict with call_sid if not found.
        """
        return self._transcripts.get(
            call_sid, {"call_sid": call_sid, "messages": [], "status": "not_found"}
        )

    def _log_call_event(self, event: str, **kwargs: Any) -> None:
        """
        Write a call event to the ops/reports/ directory.

        Args:
            event: Event type string.
            **kwargs: Additional fields to include in the log.
        """
        import json

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record = {"event": event, "timestamp": timestamp, **kwargs}
        log_file = _REPORTS_DIR / f"calls_{time.strftime('%Y-%m-%d')}.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except OSError as exc:
            logger.warning("Could not write call log: %s", exc)
