"""Prompt approval policy for autonomous execution modes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PromptApprovalPolicy:
	"""Enforces approved prompts for autonomous/yolo tasks."""

	def __init__(
		self,
		approved_path: Path | None = None,
	) -> None:
		root = Path(__file__).resolve().parents[2]
		self.approved_path = approved_path or (root / "data" / "prompt_registry" / "approved_prompts.json")
		self._approved_cache: set[str] = set()
		self._load()

	def _load(self) -> None:
		if not self.approved_path.exists():
			self._approved_cache = set()
			return
		payload = json.loads(self.approved_path.read_text(encoding="utf-8"))
		prompts = payload.get("approved_prompts", []) if isinstance(payload, dict) else []
		self._approved_cache = {str(item).strip() for item in prompts if str(item).strip()}

	@staticmethod
	def is_autonomous_task(task: dict[str, Any]) -> bool:
		mode = str(task.get("mode", "")).strip().lower()
		return bool(task.get("autonomous") or task.get("yolo_mode") or mode in {"autonomous", "yolo"})

	@staticmethod
	def prompt_reference(task: dict[str, Any]) -> str:
		for key in ("prompt_id", "prompt_ref", "prompt_path"):
			val = task.get(key)
			if isinstance(val, str) and val.strip():
				return val.strip()
		return ""

	def is_approved(self, prompt_ref: str) -> bool:
		return prompt_ref in self._approved_cache

	def validate(self, task: dict[str, Any]) -> tuple[bool, str]:
		if not self.is_autonomous_task(task):
			return True, "non-autonomous mode"

		prompt_ref = self.prompt_reference(task)
		if not prompt_ref:
			return False, "autonomous mode requires task.prompt_id, task.prompt_ref, or task.prompt_path"

		if not self._approved_cache:
			return False, f"no approved prompts configured ({self.approved_path})"

		if not self.is_approved(prompt_ref):
			return False, f"prompt not approved for autonomous mode: {prompt_ref}"

		return True, "approved"
