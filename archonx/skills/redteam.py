from __future__ import annotations
import logging
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult
from archonx.security.pentest import get_pentest_scanner

logger = logging.getLogger("archonx.skills.redteam")

class RedteamSkill(BaseSkill):
    """
    Skill for autonomous redteaming and security validation.
    Phase 7: Autonomous QA & Redteaming.
    """
    name = "redteam"
    description = "Autonomous security auditing and secret exposure scanning"
    category = SkillCategory.SYSTEM # or SECURITY if it existed
    _ACTIONS = {"scan", "audit", "verify"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scanner = get_pentest_scanner()

    async def execute(self, context: SkillContext) -> SkillResult:
        action = str(context.params.get("action", "scan")).lower()
        if action not in self._ACTIONS:
            return SkillResult(skill=self.name, status="error", error=f"Unsupported action '{action}'")

        if action in ("scan", "audit"):
            findings = self.scanner.scan_project()
            
            status = "success" if not findings else "warning"
            message = "Scan complete. No vulnerabilities found." if not findings else f"Scan complete. Found {len(findings)} critical vulnerabilities."
            
            return SkillResult(
                skill=self.name,
                status=status,
                data={
                    "findings": findings,
                    "count": len(findings),
                    "message": message
                }
            )
            
        return SkillResult(
            skill=self.name,
            status="success",
            data={"action": action, "message": "Action completed"}
        )
