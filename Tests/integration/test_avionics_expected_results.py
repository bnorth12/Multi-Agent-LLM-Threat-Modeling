"""Avionics expected-results integration tests for S08.

Covers two goals in one file:
1) Artifact expectations for a full avionics fixture pipeline run.
2) HITL gate outcomes and resume behavior with automated accept-as-is decisions.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from threat_modeler.agents.agent_01_input_normalizer import InputNormalizerAgent
from threat_modeler.agents.agent_02_context_builder import ContextBuilderAgent
from threat_modeler.agents.agent_03_trust_boundary_validator import TrustBoundaryValidatorAgent
from threat_modeler.agents.agent_04_stride_scorer import StrideScorer
from threat_modeler.agents.agent_05_threat_generator import ThreatGeneratorAgent
from threat_modeler.agents.agent_06_stix_packager import StixPackagerAgent
from threat_modeler.agents.agent_07_mitigation_generator import MitigationGeneratorAgent
from threat_modeler.agents.agent_08_diagram_generator import DiagramGeneratorAgent
from threat_modeler.agents.agent_09_report_writer import ReportWriterAgent
from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from threat_modeler.hitl import GateAction, GatePausedError, GateStatus
from threat_modeler.llm.base import FixtureAdapter
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState


_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "agents"


def _avionics_agents() -> dict[str, object]:
    return {
        "agent_01": InputNormalizerAgent(adapter=FixtureAdapter(_FIXTURES / "agent_01_avionics_output.json")),
        "agent_02": ContextBuilderAgent(adapter=FixtureAdapter(_FIXTURES / "agent_02_avionics_output.json")),
        "agent_03": TrustBoundaryValidatorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_03_avionics_output.json")),
        "agent_04": StrideScorer(adapter=FixtureAdapter(_FIXTURES / "agent_04_avionics_output.json")),
        "agent_05": ThreatGeneratorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_05_avionics_output.json")),
        "agent_06": StixPackagerAgent(adapter=FixtureAdapter(_FIXTURES / "agent_06_avionics_output.json")),
        "agent_07": MitigationGeneratorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_07_avionics_output.json")),
        "agent_08": DiagramGeneratorAgent(adapter=FixtureAdapter(_FIXTURES / "agent_08_avionics_output.txt")),
        "agent_09": ReportWriterAgent(adapter=FixtureAdapter(_FIXTURES / "agent_09_avionics_output.md")),
    }


def _settings(require_hitl_gates: bool) -> RuntimeSettings:
    return RuntimeSettings(
        model=ModelSelection(provider="fixture", model_name="fixture-placeholder", offline_only=True),
        pipeline=PipelineSettings(
            execution_mode="langgraph-compatible",
            require_hitl_gates=require_hitl_gates,
            stop_on_validation_error=True,
        ),
    )


class TestAvionicsExpectedArtifacts:
    def test_full_avionics_fixture_run_matches_expected_outputs(self):
        orchestrator = FrameworkOrchestrator(settings=_settings(require_hitl_gates=False), run_id="s08-avionics-artifacts")
        orchestrator.agents = _avionics_agents()

        state = FrameworkState(raw_text="Avionics scenario fixture run for expected-results validation.")
        result = orchestrator.run_planned_stages(state)

        assert result.canonical_graph is not None
        assert result.canonical_graph.system.name == "Avionics Data Network"
        assert len(result.canonical_graph.subsystems) == 2
        assert len(result.canonical_graph.interfaces) == 1

        interface = result.canonical_graph.interfaces[0]
        assert interface.protocol == "ACARS"
        assert interface.trust_boundary_crossing is True
        assert interface.trust_boundary_name == "Air-Ground Boundary"
        assert len(interface.threats) >= 1
        assert interface.threats[0].name == "Route Spoofing via Unauthenticated ACARS Uplink"

        assert result.stix_bundle is not None
        assert result.stix_bundle.get("type") == "bundle"
        stix_types = {obj.get("type") for obj in result.stix_bundle.get("objects", []) if isinstance(obj, dict)}
        assert "attack-pattern" in stix_types
        assert "course-of-action" in stix_types

        assert set(result.mermaid_diagrams.keys()) >= {"level_0", "level_1", "level_2"}
        assert result.final_report is not None
        assert "Executive Summary" in result.final_report
        assert "Route Spoofing via Unauthenticated ACARS Uplink" in result.final_report


class TestAvionicsHitlGateOutcomes:
    def test_avionics_run_pauses_and_resumes_through_mandatory_gates(self):
        orchestrator = FrameworkOrchestrator(settings=_settings(require_hitl_gates=True), run_id="s08-avionics-gates")
        orchestrator.agents = _avionics_agents()

        state = FrameworkState(raw_text="Avionics scenario with HITL gates enabled.")

        with pytest.raises(GatePausedError) as first_pause:
            orchestrator.run_planned_stages(state)

        assert first_pause.value.gate_record.gate_id == "gate_0_input_integrity"

        gate_sequence = [
            "gate_0_input_integrity",
            "gate_1_normalization_review",
            "gate_1_scope_confirmation",
            "gate_2_boundary_approval",
            "gate_3_stride_calibration",
            "gate_4_threat_plausibility",
            "gate_9_stix_packaging_review",
            "gate_5_mitigation_adequacy",
            "gate_8_diagram_review",
        ]

        paused_gate = first_pause.value.gate_record.gate_id

        for index, gate_id in enumerate(gate_sequence):
            assert paused_gate == gate_id

            orchestrator.hitl_service.submit_decision(
                gate_id=gate_id,
                actor="s08_reviewer",
                role="Reviewer",
                action=GateAction.ACCEPT_AS_IS,
                rationale=f"Approve {gate_id} for avionics expected-results baseline.",
            )

            try:
                state = orchestrator.resume_from_checkpoint(state, gate_id)
                paused_gate = None
            except GatePausedError as pause:
                paused_gate = pause.gate_record.gate_id
                if index == len(gate_sequence) - 1:
                    pytest.fail(f"Unexpected pause after final mandatory gate: {paused_gate}")

        assert paused_gate is None
        assert state.final_report is not None
        assert "Avionics Data Network" in state.final_report

        for gate_id in gate_sequence:
            assert orchestrator.hitl_service.gate_record(gate_id).status == GateStatus.ACCEPTED_AS_IS

        decided_gate_ids = {entry.gate_id for entry in orchestrator.hitl_service.audit_log.entries}
        assert decided_gate_ids == set(gate_sequence)
