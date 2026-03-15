"""
Content Writing Skill
=====================
Write blog posts, articles, copy, social posts using LLM generation.
Supports multiple content types, tones, and SEO optimization.

Podcast use case: "content creation — blogs, articles, marketing copy"
"""

from __future__ import annotations

import logging
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.content_writing")

# Content type templates
CONTENT_TEMPLATES = {
    "blog": {
        "structure": ["hook", "introduction", "body", "conclusion", "cta"],
        "default_length": 1000,
        "format": "markdown"
    },
    "article": {
        "structure": ["headline", "lead", "body", "conclusion"],
        "default_length": 1500,
        "format": "markdown"
    },
    "copy": {
        "structure": ["headline", "subheadline", "benefits", "cta"],
        "default_length": 300,
        "format": "plain"
    },
    "social": {
        "structure": ["hook", "message", "hashtags"],
        "default_length": 280,
        "format": "plain"
    },
    "email": {
        "structure": ["subject", "greeting", "body", "signature"],
        "default_length": 200,
        "format": "plain"
    },
    "landing_page": {
        "structure": ["hero", "benefits", "features", "testimonials", "cta"],
        "default_length": 500,
        "format": "html"
    },
    "press_release": {
        "structure": ["headline", "dateline", "introduction", "body", "boilerplate", "contact"],
        "default_length": 400,
        "format": "plain"
    }
}

# Tone guidelines
TONE_GUIDELINES = {
    "professional": "Use formal language, industry terminology, and a confident voice.",
    "casual": "Use conversational language, contractions, and a friendly tone.",
    "humorous": "Include wit, playful language, and light-hearted jokes where appropriate.",
    "inspirational": "Use motivational language, stories of success, and uplifting messages.",
    "educational": "Focus on teaching, use examples and clear explanations.",
    "persuasive": "Use strong calls to action, benefits-focused language, and urgency.",
    "technical": "Use precise terminology, detailed explanations, and data-driven content.",
    "storytelling": "Use narrative structure, character development, and emotional arcs."
}


