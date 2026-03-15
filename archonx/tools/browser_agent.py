"""
FrankenClaw Browser Agent — Persistent Browser Engine
Inspired by GStack's persistent headless Chromium pattern.
Reduces browser action latency from 3-5s → 100-200ms.

BEAD: BEAD-MASTER-002
ZTE: FRANKENCLAW-BROWSER-v2
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

BROWSER_IDLE_TIMEOUT_MINUTES = 30  # Auto-shutdown after 30min inactivity (GStack pattern)


@dataclass
class BrowserSession:
    """Persistent browser session — stays alive between commands"""
    session_id: str
    headless: bool
    browser_type: str
    current_url: Optional[str] = None
    is_open: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_action_at: float = field(default_factory=time.time)
    screenshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self):
        """Update last action time to prevent idle shutdown"""
        self.last_action_at = time.time()

    def is_idle(self) -> bool:
        return (time.time() - self.last_action_at) > (BROWSER_IDLE_TIMEOUT_MINUTES * 60)


class PersistentBrowserEngine:
    """
    FrankenClaw Persistent Browser Engine.

    Key difference from standard browser agents:
    - Browser launches ONCE and stays alive (GStack pattern)
    - Subsequent actions reuse the live context — no cold-start delay
    - Cookies, sessions, tabs persist between commands
    - Auto-shuts down after 30min inactivity
    - Action latency: 100-200ms vs 3-5s for ephemeral browsers

    Usage:
        engine = PersistentBrowserEngine()
        await engine.start()
        await engine.navigate("https://example.com")
        screenshot = await engine.screenshot()
        await engine.click("#login-btn")
        # Browser stays alive for next command...
        await engine.stop()  # Or auto-stops after 30min idle
    """

    _instance: Optional["PersistentBrowserEngine"] = None  # Singleton for reuse

    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._session: Optional[BrowserSession] = None
        self._idle_monitor_task = None

    @classmethod
    async def get_instance(cls, headless: bool = True) -> "PersistentBrowserEngine":
        """Get or create singleton persistent browser (GStack pattern)"""
        if cls._instance is None or not cls._instance.is_running():
            cls._instance = cls(headless=headless)
            await cls._instance.start()
        cls._instance._session.touch()
        return cls._instance

    def is_running(self) -> bool:
        return self._browser is not None and self._page is not None

    async def start(self, session_id: str = "default") -> BrowserSession:
        """Launch persistent browser — called ONCE, reused for all subsequent actions"""
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().__aenter__()
            browser_launcher = getattr(self._playwright, self.browser_type)
            self._browser = await browser_launcher.launch(headless=self.headless)
            self._context = await self._browser.new_context(
                user_agent="Mozilla/5.0 (compatible; ArchonX-FrankenClaw/2.0)"
            )
            self._page = await self._context.new_page()
            self._session = BrowserSession(
                session_id=session_id,
                headless=self.headless,
                browser_type=self.browser_type,
                is_open=True
            )
            # Start idle monitor
            self._idle_monitor_task = asyncio.create_task(self._idle_monitor())
            logger.info("FrankenClaw persistent browser started [%s]", self.browser_type)
            return self._session
        except ImportError:
            logger.warning("Playwright not installed. Run: pip install playwright && playwright install")
            raise

    async def navigate(self, url: str, wait_for: str = "networkidle") -> Dict[str, Any]:
        """Navigate to URL — reuses live browser context"""
        self._session.touch()
        await self._page.goto(url, wait_until=wait_for)
        self._session.current_url = url
        logger.info("Navigated to %s", url)
        return {"url": url, "status": "navigated"}

    async def screenshot(self, path: Optional[str] = None, full_page: bool = True) -> bytes:
        """Capture screenshot of current page"""
        self._session.touch()
        if path:
            await self._page.screenshot(path=path, full_page=full_page)
            self._session.screenshots.append(path)
            return path
        return await self._page.screenshot(full_page=full_page)

    async def click(self, selector: str) -> bool:
        """Click element by CSS selector"""
        self._session.touch()
        await self._page.click(selector)
        return True

    async def fill(self, selector: str, value: str) -> bool:
        """Fill input field"""
        self._session.touch()
        await self._page.fill(selector, value)
        return True

    async def evaluate(self, script: str) -> Any:
        """Execute JavaScript in browser context"""
        self._session.touch()
        return await self._page.evaluate(script)

    async def get_content(self) -> str:
        """Get full page HTML"""
        self._session.touch()
        return await self._page.content()

    async def get_text(self, selector: str) -> str:
        """Get text content of element"""
        self._session.touch()
        return await self._page.text_content(selector) or ""

    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear"""
        self._session.touch()
        await self._page.wait_for_selector(selector, timeout=timeout)
        return True

    async def new_tab(self) -> None:
        """Open new tab — context persists (cookies, auth stay active)"""
        self._session.touch()
        self._page = await self._context.new_page()

    async def stop(self) -> None:
        """Shut down browser cleanly"""
        if self._idle_monitor_task:
            self._idle_monitor_task.cancel()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.__aexit__(None, None, None)
        self._browser = None
        self._page = None
        self._context = None
        logger.info("FrankenClaw persistent browser stopped")

    async def _idle_monitor(self) -> None:
        """Auto-shutdown after 30min inactivity (GStack pattern)"""
        while True:
            await asyncio.sleep(60)
            if self._session and self._session.is_idle():
                logger.info("Browser idle for 30min — auto-stopping")
                await self.stop()
                PersistentBrowserEngine._instance = None
                break


# Backwards compatible alias
BrowserAgent = PersistentBrowserEngine
