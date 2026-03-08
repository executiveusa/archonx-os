"""
Browser Automation Agent - Playwright integration

First-class browser control for web-based automation tasks:
- Launch/reuse browser sessions
- Navigate and interact with web pages
- Form filling and submission
- Screenshot capture
- JavaScript evaluation
- Download handling

ZTE-20260308-0003: Browser agent with Playwright
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """Browser automation session"""
    session_id: str
    headless: bool
    browser_type: str  # "chromium", "firefox", "webkit"
    current_url: Optional[str] = None
    is_open: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    screenshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrowserAgent:
    """Playwright-based browser automation"""

    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        """Initialize browser agent"""
        self.headless = headless
        self.browser_type = browser_type
        self.browser = None
        self.context = None
        self.page = None
        self._sessions: Dict[str, BrowserSession] = {}
        self._playwright = None

    async def initialize(self) -> bool:
        """Initialize Playwright"""
        try:
            from playwright.async_api import async_playwright
            self._playwright = async_playwright()
            return True
        except ImportError:
            logger.warning("Playwright not installed, using mock browser")
            return False

    async def launch(self, session_id: str) -> Optional[BrowserSession]:
        """Launch browser session"""
        try:
            if not self._playwright:
                # Mock session
                session = BrowserSession(
                    session_id=session_id,
                    headless=self.headless,
                    browser_type=self.browser_type
                )
                session.is_open = True
                self._sessions[session_id] = session
                return session

            pw = await self._playwright.__aenter__()
            browser = await getattr(pw, self.browser_type).launch(headless=self.headless)
            self.browser = browser
            self.context = await browser.new_context()
            self.page = await self.context.new_page()

            session = BrowserSession(
                session_id=session_id,
                headless=self.headless,
                browser_type=self.browser_type
            )
            session.is_open = True
            self._sessions[session_id] = session

            logger.info(f"Browser session {session_id} launched")
            return session

        except Exception as e:
            logger.error(f"Launch error: {e}")
            return None

    async def goto(self, session_id: str, url: str) -> bool:
        """Navigate to URL"""
        try:
            if not self.page:
                logger.warning("Browser not open")
                return False

            await self.page.goto(url)
            if session_id in self._sessions:
                self._sessions[session_id].current_url = url
            return True

        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False

    async def click(self, session_id: str, selector: str) -> bool:
        """Click element"""
        try:
            if not self.page:
                return False

            await self.page.click(selector)
            return True

        except Exception as e:
            logger.error(f"Click error: {e}")
            return False

    async def fill(self, session_id: str, selector: str, text: str) -> bool:
        """Fill form field"""
        try:
            if not self.page:
                return False

            await self.page.fill(selector, text)
            return True

        except Exception as e:
            logger.error(f"Fill error: {e}")
            return False

    async def type(self, session_id: str, selector: str, text: str) -> bool:
        """Type into field"""
        try:
            if not self.page:
                return False

            await self.page.focus(selector)
            await self.page.keyboard.type(text)
            return True

        except Exception as e:
            logger.error(f"Type error: {e}")
            return False

    async def select_option(self, session_id: str, selector: str, value: str) -> bool:
        """Select dropdown option"""
        try:
            if not self.page:
                return False

            await self.page.select_option(selector, value)
            return True

        except Exception as e:
            logger.error(f"Select error: {e}")
            return False

    async def screenshot(self, session_id: str, path: Optional[str] = None) -> Optional[bytes]:
        """Capture screenshot"""
        try:
            if not self.page:
                return None

            data = await self.page.screenshot(path=path)
            if session_id in self._sessions:
                self._sessions[session_id].screenshots.append(path or "screenshot")
            return data

        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    async def extract_text(self, session_id: str) -> Optional[str]:
        """Extract all page text"""
        try:
            if not self.page:
                return None

            content = await self.page.content()
            # Strip HTML tags - basic implementation
            import re
            text = re.sub('<[^<]+?>', '', content)
            return text[:5000]  # Limit to 5000 chars

        except Exception as e:
            logger.error(f"Extract text error: {e}")
            return None

    async def evaluate(self, session_id: str, script: str) -> Any:
        """Evaluate JavaScript"""
        try:
            if not self.page:
                return None

            result = await self.page.evaluate(script)
            return result

        except Exception as e:
            logger.error(f"Evaluate error: {e}")
            return None

    async def wait_for_selector(self, session_id: str, selector: str, timeout: int = 5000) -> bool:
        """Wait for element to appear"""
        try:
            if not self.page:
                return False

            await self.page.wait_for_selector(selector, timeout=timeout)
            return True

        except Exception as e:
            logger.error(f"Wait error: {e}")
            return False

    async def get_current_url(self, session_id: str) -> Optional[str]:
        """Get current page URL"""
        try:
            if not self.page:
                return None

            return self.page.url

        except Exception as e:
            logger.error(f"Get URL error: {e}")
            return None

    async def close(self, session_id: str) -> bool:
        """Close browser session"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

            if session_id in self._sessions:
                self._sessions[session_id].is_open = False

            logger.info(f"Browser session {session_id} closed")
            return True

        except Exception as e:
            logger.error(f"Close error: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get session info"""
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[BrowserSession]:
        """List all sessions"""
        return list(self._sessions.values())
