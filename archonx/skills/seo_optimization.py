"""
SEO Optimization Skill
======================
Audit sites, optimize content, track rankings using web scraping and analysis.
Provides comprehensive SEO recommendations and scoring.

Podcast use case: "SEO — audit pages, suggest improvements, track rankings"
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urlparse

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.seo_optimization")

# SEO scoring weights
SEO_WEIGHTS = {
    "title_tag": 15,
    "meta_description": 10,
    "h1_tag": 10,
    "h2_tags": 5,
    "image_alt": 10,
    "internal_links": 10,
    "external_links": 5,
    "page_speed": 15,
    "mobile_friendly": 10,
    "schema_markup": 5,
    "canonical_url": 5,
}

# Title tag best practices
TITLE_BEST_PRACTICES = {
    "min_length": 30,
    "max_length": 60,
    "ideal_length": 50,
}

# Meta description best practices
META_DESC_BEST_PRACTICES = {
    "min_length": 120,
    "max_length": 160,
    "ideal_length": 150,
}


class SEOOptimizationSkill(BaseSkill):
    """Audit sites, optimize content for SEO, and track rankings."""

    name = "seo_optimization"
    description = "Audit sites, optimize content for SEO, and track rankings"
    category = SkillCategory.RESEARCH

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Perform SEO analysis and optimization.

        Params:
            action: 'audit' | 'optimize' | 'analyze_keywords' | 'check_backlinks' | 'report'
            url: Target URL to analyze (required for audit/optimize)
            content: HTML content to analyze (optional, fetched if not provided)
            keywords: Target keywords to check (optional)
            competitor_urls: Competitor URLs for comparison (optional)
            include_suggestions: Whether to include improvement suggestions (default: True)
        """
        action = context.params.get("action", "audit")
        url = context.params.get("url", "")
        content = context.params.get("content", "")
        keywords = context.params.get("keywords", [])
        competitor_urls = context.params.get("competitor_urls", [])
        include_suggestions = context.params.get("include_suggestions", True)

        if not url and action in ["audit", "optimize"]:
            return SkillResult(
                skill=self.name,
                status="error",
                error="URL is required for SEO audit/optimization",
                data={}
            )

        # Execute the appropriate action
        try:
            if action == "audit":
                result = await self._audit_page(url, content, keywords, context)
            elif action == "optimize":
                result = await self._optimize_content(url, content, keywords, context)
            elif action == "analyze_keywords":
                result = await self._analyze_keywords(url, keywords, context)
            elif action == "check_backlinks":
                result = await self._check_backlinks(url, context)
            elif action == "report":
                result = await self._generate_report(url, context)
            else:
                return SkillResult(
                    skill=self.name,
                    status="error",
                    error=f"Unknown action: {action}",
                    data={"action": action}
                )

            # Add suggestions if requested
            if include_suggestions and "score" in result:
                result["suggestions"] = self._generate_suggestions(result)

            return SkillResult(
                skill=self.name,
                status="success",
                data=result,
                metadata={
                    "action": action,
                    "url": url,
                    "keywords_analyzed": keywords
                }
            )

        except Exception as e:
            logger.error("SEO optimization failed: %s", str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"url": url}
            )

    async def _audit_page(
        self,
        url: str,
        content: str | None,
        keywords: list[str],
        context: SkillContext
    ) -> dict[str, Any]:
        """Perform comprehensive SEO audit of a page."""
        # Fetch content if not provided
        if not content:
            content = await self._fetch_page_content(url, context)

        if not content:
            return {"error": "Could not fetch page content", "url": url}

        # Parse HTML elements
        audit_results = {
            "url": url,
            "score": 0,
            "elements": {},
            "issues": [],
            "warnings": [],
        }

        # Check title tag
        title_result = self._check_title_tag(content)
        audit_results["elements"]["title"] = title_result
        if title_result["issues"]:
            audit_results["issues"].extend(title_result["issues"])

        # Check meta description
        meta_result = self._check_meta_description(content)
        audit_results["elements"]["meta_description"] = meta_result
        if meta_result["issues"]:
            audit_results["issues"].extend(meta_result["issues"])

        # Check headings structure
        headings_result = self._check_headings(content)
        audit_results["elements"]["headings"] = headings_result
        if headings_result["issues"]:
            audit_results["issues"].extend(headings_result["issues"])

        # Check images
        images_result = self._check_images(content)
        audit_results["elements"]["images"] = images_result
        if images_result["issues"]:
            audit_results["issues"].extend(images_result["issues"])

        # Check links
        links_result = self._check_links(content, url)
        audit_results["elements"]["links"] = links_result
        if links_result["issues"]:
            audit_results["issues"].extend(links_result["issues"])

        # Check canonical URL
        canonical_result = self._check_canonical(content)
        audit_results["elements"]["canonical"] = canonical_result

        # Check schema markup
        schema_result = self._check_schema(content)
        audit_results["elements"]["schema"] = schema_result

        # Check keyword usage if keywords provided
        if keywords:
            keyword_result = self._check_keyword_usage(content, keywords)
            audit_results["elements"]["keywords"] = keyword_result

        # Calculate overall score
        audit_results["score"] = self._calculate_seo_score(audit_results["elements"])

        return audit_results

    async def _optimize_content(
        self,
        url: str,
        content: str | None,
        keywords: list[str],
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate optimized content suggestions."""
        # First run audit
        audit = await self._audit_page(url, content, keywords, context)

        optimizations = {
            "url": url,
            "current_score": audit.get("score", 0),
            "recommendations": [],
            "optimized_elements": {},
        }

        # Generate title optimization
        if "title" in audit.get("elements", {}):
            title_data = audit["elements"]["title"]
            if title_data.get("issues"):
                optimizations["recommendations"].append({
                    "element": "title",
                    "current": title_data.get("content", ""),
                    "suggestion": self._suggest_title_optimization(title_data, keywords),
                    "priority": "high"
                })

        # Generate meta description optimization
        if "meta_description" in audit.get("elements", {}):
            meta_data = audit["elements"]["meta_description"]
            if meta_data.get("issues"):
                optimizations["recommendations"].append({
                    "element": "meta_description",
                    "current": meta_data.get("content", ""),
                    "suggestion": self._suggest_meta_optimization(meta_data, keywords),
                    "priority": "high"
                })

        # Generate heading optimizations
        if "headings" in audit.get("elements", {}):
            headings_data = audit["elements"]["headings"]
            if headings_data.get("issues"):
                optimizations["recommendations"].append({
                    "element": "headings",
                    "current_structure": headings_data.get("structure", {}),
                    "suggestion": "Ensure proper H1 → H2 → H3 hierarchy with keywords",
                    "priority": "medium"
                })

        # Generate image optimizations
        if "images" in audit.get("elements", {}):
            images_data = audit["elements"]["images"]
            if images_data.get("missing_alt", 0) > 0:
                optimizations["recommendations"].append({
                    "element": "images",
                    "issue": f"{images_data['missing_alt']} images missing alt text",
                    "suggestion": "Add descriptive alt text to all images",
                    "priority": "medium"
                })

        return optimizations

    async def _analyze_keywords(
        self,
        url: str,
        keywords: list[str],
        context: SkillContext
    ) -> dict[str, Any]:
        """Analyze keyword usage and density."""
        content = await self._fetch_page_content(url, context)

        if not content:
            return {"error": "Could not fetch page content", "url": url}

        # Extract text content
        text_content = re.sub(r"<[^>]+>", "", content)
        words = text_content.lower().split()
        total_words = len(words)

        keyword_analysis = {
            "url": url,
            "total_words": total_words,
            "keywords": {},
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_content.lower().count(keyword_lower)
            density = (count / total_words * 100) if total_words > 0 else 0

            keyword_analysis["keywords"][keyword] = {
                "count": count,
                "density": round(density, 2),
                "status": "good" if 1 <= density <= 3 else "low" if density < 1 else "high"
            }

        return keyword_analysis

    async def _check_backlinks(
        self,
        url: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Check backlink profile (mock implementation)."""
        # In production, this would use an API like Ahrefs, Moz, or SEMrush
        return {
            "url": url,
            "backlinks": {
                "total": 0,
                "referring_domains": 0,
                "dofollow": 0,
                "nofollow": 0,
            },
            "top_backlinks": [],
            "note": "Backlink analysis requires API integration (Ahrefs, Moz, or SEMrush)"
        }

    async def _generate_report(
        self,
        url: str,
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate comprehensive SEO report."""
        audit = await self._audit_page(url, None, [], context)

        report = {
            "url": url,
            "overall_score": audit.get("score", 0),
            "grade": self._get_seo_grade(audit.get("score", 0)),
            "summary": {
                "critical_issues": len([i for i in audit.get("issues", []) if i.get("severity") == "critical"]),
                "warnings": len(audit.get("warnings", [])),
                "passed_checks": self._count_passed_checks(audit.get("elements", {})),
            },
            "details": audit,
            "recommendations": self._generate_suggestions(audit),
        }

        return report

    async def _fetch_page_content(self, url: str, context: SkillContext) -> str | None:
        """Fetch page content using available tools."""
        # Check for web scraping skill or httpx
        if hasattr(context, "tools") and context.tools:
            if "web_scraping" in context.tools:
                try:
                    result = await context.tools["web_scraping"](url=url, extract_text=True)
                    return result.get("text", "")
                except Exception as e:
                    logger.warning("Web scraping failed: %s", e)

        # Try httpx directly
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; ArchonX-SEO-Bot/1.0)"
                })
                return response.text
        except Exception as e:
            logger.warning("Failed to fetch page: %s", e)
            return None

    def _check_title_tag(self, content: str) -> dict[str, Any]:
        """Check title tag presence and quality."""
        title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        result = {"present": False, "content": "", "length": 0, "issues": []}

        if title_match:
            title = title_match.group(1).strip()
            result["present"] = True
            result["content"] = title
            result["length"] = len(title)

            if len(title) < TITLE_BEST_PRACTICES["min_length"]:
                result["issues"].append({
                    "type": "title_too_short",
                    "message": f"Title is too short ({len(title)} chars). Minimum: {TITLE_BEST_PRACTICES['min_length']}",
                    "severity": "warning"
                })
            elif len(title) > TITLE_BEST_PRACTICES["max_length"]:
                result["issues"].append({
                    "type": "title_too_long",
                    "message": f"Title is too long ({len(title)} chars). Maximum: {TITLE_BEST_PRACTICES['max_length']}",
                    "severity": "warning"
                })
        else:
            result["issues"].append({
                "type": "missing_title",
                "message": "No title tag found",
                "severity": "critical"
            })

        return result

    def _check_meta_description(self, content: str) -> dict[str, Any]:
        """Check meta description presence and quality."""
        meta_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
            content, re.IGNORECASE
        )
        if not meta_match:
            meta_match = re.search(
                r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
                content, re.IGNORECASE
            )

        result = {"present": False, "content": "", "length": 0, "issues": []}

        if meta_match:
            description = meta_match.group(1).strip()
            result["present"] = True
            result["content"] = description
            result["length"] = len(description)

            if len(description) < META_DESC_BEST_PRACTICES["min_length"]:
                result["issues"].append({
                    "type": "meta_too_short",
                    "message": f"Meta description is too short ({len(description)} chars)",
                    "severity": "warning"
                })
            elif len(description) > META_DESC_BEST_PRACTICES["max_length"]:
                result["issues"].append({
                    "type": "meta_too_long",
                    "message": f"Meta description is too long ({len(description)} chars)",
                    "severity": "warning"
                })
        else:
            result["issues"].append({
                "type": "missing_meta_description",
                "message": "No meta description found",
                "severity": "critical"
            })

        return result

    def _check_headings(self, content: str) -> dict[str, Any]:
        """Check heading structure."""
        result = {"structure": {}, "issues": []}

        for i in range(1, 7):
            pattern = rf"<h{i}[^>]*>(.*?)</h{i}>"
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            result["structure"][f"h{i}"] = {
                "count": len(matches),
                "texts": [m.strip()[:100] for m in matches[:5]]  # First 5, truncated
            }

        # Check for H1
        if result["structure"]["h1"]["count"] == 0:
            result["issues"].append({
                "type": "missing_h1",
                "message": "No H1 tag found",
                "severity": "critical"
            })
        elif result["structure"]["h1"]["count"] > 1:
            result["issues"].append({
                "type": "multiple_h1",
                "message": f"Multiple H1 tags found ({result['structure']['h1']['count']})",
                "severity": "warning"
            })

        return result

    def _check_images(self, content: str) -> dict[str, Any]:
        """Check image optimization."""
        img_matches = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
        result = {
            "total": len(img_matches),
            "with_alt": 0,
            "missing_alt": 0,
            "issues": []
        }

        for img in img_matches:
            if re.search(r'alt=["\'][^"\']+["\']', img, re.IGNORECASE):
                result["with_alt"] += 1
            else:
                result["missing_alt"] += 1

        if result["missing_alt"] > 0:
            result["issues"].append({
                "type": "missing_alt_text",
                "message": f"{result['missing_alt']} images missing alt text",
                "severity": "warning"
            })

        return result

    def _check_links(self, content: str, base_url: str) -> dict[str, Any]:
        """Check link structure."""
        link_matches = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        parsed_base = urlparse(base_url)

        result = {
            "total": len(link_matches),
            "internal": 0,
            "external": 0,
            "broken_potential": 0,
            "issues": []
        }

        for href in link_matches:
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            elif href.startswith("/") or parsed_base.netloc in href:
                result["internal"] += 1
            else:
                result["external"] += 1

        return result

    def _check_canonical(self, content: str) -> dict[str, Any]:
        """Check canonical URL."""
        canonical_match = re.search(
            r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
            content, re.IGNORECASE
        )

        return {
            "present": bool(canonical_match),
            "url": canonical_match.group(1) if canonical_match else None
        }

    def _check_schema(self, content: str) -> dict[str, Any]:
        """Check for schema.org markup."""
        schema_match = re.search(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            content, re.IGNORECASE | re.DOTALL
        )

        return {
            "present": bool(schema_match),
            "type": "JSON-LD" if schema_match else None
        }

    def _check_keyword_usage(self, content: str, keywords: list[str]) -> dict[str, Any]:
        """Check keyword usage in content."""
        text_content = re.sub(r"<[^>]+>", "", content).lower()
        words = text_content.split()
        total_words = len(words)

        result = {"keywords": {}}

        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_content.count(keyword_lower)
            density = (count / total_words * 100) if total_words > 0 else 0

            result["keywords"][keyword] = {
                "count": count,
                "density": round(density, 2),
                "in_title": keyword_lower in content.lower()[:500],  # Rough title check
            }

        return result

    def _calculate_seo_score(self, elements: dict[str, Any]) -> int:
        """Calculate overall SEO score."""
        score = 0

        # Title tag
        if elements.get("title", {}).get("present"):
            title_len = elements["title"].get("length", 0)
            if TITLE_BEST_PRACTICES["min_length"] <= title_len <= TITLE_BEST_PRACTICES["max_length"]:
                score += SEO_WEIGHTS["title_tag"]
            else:
                score += SEO_WEIGHTS["title_tag"] // 2

        # Meta description
        if elements.get("meta_description", {}).get("present"):
            score += SEO_WEIGHTS["meta_description"]

        # H1 tag
        if elements.get("headings", {}).get("structure", {}).get("h1", {}).get("count", 0) == 1:
            score += SEO_WEIGHTS["h1_tag"]

        # Images
        images = elements.get("images", {})
        if images.get("total", 0) > 0:
            alt_ratio = images.get("with_alt", 0) / images.get("total", 1)
            score += int(SEO_WEIGHTS["image_alt"] * alt_ratio)

        # Links
        links = elements.get("links", {})
        if links.get("total", 0) > 0:
            score += min(SEO_WEIGHTS["internal_links"], links.get("internal", 0) * 2)

        # Canonical
        if elements.get("canonical", {}).get("present"):
            score += SEO_WEIGHTS["canonical_url"]

        # Schema
        if elements.get("schema", {}).get("present"):
            score += SEO_WEIGHTS["schema_markup"]

        return min(100, score)

    def _get_seo_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _count_passed_checks(self, elements: dict[str, Any]) -> int:
        """Count number of passed SEO checks."""
        passed = 0

        if elements.get("title", {}).get("present"):
            passed += 1
        if elements.get("meta_description", {}).get("present"):
            passed += 1
        if elements.get("headings", {}).get("structure", {}).get("h1", {}).get("count", 0) == 1:
            passed += 1
        if elements.get("canonical", {}).get("present"):
            passed += 1
        if elements.get("schema", {}).get("present"):
            passed += 1
        if elements.get("images", {}).get("missing_alt", 1) == 0:
            passed += 1

        return passed

    def _generate_suggestions(self, audit: dict[str, Any]) -> list[dict[str, str]]:
        """Generate improvement suggestions based on audit."""
        suggestions = []

        for issue in audit.get("issues", []):
            suggestion = {
                "issue": issue.get("type", ""),
                "message": issue.get("message", ""),
                "severity": issue.get("severity", "warning"),
            }

            # Add specific recommendations
            if issue.get("type") == "missing_title":
                suggestion["recommendation"] = "Add a descriptive title tag with your target keyword near the beginning."
            elif issue.get("type") == "title_too_short":
                suggestion["recommendation"] = "Expand your title to be more descriptive and include keywords."
            elif issue.get("type") == "title_too_long":
                suggestion["recommendation"] = "Shorten your title to under 60 characters for better display in search results."
            elif issue.get("type") == "missing_meta_description":
                suggestion["recommendation"] = "Add a compelling meta description that includes your target keyword."
            elif issue.get("type") == "missing_h1":
                suggestion["recommendation"] = "Add an H1 tag that clearly describes the page content."
            elif issue.get("type") == "multiple_h1":
                suggestion["recommendation"] = "Use only one H1 tag per page. Use H2-H6 for subheadings."
            elif issue.get("type") == "missing_alt_text":
                suggestion["recommendation"] = "Add descriptive alt text to all images for accessibility and SEO."

            suggestions.append(suggestion)

        return suggestions

    def _suggest_title_optimization(self, title_data: dict, keywords: list[str]) -> str:
        """Generate optimized title suggestion."""
        current = title_data.get("content", "")
        if keywords:
            primary_keyword = keywords[0]
            if primary_keyword.lower() not in current.lower():
                return f"{primary_keyword.title()} | {current}"
        return current

    def _suggest_meta_optimization(self, meta_data: dict, keywords: list[str]) -> str:
        """Generate optimized meta description suggestion."""
        current = meta_data.get("content", "")
        if keywords and len(current) < META_DESC_BEST_PRACTICES["min_length"]:
            keyword_text = ", ".join(keywords[:3])
            return f"{current} Learn about {keyword_text} and more. Expert insights and practical tips."
        return current
