"""Stage orchestration with LangGraph-backed execution."""

from dataclasses import dataclass
from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph as LangGraphStateGraph

from .agents import build_default_agents
from .config import RuntimeSettings
from .hitl import (
    ExportConsistencyMetrics,
    GatePausedError,
    GateRejectedError,
    HitlService,
    MergeConflictMetrics,
)
from .models import ExecutionEdge, ExecutionNode, LangGraphExecutionPlan
from .state import FrameworkState
from .validation import CanonicalGraphValidator, ValidationHaltError


# Stage IDs that always open a mandatory HITL gate after the stage completes.
_MANDATORY_POST_STAGE_GATES: dict[str, str] = {
    "agent_01": "gate_1_normalization_review",
    "agent_02": "gate_1_scope_confirmation",
    "agent_03": "gate_2_boundary_approval",
    "agent_04": "gate_3_stride_calibration",
    "agent_05": "gate_4_threat_plausibility",
    "agent_06": "gate_9_stix_packaging_review",
    "agent_07": "gate_5_mitigation_adequacy",
    "agent_08": "gate_8_diagram_review",
}


class FrameworkGraphEnvelope(TypedDict):
    active_state: FrameworkState


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
        self.agents = build_default_agents(settings)
        self._run_id = run_id
        self.hitl_service.initialise(run_id)

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _trigger_rules(self) -> dict[str, Any]:
        try:
            return self.hitl_service.load_trigger_rules().get("gates", {})
        except Exception:
            return {}

    def _open_mandatory_gate(self, gate_id: str, active_state: FrameworkState) -> None:
        snapshot = active_state.canonical_graph_dict()
        if gate_id == "gate_1_normalization_review":
            self.hitl_service.open_normalization_review_gate(
                artifact_snapshot=self._build_normalization_review_snapshot(active_state)
            )
        elif gate_id == "gate_1_scope_confirmation":
            self.hitl_service.open_scope_confirmation_gate(artifact_snapshot=snapshot)
        elif gate_id == "gate_2_boundary_approval":
            self.hitl_service.open_boundary_approval_gate(artifact_snapshot=snapshot)
        elif gate_id == "gate_3_stride_calibration":
            self.hitl_service.open_stride_calibration_gate(artifact_snapshot=snapshot)
        elif gate_id == "gate_4_threat_plausibility":
            self.hitl_service.open_threat_plausibility_gate(artifact_snapshot=snapshot)
        elif gate_id == "gate_5_mitigation_adequacy":
            self.hitl_service.open_mitigation_adequacy_gate(artifact_snapshot=snapshot)
        elif gate_id == "gate_8_diagram_review":
            self.hitl_service.open_diagram_review_gate(artifact_snapshot=snapshot)
        elif gate_id == "gate_9_stix_packaging_review":
            self.hitl_service.open_stix_packaging_review_gate(artifact_snapshot=snapshot)

    def _evaluate_conditional_gate_6(self, active_state: FrameworkState) -> None:
        rules = self._trigger_rules().get("merge_conflict_resolution", {})
        thresholds = rules.get("thresholds", {})
        enabled = bool(rules.get("enabled", True))

        metrics_d = getattr(active_state, "merge_conflict_metrics", {}) or {}
        metrics = MergeConflictMetrics(
            merge_conflict_count=self._safe_int(metrics_d.get("merge_conflict_count", 0)),
            approved_artifact_conflict_count=self._safe_int(metrics_d.get("approved_artifact_conflict_count", 0)),
            critical_field_conflict_count=self._safe_int(metrics_d.get("critical_field_conflict_count", 0)),
            conflict_severity_max=str(metrics_d.get("conflict_severity_max", "low")),
        )

        self.hitl_service.evaluate_and_open_merge_conflict_gate(
            metrics=metrics,
            artifact_snapshot=metrics_d,
            thresholds=thresholds,
            enabled=enabled,
        )

    def _evaluate_conditional_gate_7(self, active_state: FrameworkState) -> None:
        rules = self._trigger_rules().get("export_consistency", {})
        thresholds = rules.get("thresholds", {})
        enabled = bool(rules.get("enabled", True))

        metrics_d = getattr(active_state, "export_consistency_metrics", {}) or {}
        metrics = ExportConsistencyMetrics(
            canonical_stix_error_count=self._safe_int(metrics_d.get("canonical_stix_error_count", 0)),
            canonical_report_error_count=self._safe_int(metrics_d.get("canonical_report_error_count", 0)),
            diagram_reference_error_count=self._safe_int(metrics_d.get("diagram_reference_error_count", 0)),
            consistency_warning_count=self._safe_int(metrics_d.get("consistency_warning_count", 0)),
        )

        self.hitl_service.evaluate_and_open_export_consistency_gate(
            metrics=metrics,
            artifact_snapshot=metrics_d,
            thresholds=thresholds,
            enabled=enabled,
        )

    def _record_gate_pause_or_reject(self, active_state: FrameworkState, exc: Exception) -> None:
        if isinstance(exc, (GatePausedError, GateRejectedError)):
            active_state.hitl_gate_checkpoint = self.hitl_service.checkpoint_state()
            if isinstance(exc, GatePausedError):
                active_state.hitl_paused_at_gate = exc.gate_record.gate_id
            else:
                active_state.hitl_rejected_at_gate = exc.gate_record.gate_id

    def _build_input_integrity_snapshot(self, active_state: FrameworkState) -> dict[str, Any]:
        raw_text = active_state.raw_text or ""
        tables = active_state.tables or []
        table_headers: list[str] = []
        for table in tables[:3]:
            if isinstance(table, dict):
                table_headers.extend([str(k) for k in list(table.keys())[:5]])

        return {
            "input_preflight": {
                "raw_text_length": len(raw_text),
                "raw_text_preview": raw_text[:500],
                "table_count": len(tables),
                "table_headers_preview": table_headers[:12],
                "checks": {
                    "has_raw_text": len(raw_text.strip()) > 0,
                    "has_tables": len(tables) > 0,
                    "source_present": bool(raw_text.strip() or tables),
                },
            }
        }

    def _build_normalization_review_snapshot(self, active_state: FrameworkState) -> dict[str, Any]:
        graph = active_state.canonical_graph_dict()
        if not graph:
            return {
                "normalization_review": {
                    "status": "missing_canonical_graph",
                    "checks": {
                        "graph_present": False,
                        "system_name_present": False,
                    },
                }
            }

        interfaces = graph.get("interfaces", []) if isinstance(graph.get("interfaces"), list) else []
        first_interfaces = []
        for item in interfaces[:8]:
            if isinstance(item, dict):
                first_interfaces.append(
                    {
                        "id": item.get("id", ""),
                        "name": item.get("name", ""),
                        "from": item.get("from_node", ""),
                        "to": item.get("to_node", ""),
                        "protocol": item.get("protocol", ""),
                        "trust_boundary_crossing": bool(item.get("trust_boundary_crossing", False)),
                    }
                )

        system = graph.get("system", {}) if isinstance(graph.get("system"), dict) else {}
        return {
            "normalization_review": {
                "system": {
                    "name": system.get("name", ""),
                    "description": system.get("description", ""),
                    "mission_criticality": system.get("mission_criticality", ""),
                    "safety_criticality": system.get("safety_criticality", ""),
                },
                "counts": {
                    "subsystems": len(graph.get("subsystems", [])) if isinstance(graph.get("subsystems"), list) else 0,
                    "components": len(graph.get("components", [])) if isinstance(graph.get("components"), list) else 0,
                    "functions": len(graph.get("functions", [])) if isinstance(graph.get("functions"), list) else 0,
                    "interfaces": len(interfaces),
                },
                "interfaces_preview": first_interfaces,
                "checks": {
                    "graph_present": True,
                    "system_name_present": bool(system.get("name")),
                    "interface_count_nonzero": len(interfaces) > 0,
                },
            }
        }

    def _build_stage_runner(self, stage_id: str) -> Callable[[FrameworkGraphEnvelope], FrameworkGraphEnvelope]:
        def _runner(envelope: FrameworkGraphEnvelope) -> FrameworkGraphEnvelope:
            active_state = envelope["active_state"]
            active_state.next_stage_id = stage_id
            self.run_stage(active_state, stage_id)

            result = self.validator.validate(active_state)
            if not result.is_valid and self.settings.pipeline.stop_on_validation_error:
                raise ValidationHaltError(result, stage_id)

            if self.settings.pipeline.require_hitl_gates and stage_id in _MANDATORY_POST_STAGE_GATES:
                gate_id = _MANDATORY_POST_STAGE_GATES[stage_id]
                try:
                    self._open_mandatory_gate(gate_id, active_state)
                except (GatePausedError, GateRejectedError) as exc:
                    self._record_gate_pause_or_reject(active_state, exc)
                    raise

            if self.settings.pipeline.require_hitl_gates and stage_id == "agent_02":
                try:
                    self._evaluate_conditional_gate_6(active_state)
                except (GatePausedError, GateRejectedError) as exc:
                    self._record_gate_pause_or_reject(active_state, exc)
                    raise

            return {"active_state": active_state}

        return _runner

    def _run_stage_sequence_langgraph(
        self,
        active_state: FrameworkState,
        stage_ids: list[str],
    ) -> FrameworkState:
        if not stage_ids:
            return active_state

        graph = LangGraphStateGraph(FrameworkGraphEnvelope)
        for stage_id in stage_ids:
            graph.add_node(stage_id, self._build_stage_runner(stage_id))

        graph.add_edge(START, stage_ids[0])
        for index in range(len(stage_ids) - 1):
            graph.add_edge(stage_ids[index], stage_ids[index + 1])
        graph.add_edge(stage_ids[-1], END)

        app = graph.compile()
        result = app.invoke({"active_state": active_state})
        return result["active_state"]

    def resume_from_checkpoint(self, state: FrameworkState, gate_id: str) -> FrameworkState:
        """Resume execution after a gate is resolved without recomputing prior stages."""
        self.hitl_service.resume_from_checkpoint(gate_id)
        gate_record = self.hitl_service.gate_record(gate_id)
        stage_ids = self.planned_stage_ids()
        if gate_record.stage_id not in stage_ids:
            return state

        stage_index = stage_ids.index(gate_record.stage_id)
        # Gate 0 is a pre-stage review, so resuming should start at agent_01.
        start_index = stage_index if gate_id == "gate_0_input_integrity" else stage_index + 1
        active_state = self._run_stage_sequence_langgraph(state, stage_ids[start_index:])

        if self.settings.pipeline.require_hitl_gates:
            try:
                self._evaluate_conditional_gate_7(active_state)
            except (GatePausedError, GateRejectedError) as exc:
                self._record_gate_pause_or_reject(active_state, exc)
                raise

        return active_state

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
        try:
            updated_state = agent.run(state)
        except Exception as exc:
            state.record_message(stage_id, f"{agent.display_name} failed: {type(exc).__name__}: {exc}")
            raise RuntimeError(
                f"Stage {stage_id} ({agent.display_name}) failed: {type(exc).__name__}: {exc}"
            ) from exc
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

        return active_state

    def run_langgraph_compatible(self, state: FrameworkState | None = None) -> FrameworkState:
        active_state = state or self.initialize_state()
        plan = self.build_langgraph_execution_plan()

        if plan.start_node_id is None:
            return active_state

        # Gate 0: Input Integrity — explicit preflight pause before first stage.
        if self.settings.pipeline.require_hitl_gates:
            try:
                self.hitl_service.open_input_integrity_gate(
                    artifact_snapshot=self._build_input_integrity_snapshot(active_state),
                )
            except GatePausedError as exc:
                active_state.hitl_paused_at_gate = exc.gate_record.gate_id
                active_state.hitl_gate_checkpoint = self.hitl_service.checkpoint_state()
                raise

        stage_ids = [node.node_id for node in plan.nodes]
        active_state = self._run_stage_sequence_langgraph(active_state, stage_ids)

        # Conditional Gate 7 before publication / return.
        if self.settings.pipeline.require_hitl_gates:
            try:
                self._evaluate_conditional_gate_7(active_state)
            except (GatePausedError, GateRejectedError) as exc:
                self._record_gate_pause_or_reject(active_state, exc)
                raise

        return active_state
