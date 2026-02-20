"""
KPI Dashboard
=============
Performance tracking and reporting for ArchonX agents.

Features:
- Agent performance metrics
- Task completion tracking
- Revenue tracking for $100M goal
- Daily/weekly/monthly reports
- Automated reporting

BEAD-005: KPI Dashboard Implementation
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("archonx.kpis.dashboard")


class MetricType(str, Enum):
    """Types of metrics tracked."""
    TASKS_COMPLETED = "tasks_completed"
    TASKS_FAILED = "tasks_failed"
    AVERAGE_DURATION = "average_duration"
    SUCCESS_RATE = "success_rate"
    REVENUE_GENERATED = "revenue_generated"
    CLIENTS_ACQUIRED = "clients_acquired"
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"


@dataclass
class AgentMetrics:
    """Performance metrics for a single agent."""
    agent_id: str
    agent_name: str
    crew: str
    role: str
    
    # Task metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_in_progress: int = 0
    
    # Time metrics
    total_time_spent: float = 0.0  # seconds
    average_task_duration: float = 0.0  # seconds
    
    # Quality metrics
    success_rate: float = 0.0  # 0.0 - 1.0
    quality_score: float = 0.0  # 0.0 - 100.0
    
    # Revenue metrics
    revenue_generated: float = 0.0  # USD
    clients_served: int = 0
    
    # Status
    current_status: str = "idle"
    last_task_at: Optional[float] = None
    last_success_at: Optional[float] = None
    
    # History
    daily_tasks: dict[str, int] = field(default_factory=dict)  # date -> count
    weekly_revenue: dict[str, float] = field(default_factory=dict)  # week -> amount
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "crew": self.crew,
            "role": self.role,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "tasks_in_progress": self.tasks_in_progress,
            "total_time_spent": self.total_time_spent,
            "average_task_duration": self.average_task_duration,
            "success_rate": self.success_rate,
            "quality_score": self.quality_score,
            "revenue_generated": self.revenue_generated,
            "clients_served": self.clients_served,
            "current_status": self.current_status,
            "last_task_at": self.last_task_at,
            "last_success_at": self.last_success_at,
            "daily_tasks": self.daily_tasks,
            "weekly_revenue": self.weekly_revenue
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentMetrics:
        return cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            crew=data["crew"],
            role=data["role"],
            tasks_completed=data.get("tasks_completed", 0),
            tasks_failed=data.get("tasks_failed", 0),
            tasks_in_progress=data.get("tasks_in_progress", 0),
            total_time_spent=data.get("total_time_spent", 0.0),
            average_task_duration=data.get("average_task_duration", 0.0),
            success_rate=data.get("success_rate", 0.0),
            quality_score=data.get("quality_score", 0.0),
            revenue_generated=data.get("revenue_generated", 0.0),
            clients_served=data.get("clients_served", 0),
            current_status=data.get("current_status", "idle"),
            last_task_at=data.get("last_task_at"),
            last_success_at=data.get("last_success_at"),
            daily_tasks=data.get("daily_tasks", {}),
            weekly_revenue=data.get("weekly_revenue", {})
        )

    def record_task_completion(
        self,
        success: bool,
        duration: float,
        revenue: float = 0.0,
        client_id: Optional[str] = None
    ) -> None:
        """Record a task completion."""
        if success:
            self.tasks_completed += 1
            self.last_success_at = time.time()
            self.revenue_generated += revenue
        else:
            self.tasks_failed += 1
        
        self.total_time_spent += duration
        self.last_task_at = time.time()
        
        # Update averages
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.success_rate = self.tasks_completed / total_tasks
            self.average_task_duration = self.total_time_spent / total_tasks
        
        # Update daily tasks
        today = datetime.now(timezone.UTC).strftime("%Y-%m-%d")
        self.daily_tasks[today] = self.daily_tasks.get(today, 0) + 1
        
        # Update weekly revenue
        week = datetime.now(timezone.UTC).strftime("%Y-W%W")
        if revenue > 0:
            self.weekly_revenue[week] = self.weekly_revenue.get(week, 0.0) + revenue
        
        if client_id:
            self.clients_served += 1


@dataclass
class RevenueGoal:
    """Revenue goal tracking for $100M target."""
    target_amount: float = 100_000_000.0  # $100M
    current_amount: float = 0.0
    start_date: str = "2024-01-01"
    target_date: str = "2030-01-01"
    
    # Milestones
    milestones: list[dict[str, Any]] = field(default_factory=list)
    
    # Progress tracking
    monthly_revenue: dict[str, float] = field(default_factory=dict)
    quarterly_revenue: dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.milestones:
            self.milestones = [
                {"amount": 1_000_000, "name": "First Million", "achieved": False, "achieved_at": None},
                {"amount": 5_000_000, "name": "Five Million", "achieved": False, "achieved_at": None},
                {"amount": 10_000_000, "name": "Ten Million", "achieved": False, "achieved_at": None},
                {"amount": 25_000_000, "name": "Quarter Way", "achieved": False, "achieved_at": None},
                {"amount": 50_000_000, "name": "Half Way", "achieved": False, "achieved_at": None},
                {"amount": 75_000_000, "name": "Three Quarters", "achieved": False, "achieved_at": None},
                {"amount": 100_000_000, "name": "Target Reached", "achieved": False, "achieved_at": None},
            ]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "start_date": self.start_date,
            "target_date": self.target_date,
            "progress_percentage": self.progress_percentage,
            "milestones": self.milestones,
            "monthly_revenue": self.monthly_revenue,
            "quarterly_revenue": self.quarterly_revenue
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RevenueGoal:
        return cls(
            target_amount=data.get("target_amount", 100_000_000.0),
            current_amount=data.get("current_amount", 0.0),
            start_date=data.get("start_date", "2024-01-01"),
            target_date=data.get("target_date", "2030-01-01"),
            milestones=data.get("milestones", []),
            monthly_revenue=data.get("monthly_revenue", {}),
            quarterly_revenue=data.get("quarterly_revenue", {})
        )
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress towards goal."""
        return (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0.0
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to goal."""
        return max(0, self.target_amount - self.current_amount)
    
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining to target date."""
        target = datetime.fromisoformat(self.target_date)
        now = datetime.now(timezone.UTC)
        delta = target - now
        return max(0, delta.days)
    
    @property
    def required_daily_revenue(self) -> float:
        """Calculate required daily revenue to hit goal."""
        days = self.days_remaining
        return self.remaining_amount / days if days > 0 else 0.0
    
    def add_revenue(self, amount: float) -> list[dict[str, Any]]:
        """
        Add revenue and check milestones.
        
        Returns:
            List of newly achieved milestones
        """
        self.current_amount += amount
        
        # Track monthly
        month = datetime.now(timezone.UTC).strftime("%Y-%m")
        self.monthly_revenue[month] = self.monthly_revenue.get(month, 0.0) + amount
        
        # Track quarterly
        quarter = f"{datetime.now(timezone.UTC).year}-Q{(datetime.now(timezone.UTC).month - 1) // 3 + 1}"
        self.quarterly_revenue[quarter] = self.quarterly_revenue.get(quarter, 0.0) + amount
        
        # Check milestones
        newly_achieved = []
        for milestone in self.milestones:
            if not milestone["achieved"] and self.current_amount >= milestone["amount"]:
                milestone["achieved"] = True
                milestone["achieved_at"] = datetime.now(timezone.UTC).isoformat()
                newly_achieved.append(milestone)
                logger.info(f"🎉 Milestone achieved: {milestone['name']} (${milestone['amount']:,.0f})")
        
        return newly_achieved


class RevenueTracker:
    """
    Tracks revenue generation across the agent ecosystem.
    
    Features:
    - Revenue goal tracking ($100M by 2030)
    - Client acquisition tracking
    - Revenue source attribution
    - Automated milestone detection
    """
    
    def __init__(self, store_path: Optional[Path] = None) -> None:
        self.store_path = store_path or Path.home() / ".archonx" / "revenue.json"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.goal = RevenueGoal()
        self._sources: dict[str, float] = {}  # source -> amount
        self._clients: dict[str, dict[str, Any]] = {}  # client_id -> info
        
        self._load()
    
    def _load(self) -> None:
        """Load revenue data from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.goal = RevenueGoal.from_dict(data.get("goal", {}))
                    self._sources = data.get("sources", {})
                    self._clients = data.get("clients", {})
                logger.info(f"Loaded revenue data: ${self.goal.current_amount:,.2f}")
            except Exception as e:
                logger.warning(f"Failed to load revenue data: {e}")
    
    def _save(self) -> None:
        """Save revenue data to disk."""
        data = {
            "goal": self.goal.to_dict(),
            "sources": self._sources,
            "clients": self._clients
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def record_revenue(
        self,
        amount: float,
        source: str,
        client_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """
        Record revenue generation.
        
        Args:
            amount: Revenue amount in USD
            source: Revenue source (e.g., "consulting", "saas", "api")
            client_id: Optional client ID
            agent_id: Optional agent that generated the revenue
            metadata: Additional metadata
            
        Returns:
            List of newly achieved milestones
        """
        # Track by source
        self._sources[source] = self._sources.get(source, 0.0) + amount
        
        # Track client
        if client_id:
            if client_id not in self._clients:
                self._clients[client_id] = {
                    "total_revenue": 0.0,
                    "first_transaction": datetime.now(timezone.UTC).isoformat(),
                    "transactions": []
                }
            self._clients[client_id]["total_revenue"] += amount
            self._clients[client_id]["last_transaction"] = datetime.now(timezone.UTC).isoformat()
            self._clients[client_id]["transactions"].append({
                "amount": amount,
                "source": source,
                "agent_id": agent_id,
                "timestamp": time.time()
            })
        
        # Add to goal and check milestones
        milestones = self.goal.add_revenue(amount)
        
        self._save()
        
        logger.info(f"Recorded ${amount:,.2f} from {source} (total: ${self.goal.current_amount:,.2f})")
        
        return milestones
    
    def get_stats(self) -> dict[str, Any]:
        """Get revenue statistics."""
        return {
            "goal": self.goal.to_dict(),
            "sources": self._sources,
            "total_clients": len(self._clients),
            "top_clients": sorted(
                [(k, v["total_revenue"]) for k, v in self._clients.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


class KPIDashboard:
    """
    Key Performance Indicators dashboard for ArchonX.
    
    Features:
    - Agent performance tracking
    - Task completion metrics
    - Revenue tracking for $100M goal
    - Daily/weekly/monthly reports
    - Automated reporting
    
    Output: /memory/kpis/agent_performance.json
    
    Usage:
        dashboard = KPIDashboard()
        
        # Record task completion
        dashboard.record_task(
            agent_id="synthia_queen_white",
            task_id="task-000001",
            success=True,
            duration=120.5,
            revenue=500.0
        )
        
        # Get report
        report = dashboard.generate_report()
    """
    
    def __init__(
        self,
        store_path: Optional[Path] = None,
        registry: Optional[Any] = None
    ) -> None:
        """
        Initialize KPI dashboard.
        
        Args:
            store_path: Path to store KPI data
            registry: Agent registry for metrics
        """
        self.store_path = store_path or Path("memory/kpis/agent_performance.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.registry = registry
        self.revenue_tracker = RevenueTracker()
        
        self._agent_metrics: dict[str, AgentMetrics] = {}
        self._task_history: list[dict[str, Any]] = []
        self._reports: dict[str, dict[str, Any]] = {}  # date -> report
        
        self._load()
        
        logger.info(f"KPI Dashboard initialized at {self.store_path}")

    def _load(self) -> None:
        """Load KPI data from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    for agent_id, metrics_data in data.get("agent_metrics", {}).items():
                        self._agent_metrics[agent_id] = AgentMetrics.from_dict(metrics_data)
                    
                    self._task_history = data.get("task_history", [])
                    self._reports = data.get("reports", {})
                    
            except Exception as e:
                logger.warning(f"Failed to load KPI data: {e}")

    def _save(self) -> None:
        """Save KPI data to disk."""
        data = {
            "agent_metrics": {
                agent_id: metrics.to_dict()
                for agent_id, metrics in self._agent_metrics.items()
            },
            "task_history": self._task_history[-1000:],  # Keep last 1000 tasks
            "reports": self._reports,
            "last_updated": datetime.now(timezone.UTC).isoformat()
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def initialize_agent(
        self,
        agent_id: str,
        agent_name: str,
        crew: str,
        role: str
    ) -> AgentMetrics:
        """Initialize metrics for a new agent."""
        if agent_id not in self._agent_metrics:
            self._agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_name=agent_name,
                crew=crew,
                role=role
            )
            self._save()
        return self._agent_metrics[agent_id]

    def record_task(
        self,
        agent_id: str,
        task_id: str,
        success: bool,
        duration: float,
        revenue: float = 0.0,
        client_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Record a task completion.
        
        Args:
            agent_id: Agent that completed the task
            task_id: Task ID
            success: Whether the task succeeded
            duration: Task duration in seconds
            revenue: Revenue generated (if any)
            client_id: Client ID (if applicable)
            metadata: Additional metadata
        """
        # Get or create agent metrics
        metrics = self._agent_metrics.get(agent_id)
        if not metrics:
            # Try to get from registry
            if self.registry:
                agent = self.registry.get(agent_id)
                if agent:
                    metrics = self.initialize_agent(
                        agent_id,
                        agent.name,
                        agent.crew.value,
                        agent.role.value
                    )
        
        if metrics:
            metrics.record_task_completion(success, duration, revenue, client_id)
            metrics.current_status = "idle" if success else "error"
        
        # Record in task history
        self._task_history.append({
            "task_id": task_id,
            "agent_id": agent_id,
            "success": success,
            "duration": duration,
            "revenue": revenue,
            "client_id": client_id,
            "timestamp": time.time(),
            "metadata": metadata or {}
        })
        
        # Record revenue
        if revenue > 0:
            self.revenue_tracker.record_revenue(
                amount=revenue,
                source="task_completion",
                client_id=client_id,
                agent_id=agent_id
            )
        
        self._save()
        
        logger.debug(f"Recorded task {task_id} for {agent_id}: success={success}")

    def update_agent_status(
        self,
        agent_id: str,
        status: str
    ) -> None:
        """Update an agent's current status."""
        metrics = self._agent_metrics.get(agent_id)
        if metrics:
            metrics.current_status = status
            self._save()

    def generate_report(
        self,
        period: str = "daily"
    ) -> dict[str, Any]:
        """
        Generate a KPI report.
        
        Args:
            period: Report period (daily, weekly, monthly)
            
        Returns:
            Report dictionary
        """
        now = datetime.now(timezone.UTC)
        today = now.strftime("%Y-%m-%d")
        
        # Calculate aggregate metrics
        total_tasks = sum(m.tasks_completed for m in self._agent_metrics.values())
        total_failed = sum(m.tasks_failed for m in self._agent_metrics.values())
        total_revenue = sum(m.revenue_generated for m in self._agent_metrics.values())
        
        # Top performers
        by_completed = sorted(
            self._agent_metrics.values(),
            key=lambda m: m.tasks_completed,
            reverse=True
        )[:10]
        
        by_revenue = sorted(
            self._agent_metrics.values(),
            key=lambda m: m.revenue_generated,
            reverse=True
        )[:10]
        
        by_success_rate = sorted(
            [m for m in self._agent_metrics.values() if m.tasks_completed + m.tasks_failed > 0],
            key=lambda m: m.success_rate,
            reverse=True
        )[:10]
        
        # Crew performance
        white_metrics = [m for m in self._agent_metrics.values() if m.crew == "white"]
        black_metrics = [m for m in self._agent_metrics.values() if m.crew == "black"]
        
        report = {
            "report_date": today,
            "report_period": period,
            "generated_at": now.isoformat(),
            "summary": {
                "total_agents": len(self._agent_metrics),
                "total_tasks_completed": total_tasks,
                "total_tasks_failed": total_failed,
                "overall_success_rate": total_tasks / (total_tasks + total_failed) if (total_tasks + total_failed) > 0 else 0,
                "total_revenue": total_revenue
            },
            "revenue": self.revenue_tracker.get_stats(),
            "top_performers": {
                "by_tasks_completed": [
                    {"agent_id": m.agent_id, "name": m.agent_name, "value": m.tasks_completed}
                    for m in by_completed
                ],
                "by_revenue": [
                    {"agent_id": m.agent_id, "name": m.agent_name, "value": m.revenue_generated}
                    for m in by_revenue
                ],
                "by_success_rate": [
                    {"agent_id": m.agent_id, "name": m.agent_name, "value": m.success_rate}
                    for m in by_success_rate
                ]
            },
            "crew_performance": {
                "white": {
                    "agents": len(white_metrics),
                    "tasks_completed": sum(m.tasks_completed for m in white_metrics),
                    "revenue": sum(m.revenue_generated for m in white_metrics)
                },
                "black": {
                    "agents": len(black_metrics),
                    "tasks_completed": sum(m.tasks_completed for m in black_metrics),
                    "revenue": sum(m.revenue_generated for m in black_metrics)
                }
            },
            "agent_metrics": {
                agent_id: metrics.to_dict()
                for agent_id, metrics in self._agent_metrics.items()
            }
        }
        
        # Store report
        self._reports[today] = report
        self._save()
        
        return report

    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent."""
        return self._agent_metrics.get(agent_id)

    def get_all_metrics(self) -> dict[str, AgentMetrics]:
        """Get all agent metrics."""
        return self._agent_metrics

    def get_revenue_progress(self) -> dict[str, Any]:
        """Get revenue progress towards $100M goal."""
        return self.revenue_tracker.goal.to_dict()


# Singleton instance
_dashboard: Optional[KPIDashboard] = None


def get_kpi_dashboard() -> KPIDashboard:
    """Get the singleton KPIDashboard."""
    global _dashboard
    if _dashboard is None:
        _dashboard = KPIDashboard()
    return _dashboard
