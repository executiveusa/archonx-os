"""Tests for transcript-driven onboarding runner."""

from __future__ import annotations

import asyncio
import json

import pytest

from archonx.onboarding.voice_agent.runner import OnboardingVoiceRunner


@pytest.fixture
def sample_runner(tmp_path):
    transcript = tmp_path / "transcript.md"
    transcript.write_text(
        """
Business objective: Launch multi-agent automation studio
Current system stack: FastAPI, Hono, React
Constraints: Tight timeline and limited budget
Security/compliance requirements: SOC2-ready controls
Launch channel priority: coolify, cloudflare, vercel
""".strip(),
        encoding="utf-8",
    )

    tasks = tmp_path / "tasks.json"
    tasks.write_text(
        json.dumps(
            {
                "tasks": [
                    {"id": "t1", "type": "mission_parse", "crew": "both", "params": {}},
                    {"id": "t2", "type": "launch_plan", "crew": "white", "params": {}},
                ]
            }
        ),
        encoding="utf-8",
    )
    return OnboardingVoiceRunner(transcript_path=transcript, tasks_path=tasks)


def test_parse_sections(sample_runner: OnboardingVoiceRunner) -> None:
    sections = sample_runner.parse_transcript_sections(sample_runner.load_transcript())
    assert "Launch multi-agent automation studio" in sections["business_objective"]
    assert "FastAPI" in sections["current_stack"]


def test_build_profile(sample_runner: OnboardingVoiceRunner) -> None:
    profile = sample_runner.build_profile(sample_runner.load_transcript(), org_id="org-1", project_id="proj-1")
    assert profile["org_id"] == "org-1"
    assert profile["project_id"] == "proj-1"
    assert "SOC2" in profile["security"]


def test_run_plan_executes_all_tasks(sample_runner: OnboardingVoiceRunner) -> None:
    calls: list[dict[str, object]] = []

    async def fake_executor(task):
        calls.append(task)
        return {"status": "completed"}

    result = asyncio.run(
        sample_runner.run_plan(
            executor=fake_executor,
            transcript_text=sample_runner.load_transcript(),
            org_id="org-2",
            project_id="proj-2",
        )
    )

    assert result["status"] == "completed"
    assert result["tasks_executed"] == 2
    assert len(calls) == 2
    assert calls[0]["params"]["org_id"] == "org-2"
