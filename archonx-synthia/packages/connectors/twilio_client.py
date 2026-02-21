"""Twilio connector — voice webhook handler for push-to-talk MVP.

STUB — full implementation in P3.
"""

from __future__ import annotations

import uuid

import httpx


class TwilioClient:
    """Adapter for Twilio voice calls."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self._http = httpx.AsyncClient(
            base_url=f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}",
            auth=(account_sid, auth_token),
            timeout=30.0,
        )

    async def say(self, call_sid: str, text: str):
        """Send TwiML to an active call to speak text."""
        # STUB
        return {"ok": True, "data": {"call_sid": call_sid, "spoken": True}, "trace_id": str(uuid.uuid4())}

    async def make_call(self, to_number: str, twiml_url: str):
        """Initiate an outbound call."""
        # STUB
        return {"ok": True, "data": {"call_sid": "stub-call-001"}, "trace_id": str(uuid.uuid4())}

    async def close(self):
        await self._http.aclose()
