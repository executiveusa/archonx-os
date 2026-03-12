"""
ArchonX Orchestration Module
============================
Agent swarm deployment and coordination.
"""

from archonx.orchestration.swarm import (
    Agent,
    AgentRole,
    CrewType,
    SwarmOrchestrator,
    WaveResult,
    create_swarm,
    deploy_yolo_swarm,
)
from archonx.orchestration.contracts import TaskEnvelope
from archonx.orchestration.workers import (
    WorkerCapability,
    WorkerKind,
    WorkerRegistry,
    build_default_worker_registry,
)

__all__ = [
    "Agent",
    "AgentRole",
    "CrewType",
    "SwarmOrchestrator",
    "WaveResult",
    "create_swarm",
    "deploy_yolo_swarm",
    "TaskEnvelope",
    "WorkerCapability",
    "WorkerKind",
    "WorkerRegistry",
    "build_default_worker_registry",
]