class ContentWritingSkill(BaseSkill):
    """Write blog posts, articles, marketing copy, and social content."""

    name = "content_writing"
    description = "Write blog posts, articles, marketing copy, and social content"
    category = SkillCategory.CREATIVE

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Generate content based on the specified type and topic.

        Params:
            type: Content type - 'blog' | 'article' | 'copy' | 'social' | 'email' | 'landing_page' | 'press_release'
            topic: Main topic or subject of the content
            tone: Writing tone - 'professional' | 'casual' | 'humorous' | 'inspirational' | 'educational' | 'persuasive' | 'technical' | 'storytelling'
            keywords: List of SEO keywords to include
            length: Target word count (optional, uses defaults)
            audience: Target audience description
            cta: Call to action text (optional)
            outline: Custom outline/structure (optional)
            brand_voice: Brand voice guidelines (optional)
            include_meta: Whether to include SEO metadata (default: False)
        """
        content_type = context.params.get("type", "blog")
        topic = context.params.get("topic", "")
        tone = context.params.get("tone", "professional")
        keywords = context.params.get("keywords", [])
        length = context.params.get("length")
        audience = context.params.get("audience", "general readers")
        cta = context.params.get("cta")
        outline = context.params.get("outline")
        brand_voice = context.params.get("brand_voice", "")
        include_meta = context.params.get("include_meta", False)

        if not topic:
            return SkillResult(
                skill=self.name,
                status="error",
                error="Topic is required for content generation",
                data={}
            )

        # Get template for content type
        template = CONTENT_TEMPLATES.get(content_type, CONTENT_TEMPLATES["blog"])
        target_length = length or template["default_length"]

        # Get tone guidelines
        tone_guide = TONE_GUIDELINES.get(tone, TONE_GUIDELINES["professional"])

        # Build the content generation prompt
        content = await self._generate_content(
            content_type=content_type,
            topic=topic,
            tone=tone,
            tone_guide=tone_guide,
            keywords=keywords,
            target_length=target_length,
            audience=audience,
            cta=cta,
            outline=outline or template["structure"],
            brand_voice=brand_voice,
            format_type=template["format"],
            context=context
        )

        # Generate SEO metadata if requested
        metadata = {}
        if include_meta:
            metadata = self._generate_seo_metadata(topic, keywords, content)

        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "type": content_type,
                "topic": topic,
                "tone": tone,
                "content": content,
                "word_count": len(content.split()),
                "format": template["format"],
                **metadata
            },
            metadata={
                "target_length": target_length,
                "keywords_included": keywords,
                "audience": audience
            }
        )

    async def _generate_content(
        self,
        content_type: str,
        topic: str,
        tone: str,
        tone_guide: str,
        keywords: list[str],
        target_length: int,
        audience: str,
        cta: str | None,
        outline: list[str],
        brand_voice: str,
        format_type: str,
        context: SkillContext
    ) -> str:
        """Generate content using LLM or fallback to template-based generation."""
        # Check for LLM tool availability
        llm_tool = None
        if hasattr(context, "tools") and context.tools:
            llm_tool = context.tools.get("llm_generate") or context.tools.get("generate")

        # Build the prompt
        prompt = self._build_generation_prompt(
            content_type, topic, tone, tone_guide, keywords,
            target_length, audience, cta, outline, brand_voice, format_type
        )

        if llm_tool:
            try:
                # Use LLM for generation
                result = await llm_tool(prompt=prompt, max_tokens=target_length * 2)
                return result.get("text", result.get("content", ""))
            except Exception as e:
                logger.warning("LLM generation failed, using template: %s", e)

        # Template-based generation (fallback)
        return self._template_generate(
            content_type, topic, tone, keywords, outline, format_type
        )

    def _build_generation_prompt(
        self,
        content_type: str,
        topic: str,
        tone: str,
        tone_guide: str,
        keywords: list[str],
        target_length: int,
        audience: str,
        cta: str | None,
        outline: list[str],
        brand_voice: str,
        format_type: str
    ) -> str:
        """Build the content generation prompt."""
        prompt_parts = [
            f"Write a {content_type} about: {topic}",
            f"\nTarget audience: {audience}",
            f"\nTone: {tone} - {tone_guide}",
            f"\nTarget length: {target_length} words",
            f"\nFormat: {format_type}",
        ]

        if keywords:
            prompt_parts.append(f"\nInclude these keywords naturally: {', '.join(keywords)}")

        if outline:
            prompt_parts.append(f"\nStructure: {' → '.join(outline)}")

        if cta:
            prompt_parts.append(f"\nCall to action: {cta}")

        if brand_voice:
            prompt_parts.append(f"\nBrand voice: {brand_voice}")

        prompt_parts.append("\n\nGenerate the content now:")

        return "\n".join(prompt_parts)

    def _template_generate(
        self,
        content_type: str,
        topic: str,
        tone: str,
        keywords: list[str],
        outline: list[str],
        format_type: str
    ) -> str:
        """Generate content using templates when LLM is not available."""
        # Build a structured template-based content
        sections = []

        for section in outline:
            if section == "hook":
                sections.append(f"# {topic}\n\nDiscover the essential insights about {topic}.")
            elif section == "introduction" or section == "lead":
                sections.append(f"\n\n## Introduction\n\nIn this {content_type}, we explore {topic} and its significance for modern readers.")
            elif section == "body":
                body_text = f"\n\n## Key Points\n\n"
                for i, keyword in enumerate(keywords[:3], 1):
                    body_text += f"\n{i}. **{keyword.title()}**: Understanding {keyword} is crucial for {topic.lower()}.\n"
                sections.append(body_text)
            elif section == "conclusion":
                sections.append(f"\n\n## Conclusion\n\n{topic} represents an important area of focus. By understanding its key aspects, you can make informed decisions.")
            elif section == "cta":
                sections.append(f"\n\n**Ready to learn more?** Take the next step today.")
            elif section == "headline":
                sections.append(f"# {topic}: A Comprehensive Guide")
            elif section == "subheadline":
                sections.append(f"\n\n*Everything you need to know about {topic}*\n")
            elif section == "benefits":
                sections.append(f"\n\n## Benefits\n\n- Understand {topic} deeply\n- Apply insights immediately\n- Stay ahead of the curve")
            elif section == "hashtags":
                hashtags = " ".join(f"#{kw.replace(' ', '')}" for kw in keywords[:5])
                sections.append(f"\n\n{hashtags}")
            elif section == "subject":
                sections.append(f"Subject: {topic} - Important Update")
            elif section == "greeting":
                sections.append("\n\nDear Reader,")
            elif section == "signature":
                sections.append("\n\nBest regards,\nThe Team")
            else:
                sections.append(f"\n\n## {section.title()}\n\n[Content for {section}]")

        return "".join(sections)

    def _generate_seo_metadata(
        self,
        topic: str,
        keywords: list[str],
        content: str
    ) -> dict[str, str]:
        """Generate SEO metadata for the content."""
        # Generate title tag (50-60 characters)
        title = f"{topic} | Complete Guide"
        if len(title) > 60:
            title = title[:57] + "..."

        # Generate meta description (150-160 characters)
        meta_desc = f"Discover everything about {topic}. "
        if keywords:
            meta_desc += f"Learn about {', '.join(keywords[:3])} and more. "
        meta_desc += "Expert insights and practical tips."
        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."

        # Generate slug
        slug = topic.lower().replace(" ", "-").replace("'", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        return {
            "seo_title": title,
            "meta_description": meta_desc,
            "slug": slug,
            "focus_keyword": keywords[0] if keywords else topic
        }

    def _calculate_readability(self, content: str) -> dict[str, Any]:
        """Calculate readability metrics for the content."""
        words = content.split()
        sentences = content.count(".") + content.count("!") + content.count("?")
        syllables = sum(self._count_syllables(word) for word in words)

        if sentences == 0:
            sentences = 1

        # Flesch Reading Ease
        if len(words) == 0:
            flesch = 0
        else:
            flesch = 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))

        # Grade level
        if len(words) == 0:
            grade = 0
        else:
            grade = 0.39 * (len(words) / sentences) + 11.8 * (syllables / len(words)) - 15.59

        return {
            "word_count": len(words),
            "sentence_count": sentences,
            "flesch_reading_ease": round(flesch, 1),
            "grade_level": round(grade, 1),
            "readability": "Easy" if flesch > 70 else "Medium" if flesch > 50 else "Difficult"
        }

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1

        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        # Adjust for silent e
        if word.endswith("e"):
            count -= 1

        return max(1, count)
