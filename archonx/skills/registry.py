"""
Skill Registry
==============
Central registry and auto-discovery for all ArchonX skills.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.registry")


class SkillRegistry:
    """Discover, register, and execute skills."""

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill
        logger.info("Skill registered: %s [%s]", skill.name, skill.category.value)

    def get(self, name: str) -> BaseSkill:
        if name not in self._skills:
            raise KeyError(f"Skill not found: {name}")
        return self._skills[name]

    def list_skills(self) -> list[BaseSkill]:
        return list(self._skills.values())

    def by_category(self, category: SkillCategory) -> list[BaseSkill]:
        return [s for s in self._skills.values() if s.category == category]

    def all(self) -> list[BaseSkill]:
        return list(self._skills.values())

    async def execute(self, name: str, context: SkillContext) -> SkillResult:
        skill = self.get(name)
        try:
            result = await skill.execute(context)
            if result.improvements_found:
                logger.info(
                    "Skill %s reported %d improvements",
                    name,
                    len(result.improvements_found),
                )
            return result
        except Exception as exc:
            logger.exception("Skill %s failed", name)
            return SkillResult(skill=name, status="error", error=str(exc))

    def auto_discover(self) -> None:
        """Scan archonx.skills package for BaseSkill subclasses and register them."""
        import archonx.skills as skills_pkg

        for _importer, modname, _ispkg in pkgutil.walk_packages(
            skills_pkg.__path__, prefix="archonx.skills."
        ):
            if modname in ("archonx.skills.base", "archonx.skills.registry"):
                continue
            try:
                mod = importlib.import_module(modname)
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseSkill)
                        and attr is not BaseSkill
                        and hasattr(attr, "name")
                        and isinstance(getattr(attr, "name", None), str)
                    ):
                        instance = attr()
                        if instance.name not in self._skills:
                            self.register(instance)
            except Exception:
                logger.debug("Could not import %s for skill discovery", modname)
