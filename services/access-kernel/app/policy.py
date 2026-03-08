import hashlib
import json
from pathlib import Path
from typing import Any


class PolicyEngine:
    def __init__(self, policy_path: str) -> None:
        self.policy_path = Path(policy_path)
        self._policy = self._load()

    def _load(self) -> dict[str, Any]:
        with self.policy_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def reload(self) -> None:
        self._policy = self._load()

    @property
    def hash(self) -> str:
        raw = json.dumps(self._policy, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def evaluate(self, principal_type: str, resource: str, action: str) -> dict[str, Any]:
        for rule in self._policy.get("rules", []):
            if (
                rule.get("principal_type") == principal_type
                and rule.get("resource") == resource
                and rule.get("action") == action
            ):
                return {
                    "allow": bool(rule.get("allow", False)),
                    "approval_required": bool(rule.get("approval_required", False)),
                    "matched_rule": rule,
                }

        return {
            "allow": False if self._policy.get("deny_by_default", True) else True,
            "approval_required": False,
            "matched_rule": None,
        }
