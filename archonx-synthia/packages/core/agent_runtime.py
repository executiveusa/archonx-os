"""Agent runtime — planner/executor loop for GLM-5 function calling.

This module implements the core agent loop:
1. Fetch tasks from Notion (brain)
2. Rank and pick next task
3. Decide execution strategy (Orgo / Docker / reasoning)
4. Execute with budget enforcement (steps, tool calls, time)
5. Log every step to Notion Runs DB
6. Gate irreversible actions through approval flow
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    KILLED = "killed"
    DONE = "done"
    FAILED = "failed"


class ExecutionStrategy(str, Enum):
    REASONING = "reasoning"  # Pure LLM reasoning — no tools
    CODE_RUNNER = "code_runner"  # Docker sandbox
    COMPUTER_USE = "computer_use"  # Orgo browser/UI automation
    HYBRID = "hybrid"  # Mix of above


@dataclass
class Budget:
    max_steps: int = 40
    max_tool_calls: int = 80
    max_runtime_seconds: int = 1800
    steps_used: int = 0
    tool_calls_used: int = 0
    started_at: float = field(default_factory=time.time)

    @property
    def exhausted(self) -> bool:
        elapsed = time.time() - self.started_at
        return (
            self.steps_used >= self.max_steps
            or self.tool_calls_used >= self.max_tool_calls
            or elapsed >= self.max_runtime_seconds
        )


@dataclass
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error: str | None = None
    trace_id: str = ""
    redactions: list[str] = field(default_factory=list)


@dataclass
class AgentState:
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "synthia"
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: str | None = None
    computer_id: str | None = None
    run_id: str | None = None
    budget: Budget = field(default_factory=Budget)
    tools_allowed: list[str] = field(default_factory=list)
    log: list[dict] = field(default_factory=list)


async def run_agent_loop(state: AgentState, *, connectors: dict) -> AgentState:
    """Main agent execution loop. STUB — full implementation in P3.

    Flow:
    1. While budget not exhausted and status == RUNNING:
       a. Ask GLM-5 for next action (function call)
       b. Validate tool is in allowlist
       c. Check if action requires approval → gate
       d. Execute tool
       e. Log step to Notion Runs DB
       f. Feed result back to GLM-5
    2. On completion → update task status, destroy Orgo computer
    """
    state.status = AgentStatus.RUNNING
    state.run_id = str(uuid.uuid4())

    # STUB: P3 will implement the full loop with:
    # - connectors["glm5"].chat_with_tools()
    # - connectors["notion"].append_run_log()
    # - connectors["orgo"].screenshot() / .input()
    # - connectors["runner"].exec()
    # - policy.check_allowlist() / policy.request_approval()

    state.status = AgentStatus.DONE
    return state
