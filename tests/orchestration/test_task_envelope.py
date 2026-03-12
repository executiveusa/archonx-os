"""Tests for canonical Archon task envelopes."""

from archonx.orchestration import TaskEnvelope


def test_task_envelope_validates_required_fields() -> None:
    envelope = TaskEnvelope(
        objective="Implement worker capability routing",
        intent="code_change",
        repo="executiveusa/archonx-os",
        allowed_tools=["mcp2cli", "DesktopCommanderMCP"],
        trace_id="trace-001",
    )

    assert envelope.validate() == []
    assert envelope.to_dict()["requested_by"] == "archonx-os"


def test_task_envelope_rejects_non_archon_requester() -> None:
    envelope = TaskEnvelope(
        objective="",
        intent="",
        repo="",
        requested_by="worker",
    )

    errors = envelope.validate()
    assert "objective is required" in errors
    assert "intent is required" in errors
    assert "repo is required" in errors
    assert "requested_by must be archonx-os" in errors
