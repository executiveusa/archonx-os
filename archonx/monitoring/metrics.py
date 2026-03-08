import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class SwarmMetrics:
    """
    Real-time telemetry aggregator for the ArchonX Agent Swarm.
    Phase 5: Monitoring & Observability implementation.
    """
    
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    start_time: float = field(default_factory=time.time)
    
    # Sliding window for velocity (tasks per hour)
    task_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Token savings tracking (bridged from jcodemunch)
    tokens_saved: int = 0
    cost_avoided: float = 0.0

    def record_task(self, success: bool, tokens: int = 0, cost: float = 0.0):
        self.total_tasks += 1
        if success:
            self.completed_tasks += 1
        else:
            self.failed_tasks += 1
        
        self.task_history.append((time.time(), success))
        self.tokens_saved += tokens
        self.cost_avoided += cost

    def get_summary(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        success_rate = (self.completed_tasks / self.total_tasks * 100) if self.total_tasks > 0 else 0
        
        return {
            "uptime_seconds": int(uptime),
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": round(success_rate, 2),
            "tokens_saved": self.tokens_saved,
            "cost_avoided": round(self.cost_avoided, 2),
            "velocity_last_hour": self._calculate_velocity(3600)
        }

    def _calculate_velocity(self, window_seconds: int) -> int:
        now = time.time()
        cutoff = now - window_seconds
        return sum(1 for ts, _ in self.task_history if ts > cutoff)

# Global metrics singleton
metrics = SwarmMetrics()
