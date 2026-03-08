"""
Open Interpreter Runtime Integration for ArchonX

Integrates Open Interpreter fork as the primary reasoning and tool-routing engine.
Handles prompt execution, browser/desktop action delegation, and session lifecycle.

ZTE-20260308-0001: Open Interpreter integration layer
"""

import os
import asyncio
import json
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class InterpreterSession:
    """Open Interpreter execution session"""
    session_id: str
    task: str
    mode: str  # "browser", "desktop", "hybrid", "agent"
    model: str
    backend: str  # "anthropic", "openai", "local"
    created_at: str
    updated_at: str
    status: str  # "pending", "running", "completed", "error"
    messages: List[Dict[str, str]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class OpenInterpreterRuntime:
    """Open Interpreter integration - handles multi-modal task execution"""

    def __init__(
        self,
        interpreter_path: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet",
        backend: str = "anthropic"
    ):
        """Initialize Open Interpreter runtime"""
        self.interpreter_path = interpreter_path or os.getenv("OPEN_INTERPRETER_PATH")
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.backend = backend
        self.interpreter = None
        self._sessions: Dict[str, InterpreterSession] = {}
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize interpreter runtime"""
        try:
            if self.interpreter_path:
                import sys
                sys.path.insert(0, self.interpreter_path)

            # Import Open Interpreter fork
            try:
                from interpreter import Interpreter
            except ImportError:
                logger.warning("Open Interpreter not installed, using mock runtime")
                return False

            self.interpreter = Interpreter()

            # Configure with backend
            if self.backend == "anthropic":
                self.interpreter.model = self.model
                self.interpreter.api_key = self.api_key

            self._initialized = True
            logger.info(f"Open Interpreter initialized with {self.backend}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize interpreter: {e}")
            return False

    async def create_session(
        self,
        task: str,
        mode: str = "browser",
        metadata: Dict[str, Any] = None
    ) -> InterpreterSession:
        """Create new interpreter session"""
        now = datetime.now().isoformat()
        session = InterpreterSession(
            session_id=f"interp-{now.replace(':', '-')}",
            task=task,
            mode=mode,
            model=self.model,
            backend=self.backend,
            created_at=now,
            updated_at=now,
            status="pending",
            metadata=metadata or {}
        )
        self._sessions[session.session_id] = session
        return session

    async def execute(
        self,
        session_id: str,
        prompt: str
    ) -> AsyncGenerator[str, None]:
        """Execute task with streaming output"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._sessions[session_id]
        session.status = "running"
        session.updated_at = datetime.now().isoformat()

        try:
            # Add user message
            session.messages.append({
                "role": "user",
                "content": prompt
            })

            if not self._initialized:
                # Mock execution
                yield f"[Mock Execution] {prompt[:100]}..."
                session.result = "Mock result"
                session.status = "completed"
            else:
                # Real execution with Open Interpreter
                if hasattr(self.interpreter, 'chat'):
                    # Use chat interface if available
                    for chunk in self.interpreter.chat(prompt, stream=True):
                        yield chunk
                        session.artifacts.append(chunk)
                else:
                    # Fallback: direct execution
                    result = await self._execute_task(session, prompt)
                    yield result

            session.status = "completed"

        except Exception as e:
            logger.error(f"Execution error in {session_id}: {e}")
            session.status = "error"
            session.error = str(e)
            yield f"ERROR: {str(e)}"

        finally:
            session.updated_at = datetime.now().isoformat()

    async def _execute_task(
        self,
        session: InterpreterSession,
        task: str
    ) -> str:
        """Internal task execution"""
        # Route based on mode
        if session.mode == "browser":
            return await self._execute_browser_task(session, task)
        elif session.mode == "desktop":
            return await self._execute_desktop_task(session, task)
        elif session.mode == "hybrid":
            return await self._execute_hybrid_task(session, task)
        elif session.mode == "agent":
            return await self._execute_agent_task(session, task)
        else:
            raise ValueError(f"Unknown mode: {session.mode}")

    async def _execute_browser_task(
        self,
        session: InterpreterSession,
        task: str
    ) -> str:
        """Execute browser automation task"""
        logger.info(f"Executing browser task: {task[:50]}...")
        # Phase 2: Integrate with Playwright browser agent
        return f"[Browser] {task[:80]}..."

    async def _execute_desktop_task(
        self,
        session: InterpreterSession,
        task: str
    ) -> str:
        """Execute desktop automation task"""
        logger.info(f"Executing desktop task: {task[:50]}...")
        # Phase 2: Integrate with Desktop Commander runtime
        return f"[Desktop] {task[:80]}..."

    async def _execute_hybrid_task(
        self,
        session: InterpreterSession,
        task: str
    ) -> str:
        """Execute hybrid browser + desktop task"""
        logger.info(f"Executing hybrid task: {task[:50]}...")
        # Phase 2: Route between browser and desktop based on task
        return f"[Hybrid] {task[:80]}..."

    async def _execute_agent_task(
        self,
        session: InterpreterSession,
        task: str
    ) -> str:
        """Execute ARCHONX agent task"""
        logger.info(f"Executing agent task: {task[:50]}...")
        # Route to agent crews (White/Black)
        return f"[Agent] {task[:80]}..."

    def get_session(self, session_id: str) -> Optional[InterpreterSession]:
        """Get session by ID"""
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[InterpreterSession]:
        """List all sessions"""
        return list(self._sessions.values())

    async def screenshot(self, session_id: str) -> Optional[str]:
        """Capture screenshot in session"""
        if session_id not in self._sessions:
            return None

        try:
            # Phase 2: Integrate with browser/desktop screenshot capture
            session = self._sessions[session_id]
            filename = f"{session_id}-{datetime.now().timestamp()}.png"
            session.screenshots.append(filename)
            return filename
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    async def close_session(self, session_id: str) -> bool:
        """Close session and cleanup"""
        if session_id not in self._sessions:
            return False

        try:
            session = self._sessions[session_id]
            session.status = "closed"
            logger.info(f"Session {session_id} closed")
            return True
        except Exception as e:
            logger.error(f"Close session error: {e}")
            return False


# Global runtime instance
_runtime_instance: Optional[OpenInterpreterRuntime] = None


async def get_runtime() -> OpenInterpreterRuntime:
    """Get or create global interpreter runtime"""
    global _runtime_instance
    if _runtime_instance is None:
        _runtime_instance = OpenInterpreterRuntime()
        await _runtime_instance.initialize()
    return _runtime_instance
