from __future__ import annotations

import pytest

from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState
from threat_modeler.validation import ValidationHaltError


class TestFrameworkOrchestratorLangGraphCoverage:
    def test_build_langgraph_execution_plan_respects_enabled_stages(self) -> None:
        settings = RuntimeSettings(
            model=ModelSelection(provider="test", model_name="mock", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="langgraph-compatible",
                enabled_stage_ids=("agent_01", "agent_03"),
                require_hitl_gates=False,
            ),
        )
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="unit-plan")

        plan = orchestrator.build_langgraph_execution_plan()

        assert plan.start_node_id == "agent_01"
        assert plan.end_node_id == "agent_03"
        assert [node.node_id for node in plan.nodes] == ["agent_01", "agent_03"]
        assert len(plan.edges) == 1
        assert plan.edges[0].from_node_id == "agent_01"
        assert plan.edges[0].to_node_id == "agent_03"

    def test_run_planned_stages_dispatches_to_langgraph_mode(self, monkeypatch) -> None:
        settings = RuntimeSettings(
            model=ModelSelection(provider="test", model_name="mock", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="langgraph-compatible",
                require_hitl_gates=False,
            ),
        )
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="unit-dispatch")
        called = {"langgraph": False}

        def _fake_run_langgraph(self, state=None):
            called["langgraph"] = True
            return state or self.initialize_state()

        monkeypatch.setattr(FrameworkOrchestrator, "run_langgraph_compatible", _fake_run_langgraph)

        _ = orchestrator.run_planned_stages()

        assert called["langgraph"] is True

    def test_linear_mode_halts_on_validation_failure(self, monkeypatch) -> None:
        settings = RuntimeSettings(
            model=ModelSelection(provider="test", model_name="mock", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="linear",
                enabled_stage_ids=("agent_01", "agent_02"),
                stop_on_validation_error=True,
                require_hitl_gates=False,
            ),
        )
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="unit-linear-halt")

        def _fake_run_stage(self, state, stage_id):
            # Keep canonical_graph unset to force validation failure at stage boundary.
            return None

        monkeypatch.setattr(FrameworkOrchestrator, "run_stage", _fake_run_stage)

        with pytest.raises(ValidationHaltError) as exc_info:
            orchestrator.run_planned_stages(FrameworkState(raw_text="unit"))

        assert exc_info.value.stage_id == "agent_02"

    def test_resume_from_checkpoint_runs_only_remaining_stages(self, monkeypatch) -> None:
        settings = RuntimeSettings(
            model=ModelSelection(provider="test", model_name="mock", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="langgraph-compatible",
                enabled_stage_ids=("agent_01", "agent_02", "agent_03", "agent_04"),
                require_hitl_gates=False,
            ),
        )
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="unit-resume")
        captured: dict[str, list[str]] = {}

        class _GateRecord:
            stage_id = "agent_02"

        monkeypatch.setattr(orchestrator.hitl_service, "resume_from_checkpoint", lambda gate_id: None)
        monkeypatch.setattr(orchestrator.hitl_service, "gate_record", lambda gate_id: _GateRecord())

        def _fake_run_stage_sequence(active_state, stage_ids):
            captured["stage_ids"] = list(stage_ids)
            return active_state

        monkeypatch.setattr(orchestrator, "_run_stage_sequence_langgraph", _fake_run_stage_sequence)

        state = FrameworkState(raw_text="resume")
        resumed = orchestrator.resume_from_checkpoint(state, "gate_1_scope_confirmation")

        assert resumed is state
        assert captured["stage_ids"] == ["agent_03", "agent_04"]
