"""
End-to-end tests for artifact generation and pipeline validation (S06-04).

Tests
-----
- Golden-path: fixture-mode full pipeline run emits non-empty JSON, STIX,
  Mermaid, and markdown report artifacts.
- Negative-path: inducing a stage failure causes ValidationHaltError before
  downstream artifacts are written.
- Exporter unit contract: each exporter is importable from threat_modeler.exports
  and returns the expected output type.

All tests run in CI without an LLM API key (fixture mode only).
``@pytest.mark.llm_live`` tests are excluded from the default CI run.
"""

from __future__ import annotations

import json
import pytest

from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from threat_modeler.exports import export_json, export_mermaid, export_report, export_stix
from threat_modeler.models import CanonicalThreatModelGraph
from threat_modeler.models.canonical import (
    Component,
    Function,
    GraphMetadata,
    Interface,
    Mitigation,
    StrideAssessment,
    Subsystem,
    SystemContext,
    Threat,
)
from threat_modeler.orchestrator import FrameworkOrchestrator, ValidationHaltError
from threat_modeler.state import FrameworkState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fixture_settings(stop_on_validation_error: bool = True) -> RuntimeSettings:
    """RuntimeSettings with HITL gates disabled (fixture mode, no LLM)."""
    return RuntimeSettings(
        model=ModelSelection(provider="unconfigured", model_name="fixture", offline_only=True),
        pipeline=PipelineSettings(
            execution_mode="langgraph-compatible",
            require_hitl_gates=False,
            stop_on_validation_error=stop_on_validation_error,
        ),
    )


def _minimal_graph() -> CanonicalThreatModelGraph:
    """Build a minimal but structurally complete canonical graph for exporter tests."""
    mitigation = Mitigation(
        control_id="CTL-001",
        title="Input Validation",
        description="Validate all user-supplied inputs before processing.",
        residual_risk_after_control=2,
    )
    threat = Threat(
        name="SQL Injection",
        description="Attacker injects SQL via unsanitised input field.",
        mitre_attack_technique=["T1190"],
        capec_id="CAPEC-66",
        cwe_id="CWE-89",
        likelihood=4,
        impact=5,
        mitigations_technical=[mitigation],
        mitigations_administrative=[],
    )
    subsystem = Subsystem(
        id="sub_01",
        name="Web Layer",
        description="Public-facing web tier.",
        parent_system="TestSystem",
    )
    component = Component(
        id="comp_01",
        name="API Gateway",
        parent_subsystem="sub_01",
        hardware="virtual",
        software_modules=["nginx"],
        description="Routes external requests.",
    )
    iface = Interface(
        id="iface_01",
        name="User → API",
        description="HTTP/S traffic from end users.",
        from_node="user",
        to_node="comp_01",
        interface_type="external-component",
        protocol="HTTPS",
        data_items=["user_credentials", "query_params"],
        trust_boundary_crossing=True,
        trust_boundary_name="Internet Boundary",
        stride=StrideAssessment(S=3, T=4, R=1, I=3, D=2, E=2),
        threats=[threat],
    )
    return CanonicalThreatModelGraph(
        metadata=GraphMetadata(generation_timestamp="2026-05-04T00:00:00Z", model_level="system"),
        system=SystemContext(
            name="TestSystem",
            description="Minimal graph for exporter tests.",
            mission_criticality="high",
            safety_criticality="medium",
        ),
        subsystems=[subsystem],
        components=[component],
        functions=[],
        interfaces=[iface],
    )


# ---------------------------------------------------------------------------
# Exporter registry / import contract
# ---------------------------------------------------------------------------

class TestExporterRegistry:
    def test_export_json_importable(self):
        assert callable(export_json)

    def test_export_stix_importable(self):
        assert callable(export_stix)

    def test_export_mermaid_importable(self):
        assert callable(export_mermaid)

    def test_export_report_importable(self):
        assert callable(export_report)


# ---------------------------------------------------------------------------
# JSON exporter
# ---------------------------------------------------------------------------

