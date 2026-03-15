"""
Tests — Skills Framework (BaseSkill, SkillRegistry, auto-discovery)
"""

import asyncio
from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult
from archonx.skills.registry import SkillRegistry


class _DummySkill(BaseSkill):
    name = "dummy_test_skill"
    description = "A test skill"
    category = SkillCategory.AUTOMATION

    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(
            skill=self.name,
            status="success",
            data={"echo": context.task},
            improvements_found=["test-improvement"],
        )


class _FailingSkill(BaseSkill):
    name = "failing_test_skill"
    description = "Always raises"
    category = SkillCategory.SECURITY

    async def execute(self, context: SkillContext) -> SkillResult:
        raise RuntimeError("intentional failure")


def _ctx(task_desc: str = "test") -> SkillContext:
    return SkillContext(task={"description": task_desc}, agent_id="test_agent")


# --- BaseSkill ---

def test_skill_to_dict() -> None:
    s = _DummySkill()
    d = s.to_dict()
    assert d["name"] == "dummy_test_skill"
    assert d["category"] == "automation"
    assert d["version"] == "0.1.0"


def test_skill_execute_returns_result() -> None:
    s = _DummySkill()
    result = asyncio.get_event_loop().run_until_complete(s.execute(_ctx("hello")))
    assert result.status == "success"
    assert result.data["echo"]["description"] == "hello"
    assert result.improvements_found == ["test-improvement"]


# --- SkillRegistry ---

def test_register_and_get() -> None:
    reg = SkillRegistry()
    reg.register(_DummySkill())
    skill = reg.get("dummy_test_skill")
    assert skill.name == "dummy_test_skill"


def test_get_missing_raises() -> None:
    reg = SkillRegistry()
    try:
        reg.get("nonexistent")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_list_skills_returns_objects() -> None:
    reg = SkillRegistry()
    reg.register(_DummySkill())
    skills = reg.list_skills()
    assert len(skills) == 1
    assert isinstance(skills[0], BaseSkill)


def test_by_category() -> None:
    reg = SkillRegistry()
    reg.register(_DummySkill())
    reg.register(_FailingSkill())
    auto = reg.by_category(SkillCategory.AUTOMATION)
    sec = reg.by_category(SkillCategory.SECURITY)
    assert len(auto) == 1
    assert len(sec) == 1
    assert auto[0].name == "dummy_test_skill"


def test_execute_success() -> None:
    reg = SkillRegistry()
    reg.register(_DummySkill())
    result = asyncio.get_event_loop().run_until_complete(reg.execute("dummy_test_skill", _ctx()))
    assert result.status == "success"


def test_execute_failing_returns_error() -> None:
    reg = SkillRegistry()
    reg.register(_FailingSkill())
    result = asyncio.get_event_loop().run_until_complete(reg.execute("failing_test_skill", _ctx()))
    assert result.status == "error"
    assert "intentional failure" in result.error


def test_auto_discover_finds_all_skills() -> None:
    reg = SkillRegistry()
    reg.auto_discover()
    skills = reg.list_skills()
    assert len(skills) >= 22, f"Expected ≥22 skills, found {len(skills)}"
    names = {s.name for s in skills}
    assert "web_scraping" in names
    assert "upwork_scout" in names
    assert "email_management" in names
    assert "security_audit" in names


def test_auto_discover_no_duplicates() -> None:
    reg = SkillRegistry()
    reg.auto_discover()
    reg.auto_discover()  # intentional double call
    names = [s.name for s in reg.list_skills()]
    assert len(names) == len(set(names)), "Duplicate skills after double discover"


def test_all_skills_have_required_attrs() -> None:
    reg = SkillRegistry()
    reg.auto_discover()
    for skill in reg.all():
        assert hasattr(skill, "name") and isinstance(skill.name, str)
        assert hasattr(skill, "description") and isinstance(skill.description, str)
        assert hasattr(skill, "category") and isinstance(skill.category, SkillCategory)
