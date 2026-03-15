"""Canonical intent-to-graph specification for Archon-X."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from archonx.orchestration.dispatch import DispatchDecision


@dataclass
class IntentGraphNode:
    """Executable or editable node in an Archon intent graph."""

    node_id: str
    node_type: str
    label: str
    config: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IntentGraphEdge:
    """Directed edge between graph nodes."""

    from_node: str
    to_node: str
    edge_type: str
    condition: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IntentGraphSpec:
    """Human-editable and runtime-ready graph blueprint."""

    graph_id: str
    intent: str
    source: str
    objective: str
    nodes: list[IntentGraphNode] = field(default_factory=list)
    edges: list[IntentGraphEdge] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "intent": self.intent,
            "source": self.source,
            "objective": self.objective,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }


def build_intent_graph_from_dispatch(
    decision: DispatchDecision,
    source: str = "archonx-os",
) -> IntentGraphSpec:
    """Compile a dispatch decision into a canonical graph spec."""

    nodes = [
        IntentGraphNode(
            node_id="intent",
            node_type="intent_input",
            label="Intent Input",
            config={"task_name": decision.plan.task_name, "team_id": decision.plan.team_id},
        ),
        IntentGraphNode(
            node_id="planner",
            node_type="planner",
            label="Archon Planner",
            config={"requested_by": decision.envelope.requested_by},
        ),
        IntentGraphNode(
            node_id="policy",
            node_type="policy_gate",
            label="Integration Policy",
            config=decision.policy,
        ),
        IntentGraphNode(
            node_id="env",
            node_type="env_gate",
            label="Environment Readiness",
            config=decision.env_audit,
        ),
        IntentGraphNode(
            node_id="worker",
            node_type="worker",
            label=decision.primary_worker.id,
            config={
                "role": decision.primary_worker.role,
                "tools": decision.primary_worker.tools,
                "dependencies": decision.primary_worker.dependencies,
            },
        ),
        IntentGraphNode(
            node_id="result",
            node_type="result_schema",
            label="Result Schema",
            config=decision.envelope.result_schema,
        ),
    ]

    edges = [
        IntentGraphEdge("intent", "planner", "control_flow"),
        IntentGraphEdge("planner", "policy", "control_flow"),
        IntentGraphEdge("policy", "env", "control_flow"),
        IntentGraphEdge("env", "worker", "control_flow", condition="env_ready"),
        IntentGraphEdge("worker", "result", "message_flow"),
    ]

    metadata = {
        "required_integrations": [
            integration.id for integration in decision.required_integrations
        ],
        "required_env_categories": decision.required_env_categories,
        "trace_id": decision.envelope.trace_id,
        "approval_integrations": decision.policy.get("approval_integrations", []),
        "editable": True,
        "runtime_ready": True,
    }

    return IntentGraphSpec(
        graph_id=decision.envelope.trace_id or f"graph:{decision.plan.task_name}",
        intent=decision.plan.task_intent,
        source=source,
        objective=decision.envelope.objective,
        nodes=nodes,
        edges=edges,
        metadata=metadata,
    )