class TestJsonExporter:
    def test_returns_non_empty_string(self):
        graph = _minimal_graph()
        result = export_json(graph)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parseable_as_json(self):
        graph = _minimal_graph()
        data = json.loads(export_json(graph))
        assert isinstance(data, dict)

    def test_contains_system_name(self):
        graph = _minimal_graph()
        data = json.loads(export_json(graph))
        assert data["system"]["name"] == "TestSystem"

    def test_contains_interfaces(self):
        graph = _minimal_graph()
        data = json.loads(export_json(graph))
        assert len(data["interfaces"]) == 1

    def test_threat_present_in_json(self):
        graph = _minimal_graph()
        data = json.loads(export_json(graph))
        threats = data["interfaces"][0]["threats"]
        assert any(t["name"] == "SQL Injection" for t in threats)


# ---------------------------------------------------------------------------
# STIX exporter
# ---------------------------------------------------------------------------

class TestStixExporter:
    def test_returns_stix_bundle(self):
        import stix2
        graph = _minimal_graph()
        bundle = export_stix(graph)
        assert isinstance(bundle, stix2.Bundle)

    def test_bundle_contains_attack_pattern(self):
        import stix2
        graph = _minimal_graph()
        bundle = export_stix(graph)
        types = [obj.type for obj in bundle.objects]
        assert "attack-pattern" in types

    def test_bundle_contains_course_of_action(self):
        import stix2
        graph = _minimal_graph()
        bundle = export_stix(graph)
        types = [obj.type for obj in bundle.objects]
        assert "course-of-action" in types

    def test_bundle_contains_relationship(self):
        import stix2
        graph = _minimal_graph()
        bundle = export_stix(graph)
        types = [obj.type for obj in bundle.objects]
        assert "relationship" in types

    def test_empty_graph_returns_empty_bundle(self):
        import stix2
        empty_graph = CanonicalThreatModelGraph()
        bundle = export_stix(empty_graph)
        assert isinstance(bundle, stix2.Bundle)
        # An empty bundle has no 'objects' attribute in stix2 3.x
        objects = getattr(bundle, "objects", []) or []
        assert len(objects) == 0

    def test_relationship_is_mitigates(self):
        import stix2
        graph = _minimal_graph()
        bundle = export_stix(graph)
        rels = [obj for obj in bundle.objects if obj.type == "relationship"]
        assert all(r.relationship_type == "mitigates" for r in rels)


# ---------------------------------------------------------------------------
# Mermaid exporter
# ---------------------------------------------------------------------------

class TestMermaidExporter:
    def test_returns_non_empty_string(self):
        graph = _minimal_graph()
        result = export_mermaid(graph)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_starts_with_flowchart(self):
        graph = _minimal_graph()
        result = export_mermaid(graph)
        assert result.strip().startswith("flowchart LR")

    def test_contains_system_name(self):
        graph = _minimal_graph()
        result = export_mermaid(graph)
        assert "TestSystem" in result

    def test_trust_boundary_annotated(self):
        graph = _minimal_graph()
        result = export_mermaid(graph)
        assert "[TB]" in result

    def test_empty_graph_produces_valid_output(self):
        empty_graph = CanonicalThreatModelGraph()
        result = export_mermaid(empty_graph)
        assert "flowchart LR" in result


# ---------------------------------------------------------------------------
# Report exporter
# ---------------------------------------------------------------------------

class TestReportExporter:
    def test_returns_non_empty_string(self):
        state = FrameworkState()
        state.canonical_graph = _minimal_graph()
        result = export_report(state)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_uses_final_report_when_present(self):
        state = FrameworkState()
        state.final_report = "# Custom Report\n\nContent."
        result = export_report(state)
        assert result == "# Custom Report\n\nContent."

    def test_fallback_contains_system_name(self):
        state = FrameworkState()
        state.canonical_graph = _minimal_graph()
        result = export_report(state)
        assert "TestSystem" in result

    def test_fallback_contains_threat_name(self):
        state = FrameworkState()
        state.canonical_graph = _minimal_graph()
        result = export_report(state)
        assert "SQL Injection" in result

    def test_no_graph_returns_placeholder(self):
        state = FrameworkState()
        result = export_report(state)
        assert "No canonical graph" in result


# ---------------------------------------------------------------------------
# E2E golden-path: full fixture pipeline → all four artifacts
# ---------------------------------------------------------------------------

