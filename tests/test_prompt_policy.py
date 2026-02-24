from pathlib import Path

from archonx.security.prompt_policy import PromptApprovalPolicy


def test_non_autonomous_task_is_allowed(tmp_path: Path) -> None:
	approved_path = tmp_path / "approved_prompts.json"
	approved_path.write_text('{"approved_prompts": ["prompt-00001"]}', encoding="utf-8")

	policy = PromptApprovalPolicy(approved_path=approved_path)
	ok, reason = policy.validate({"task": "normal"})

	assert ok is True
	assert reason == "non-autonomous mode"


def test_autonomous_requires_approved_prompt(tmp_path: Path) -> None:
	approved_path = tmp_path / "approved_prompts.json"
	approved_path.write_text('{"approved_prompts": ["prompt-00001"]}', encoding="utf-8")

	policy = PromptApprovalPolicy(approved_path=approved_path)

	ok_missing, _ = policy.validate({"mode": "autonomous"})
	ok_unapproved, _ = policy.validate({"mode": "autonomous", "prompt_id": "prompt-00009"})
	ok_approved, _ = policy.validate({"mode": "autonomous", "prompt_id": "prompt-00001"})

	assert ok_missing is False
	assert ok_unapproved is False
	assert ok_approved is True