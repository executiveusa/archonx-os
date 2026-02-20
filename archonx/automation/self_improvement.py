"""
Daily Self-Improvement Cycle
=============================
Automated tasks for continuous improvement.

Features:
- 3 AM automated tasks
- PAULIWHEEL sync meetings (3x daily)
- Automated reporting
- Code quality checks
- Performance optimization
- Knowledge extraction

BEAD-006: Daily Self-Improvement Cycle Implementation
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, time as dt_time
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable, Awaitable

logger = logging.getLogger("archonx.automation.self_improvement")


class TaskFrequency(str, Enum):
    """Frequency of automated tasks."""
    HOURLY = "hourly"
    EVERY_3_HOURS = "every_3_hours"
    EVERY_6_HOURS = "every_6_hours"
    DAILY = "daily"
    WEEKLY = "weekly"


class TaskPriority(str, Enum):
    """Priority of automated tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class AutomatedTask:
    """Definition of an automated task."""
    task_id: str
    name: str
    description: str
    frequency: TaskFrequency
    scheduled_time: Optional[str] = None  # HH:MM format for daily tasks
    priority: TaskPriority = TaskPriority.NORMAL
    enabled: bool = True
    last_run: Optional[float] = None
    last_result: Optional[str] = None
    run_count: int = 0
    handler: Optional[Callable[[], Awaitable[dict[str, Any]]]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency.value,
            "scheduled_time": self.scheduled_time,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "last_result": self.last_result,
            "run_count": self.run_count
        }


@dataclass
class SyncMeetingResult:
    """Result of a PAULIWHEEL sync meeting."""
    meeting_id: str
    timestamp: float
    participants: list[str]
    acked_agents: list[str]
    restricted_agents: list[str]
    eco_prompt_version: str
    toolbox_version: str
    contracts_hash: str
    decisions: list[dict[str, Any]]
    action_items: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "timestamp": self.timestamp,
            "participants": self.participants,
            "acked_agents": self.acked_agents,
            "restricted_agents": self.restricted_agents,
            "eco_prompt_version": self.eco_prompt_version,
            "toolbox_version": self.toolbox_version,
            "contracts_hash": self.contracts_hash,
            "decisions": self.decisions,
            "action_items": self.action_items
        }


class PAULIWHEELSync:
    """
    PAULIWHEEL sync meeting scheduler and executor.
    
    Per AGENTS.md:
    - Run PAULIWHEEL sync meetings at least 3 times per day
    - Agents must ACK the latest eco-prompt, toolbox version, and contracts hash
    - Non-ACKed agents are `restricted`
    
    Default schedule:
    - 09:00 UTC - Morning sync
    - 15:00 UTC - Afternoon sync
    - 21:00 UTC - Evening sync
    """
    
    def __init__(
        self,
        schedule: Optional[list[str]] = None,
        registry: Optional[Any] = None
    ) -> None:
        """
        Initialize PAULIWHEEL sync.
        
        Args:
            schedule: List of times in HH:MM format (UTC)
            registry: Agent registry
        """
        self.schedule = schedule or ["09:00", "15:00", "21:00"]
        self.registry = registry
        
        self._meeting_history: list[SyncMeetingResult] = []
        self._current_versions = {
            "eco_prompt": "1.0.0",
            "toolbox": "1.0.0",
            "contracts_hash": "abc123"
        }
        
        logger.info(f"PAULIWHEEL Sync initialized with schedule: {self.schedule}")

    async def run_meeting(self) -> SyncMeetingResult:
        """
        Run a PAULIWHEEL sync meeting.
        
        Returns:
            SyncMeetingResult with meeting details
        """
        meeting_id = f"sync-{datetime.now(timezone.UTC).strftime('%Y%m%d-%H%M%S')}"
        timestamp = time.time()
        
        logger.info(f"Starting PAULIWHEEL sync meeting: {meeting_id}")
        
        # Get all agents
        participants = []
        acked_agents = []
        restricted_agents = []
        
        if self.registry:
            for agent in self.registry.all():
                participants.append(agent.agent_id)
                
                # Simulate ACK (in production, this would be actual agent responses)
                # For now, all active agents are considered ACKed
                if agent.status.value in ["active", "idle"]:
                    acked_agents.append(agent.agent_id)
                else:
                    restricted_agents.append(agent.agent_id)
        
        # Make decisions based on current state
        decisions = []
        action_items = []
        
        # Check if any agents are restricted
        if restricted_agents:
            decisions.append({
                "type": "restriction_notice",
                "agents": restricted_agents,
                "reason": "Did not ACK in previous meeting"
            })
            action_items.append({
                "action": "follow_up_restricted",
                "agents": restricted_agents,
                "priority": "high"
            })
        
        # Record meeting
        result = SyncMeetingResult(
            meeting_id=meeting_id,
            timestamp=timestamp,
            participants=participants,
            acked_agents=acked_agents,
            restricted_agents=restricted_agents,
            eco_prompt_version=self._current_versions["eco_prompt"],
            toolbox_version=self._current_versions["toolbox"],
            contracts_hash=self._current_versions["contracts_hash"],
            decisions=decisions,
            action_items=action_items
        )
        
        self._meeting_history.append(result)
        
        logger.info(
            f"PAULIWHEEL sync complete: {len(acked_agents)} ACKed, "
            f"{len(restricted_agents)} restricted"
        )
        
        return result

    def get_last_meeting(self) -> Optional[SyncMeetingResult]:
        """Get the last meeting result."""
        return self._meeting_history[-1] if self._meeting_history else None

    def get_meeting_history(self, limit: int = 10) -> list[SyncMeetingResult]:
        """Get meeting history."""
        return self._meeting_history[-limit:]


