"""
Skill Base & Context
====================
Every ArchonX skill implements BaseSkill.
Skills differ from tools: a tool is a single operation, a skill is a
multi-step workflow that may use several tools + LLM reasoning.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("archonx.skills.base")


class SkillCategory(str, Enum):
    AUTOMATION = "automation"
    RESEARCH = "research"
    CREATIVE = "creative"
    DEPLOYMENT = "deployment"
    COMMUNICATION = "communication"
    SECURITY = "security"
    FINANCIAL = "financial"
    PERSONAL = "personal"
    COMPUTER_USE = "computer_use"


@dataclass
class SkillContext:
    """Runtime context passed into every skill execution."""

    task: dict[str, Any]
    agent_id: str
    session_id: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    tools: Any = None  # ToolRegistry reference
    skills: Any = None  # SkillRegistry reference (for sub-skill calls)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillResult:
    """Standard output from a skill execution."""

    skill: str
    status: str  # "success" | "error" | "partial"
    data: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    # Flywheel hook: every skill can report friction points it discovered
    improvements_found: list[str] = field(default_factory=list)


class BaseSkill(ABC):
    """Interface every ArchonX skill must implement."""

    name: str
    description: str
    category: SkillCategory
    required_tools: list[str] = []
    version: str = "0.1.0"

    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """Run the skill with the given context."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "required_tools": self.required_tools,
            "version": self.version,
        }
