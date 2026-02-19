"""
Lead Generation Skill
=====================
Find, qualify, and nurture leads across platforms using web scraping and APIs.
Supports LinkedIn, directories, and custom lead sources.

Podcast use case: "find leads — scrape directories, qualify via criteria"
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.lead_generation")


class LeadStatus(str, Enum):
    """Lead status in the sales funnel."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadScore(int, Enum):
    """Lead quality score."""
    HOT = 90
    WARM = 70
    COOL = 50
    COLD = 30


@dataclass
class Lead:
    """Represents a sales lead."""
    name: str
    email: str | None = None
    company: str | None = None
    title: str | None = None
    phone: str | None = None
    website: str | None = None
    linkedin: str | None = None
    source: str | None = None
    status: LeadStatus = LeadStatus.NEW
    score: int = 0
    notes: list[str] | None = None
    created_at: str | None = None
    tags: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert lead to dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "title": self.title,
            "phone": self.phone,
            "website": self.website,
            "linkedin": self.linkedin,
            "source": self.source,
            "status": self.status.value,
            "score": self.score,
            "notes": self.notes or [],
            "created_at": self.created_at,
            "tags": self.tags or [],
        }


class LeadGenerationSkill(BaseSkill):
    """Find, qualify, and nurture sales leads."""

    name = "lead_generation"
    description = "Find, qualify, and nurture sales leads"
    category = SkillCategory.FINANCIAL

    # Lead sources configuration
    LEAD_SOURCES = {
        "linkedin": {
            "requires_auth": True,
            "rate_limit": "100/day",
        },
        "crunchbase": {
            "requires_auth": True,
            "rate_limit": "1000/month",
        },
        "yelp": {
            "requires_auth": False,
            "rate_limit": "unlimited",
        },
        "google_maps": {
            "requires_auth": True,
            "rate_limit": "varies",
        },
        "directory": {
            "requires_auth": False,
            "rate_limit": "varies",
        },
    }

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Generate and manage leads.

        Params:
            action: 'search' | 'qualify' | 'outreach' | 'nurture' | 'enrich' | 'score'
            criteria: Search criteria dict with:
                - industry: Target industry
                - location: Geographic location
                - company_size: Employee count range
                - title: Job title filter
                - keywords: Keywords to search
                - source: Lead source (linkedin, crunchbase, directory, etc.)
            leads: List of leads to process (for qualify/outreach/nurture)
            scoring_model: Custom scoring weights (optional)
            outreach_template: Template for outreach messages (optional)
            max_results: Maximum leads to return (default: 50)
        """
        action = context.params.get("action", "search")
        criteria = context.params.get("criteria", {})
        leads = context.params.get("leads", [])
        scoring_model = context.params.get("scoring_model")
        outreach_template = context.params.get("outreach_template")
        max_results = context.params.get("max_results", 50)

        try:
            if action == "search":
                result = await self._search_leads(criteria, max_results, context)
            elif action == "qualify":
                result = await self._qualify_leads(leads, criteria, context)
            elif action == "outreach":
                result = await self._outreach_leads(leads, outreach_template, context)
            elif action == "nurture":
                result = await self._nurture_leads(leads, context)
            elif action == "enrich":
                result = await self._enrich_leads(leads, context)
            elif action == "score":
                result = await self._score_leads(leads, scoring_model, context)
            else:
                return SkillResult(
                    skill=self.name,
                    status="error",
                    error=f"Unknown action: {action}",
                    data={"action": action}
                )

            return SkillResult(
                skill=self.name,
                status="success",
                data=result,
                metadata={
                    "action": action,
                    "criteria": criteria,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            logger.error("Lead generation failed: %s", str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"action": action}
            )

    async def _search_leads(
        self,
        criteria: dict[str, Any],
        max_results: int,
        context: SkillContext
    ) -> dict[str, Any]:
        """Search for leads based on criteria."""
        source = criteria.get("source", "directory")
        industry = criteria.get("industry", "")
        location = criteria.get("location", "")
        keywords = criteria.get("keywords", [])
        title = criteria.get("title", "")

        leads = []

        # Check for web scraping capability
        if hasattr(context, "tools") and "web_scraping" in context.tools:
            # Use web scraping to find leads
            leads = await self._scrape_leads(criteria, max_results, context)
        else:
            # Generate mock leads for demonstration
            leads = self._generate_mock_leads(criteria, max_results)

        return {
            "leads": [lead.to_dict() for lead in leads],
            "total_found": len(leads),
            "source": source,
            "criteria": criteria,
        }

    async def _scrape_leads(
        self,
        criteria: dict[str, Any],
        max_results: int,
        context: SkillContext
    ) -> list[Lead]:
        """Scrape leads from web sources."""
        leads = []
        keywords = criteria.get("keywords", [])
        industry = criteria.get("industry", "")

        # Build search query
        query = " ".join(keywords) if keywords else industry

        # Use web scraping tool
        try:
            scrape_result = await context.tools["web_scraping"](
                url=criteria.get("url", f"https://www.google.com/search?q={query}"),
                selectors={
                    "names": "h3",
                    "companies": ".company-name",
                    "descriptions": ".description",
                },
                extract_links=True,
            )

            # Parse results into leads
            if scrape_result.get("extracted"):
                for i, name in enumerate(scrape_result["extracted"].get("names", [])[:max_results]):
                    lead = Lead(
                        name=name,
                        company=scrape_result["extracted"].get("companies", [None])[i] if i < len(scrape_result["extracted"].get("companies", [])) else None,
                        source="web_scraping",
                        created_at=datetime.utcnow().isoformat(),
                    )
                    leads.append(lead)

        except Exception as e:
            logger.warning("Lead scraping failed: %s", e)

        return leads

    def _generate_mock_leads(
        self,
        criteria: dict[str, Any],
        max_results: int
    ) -> list[Lead]:
        """Generate mock leads for testing/demo."""
        industry = criteria.get("industry", "Technology")
        location = criteria.get("location", "San Francisco, CA")

        mock_companies = [
            {"name": "TechCorp Inc.", "employees": "50-100"},
            {"name": "Innovate Solutions", "employees": "100-500"},
            {"name": "Digital Dynamics", "employees": "10-50"},
            {"name": "Cloud Systems LLC", "employees": "500-1000"},
            {"name": "Data Insights Co.", "employees": "50-100"},
        ]

        mock_titles = [
            "CEO", "CTO", "VP of Engineering", "Director of Operations",
            "Head of Product", "Engineering Manager", "Founder", "COO"
        ]

        leads = []
        for i in range(min(max_results, 10)):
            company = mock_companies[i % len(mock_companies)]
            lead = Lead(
                name=f"Lead {i+1}",
                email=f"contact{i+1}@{company['name'].lower().replace(' ', '').replace('.', '')}.com",
                company=company["name"],
                title=mock_titles[i % len(mock_titles)],
                source="mock_data",
                status=LeadStatus.NEW,
                score=50 + (i * 5),
                created_at=datetime.utcnow().isoformat(),
                tags=[industry, location],
            )
            leads.append(lead)

        return leads

    async def _qualify_leads(
        self,
        leads: list[dict[str, Any]],
        criteria: dict[str, Any],
        context: SkillContext
    ) -> dict[str, Any]:
        """Qualify leads based on criteria."""
        qualified = []
        disqualified = []

        min_score = criteria.get("min_score", 50)
        required_fields = criteria.get("required_fields", ["email"])
        company_size = criteria.get("company_size", {})
        industries = criteria.get("industries", [])

        for lead_data in leads:
            lead = Lead(**lead_data) if isinstance(lead_data, dict) else lead_data

            # Check required fields
            has_required = all(
                getattr(lead, field, None) for field in required_fields
            )

            # Check score threshold
            meets_score = lead.score >= min_score

            # Check industry match
            industry_match = not industries or any(
                tag.lower() in [i.lower() for i in industries]
                for tag in (lead.tags or [])
            )

            if has_required and meets_score and industry_match:
                lead.status = LeadStatus.QUALIFIED
                qualified.append(lead.to_dict())
            else:
                disqualified.append({
                    "lead": lead.to_dict(),
                    "reason": self._get_disqualification_reason(
                        lead, has_required, meets_score, industry_match
                    ),
                })

        return {
            "qualified": qualified,
            "disqualified": disqualified,
            "qualification_rate": len(qualified) / len(leads) if leads else 0,
        }

    def _get_disqualification_reason(
        self,
        lead: Lead,
        has_required: bool,
        meets_score: bool,
        industry_match: bool
    ) -> str:
        """Get the reason for lead disqualification."""
        reasons = []
        if not has_required:
            reasons.append("missing required fields")
        if not meets_score:
            reasons.append("score below threshold")
        if not industry_match:
            reasons.append("industry mismatch")
        return ", ".join(reasons) or "unknown"

    async def _outreach_leads(
        self,
        leads: list[dict[str, Any]],
        template: str | None,
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate outreach messages for leads."""
        outreach_results = []

        default_template = """
Hi {name},

I noticed your work at {company} and wanted to reach out. 
I believe our solution could help {company} achieve {benefit}.

Would you be open to a brief call to discuss?

Best regards,
[Your Name]
"""

        template = template or default_template

        for lead_data in leads:
            lead = Lead(**lead_data) if isinstance(lead_data, dict) else lead_data

            # Personalize message
            message = template.format(
                name=lead.name or "there",
                company=lead.company or "your company",
                title=lead.title or "your role",
                benefit="your goals",
            )

            outreach_results.append({
                "lead": lead.to_dict(),
                "message": message,
                "channel": "email" if lead.email else "linkedin",
                "status": "ready",
            })

        return {
            "outreach": outreach_results,
            "total": len(outreach_results),
        }

    async def _nurture_leads(
        self,
        leads: list[dict[str, Any]],
        context: SkillContext
    ) -> dict[str, Any]:
        """Create nurture sequences for leads."""
        nurture_sequences = []

        for lead_data in leads:
            lead = Lead(**lead_data) if isinstance(lead_data, dict) else lead_data

            # Create nurture sequence based on lead score
            if lead.score >= LeadScore.HOT:
                sequence = [
                    {"day": 0, "action": "personal_email"},
                    {"day": 2, "action": "linkedin_connect"},
                    {"day": 5, "action": "follow_up_email"},
                    {"day": 10, "action": "phone_call"},
                ]
            elif lead.score >= LeadScore.WARM:
                sequence = [
                    {"day": 0, "action": "automated_email"},
                    {"day": 3, "action": "linkedin_connect"},
                    {"day": 7, "action": "follow_up_email"},
                    {"day": 14, "action": "value_add_content"},
                ]
            else:
                sequence = [
                    {"day": 0, "action": "automated_email"},
                    {"day": 7, "action": "follow_up_email"},
                    {"day": 14, "action": "newsletter_subscribe"},
                ]

            nurture_sequences.append({
                "lead": lead.to_dict(),
                "sequence": sequence,
                "status": "active",
            })

        return {
            "sequences": nurture_sequences,
            "total": len(nurture_sequences),
        }

    async def _enrich_leads(
        self,
        leads: list[dict[str, Any]],
        context: SkillContext
    ) -> dict[str, Any]:
        """Enrich leads with additional data."""
        enriched = []

        for lead_data in leads:
            lead = Lead(**lead_data) if isinstance(lead_data, dict) else lead_data

            # Mock enrichment - in production, use Clearbit, ZoomInfo, etc.
            enrichment = {
                "lead": lead.to_dict(),
                "enriched_data": {
                    "company_size": "50-100",
                    "revenue": "$1M-$10M",
                    "technologies": ["React", "Node.js", "AWS"],
                    "social_profiles": {
                        "linkedin": lead.linkedin or f"linkedin.com/company/{lead.company}",
                    },
                },
                "enriched_at": datetime.utcnow().isoformat(),
            }

            enriched.append(enrichment)

        return {
            "enriched": enriched,
            "total": len(enriched),
            "note": "Mock enrichment. Integrate Clearbit/ZoomInfo for real data.",
        }

    async def _score_leads(
        self,
        leads: list[dict[str, Any]],
        scoring_model: dict[str, int] | None,
        context: SkillContext
    ) -> dict[str, Any]:
        """Score leads based on criteria."""
        default_model = {
            "has_email": 10,
            "has_phone": 5,
            "has_linkedin": 5,
            "company_match": 20,
            "title_match": 15,
            "industry_match": 15,
            "engagement": 10,
            "source_quality": 10,
        }

        model = scoring_model or default_model
        scored = []

        for lead_data in leads:
            lead = Lead(**lead_data) if isinstance(lead_data, dict) else lead_data

            score = 0
            score_breakdown = {}

            # Calculate score
            if lead.email:
                score += model.get("has_email", 0)
                score_breakdown["has_email"] = model.get("has_email", 0)

            if lead.phone:
                score += model.get("has_phone", 0)
                score_breakdown["has_phone"] = model.get("has_phone", 0)

            if lead.linkedin:
                score += model.get("has_linkedin", 0)
                score_breakdown["has_linkedin"] = model.get("has_linkedin", 0)

            # Update lead score
            lead.score = min(100, score)

            scored.append({
                "lead": lead.to_dict(),
                "score": lead.score,
                "score_breakdown": score_breakdown,
                "tier": self._get_lead_tier(lead.score),
            })

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)

        return {
            "scored": scored,
            "total": len(scored),
            "average_score": sum(s["score"] for s in scored) / len(scored) if scored else 0,
        }

    def _get_lead_tier(self, score: int) -> str:
        """Get lead tier based on score."""
        if score >= LeadScore.HOT:
            return "hot"
        elif score >= LeadScore.WARM:
            return "warm"
        elif score >= LeadScore.COOL:
            return "cool"
        else:
            return "cold"