class DailySelfImprovement:
    """
    Daily self-improvement cycle for ArchonX.
    
    Features:
    - 3 AM automated tasks (code quality, optimization)
    - PAULIWHEEL sync meetings (3x daily)
    - Automated reporting
    - Knowledge extraction
    - Performance monitoring
    
    Schedule:
    - 03:00 UTC - Daily self-improvement tasks
    - 09:00 UTC - Morning PAULIWHEEL sync
    - 15:00 UTC - Afternoon PAULIWHEEL sync
    - 21:00 UTC - Evening PAULIWHEEL sync
    
    Usage:
        improvement = DailySelfImprovement()
        await improvement.start()
        
        # Or run specific tasks
        await improvement.run_daily_tasks()
        await improvement.run_sync_meeting()
    """
    
    def __init__(
        self,
        registry: Optional[Any] = None,
        kpi_dashboard: Optional[Any] = None,
        orchestrator: Optional[Any] = None,
        reports_path: Optional[Path] = None
    ) -> None:
        """
        Initialize daily self-improvement.
        
        Args:
            registry: Agent registry
            kpi_dashboard: KPI dashboard for reporting
            orchestrator: Orchestrator for task management
            reports_path: Path for reports output
        """
        self.registry = registry
        self.kpi_dashboard = kpi_dashboard
        self.orchestrator = orchestrator
        
        self.reports_path = reports_path or Path("ops/reports")
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        self.pauliwheel_sync = PAULIWHEELSync(registry=registry)
        
        self._tasks: dict[str, AutomatedTask] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Register default tasks
        self._register_default_tasks()
        
        logger.info("Daily Self-Improvement initialized")

    def _register_default_tasks(self) -> None:
        """Register default automated tasks."""
        default_tasks = [
            AutomatedTask(
                task_id="daily_report",
                name="Generate Daily Report",
                description="Generate daily KPI report",
                frequency=TaskFrequency.DAILY,
                scheduled_time="03:00",
                priority=TaskPriority.HIGH,
                handler=self._generate_daily_report
            ),
            AutomatedTask(
                task_id="code_quality_check",
                name="Code Quality Check",
                description="Run code quality checks (ruff, mypy)",
                frequency=TaskFrequency.DAILY,
                scheduled_time="03:15",
                priority=TaskPriority.HIGH,
                handler=self._run_code_quality
            ),
            AutomatedTask(
                task_id="performance_optimization",
                name="Performance Optimization",
                description="Analyze and optimize performance",
                frequency=TaskFrequency.DAILY,
                scheduled_time="03:30",
                priority=TaskPriority.NORMAL,
                handler=self._run_performance_optimization
            ),
            AutomatedTask(
                task_id="knowledge_extraction",
                name="Knowledge Extraction",
                description="Extract patterns and learnings from recent tasks",
                frequency=TaskFrequency.DAILY,
                scheduled_time="03:45",
                priority=TaskPriority.NORMAL,
                handler=self._run_knowledge_extraction
            ),
            AutomatedTask(
                task_id="cleanup_expired",
                name="Cleanup Expired Data",
                description="Clean up expired sessions, tokens, and old data",
                frequency=TaskFrequency.DAILY,
                scheduled_time="04:00",
                priority=TaskPriority.LOW,
                handler=self._run_cleanup
            ),
            AutomatedTask(
                task_id="health_check",
                name="System Health Check",
                description="Check health of all agents and services",
                frequency=TaskFrequency.EVERY_6_HOURS,
                priority=TaskPriority.CRITICAL,
                handler=self._run_health_check
            ),
        ]
        
        for task in default_tasks:
            self._tasks[task.task_id] = task

    def register_task(
        self,
        task_id: str,
        name: str,
        description: str,
        frequency: TaskFrequency,
        handler: Callable[[], Awaitable[dict[str, Any]]],
        scheduled_time: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> AutomatedTask:
        """Register a new automated task."""
        task = AutomatedTask(
            task_id=task_id,
            name=name,
            description=description,
            frequency=frequency,
            scheduled_time=scheduled_time,
            priority=priority,
            handler=handler
        )
        self._tasks[task_id] = task
        logger.info(f"Registered automated task: {task_id}")
        return task

    async def start(self) -> None:
        """Start the automated task scheduler."""
        if self._running:
            logger.warning("Self-improvement already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        
        logger.info("Daily Self-Improvement scheduler started")

    async def stop(self) -> None:
        """Stop the automated task scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Daily Self-Improvement scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                now = datetime.now(timezone.UTC)
                current_time = now.strftime("%H:%M")
                
                # Check for tasks to run
                for task in self._tasks.values():
                    if not task.enabled:
                        continue
                    
                    should_run = False
                    
                    if task.frequency == TaskFrequency.DAILY:
                        if task.scheduled_time == current_time:
                            should_run = True
                    elif task.frequency == TaskFrequency.HOURLY:
                        if now.minute == 0:
                            should_run = True
                    elif task.frequency == TaskFrequency.EVERY_3_HOURS:
                        if now.minute == 0 and now.hour % 3 == 0:
                            should_run = True
                    elif task.frequency == TaskFrequency.EVERY_6_HOURS:
                        if now.minute == 0 and now.hour % 6 == 0:
                            should_run = True
                    
                    if should_run:
                        asyncio.create_task(self._run_task(task))
                
                # Check for PAULIWHEEL sync meetings
                if current_time in self.pauliwheel_sync.schedule:
                    asyncio.create_task(self.pauliwheel_sync.run_meeting())
                
                # Sleep for 1 minute
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)

    async def _run_task(self, task: AutomatedTask) -> None:
        """Run a single automated task."""
        logger.info(f"Running automated task: {task.name}")
        
        start_time = time.time()
        
        try:
            if task.handler:
                result = await task.handler()
            else:
                result = {"status": "skipped", "reason": "No handler"}
            
            task.last_run = time.time()
            task.last_result = json.dumps(result)
            task.run_count += 1
            
            duration = time.time() - start_time
            
            logger.info(f"Task {task.name} completed in {duration:.2f}s")
            
            # Save report
            await self._save_task_report(task, result, duration)
            
        except Exception as e:
            logger.exception(f"Task {task.name} failed: {e}")
            task.last_result = json.dumps({"status": "error", "error": str(e)})

    async def _save_task_report(
        self,
        task: AutomatedTask,
        result: dict[str, Any],
        duration: float
    ) -> None:
        """Save task report to disk."""
        report = {
            "task_id": task.task_id,
            "task_name": task.name,
            "timestamp": datetime.now(timezone.UTC).isoformat(),
            "duration_seconds": duration,
            "result": result,
            "run_count": task.run_count
        }
        
        report_path = self.reports_path / f"{task.task_id}_{datetime.now(timezone.UTC).strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    # --- Default Task Handlers ---

    async def _generate_daily_report(self) -> dict[str, Any]:
        """Generate daily KPI report."""
        if self.kpi_dashboard:
            report = self.kpi_dashboard.generate_report(period="daily")
            return {
                "status": "success",
                "report_date": report.get("report_date"),
                "total_tasks": report.get("summary", {}).get("total_tasks_completed", 0),
                "total_revenue": report.get("summary", {}).get("total_revenue", 0)
            }
        return {"status": "skipped", "reason": "No KPI dashboard"}

    async def _run_code_quality(self) -> dict[str, Any]:
        """Run code quality checks."""
        # In production, this would run ruff, mypy, etc.
        return {
            "status": "success",
            "checks": ["ruff", "mypy", "black"],
            "issues_found": 0,
            "note": "Simulated - implement actual checks"
        }

    async def _run_performance_optimization(self) -> dict[str, Any]:
        """Run performance optimization analysis."""
        return {
            "status": "success",
            "optimizations": [],
            "note": "Analyze slow queries, memory usage, etc."
        }

    async def _run_knowledge_extraction(self) -> dict[str, Any]:
        """Extract patterns and learnings from recent tasks."""
        return {
            "status": "success",
            "patterns_extracted": 0,
            "note": "Extract successful patterns for agent learning"
        }

    async def _run_cleanup(self) -> dict[str, Any]:
        """Clean up expired data."""
        cleaned = {
            "expired_sessions": 0,
            "old_tokens": 0,
            "old_messages": 0
        }
        
        # Clean up sessions if available
        if hasattr(self, 'session_manager'):
            cleaned["expired_sessions"] = await self.session_manager.cleanup_expired()
        
        return {"status": "success", "cleaned": cleaned}

    async def _run_health_check(self) -> dict[str, Any]:
        """Check health of all agents and services."""
        health = {
            "agents": {"healthy": 0, "unhealthy": 0},
            "services": {}
        }
        
        if self.registry:
            for agent in self.registry.all():
                if agent.health >= 0.8:
                    health["agents"]["healthy"] += 1
                else:
                    health["agents"]["unhealthy"] += 1
        
        return {
            "status": "success",
            "health": health,
            "timestamp": datetime.now(timezone.UTC).isoformat()
        }

    # --- Manual Triggers ---

    async def run_daily_tasks(self) -> dict[str, Any]:
        """Manually trigger all daily tasks."""
        results = {}
        
        for task in self._tasks.values():
            if task.frequency == TaskFrequency.DAILY:
                await self._run_task(task)
                results[task.task_id] = task.last_result
        
        return results

    async def run_sync_meeting(self) -> SyncMeetingResult:
        """Manually trigger a PAULIWHEEL sync meeting."""
        return await self.pauliwheel_sync.run_meeting()

    def get_task_status(self) -> dict[str, Any]:
        """Get status of all automated tasks."""
        return {
            "running": self._running,
            "tasks": {
                task_id: task.to_dict()
                for task_id, task in self._tasks.items()
            },
            "sync_schedule": self.pauliwheel_sync.schedule,
            "last_sync": self.pauliwheel_sync.get_last_meeting().to_dict() if self.pauliwheel_sync.get_last_meeting() else None
        }


# Singleton instance
_self_improvement: Optional[DailySelfImprovement] = None


def get_self_improvement() -> DailySelfImprovement:
    """Get the singleton DailySelfImprovement."""
    global _self_improvement
    if _self_improvement is None:
        _self_improvement = DailySelfImprovement()
    return _self_improvement
