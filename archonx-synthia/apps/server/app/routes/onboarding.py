"""Onboarding API — first-run profile creation (OS1-style, enterprise-safe)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class OnboardingPayload(BaseModel):
    name: str
    role: str
    goals: list[str]  # 3 bullets
    tools_allowed: list[str]
    approval_rules: dict[str, bool]  # e.g. {"communications": True, "payments": False}
    work_hours: str  # e.g. "09:00-18:00 PST"
    interrupt_policy: str  # "brief" | "confirm-first"
    voice_persona: str  # "proactive" | "confirm-first"


@router.post("/")
async def create_profile(body: OnboardingPayload):
    """Create a Synthia operator profile in Notion Profiles DB."""
    # STUB — will call notion.create in P3
    return {
        "ok": True,
        "data": {
            "profile_id": "stub-profile-001",
            **body.model_dump(),
        },
    }


@router.get("/schema")
async def onboarding_schema():
    """Return the onboarding form schema for the Control Tower UI."""
    return {
        "ok": True,
        "data": {
            "fields": [
                {"name": "name", "type": "text", "required": True},
                {"name": "role", "type": "text", "required": True},
                {"name": "goals", "type": "text_list", "required": True, "max_items": 5},
                {
                    "name": "tools_allowed",
                    "type": "multi_select",
                    "options": [
                        "notion", "orgo", "code_runner", "voice",
                        "web_browse", "email", "calendar",
                    ],
                },
                {
                    "name": "approval_rules",
                    "type": "toggle_group",
                    "options": {
                        "communications": "Require approval for external comms",
                        "calendar": "Require approval for calendar invites",
                        "payments": "Always require approval (locked on)",
                    },
                },
                {"name": "work_hours", "type": "text", "placeholder": "09:00-18:00 PST"},
                {
                    "name": "voice_persona",
                    "type": "select",
                    "options": ["proactive", "confirm-first"],
                },
            ],
        },
    }
