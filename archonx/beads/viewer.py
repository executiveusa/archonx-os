"""
Beads Viewer Dashboard
======================
Web dashboard for task management on port 8766.

Features:
- Real-time task visualization
- Robot triage mode
- Ralphy loop tracking (PLAN → IMPLEMENT → TEST → EVALUATE → PATCH → REPEAT)
- Agent assignment
- Progress monitoring

BEAD-003: Beads Viewer Dashboard Implementation
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable, Awaitable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger("archonx.beads.viewer")


class TaskStatus(str, Enum):
    """Task status following Ralphy loop stages."""
    PENDING = "pending"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    EVALUATING = "evaluating"
    PATCHING = "patching"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Task:
    """
    Task representation with Ralphy loop tracking.
    
    Each task follows the Ralphy loop:
    PLAN → IMPLEMENT → TEST → EVALUATE → PATCH → REPEAT
    """
    id: str
    bead_id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    assigned_agent: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Ralphy loop tracking
    current_stage: str = "PLAN"
    stage_history: list[dict[str, Any]] = field(default_factory=list)
    iteration_count: int = 0
    max_iterations: int = 5
    
    # Metadata
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Results
    result: Optional[str] = None
    error: Optional[str] = None
    test_results: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "bead_id": self.bead_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "current_stage": self.current_stage,
            "stage_history": self.stage_history,
            "iteration_count": self.iteration_count,
            "max_iterations": self.max_iterations,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "result": self.result,
            "error": self.error,
            "test_results": self.test_results
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=data["id"],
            bead_id=data.get("bead_id", ""),
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "pending")),
            priority=TaskPriority(data.get("priority", "normal")),
            assigned_agent=data.get("assigned_agent"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            current_stage=data.get("current_stage", "PLAN"),
            stage_history=data.get("stage_history", []),
            iteration_count=data.get("iteration_count", 0),
            max_iterations=data.get("max_iterations", 5),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {}),
            result=data.get("result"),
            error=data.get("error"),
            test_results=data.get("test_results", [])
        )


class TaskManager:
    """
    Manages task lifecycle and Ralphy loop progression.
    
    Features:
    - Task creation and assignment
    - Status transitions
    - Ralphy loop stage management
    - Dependency tracking
    """

    def __init__(self, store_path: Optional[Path] = None) -> None:
        self.store_path = store_path or Path.home() / ".archonx" / "tasks.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._tasks: dict[str, Task] = {}
        self._agent_tasks: dict[str, list[str]] = defaultdict(list)
        self._counter = 0
        
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load tasks from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._counter = data.get("counter", 0)
                    for task_data in data.get("tasks", []):
                        task = Task.from_dict(task_data)
                        self._tasks[task.id] = task
                        if task.assigned_agent:
                            self._agent_tasks[task.assigned_agent].append(task.id)
                logger.info(f"Loaded {len(self._tasks)} tasks")
            except Exception as e:
                logger.warning(f"Failed to load tasks: {e}")

    def _save_tasks(self) -> None:
        """Save tasks to disk."""
        data = {
            "counter": self._counter,
            "tasks": [t.to_dict() for t in self._tasks.values()]
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_task(
        self,
        title: str,
        description: str = "",
        bead_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        assigned_agent: Optional[str] = None,
        tags: Optional[list[str]] = None,
        dependencies: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            bead_id: Bead identifier for tracking
            priority: Task priority
            assigned_agent: Agent to assign task to
            tags: Task tags
            dependencies: Task dependencies (task IDs)
            metadata: Additional metadata
            
        Returns:
            The created Task
        """
        self._counter += 1
        
        task = Task(
            id=f"task-{self._counter:06d}",
            bead_id=bead_id or f"BEAD-{self._counter:03d}",
            title=title,
            description=description,
            priority=priority,
            assigned_agent=assigned_agent,
            tags=tags or [],
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self._tasks[task.id] = task
        
        if assigned_agent:
            self._agent_tasks[assigned_agent].append(task.id)
        
        self._save_tasks()
        
        logger.info(f"Created task {task.id}: {title}")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(
        self,
        status: Optional[TaskStatus] = None,
        agent: Optional[str] = None,
        priority: Optional[TaskPriority] = None
    ) -> list[Task]:
        """Get tasks with optional filtering."""
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        if agent:
            tasks = [t for t in tasks if t.assigned_agent == agent]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def assign_task(self, task_id: str, agent_id: str) -> Optional[Task]:
        """Assign a task to an agent."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        # Remove from old agent
        if task.assigned_agent:
            try:
                self._agent_tasks[task.assigned_agent].remove(task_id)
            except ValueError:
                pass
        
        task.assigned_agent = agent_id
        task.updated_at = time.time()
        self._agent_tasks[agent_id].append(task_id)
        
        self._save_tasks()
        
        logger.info(f"Assigned task {task_id} to {agent_id}")
        return task

    def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[str] = None,
        error: Optional[str] = None
    ) -> Optional[Task]:
        """Update task status."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        old_status = task.status
        task.status = status
        task.updated_at = time.time()
        
        if status == TaskStatus.IMPLEMENTING and not task.started_at:
            task.started_at = time.time()
        
        if status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            task.completed_at = time.time()
        
        if result:
            task.result = result
        if error:
            task.error = error
        
        # Record stage history
        task.stage_history.append({
            "from_status": old_status.value,
            "to_status": status.value,
            "timestamp": time.time()
        })
        
        self._save_tasks()
        
        logger.info(f"Task {task_id} status: {old_status.value} → {status.value}")
        return task

    def advance_stage(self, task_id: str) -> Optional[Task]:
        """
        Advance task to next Ralphy loop stage.
        
        PLAN → IMPLEMENT → TEST → EVALUATE → PATCH → REPEAT
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        stages = ["PLAN", "IMPLEMENT", "TEST", "EVALUATE", "PATCH"]
        current_idx = stages.index(task.current_stage) if task.current_stage in stages else -1
        
        if current_idx < len(stages) - 1:
            task.current_stage = stages[current_idx + 1]
        else:
            # End of loop - check if should repeat
            task.iteration_count += 1
            if task.iteration_count < task.max_iterations:
                task.current_stage = "PLAN"
            else:
                task.current_stage = "COMPLETE"
        
        task.updated_at = time.time()
        task.stage_history.append({
            "stage": task.current_stage,
            "iteration": task.iteration_count,
            "timestamp": time.time()
        })
        
        self._save_tasks()
        
        logger.info(f"Task {task_id} advanced to stage {task.current_stage}")
        return task

    def get_agent_tasks(self, agent_id: str) -> list[Task]:
        """Get all tasks assigned to an agent."""
        task_ids = self._agent_tasks.get(agent_id, [])
        return [self._tasks[tid] for tid in task_ids if tid in self._tasks]

    def get_stats(self) -> dict[str, Any]:
        """Get task statistics."""
        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        
        for task in self._tasks.values():
            status_counts[task.status.value] += 1
            priority_counts[task.priority.value] += 1
        
        return {
            "total_tasks": len(self._tasks),
            "by_status": dict(status_counts),
            "by_priority": dict(priority_counts),
            "agents_with_tasks": len(self._agent_tasks)
        }


class RobotTriage:
    """
    Automated task triage system.
    
    Features:
    - Priority assessment
    - Agent matching
    - Dependency resolution
    """

    def __init__(self, task_manager: TaskManager) -> None:
        self.task_manager = task_manager
        
        # Agent capabilities mapping
        self._agent_capabilities: dict[str, list[str]] = {}

    def register_agent_capabilities(
        self,
        agent_id: str,
        capabilities: list[str]
    ) -> None:
        """Register an agent's capabilities."""
        self._agent_capabilities[agent_id] = capabilities
        logger.info(f"Registered capabilities for {agent_id}: {capabilities}")

    def assess_priority(self, task: Task) -> TaskPriority:
        """Assess and potentially adjust task priority."""
        # Check for keywords that indicate priority
        title_lower = task.title.lower()
        desc_lower = task.description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        if any(kw in combined for kw in ["critical", "urgent", "blocking", "down"]):
            return TaskPriority.CRITICAL
        elif any(kw in combined for kw in ["important", "high", "asap"]):
            return TaskPriority.HIGH
        elif any(kw in combined for kw in ["low", "nice to have", "eventually"]):
            return TaskPriority.LOW
        
        return task.priority

    def find_best_agent(self, task: Task) -> Optional[str]:
        """Find the best agent for a task based on capabilities."""
        if not self._agent_capabilities:
            return None
        
        # Extract required capabilities from task
        required = set(task.tags + [task.metadata.get("skill", "")])
        
        best_agent = None
        best_score = -1
        
        for agent_id, capabilities in self._agent_capabilities.items():
            agent_caps = set(capabilities)
            score = len(required & agent_caps)
            
            # Bonus for having fewer current tasks
            agent_tasks = self.task_manager.get_agent_tasks(agent_id)
            pending = len([t for t in agent_tasks if t.status == TaskStatus.PENDING])
            score -= pending * 0.1
            
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent

    def check_dependencies(self, task: Task) -> tuple[bool, list[str]]:
        """Check if all dependencies are satisfied."""
        unsatisfied = []
        
        for dep_id in task.dependencies:
            dep_task = self.task_manager.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                unsatisfied.append(dep_id)
        
        return len(unsatisfied) == 0, unsatisfied

    async def triage_task(self, task_id: str) -> dict[str, Any]:
        """
        Perform automated triage on a task.
        
        Returns:
            Triage result with recommendations
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": "Task not found"}
        
        # Assess priority
        assessed_priority = self.assess_priority(task)
        
        # Check dependencies
        deps_ok, unsatisfied = self.check_dependencies(task)
        
        # Find best agent
        best_agent = self.find_best_agent(task)
        
        result = {
            "task_id": task_id,
            "assessed_priority": assessed_priority.value,
            "original_priority": task.priority.value,
            "dependencies_satisfied": deps_ok,
            "unsatisfied_dependencies": unsatisfied,
            "recommended_agent": best_agent,
            "triage_timestamp": time.time()
        }
        
        # Auto-assign if agent found and dependencies OK
        if best_agent and deps_ok and not task.assigned_agent:
            self.task_manager.assign_task(task_id, best_agent)
            result["auto_assigned"] = True
        
        # Update priority if different
        if assessed_priority != task.priority:
            task.priority = assessed_priority
            self.task_manager._save_tasks()
            result["priority_updated"] = True
        
        return result


# WebSocket connection manager for dashboard
class DashboardConnectionManager:
    """Manages WebSocket connections for the dashboard."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        raw = json.dumps(message)
        for connection in self._connections:
            try:
                await connection.send_text(raw)
            except Exception:
                pass


class BeadsViewer:
    """
    Web dashboard for task management on port 8766.
    
    Features:
    - Real-time task visualization
    - Robot triage mode
    - Ralphy loop tracking
    - Agent assignment
    - Progress monitoring
    
    Usage:
        viewer = BeadsViewer(port=8766)
        await viewer.start()
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8766
    ) -> None:
        self.host = host
        self.port = port
        
        self.app = FastAPI(title="Beads Viewer", version="1.0.0")
        self.task_manager = TaskManager()
        self.triage = RobotTriage(self.task_manager)
        self.ws_manager = DashboardConnectionManager()
        
        self._setup_routes()
        
        logger.info(f"Beads Viewer initialized on {host}:{port}")

    def _setup_routes(self) -> None:
        """Set up FastAPI routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self._get_dashboard_html()

        @self.app.get("/api/tasks")
        async def get_tasks(
            status: Optional[str] = None,
            agent: Optional[str] = None,
            priority: Optional[str] = None
        ):
            filters = {}
            if status:
                filters["status"] = TaskStatus(status)
            if agent:
                filters["agent"] = agent
            if priority:
                filters["priority"] = TaskPriority(priority)
            
            tasks = self.task_manager.get_all_tasks(**filters)
            return {"tasks": [t.to_dict() for t in tasks]}

        @self.app.get("/api/tasks/{task_id}")
        async def get_task(task_id: str):
            task = self.task_manager.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task.to_dict()

        @self.app.post("/api/tasks")
        async def create_task(task_data: dict[str, Any]):
            task = self.task_manager.create_task(
                title=task_data.get("title", "Untitled"),
                description=task_data.get("description", ""),
                bead_id=task_data.get("bead_id"),
                priority=TaskPriority(task_data.get("priority", "normal")),
                assigned_agent=task_data.get("assigned_agent"),
                tags=task_data.get("tags", []),
                dependencies=task_data.get("dependencies", []),
                metadata=task_data.get("metadata", {})
            )
            
            # Broadcast to dashboard
            await self.ws_manager.broadcast({
                "type": "task_created",
                "task": task.to_dict()
            })
            
            return task.to_dict()

        @self.app.patch("/api/tasks/{task_id}")
        async def update_task(task_id: str, updates: dict[str, Any]):
            task = self.task_manager.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            
            if "status" in updates:
                self.task_manager.update_status(
                    task_id,
                    TaskStatus(updates["status"]),
                    updates.get("result"),
                    updates.get("error")
                )
            
            if "assigned_agent" in updates:
                self.task_manager.assign_task(task_id, updates["assigned_agent"])
            
            # Broadcast update
            updated_task = self.task_manager.get_task(task_id)
            await self.ws_manager.broadcast({
                "type": "task_updated",
                "task": updated_task.to_dict() if updated_task else None
            })
            
            return updated_task.to_dict() if updated_task else {}

        @self.app.post("/api/tasks/{task_id}/advance")
        async def advance_task(task_id: str):
            task = self.task_manager.advance_stage(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            
            await self.ws_manager.broadcast({
                "type": "task_advanced",
                "task": task.to_dict()
            })
            
            return task.to_dict()

        @self.app.post("/api/tasks/{task_id}/triage")
        async def triage_task(task_id: str):
            result = await self.triage.triage_task(task_id)
            
            await self.ws_manager.broadcast({
                "type": "task_triaged",
                "result": result
            })
            
            return result

        @self.app.get("/api/stats")
        async def get_stats():
            return self.task_manager.get_stats()

        @self.app.get("/api/agents/{agent_id}/tasks")
        async def get_agent_tasks(agent_id: str):
            tasks = self.task_manager.get_agent_tasks(agent_id)
            return {"tasks": [t.to_dict() for t in tasks]}

        @self.app.post("/api/agents/{agent_id}/capabilities")
        async def register_capabilities(agent_id: str, capabilities: list[str]):
            self.triage.register_agent_capabilities(agent_id, capabilities)
            return {"status": "ok"}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.ws_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    # Handle incoming WebSocket messages
                    try:
                        message = json.loads(data)
                        if message.get("type") == "ping":
                            await websocket.send_text(json.dumps({"type": "pong"}))
                    except json.JSONDecodeError:
                        pass
            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)

    def _get_dashboard_html(self) -> str:
        """Get the dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beads Viewer - ArchonX Task Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0a0e14;
            color: #e6e6e6;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%);
            padding: 20px;
            border-bottom: 1px solid #30363d;
        }
        .header h1 {
            font-size: 24px;
            color: #58a6ff;
        }
        .header .subtitle {
            color: #8b949e;
            font-size: 14px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
        }
        .stat-card h3 {
            color: #8b949e;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #58a6ff;
        }
        .tasks-container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }
        .tasks-header {
            padding: 16px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .tasks-header h2 {
            font-size: 18px;
        }
        .task-list {
            max-height: 600px;
            overflow-y: auto;
        }
        .task-item {
            padding: 16px;
            border-bottom: 1px solid #30363d;
            cursor: pointer;
            transition: background 0.2s;
        }
        .task-item:hover {
            background: #1f2428;
        }
        .task-item:last-child {
            border-bottom: none;
        }
        .task-title {
            font-weight: 500;
            margin-bottom: 8px;
        }
        .task-meta {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #8b949e;
        }
        .status-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }
        .status-pending { background: #30363d; color: #8b949e; }
        .status-planning { background: #1f3a5f; color: #58a6ff; }
        .status-implementing { background: #3d2f1f; color: #f0883e; }
        .status-testing { background: #2f3d1f; color: #a5d63a; }
        .status-completed { background: #1f3d2f; color: #3fb950; }
        .status-failed { background: #3d1f1f; color: #f85149; }
        .priority-critical { border-left: 3px solid #f85149; }
        .priority-high { border-left: 3px solid #f0883e; }
        .priority-normal { border-left: 3px solid #58a6ff; }
        .priority-low { border-left: 3px solid #8b949e; }
        .stage-indicator {
            display: flex;
            gap: 4px;
            margin-top: 8px;
        }
        .stage-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #30363d;
        }
        .stage-dot.active {
            background: #58a6ff;
        }
        .stage-dot.completed {
            background: #3fb950;
        }
        .btn {
            background: #238636;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn:hover {
            background: #2ea043;
        }
        .connection-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }
        .connection-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #3fb950;
        }
        .connection-dot.disconnected {
            background: #f85149;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Beads Viewer</h1>
        <div class="subtitle">ArchonX Task Management Dashboard</div>
    </div>
    
    <div class="container">
        <div class="stats-grid" id="stats">
            <div class="stat-card">
                <h3>Total Tasks</h3>
                <div class="value" id="stat-total">0</div>
            </div>
            <div class="stat-card">
                <h3>Pending</h3>
                <div class="value" id="stat-pending">0</div>
            </div>
            <div class="stat-card">
                <h3>In Progress</h3>
                <div class="value" id="stat-progress">0</div>
            </div>
            <div class="stat-card">
                <h3>Completed</h3>
                <div class="value" id="stat-completed">0</div>
            </div>
        </div>
        
        <div class="tasks-container">
            <div class="tasks-header">
                <h2>Tasks</h2>
                <div class="connection-status">
                    <div class="connection-dot" id="connection-dot"></div>
                    <span id="connection-text">Connected</span>
                </div>
            </div>
            <div class="task-list" id="task-list">
                <div style="padding: 40px; text-align: center; color: #8b949e;">
                    Loading tasks...
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        let tasks = [];
        
        ws.onopen = () => {
            document.getElementById('connection-dot').classList.remove('disconnected');
            document.getElementById('connection-text').textContent = 'Connected';
        };
        
        ws.onclose = () => {
            document.getElementById('connection-dot').classList.add('disconnected');
            document.getElementById('connection-text').textContent = 'Disconnected';
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'task_created' || data.type === 'task_updated') {
                loadTasks();
            }
        };
        
        async function loadTasks() {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            tasks = data.tasks;
            renderTasks();
            updateStats();
        }
        
        function renderTasks() {
            const container = document.getElementById('task-list');
            
            if (tasks.length === 0) {
                container.innerHTML = `
                    <div style="padding: 40px; text-align: center; color: #8b949e;">
                        No tasks found. Create a task to get started.
                    </div>
                `;
                return;
            }
            
            container.innerHTML = tasks.map(task => `
                <div class="task-item priority-${task.priority}" onclick="showTask('${task.id}')">
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        <span class="status-badge status-${task.status}">${task.status}</span>
                        <span>${task.bead_id}</span>
                        <span>${task.assigned_agent || 'Unassigned'}</span>
                    </div>
                    <div class="stage-indicator">
                        ${['PLAN', 'IMPLEMENT', 'TEST', 'EVALUATE', 'PATCH'].map((stage, i) => `
                            <div class="stage-dot ${stage === task.current_stage ? 'active' : ''}"></div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }
        
        function updateStats() {
            const stats = {
                total: tasks.length,
                pending: tasks.filter(t => t.status === 'pending').length,
                progress: tasks.filter(t => ['planning', 'implementing', 'testing'].includes(t.status)).length,
                completed: tasks.filter(t => t.status === 'completed').length
            };
            
            document.getElementById('stat-total').textContent = stats.total;
            document.getElementById('stat-pending').textContent = stats.pending;
            document.getElementById('stat-progress').textContent = stats.progress;
            document.getElementById('stat-completed').textContent = stats.completed;
        }
        
        function showTask(taskId) {
            const task = tasks.find(t => t.id === taskId);
            if (task) {
                console.log('Task details:', task);
            }
        }
        
        // Initial load
        loadTasks();
        
        // Refresh every 30 seconds
        setInterval(loadTasks, 30000);
    </script>
</body>
</html>
        """

    async def start(self) -> None:
        """Start the dashboard server."""
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    def get_stats(self) -> dict[str, Any]:
        """Get dashboard statistics."""
        return {
            "server": {
                "host": self.host,
                "port": self.port
            },
            "tasks": self.task_manager.get_stats()
        }


# Singleton instance
_viewer: Optional[BeadsViewer] = None


def get_beads_viewer() -> BeadsViewer:
    """Get the singleton BeadsViewer."""
    global _viewer
    if _viewer is None:
        _viewer = BeadsViewer()
    return _viewer
