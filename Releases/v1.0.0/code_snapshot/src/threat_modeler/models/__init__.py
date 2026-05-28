"""
Stub execution plan and node/edge dataclasses for orchestrator compatibility.
"""
from dataclasses import dataclass
from typing import List
from .canonical import CanonicalThreatModelGraph

@dataclass
class ExecutionNode:
    node_id: str
    display_name: str

@dataclass
class ExecutionEdge:
    from_node_id: str
    to_node_id: str

@dataclass
class LangGraphExecutionPlan:
    start_node_id: str
    end_node_id: str
    nodes: List[ExecutionNode]
    edges: List[ExecutionEdge]
