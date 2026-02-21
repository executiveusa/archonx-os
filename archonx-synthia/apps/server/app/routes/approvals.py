"""Approvals API — human-in-the-loop gating for irreversible actions."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ApprovalDecision(BaseModel):
    decision: str  # "approved" | "denied"
    decided_by: str = "operator"


@router.get("/")
async def list_pending():
    """List all pending approval requests."""
    # STUB — will query Notion Approvals DB in P3
    return {"ok": True, "data": []}


@router.post("/{approval_id}/resolve")
async def resolve_approval(approval_id: str, body: ApprovalDecision):
    """Approve or deny a pending action."""
    if body.decision not in ("approved", "denied"):
        return {"ok": False, "error": "Decision must be 'approved' or 'denied'"}
    # STUB — will call notion.resolve_approval_request() in P3
    return {
        "ok": True,
        "data": {
            "approval_id": approval_id,
            "status": body.decision,
            "decided_by": body.decided_by,
        },
    }


@router.get("/{approval_id}")
async def get_approval(approval_id: str):
    """Get details of an approval request."""
    # STUB
    return {
        "ok": True,
        "data": {
            "approval_id": approval_id,
            "action": "stub_action",
            "context": "stub context",
            "status": "pending",
        },
    }
