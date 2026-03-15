"""
Memory Manager
==============
High-level memory management for ArchonX agents.

Provides:
- Context-aware memory retrieval
- Pattern extraction and storage
- Expertise file management
- Session memory tracking
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from archonx.memory.byterover_client import ByteRoverClient, MemoryLayer, get_client

logger = logging.getLogger("archonx.memory.manager")


@dataclass
class AgentExpertise:
    """Expertise record for an agent."""
    agent_id: str
    problem: str
    approach: str
    result: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.UTC).isoformat())
    reuse_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "problem": self.problem,
            "approach": self.approach,
            "result": self.result,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "reuse_count": self.reuse_count
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentExpertise:
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            problem=data["problem"],
            approach=data["approach"],
            result=data["result"],
            confidence=data.get("confidence", 0.5),
            timestamp=data.get("timestamp", datetime.now(timezone.UTC).isoformat()),
            reuse_count=data.get("reuse_count", 0)
        )


@dataclass
class SessionMemory:
    """Memory for a single agent session."""
    session_id: str
    agent_id: str
    task: str
    decisions: list[dict[str, Any]] = field(default_factory=list)
    context_used: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now(timezone.UTC).isoformat())
    end_time: Optional[str] = None
    success: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "task": self.task,
            "decisions": self.decisions,
            "context_used": self.context_used,
            "tools_used": self.tools_used,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "success": self.success
        }


class MemoryManager:
    """
    High-level memory management for ArchonX agents.
    
    Features:
    - Context-aware retrieval for tasks
    - Pattern extraction and storage
    - Expertise file management per agent
    - Session memory tracking
    - Learning from past experiences
    
    Usage:
        manager = MemoryManager()
        await manager.record_expertise("white-queen", expertise)
        context = await manager.get_task_context("Build landing page")
    """

    def __init__(
        self,
        client: Optional[ByteRoverClient] = None,
        expertise_dir: Optional[Path] = None,
        session_dir: Optional[Path] = None
    ):
        """
        Initialize memory manager.
        
        Args:
            client: ByteRover client (uses default if not provided)
            expertise_dir: Directory for expertise files
            session_dir: Directory for session files
        """
        self.client = client or get_client()
        
        # Expertise storage
        self.expertise_dir = expertise_dir or Path.home() / ".archonx" / "expertise"
        self.expertise_dir.mkdir(parents=True, exist_ok=True)
        
        # Session storage
        self.session_dir = session_dir or Path.home() / ".archonx" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Current sessions
        self._sessions: dict[str, SessionMemory] = {}
        
        logger.info("Memory manager initialized")

    async def get_task_context(
        self,
        task: str,
        agent_id: Optional[str] = None,
        max_items: int = 5
    ) -> dict[str, Any]:
        """
        Get relevant context for a task.
        
        Args:
            task: The task description
            agent_id: Optional agent ID for agent-specific context
            max_items: Maximum items per category
            
        Returns:
            Dictionary with relevant context
        """
        context = {
            "task": task,
            "patterns": [],
            "expertise": [],
            "related_memories": []
        }
        
        # Search for relevant patterns
        pattern_results = await self.client.search(
            query=task,
            layer=MemoryLayer.GLOBAL,
            limit=max_items
        )
        context["patterns"] = [
            {"key": r.entry.key, "value": r.entry.value, "score": r.score}
            for r in pattern_results
        ]
        
        # Search for project-specific memories
        project_results = await self.client.search(
            query=task,
            layer=MemoryLayer.PROJECT,
            limit=max_items
        )
        context["related_memories"] = [
            {"key": r.entry.key, "value": r.entry.value, "score": r.score}
            for r in project_results
        ]
        
        # Get agent-specific expertise
        if agent_id:
            expertise = await self.get_expertise(agent_id, task)
            context["expertise"] = expertise[:max_items]
        
        return context

    async def record_expertise(
        self,
        agent_id: str,
        problem: str,
        approach: str,
        result: str,
        confidence: float = 0.5
    ) -> AgentExpertise:
        """
        Record agent expertise.
        
        Args:
            agent_id: The agent's ID
            problem: The problem encountered
            approach: The approach taken
            result: The result achieved
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            The created AgentExpertise
        """
        expertise = AgentExpertise(
            agent_id=agent_id,
            problem=problem,
            approach=approach,
            result=result,
            confidence=confidence
        )
        
        # Save to expertise file
        agent_dir = self.expertise_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(timezone.UTC).strftime("%Y%m%d_%H%M%S")
        file_path = agent_dir / f"{timestamp}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(expertise.to_dict(), f, indent=2)
        
        # Also save to ByteRover for searchability
        await self.client.save(
            key=f"expertise:{agent_id}:{timestamp}",
            value=expertise.to_dict(),
            layer=MemoryLayer.TEAM,
            tags=["expertise", agent_id],
            confidence=confidence
        )
        
        logger.info(f"Recorded expertise for {agent_id}: {problem[:50]}...")
        return expertise

    async def get_expertise(
        self,
        agent_id: str,
        query: Optional[str] = None,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get expertise for an agent.
        
        Args:
            agent_id: The agent's ID
            query: Optional search query
            limit: Maximum results
            
        Returns:
            List of expertise records
        """
        expertise_list = []
        
        # Load from expertise directory
        agent_dir = self.expertise_dir / agent_id
        if agent_dir.exists():
            for file_path in sorted(agent_dir.glob("*.json"), reverse=True)[:limit]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        expertise = AgentExpertise.from_dict(data)
                        
                        # Filter by query if provided
                        if query:
                            query_lower = query.lower()
                            if (query_lower not in expertise.problem.lower() and
                                query_lower not in expertise.approach.lower()):
                                continue
                        
                        expertise_list.append(expertise.to_dict())
                except Exception as e:
                    logger.warning(f"Failed to load expertise {file_path}: {e}")
        
        return expertise_list

    async def start_session(
        self,
        session_id: str,
        agent_id: str,
        task: str
    ) -> SessionMemory:
        """
        Start a new agent session.
        
        Args:
            session_id: Unique session ID
            agent_id: The agent's ID
            task: The task being performed
            
        Returns:
            The created SessionMemory
        """
        session = SessionMemory(
            session_id=session_id,
            agent_id=agent_id,
            task=task
        )
        
        self._sessions[session_id] = session
        logger.info(f"Started session {session_id} for {agent_id}")
        
        return session

    async def record_decision(
        self,
        session_id: str,
        decision: str,
        reasoning: str,
        outcome: Optional[str] = None
    ) -> None:
        """
        Record a decision made during a session.
        
        Args:
            session_id: The session ID
            decision: The decision made
            reasoning: The reasoning behind it
            outcome: Optional outcome of the decision
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return
        
        session.decisions.append({
            "decision": decision,
            "reasoning": reasoning,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.UTC).isoformat()
        })

    async def record_tool_use(
        self,
        session_id: str,
        tool: str,
        purpose: str,
        success: bool = True
    ) -> None:
        """
        Record tool usage during a session.
        
        Args:
            session_id: The session ID
            tool: The tool used
            purpose: The purpose of using the tool
            success: Whether the tool use was successful
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return
        
        session.tools_used.append({
            "tool": tool,
            "purpose": purpose,
            "success": success,
            "timestamp": datetime.now(timezone.UTC).isoformat()
        })

    async def end_session(
        self,
        session_id: str,
        success: bool
    ) -> Optional[SessionMemory]:
        """
        End a session.
        
        Args:
            session_id: The session ID
            success: Whether the session was successful
            
        Returns:
            The completed SessionMemory
        """
        session = self._sessions.pop(session_id, None)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session.end_time = datetime.now(timezone.UTC).isoformat()
        session.success = success
        
        # Save session to disk
        file_path = self.session_dir / f"{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)
        
        logger.info(f"Ended session {session_id} (success: {success})")
        return session

    async def extract_pattern(
        self,
        session_id: str,
        pattern_name: str,
        pattern_type: str = "workflow"
    ) -> Optional[dict[str, Any]]:
        """
        Extract a reusable pattern from a session.
        
        Args:
            session_id: The session ID
            pattern_name: Name for the pattern
            pattern_type: Type of pattern (workflow, decision, tool_sequence)
            
        Returns:
            The extracted pattern or None
        """
        file_path = self.session_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        
        pattern = {
            "name": pattern_name,
            "type": pattern_type,
            "source_session": session_id,
            "task": session_data.get("task"),
            "decisions": session_data.get("decisions", []),
            "tools_used": session_data.get("tools_used", []),
            "success": session_data.get("success")
        }
        
        # Save pattern to global memory
        await self.client.save(
            key=f"pattern:{pattern_type}:{pattern_name}",
            value=pattern,
            layer=MemoryLayer.GLOBAL,
            tags=["pattern", pattern_type],
            confidence=0.8 if session_data.get("success") else 0.5
        )
        
        logger.info(f"Extracted pattern: {pattern_name}")
        return pattern

    async def get_session_stats(self, agent_id: Optional[str] = None) -> dict[str, Any]:
        """
        Get statistics about sessions.
        
        Args:
            agent_id: Optional agent ID filter
            
        Returns:
            Dictionary with session stats
        """
        stats = {
            "total_sessions": 0,
            "successful_sessions": 0,
            "failed_sessions": 0,
            "total_decisions": 0,
            "total_tools_used": 0,
            "by_agent": {}
        }
        
        for file_path in self.session_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    session = json.load(f)
                
                # Filter by agent if provided
                if agent_id and session.get("agent_id") != agent_id:
                    continue
                
                stats["total_sessions"] += 1
                if session.get("success"):
                    stats["successful_sessions"] += 1
                else:
                    stats["failed_sessions"] += 1
                
                stats["total_decisions"] += len(session.get("decisions", []))
                stats["total_tools_used"] += len(session.get("tools_used", []))
                
                # By agent breakdown
                agent = session.get("agent_id", "unknown")
                if agent not in stats["by_agent"]:
                    stats["by_agent"][agent] = {
                        "sessions": 0,
                        "successes": 0,
                        "failures": 0
                    }
                stats["by_agent"][agent]["sessions"] += 1
                if session.get("success"):
                    stats["by_agent"][agent]["successes"] += 1
                else:
                    stats["by_agent"][agent]["failures"] += 1
                    
            except Exception as e:
                logger.warning(f"Failed to load session {file_path}: {e}")
        
        return stats


# Singleton instance
_manager: Optional[MemoryManager] = None


def get_manager() -> MemoryManager:
    """Get the singleton MemoryManager."""
    global _manager
    if _manager is None:
        _manager = MemoryManager()
    return _manager
