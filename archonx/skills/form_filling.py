"""
Form Filling Skill
==================
Auto-fill forms, applications, and registrations using browser automation.
Integrates with Chrome DevTools MCP for web-based forms.

Podcast use case: "fill out forms — job applications, government forms, registrations"
"""

from __future__ import annotations

import logging
import re
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.form_filling")

# Common form field mappings
FIELD_MAPPINGS = {
    "name": ["name", "full_name", "fullname", "full name"],
    "first_name": ["first_name", "firstname", "first name", "fname"],
    "last_name": ["last_name", "lastname", "last name", "lname"],
    "email": ["email", "email_address", "email address", "e-mail"],
    "phone": ["phone", "phone_number", "phone number", "tel", "mobile"],
    "address": ["address", "street", "street_address", "street address"],
    "city": ["city", "town"],
    "state": ["state", "province", "region"],
    "zip": ["zip", "zip_code", "zipcode", "postal", "postal_code"],
    "country": ["country", "nation"],
    "company": ["company", "organization", "organisation", "employer"],
    "job_title": ["job_title", "jobtitle", "title", "position"],
    "website": ["website", "url", "site", "web"],
    "linkedin": ["linkedin", "linkedin_url", "linkedin profile"],
    "github": ["github", "github_url", "github profile"],
    "message": ["message", "comments", "notes", "description", "bio"],
    "resume": ["resume", "cv", "portfolio"],
    "cover_letter": ["cover_letter", "coverletter", "cover letter"],
}