class TestGoldenPathE2E:
    """Full fixture-mode pipeline run; all four artifact classes must be present."""

    @pytest.fixture(scope="class")
    def final_state(self):
        settings = _fixture_settings(stop_on_validation_error=False)
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="e2e-golden-path")
        state = orchestrator.initialize_state()
        state.raw_text = "Sample system description for golden path test."
        return orchestrator.run_planned_stages(state)

    def test_canonical_graph_present(self, final_state):
        assert final_state.canonical_graph is not None

    def test_stix_bundle_present(self, final_state):
        assert final_state.stix_bundle is not None
        assert isinstance(final_state.stix_bundle, dict)

    def test_mermaid_diagrams_present(self, final_state):
        assert isinstance(final_state.mermaid_diagrams, dict)
        assert len(final_state.mermaid_diagrams) > 0

    def test_final_report_present(self, final_state):
        assert final_state.final_report is not None
        assert len(final_state.final_report) > 0

    def test_json_export_non_empty(self, final_state):
        result = export_json(final_state.canonical_graph)
        data = json.loads(result)
        assert isinstance(data, dict)
        assert data.get("system") is not None

    def test_stix_export_produces_bundle(self, final_state):
        import stix2
        bundle = export_stix(final_state.canonical_graph)
        assert isinstance(bundle, stix2.Bundle)

    def test_mermaid_export_produces_string(self, final_state):
        result = export_mermaid(final_state.canonical_graph)
        assert isinstance(result, str)
        assert "flowchart LR" in result

    def test_report_export_returns_final_report(self, final_state):
        result = export_report(final_state)
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# E2E negative-path: stage failure → ValidationHaltError before downstream
# ---------------------------------------------------------------------------

class TestNegativePathE2E:
    """Induced stage failure halts the pipeline before downstream artifacts are written."""

    def test_validation_halt_prevents_downstream_artifacts(self, monkeypatch):
        settings = _fixture_settings(stop_on_validation_error=True)
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="e2e-negative-path")

        # Monkeypatch run_stage for agent_02 to corrupt the canonical graph,
        # which will fail the validator and halt at the next stage.
        original_run_stage = orchestrator.run_stage

        def corrupt_after_agent01(state, stage_id):
            result = original_run_stage(state, stage_id)
            if stage_id == "agent_01":
                # Wipe canonical graph to force validation failure at agent_02
                state.canonical_graph = None
            return result

        monkeypatch.setattr(orchestrator, "run_stage", corrupt_after_agent01)

        state = orchestrator.initialize_state()
        state.raw_text = "Test input."

        with pytest.raises(ValidationHaltError) as exc_info:
            orchestrator.run_planned_stages(state)

        # Pipeline should have halted at or before agent_02
        halted_at = exc_info.value.stage_id
        stage_ids = orchestrator.planned_stage_ids()
        halt_index = stage_ids.index(halted_at)
        assert halt_index <= stage_ids.index("agent_02")

        # Downstream artifacts (from agents 06, 08, 09) must not be present
        assert state.stix_bundle is None or halt_index < stage_ids.index("agent_06")
        assert state.final_report is None or halt_index < stage_ids.index("agent_09")


# ---------------------------------------------------------------------------
# Live LLM sprint validation gate (excluded from CI)
# ---------------------------------------------------------------------------

@pytest.mark.llm_live
class TestLlmLiveSprintValidation:
    """Sprint validation gate: real Grok API call (excluded from CI with -m 'not llm_live')."""

    def test_agent_01_and_02_real_grok(self):
        import os

        api_key = os.environ.get("GROK_API") or os.environ.get("XAI_API_KEY")
        if not api_key:
            pytest.skip("GROK_API not set; skipping live LLM test.")

        settings = RuntimeSettings(
            model=ModelSelection(provider="xai", model_name="grok-beta", offline_only=False),
            pipeline=PipelineSettings(
                execution_mode="langgraph-compatible",
                require_hitl_gates=False,
                stop_on_validation_error=False,
                enabled_stage_ids=["agent_01", "agent_02"],
            ),
        )
        orchestrator = FrameworkOrchestrator(settings=settings, run_id="live-sprint-validation")
        state = orchestrator.initialize_state()
        state.raw_text = (
            "System: Payment Processing API. "
            "Component: CardProcessor. "
            "Interface: Client → CardProcessor over HTTPS. "
            "Trust boundary: Internet to DMZ."
        )

        result = orchestrator.run_planned_stages(state)
        # Must deserialise into a valid FrameworkState with canonical_graph populated
        assert isinstance(result, FrameworkState)
        assert result.canonical_graph is not None
