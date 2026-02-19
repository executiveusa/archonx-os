"""
Upwork Scout Skill
==================
All pawns are scouts. This skill enables any agent to:
1. Search Upwork for matching jobs
2. Analyze job requirements vs agent capabilities
3. Generate personalized proposals
4. Optionally generate Remotion video proposals
5. Track application status

Every scout run feeds improvements back to the flywheel.
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.upwork_scout")


class UpworkScoutSkill(BaseSkill):
    """Scout Upwork for jobs, analyze fit, generate proposals."""

    name = "upwork_scout"
    description = "Search Upwork jobs, analyze fit, and generate proposals"
    category = SkillCategory.FINANCIAL

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Params:
            action: 'search' | 'analyze' | 'propose' | 'video_propose' | 'track'
            query: search terms for job discovery
            job_url: specific Upwork job URL to analyze
            skills_available: list of skills the agent can offer
            portfolio_items: list of relevant portfolio items
        """
        action = context.params.get("action", "search")

        if action == "search":
            data = await self._search_jobs(context)
        elif action == "analyze":
            data = await self._analyze_job(context)
        elif action == "propose":
            data = await self._generate_proposal(context)
        elif action == "video_propose":
            data = await self._generate_video_proposal(context)
        elif action == "track":
            data = await self._track_applications(context)
        else:
            return SkillResult(skill=self.name, status="error", error=f"Unknown action: {action}")

        # Flywheel: every scout run identifies improvements
        improvements = self._identify_improvements(action, data)

        return SkillResult(
            skill=self.name,
            status="success",
            data=data,
            improvements_found=improvements,
        )

    async def _search_jobs(self, ctx: SkillContext) -> dict[str, Any]:
        """Search Upwork for matching jobs."""
        query = ctx.params.get("query", "")
        skills = ctx.params.get("skills_available", [])
        logger.info("Scout searching: '%s' with skills: %s", query, skills)

        # In production: Orgo computer-use to browse Upwork, or Upwork API
        return {
            "query": query,
            "jobs_found": [
                {
                    "title": f"Sample job matching '{query}'",
                    "budget": "$500-$1000",
                    "skills_required": skills[:3] if skills else ["python", "automation"],
                    "posted": "2h ago",
                    "proposals": 5,
                    "fit_score": 0.85,
                },
            ],
            "total_matches": 1,
        }

    async def _analyze_job(self, ctx: SkillContext) -> dict[str, Any]:
        """Analyze a specific job for fit and strategy."""
        job_url = ctx.params.get("job_url", "")
        skills = ctx.params.get("skills_available", [])

        return {
            "job_url": job_url,
            "fit_analysis": {
                "skill_match": 0.85,
                "budget_fit": True,
                "competition_level": "moderate",
                "recommended_rate": "$75/hr",
                "win_probability": 0.6,
            },
            "strategy": {
                "unique_angle": "Emphasize automation + monitoring capabilities",
                "key_differentiators": ["64-agent swarm for parallel execution", "Self-improving system"],
                "proposal_tone": "confident_professional",
            },
        }

    async def _generate_proposal(self, ctx: SkillContext) -> dict[str, Any]:
        """Generate a text proposal for a job."""
        job_url = ctx.params.get("job_url", "")

        # In production: LLM generates personalized proposal
        return {
            "job_url": job_url,
            "proposal": {
                "opening": "I noticed your project requires [X] — I've built exactly this.",
                "body": "My approach: [tailored to job requirements]",
                "closing": "I can start immediately and deliver a working prototype within 48 hours.",
                "estimated_delivery": "48 hours",
                "proposed_rate": "$75/hr",
            },
            "video_available": True,
        }

    async def _generate_video_proposal(self, ctx: SkillContext) -> dict[str, Any]:
        """Generate a Remotion video proposal for maximum impact."""
        job_url = ctx.params.get("job_url", "")

        # In production: trigger Remotion rendering pipeline
        if ctx.tools:
            remotion_tool = ctx.tools.get("remotion")
            if remotion_tool:
                # Dispatch to Remotion tool for video generation
                pass

        return {
            "job_url": job_url,
            "video_proposal": {
                "format": "remotion",
                "duration_seconds": 60,
                "sections": [
                    "personalized_intro",
                    "problem_understanding",
                    "solution_demo",
                    "portfolio_showcase",
                    "call_to_action",
                ],
                "render_status": "queued",
            },
        }

    async def _track_applications(self, ctx: SkillContext) -> dict[str, Any]:
        """Track status of submitted applications."""
        return {
            "active_applications": [],
            "total_sent": 0,
            "response_rate": 0.0,
            "win_rate": 0.0,
        }

    def _identify_improvements(self, action: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Flywheel: identify improvements from this scout run."""
        improvements = []

        if action == "search" and data.get("total_matches", 0) == 0:
            improvements.append({
                "description": "No jobs found — broaden search criteria or add new skill keywords",
                "priority": "medium",
                "category": "scout_effectiveness",
                "suggested_action": "Expand skill tags and search query patterns",
            })

        if action == "analyze":
            fit = data.get("fit_analysis", {})
            if fit.get("skill_match", 0) < 0.5:
                improvements.append({
                    "description": f"Low skill match ({fit.get('skill_match', 0):.0%}) — skill gap identified",
                    "priority": "high",
                    "category": "skill_gap",
                    "suggested_action": "Train agent on missing skills or pair with specialist",
                })

        return improvements