class FormFillingSkill(BaseSkill):
    """Auto-fill forms, applications, and online registrations."""

    name = "form_filling"
    description = "Auto-fill forms, applications, and online registrations"
    category = SkillCategory.AUTOMATION

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Fill out a form with the provided data.

        Params:
            url: URL of the form page (optional for web forms)
            form_data: Dict of field_name: value pairs
            field_mappings: Custom field name mappings (optional)
            submit: Whether to submit the form after filling (default: False)
            screenshot: Whether to take a screenshot after filling (default: True)
            use_browser: Whether to use browser automation (default: True)
            profile: User profile data to use for filling (optional)
        """
        url = context.params.get("url", "")
        form_data = context.params.get("form_data", {})
        custom_mappings = context.params.get("field_mappings", {})
        submit = context.params.get("submit", False)
        screenshot = context.params.get("screenshot", True)
        use_browser = context.params.get("use_browser", True)
        profile = context.params.get("profile", {})

        # Merge profile data with form_data
        if profile:
            form_data = {**profile, **form_data}

        if not form_data:
            return SkillResult(
                skill=self.name,
                status="error",
                error="No form data provided",
                data={}
            )

        # Merge custom field mappings
        all_mappings = {**FIELD_MAPPINGS, **custom_mappings}

        # If browser automation is requested and we have a URL
        if use_browser and url:
            return await self._fill_web_form(
                url, form_data, all_mappings, submit, screenshot, context
            )

        # Otherwise, return the mapped data for manual use
        return await self._prepare_form_data(form_data, all_mappings)

    async def _fill_web_form(
        self,
        url: str,
        form_data: dict[str, Any],
        mappings: dict[str, list[str]],
        submit: bool,
        screenshot: bool,
        context: SkillContext
    ) -> SkillResult:
        """Fill a web form using browser automation."""
        fields_filled = 0
        fields_failed = []
        filled_fields = []

        # Check for Chrome DevTools MCP availability
        chrome_tools = context.tools if hasattr(context, "tools") else None

        if chrome_tools and "chrome_navigate" in chrome_tools:
            # Use Chrome DevTools MCP
            try:
                # Navigate to the form
                await chrome_tools["chrome_navigate"](url=url)

                # Fill each field
                for field_name, value in form_data.items():
                    selectors = self._get_selectors_for_field(field_name, mappings)

                    for selector in selectors:
                        try:
                            # Try to type into the field
                            await chrome_tools["chrome_type"](
                                selector=selector,
                                text=str(value)
                            )
                            fields_filled += 1
                            filled_fields.append({
                                "field": field_name,
                                "selector": selector,
                                "value": "***" if "password" in field_name.lower() else str(value)[:50]
                            })
                            break
                        except Exception as e:
                            logger.debug("Selector %s failed: %s", selector, e)
                            continue
                    else:
                        fields_failed.append(field_name)

                # Take screenshot if requested
                screenshot_path = None
                if screenshot:
                    screenshot_path = await chrome_tools["chrome_screenshot"](
                        path=f"/tmp/form_screenshot_{context.agent_id}.png"
                    )

                # Submit if requested
                submitted = False
                if submit:
                    try:
                        # Look for submit button
                        submit_selectors = [
                            "button[type='submit']",
                            "input[type='submit']",
                            "button:contains('Submit')",
                            "button:contains('Apply')",
                            "button:contains('Send')",
                            ".submit-button",
                            "#submit-button"
                        ]
                        for selector in submit_selectors:
                            try:
                                await chrome_tools["chrome_click"](selector=selector)
                                submitted = True
                                break
                            except Exception:
                                continue
                    except Exception as e:
                        logger.warning("Could not submit form: %s", e)

                return SkillResult(
                    skill=self.name,
                    status="success" if fields_filled > 0 else "partial",
                    data={
                        "url": url,
                        "fields_filled": fields_filled,
                        "fields_failed": fields_failed,
                        "filled_fields": filled_fields,
                        "submitted": submitted,
                        "screenshot": screenshot_path
                    },
                    metadata={
                        "total_fields": len(form_data),
                        "success_rate": fields_filled / len(form_data) if form_data else 0
                    }
                )

            except Exception as e:
                logger.error("Browser automation failed: %s", e)
                return SkillResult(
                    skill=self.name,
                    status="error",
                    error=str(e),
                    data={"url": url}
                )

        # Mock mode - no browser tools available
        logger.info("Mock form filling mode - no browser tools available")
        return SkillResult(
            skill=self.name,
            status="partial",
            data={
                "url": url,
                "fields_filled": len(form_data),
                "submitted": False,
                "mock_mode": True,
                "message": "Browser automation not available. Install Chrome DevTools MCP."
            },
            metadata={
                "form_data_prepared": form_data
            }
        )

    async def _prepare_form_data(
        self,
        form_data: dict[str, Any],
        mappings: dict[str, list[str]]
    ) -> SkillResult:
        """Prepare form data with field mappings for manual use."""
        prepared_data = {}

        for field_name, value in form_data.items():
            # Get possible field names
            possible_names = mappings.get(field_name, [field_name])
            prepared_data[field_name] = {
                "value": value,
                "possible_field_names": possible_names,
                "selectors": self._get_selectors_for_field(field_name, mappings)
            }

        return SkillResult(
            skill=self.name,
            status="success",
            data={
                "prepared": True,
                "fields": len(form_data),
                "form_data": prepared_data
            },
            metadata={
                "message": "Form data prepared. Use browser automation to fill web forms."
            }
        )

    def _get_selectors_for_field(
        self,
        field_name: str,
        mappings: dict[str, list[str]]
    ) -> list[str]:
        """Generate CSS selectors for a form field."""
        selectors = []
        possible_names = mappings.get(field_name, [field_name])

        for name in possible_names:
            # Common selector patterns
            selectors.extend([
                f"input[name='{name}']",
                f"input[id='{name}']",
                f"input[placeholder*='{name}']",
                f"textarea[name='{name}']",
                f"textarea[id='{name}']",
                f"select[name='{name}']",
                f"select[id='{name}']",
                f"#{name}",
                f".{name}",
                f"[data-field='{name}']",
                f"[data-name='{name}']",
            ])

        # Add type-specific selectors
        if "email" in field_name.lower():
            selectors.append("input[type='email']")
        elif "phone" in field_name.lower():
            selectors.append("input[type='tel']")
        elif "password" in field_name.lower():
            selectors.append("input[type='password']")
        elif "date" in field_name.lower():
            selectors.append("input[type='date']")
        elif "url" in field_name.lower() or "website" in field_name.lower():
            selectors.append("input[type='url']")
        elif "resume" in field_name.lower() or "cv" in field_name.lower():
            selectors.append("input[type='file']")
        elif "message" in field_name.lower() or "comments" in field_name.lower():
            selectors.append("textarea")

        return selectors

    def _detect_form_type(self, html: str) -> str:
        """Detect the type of form from HTML content."""
        html_lower = html.lower()

        if "job" in html_lower or "career" in html_lower or "employment" in html_lower:
            return "job_application"
        elif "register" in html_lower or "sign up" in html_lower:
            return "registration"
        elif "contact" in html_lower:
            return "contact_form"
        elif "login" in html_lower or "sign in" in html_lower:
            return "login_form"
        elif "checkout" in html_lower or "payment" in html_lower:
            return "checkout"
        elif "survey" in html_lower or "questionnaire" in html_lower:
            return "survey"
        else:
            return "generic"
