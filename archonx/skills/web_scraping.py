"""
Web Scraping Skill
==================
Extract structured data from websites using httpx + BeautifulSoup.
Supports CSS selectors, XPath-like patterns, and pagination.

Podcast use case: "scrape any website and pull structured data"
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urljoin, urlparse

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.web_scraping")

# Optional imports with fallback
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    logger.warning("httpx not installed, web scraping will use mock mode")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.warning("BeautifulSoup not installed, web scraping will use mock mode")


class WebScrapingSkill(BaseSkill):
    """Extract structured data from websites with rate limiting and error handling."""

    name = "web_scraping"
    description = "Extract structured data from websites using CSS selectors"
    category = SkillCategory.AUTOMATION

    # Rate limiting defaults
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Extract data from a website.

        Params:
            url: Target URL to scrape
            selectors: Dict of {name: css_selector} pairs
            extract_links: Whether to extract all links (default: False)
            extract_images: Whether to extract all images (default: False)
            extract_text: Whether to extract page text (default: False)
            follow_pagination: Follow next page links (default: False)
            max_pages: Maximum pages to scrape (default: 5)
            timeout: Request timeout in seconds (default: 30)
            headers: Custom headers dict
        """
        url = context.params.get("url", "")
        selectors = context.params.get("selectors", {})
        extract_links = context.params.get("extract_links", False)
        extract_images = context.params.get("extract_images", False)
        extract_text = context.params.get("extract_text", False)
        follow_pagination = context.params.get("follow_pagination", False)
        max_pages = context.params.get("max_pages", 5)
        timeout = context.params.get("timeout", self.DEFAULT_TIMEOUT)
        custom_headers = context.params.get("headers", {})

        if not url:
            return SkillResult(
                skill=self.name,
                status="error",
                error="URL is required for web scraping",
                data={}
            )

        # Check if we have the required libraries
        if not HAS_HTTPX or not HAS_BS4:
            return self._mock_scrape(url, selectors, context)

        # Perform actual scraping
        try:
            result = await self._scrape_website(
                url=url,
                selectors=selectors,
                extract_links=extract_links,
                extract_images=extract_images,
                extract_text=extract_text,
                follow_pagination=follow_pagination,
                max_pages=max_pages,
                timeout=timeout,
                custom_headers=custom_headers,
                context=context
            )
            return result
        except Exception as e:
            logger.error("Web scraping failed for %s: %s", url, str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"url": url}
            )

    async def _scrape_website(
        self,
        url: str,
        selectors: dict[str, str],
        extract_links: bool,
        extract_images: bool,
        extract_text: bool,
        follow_pagination: bool,
        max_pages: int,
        timeout: float,
        custom_headers: dict,
        context: SkillContext
    ) -> SkillResult:
        """Perform the actual web scraping."""
        headers = {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            **custom_headers
        }

        all_results = []
        pages_scraped = []
        current_url = url
        pages_count = 0

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            while current_url and pages_count < max_pages:
                pages_count += 1
                logger.info("Scraping page %d: %s", pages_count, current_url)

                try:
                    response = await client.get(current_url, headers=headers)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    logger.warning("HTTP error on page %d: %s", pages_count, str(e))
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                page_result = {
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "extracted": {}
                }

                # Extract data using selectors
                for name, selector in selectors.items():
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            page_result["extracted"][name] = self._clean_text(elements[0].get_text())
                        else:
                            page_result["extracted"][name] = [
                                self._clean_text(el.get_text()) for el in elements
                            ]
                    else:
                        page_result["extracted"][name] = None

                # Extract links if requested
                if extract_links:
                    links = []
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        full_url = urljoin(str(response.url), href)
                        links.append({
                            "url": full_url,
                            "text": self._clean_text(a.get_text()),
                            "is_external": urlparse(full_url).netloc != urlparse(str(response.url)).netloc
                        })
                    page_result["links"] = links

                # Extract images if requested
                if extract_images:
                    images = []
                    for img in soup.find_all("img", src=True):
                        src = img["src"]
                        full_url = urljoin(str(response.url), src)
                        images.append({
                            "url": full_url,
                            "alt": img.get("alt", ""),
                            "title": img.get("title", "")
                        })
                    page_result["images"] = images

                # Extract text if requested
                if extract_text:
                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer"]):
                        script.decompose()
                    page_result["text"] = self._clean_text(soup.get_text())

                all_results.append(page_result)
                pages_scraped.append(str(response.url))

                # Find next page if pagination is enabled
                if follow_pagination:
                    next_link = soup.find("a", string=re.compile(r"(?i)(next|›|>>|more)"))
                    if next_link and next_link.get("href"):
                        current_url = urljoin(str(response.url), next_link["href"])
                    else:
                        # Try rel="next"
                        next_link = soup.find("a", rel="next")
                        if next_link and next_link.get("href"):
                            current_url = urljoin(str(response.url), next_link["href"])
                        else:
                            break
                else:
                    break

        # Compile final result
        if len(all_results) == 1:
            final_data = all_results[0]
        else:
            final_data = {
                "pages": all_results,
                "total_pages": len(all_results)
            }

        # Log tool usage
        if context.config.get("enable_logging", True):
            from archonx.logs.canonical_log import get_logger
            get_logger().log_tool_use(
                agent_id=context.agent_id,
                tool="web_scraping",
                purpose=f"Scrape {url}",
                success=True,
                duration_ms=0
            )

        return SkillResult(
            skill=self.name,
            status="success",
            data=final_data,
            metadata={
                "url": url,
                "pages_scraped": pages_scraped,
                "selectors_used": list(selectors.keys()),
                "total_pages": len(all_results)
            }
        )

    def _mock_scrape(
        self,
        url: str,
        selectors: dict[str, str],
        context: SkillContext
    ) -> SkillResult:
        """Return mock data when libraries are not available."""
        logger.info("Mock scraping mode for %s", url)
        
        mock_data = {
            "url": url,
            "extracted": {name: f"[Mock data for selector: {selector}]" 
                          for name, selector in selectors.items()},
            "mock_mode": True,
            "message": "Install httpx and beautifulsoup4 for real scraping"
        }

        return SkillResult(
            skill=self.name,
            status="partial",
            data=mock_data,
            metadata={
                "mock_mode": True,
                "missing_dependencies": []
            }
        )

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace."""
        if not text:
            return ""
        # Remove extra whitespace and newlines
        text = re.sub(r"\s+", " ", text)
        return text.strip()
