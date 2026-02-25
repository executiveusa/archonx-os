"""
BEAD: AX-MERGE-009
Tests for ArchonXPhone
=======================
4 tests — mock mode (no real Twilio calls).
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from archonx.agents.archon_x_phone import ArchonXPhone


@pytest.fixture
def phone() -> ArchonXPhone:
    """Create an ArchonXPhone in mock mode (no Twilio credentials)."""
    with patch.dict(os.environ, {}, clear=False):
        env = os.environ.copy()
        env.pop("TWILIO_ACCOUNT_SID", None)
        env.pop("TWILIO_SECRET", None)
        with patch.dict(os.environ, env, clear=True):
            return ArchonXPhone()


def test_phone_validates_e164_number(phone: ArchonXPhone) -> None:
    """Valid E.164 numbers should pass _validate_number()."""
    assert phone._validate_number("+15551234567") is True
    assert phone._validate_number("+525512345678") is True
    assert phone._validate_number("+381641234567") is True
    assert phone._validate_number("+447911123456") is True


def test_phone_rejects_invalid_number(phone: ArchonXPhone) -> None:
    """Invalid or non-E.164 numbers should fail _validate_number()."""
    assert phone._validate_number("5551234567") is False       # no +
    assert phone._validate_number("+0123456789") is False      # +0 is invalid
    assert phone._validate_number("+1") is False               # too short
    assert phone._validate_number("invalid") is False
    assert phone._validate_number("") is False
    assert phone._validate_number("+1234567890123456") is False  # too long (16 digits)


def test_phone_mock_inbound_returns_twiml(phone: ArchonXPhone) -> None:
    """Mock inbound call should return valid TwiML XML."""
    twiml = phone.handle_inbound_call(
        call_sid="CA_test_001",
        from_number="+15551234567",
        persona_id="AX-SYNTHIA-001",
    )
    # Must be valid XML with Response root
    assert "<?xml" in twiml
    assert "<Response>" in twiml
    assert "</Response>" in twiml
    # Must contain SYNTHIA greeting
    assert "SYNTHIA" in twiml
    assert "Kupuri Media" in twiml

    # Transcript should be stored
    transcript = phone.get_call_transcript("CA_test_001")
    assert transcript["call_sid"] == "CA_test_001"
    assert transcript["persona_id"] == "AX-SYNTHIA-001"


def test_phone_mock_outbound_returns_call_sid(phone: ArchonXPhone) -> None:
    """Mock outbound call should return a dict with a call_sid."""
    result = phone.initiate_outbound_call(
        to_number="+15559876543",
        persona_id="AX-SYNTHIA-001",
        message="Hola, le llama SYNTHIA de Kupuri Media.",
        bead_id="BEAD-TEST-PHONE-001",
    )
    assert "call_sid" in result
    assert result["call_sid"].startswith("CA_MOCK_")
    assert result["status"] == "mock_initiated"
    assert result["to_number"] == "+15559876543"
    assert result["persona_id"] == "AX-SYNTHIA-001"
    assert result["bead_id"] == "BEAD-TEST-PHONE-001"
