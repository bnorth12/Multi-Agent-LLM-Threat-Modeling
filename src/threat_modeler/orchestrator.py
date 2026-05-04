"""Stage orchestration and compatibility state graph utilities."""

from typing import Any, Dict, Callable, List

class StateGraph:
    """
    Represents the LangGraph-style state graph for agent orchestration.
    Nodes are agent stages; edges are explicit transitions.
    """
    def __init__(self):
        self.nodes: Dict[str, Callable[[Any], Any]] = {}
        self.edges: Dict[str, List[str]] = {}
        self.checkpoints: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}

    def add_node(self, name: str, func: Callable[[Any], Any]):
        self.nodes[name] = func
        if name not in self.edges:
            self.edges[name] = []

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

    def set_checkpoint(self, node: str, state: Any):
        self.checkpoints[node] = state

    def get_checkpoint(self, node: str) -> Any:
        return self.checkpoints.get(node)

    def run(self, start_node: str, initial_state: Any):
        current_node = start_node
        self.state = initial_state
        while current_node:
            func = self.nodes[current_node]
            self.state = func(self.state)
            self.set_checkpoint(current_node, self.state)
            next_nodes = self.edges.get(current_node, [])
            current_node = next_nodes[0] if next_nodes else None
        return self.state

# Example agent stub functions (to be replaced with real agent logic)
def agent_01_input_normalizer(state):
    # ... normalize input ...
    return state

def agent_02_context_builder(state):
    # ... build context ...
    return state

# ... more agent stubs ...

def build_default_state_graph():
    sg = StateGraph()
    sg.add_node("input_normalizer", agent_01_input_normalizer)
    sg.add_node("context_builder", agent_02_context_builder)
    sg.add_edge("input_normalizer", "context_builder")
    # ... add more nodes and edges ...
    return sg

from dataclasses import dataclass

from .agents import build_default_agents
from .config import RuntimeSettings
from .hitl import GatePausedError, GateRejectedError, HitlService, InputIntegrityMetrics
from .models import ExecutionEdge, ExecutionNode, LangGraphExecutionPlan
from .state import FrameworkState
from .validation import CanonicalGraphValidator, ValidationHaltError

# Stage IDs that always open a mandatory HITL gate after the stage completes.
_MANDATORY_POST_STAGE_GATES: dict[str, str] = {
    "agent_02": "gate_1_scope_confirmation",
    "agent_03": "gate_2_boundary_approval",
}


@dataclass
class StageExecutionResult:
    stage_id: str
    success: bool


class FrameworkOrchestrator:
    def __init__(
        self,
        settings: RuntimeSettings,
        *,
        validator: CanonicalGraphValidator | None = None,
        hitl_service: HitlService | None = None,
        run_id: str = "run-default",
    ) -> None:
        self.settings = settings
        self.validator = validator or CanonicalGraphValidator()
        self.hitl_service = hitl_service or HitlService()
        self.agents = build_default_agents()
        self._run_id = run_id
        self.hitl_service.initialise(run_id)

    def planned_stage_ids(self) -> list[str]:
        return [stage_id for stage_id in self.settings.pipeline.enabled_stage_ids if stage_id in self.agents]

    def initialize_state(self) -> FrameworkState:
        state = FrameworkState()
        stage_ids = self.planned_stage_ids()
        state.next_stage_id = stage_ids[0] if stage_ids else None
        return state

    def build_langgraph_execution_plan(self) -> LangGraphExecutionPlan:
        stage_ids = self.planned_stage_ids()
        nodes = [ExecutionNode(node_id=stage_id, display_name=self.agents[stage_id].display_name) for stage_id in stage_ids]
        edges = [
            ExecutionEdge(from_node_id=stage_ids[index], to_node_id=stage_ids[index + 1])
            for index in range(len(stage_ids) - 1)
        ]
        return LangGraphExecutionPlan(
            start_node_id=stage_ids[0] if stage_ids else None,
            end_node_id=stage_ids[-1] if stage_ids else None,
            nodes=nodes,
            edges=edges,
        )

    def run_stage(self, state: FrameworkState, stage_id: str) -> StageExecutionResult:
        agent = self.agents[stage_id]
        updated_state = agent.run(state)
        state.next_stage_id = updated_state.next_stage_id
        return StageExecutionResult(stage_id=stage_id, success=True)

    def run_planned_stages(self, state: FrameworkState | None = None) -> FrameworkState:
        if self.settings.pipeline.execution_mode == "langgraph-compatible":
            return self.run_langgraph_compatible(state)

        active_state = state or self.initialize_state()

        for index, stage_id in enumerate(self.planned_stage_ids()):
            active_state.next_stage_id = stage_id
            self.run_stage(active_state, stage_id)

            if index > 0:
                result = self.validator.validate(active_state)
                if not result.is_valid and self.settings.pipeline.stop_on_validation_error:
                    raise ValidationHaltError(result, stage_id)

        # TODO: Replace linear execution with LangGraph routing and checkpointing.
        return active_state

    def run_langgraph_compatible(self, state: FrameworkState | None = None) -> FrameworkState:
        active_state = state or self.initialize_state()
        plan = self.build_langgraph_execution_plan()

        if plan.start_node_id is None:
            return active_state

        # Gate 0: Input Integrity — evaluated before first stage executes.
        if self.settings.pipeline.require_hitl_gates:
            metrics = InputIntegrityMetrics(
                parse_error_count=len(active_state.tables) == 0 and active_state.raw_text == "",
                source_provenance_complete=bool(active_state.tables or active_state.raw_text),
            )
            try:
                self.hitl_service.evaluate_and_open_input_integrity_gate(
                    metrics=metrics,
                    artifact_snapshot={"raw_text_length": len(active_state.raw_text),
                                       "table_count": len(active_state.tables)},
                )
            except GatePausedError as exc:
                active_state.hitl_paused_at_gate = exc.gate_record.gate_id
                active_state.hitl_gate_checkpoint = self.hitl_service.checkpoint_state()
                raise

        current_stage_id = plan.start_node_id
        edge_lookup = {edge.from_node_id: edge.to_node_id for edge in plan.edges}

        while current_stage_id is not None:
            active_state.next_stage_id = current_stage_id
            self.run_stage(active_state, current_stage_id)

            result = self.validator.validate(active_state)
            if not result.is_valid and self.settings.pipeline.stop_on_validation_error:
                raise ValidationHaltError(result, current_stage_id)

            # Mandatory HITL gates after specific stages.
            if self.settings.pipeline.require_hitl_gates and current_stage_id in _MANDATORY_POST_STAGE_GATES:
                gate_id = _MANDATORY_POST_STAGE_GATES[current_stage_id]
                try:
                    if gate_id == "gate_1_scope_confirmation":
                        self.hitl_service.open_scope_confirmation_gate(
                            artifact_snapshot=active_state.canonical_graph_dict()
                        )
                    elif gate_id == "gate_2_boundary_approval":
                        self.hitl_service.open_boundary_approval_gate(
                            artifact_snapshot=active_state.canonical_graph_dict()
                        )
                except GatePausedError as exc:
                    active_state.hitl_paused_at_gate = exc.gate_record.gate_id
                    active_state.hitl_gate_checkpoint = self.hitl_service.checkpoint_state()
                    raise
                except GateRejectedError as exc:
                    active_state.hitl_rejected_at_gate = exc.gate_record.gate_id
                    active_state.hitl_gate_checkpoint = self.hitl_service.checkpoint_state()
                    raise

            current_stage_id = edge_lookup.get(current_stage_id)

        # TODO: Replace this compatibility layer with a real LangGraph StateGraph.
        return active_state
