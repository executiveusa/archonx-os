"""
Onboarding Voice Runner
=======================
Turns transcript intake into a runnable onboarding plan for ArchonX.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Awaitable, Callable


DEFAULT_TRANSCRIPT_PATH = Path(__file__).resolve().parent / "transcript_intake.md"
DEFAULT_TASKS_PATH = Path(__file__).resolve().parent / "onboarding_tasks.json"


class OnboardingVoiceRunner:
    """Build onboarding profile data and execute the onboarding task bundle."""

    def __init__(
        self,
        transcript_path: Path = DEFAULT_TRANSCRIPT_PATH,
        tasks_path: Path = DEFAULT_TASKS_PATH,
    ) -> None:
        self.transcript_path = transcript_path
        self.tasks_path = tasks_path

    def load_transcript(self) -> str:
        return self.transcript_path.read_text(encoding="utf-8")

    def load_tasks(self) -> dict[str, Any]:
        return json.loads(self.tasks_path.read_text(encoding="utf-8"))

    def parse_transcript_sections(self, transcript_text: str) -> dict[str, str]:
        """Extract structured fields from free-form transcript text."""
        sections: dict[str, str] = {
            "business_objective": "",
            "current_stack": "",
            "constraints": "",
            "security_requirements": "",
            "launch_priorities": "",
            "raw": transcript_text.strip(),
        }

        current_key = ""
        for raw_line in transcript_text.splitlines():
            line = raw_line.strip()
            lowered = line.lower()
            if not line:
                continue

            if lowered.startswith("business objective"):
                current_key = "business_objective"
                sections[current_key] = line.split(":", 1)[-1].strip()
                continue
            if lowered.startswith("current system stack") or lowered.startswith("current stack"):
                current_key = "current_stack"
                sections[current_key] = line.split(":", 1)[-1].strip()
                continue
            if lowered.startswith("constraints") or lowered.startswith("deadlines"):
                current_key = "constraints"
                sections[current_key] = line.split(":", 1)[-1].strip()
                continue
            if lowered.startswith("security") or lowered.startswith("compliance"):
                current_key = "security_requirements"
                sections[current_key] = line.split(":", 1)[-1].strip()
                continue
            if lowered.startswith("launch channel priority") or lowered.startswith("launch priorities"):
                current_key = "launch_priorities"
                sections[current_key] = line.split(":", 1)[-1].strip()
                continue

            if current_key:
                existing = sections[current_key]
                sections[current_key] = f"{existing} {line}".strip()

        return sections

    def build_profile(self, transcript_text: str, org_id: str, project_id: str) -> dict[str, Any]:
        sections = self.parse_transcript_sections(transcript_text)
        return {
            "org_id": org_id,
            "project_id": project_id,
            "mission": sections.get("business_objective") or "Define and execute launch mission",
            "system_stack": sections.get("current_stack", ""),
            "constraints": sections.get("constraints", ""),
            "security": sections.get("security_requirements", ""),
            "launch_priorities": sections.get("launch_priorities", "coolify,cloudflare,vercel"),
            "transcript_sections": sections,
        }

    async def run_plan(
        self,
        executor: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        transcript_text: str,
        org_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        tasks_data = self.load_tasks()
        tasks = tasks_data.get("tasks", [])
        profile = self.build_profile(transcript_text, org_id=org_id, project_id=project_id)

        results: list[dict[str, Any]] = []
        for task in tasks:
            task_payload = deepcopy(task)
            params = task_payload.setdefault("params", {})
            params["onboarding_profile"] = profile
            params["org_id"] = org_id
            params["project_id"] = project_id
            result = await executor(task_payload)
            results.append({"task_id": task_payload.get("id"), "result": result})

        return {
            "status": "completed",
            "org_id": org_id,
            "project_id": project_id,
            "profile": profile,
            "results": results,
            "tasks_executed": len(results),
        }
