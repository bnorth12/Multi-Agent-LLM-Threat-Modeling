"""Workflow and execution-plan models for LangGraph-compatible orchestration."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExecutionNode:
    node_id: str
    display_name: str


@dataclass(frozen=True)
class ExecutionEdge:
    from_node_id: str
    to_node_id: str


@dataclass(frozen=True)
class LangGraphExecutionPlan:
    start_node_id: str | None
    end_node_id: str | None
    nodes: list[ExecutionNode] = field(default_factory=list)
    edges: list[ExecutionEdge] = field(default_factory=list)
