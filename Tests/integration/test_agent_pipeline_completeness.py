"""Tests for S06-01: Agent Pipeline Completeness.

Covers:
- build_default_agents() returns all 9 stage IDs (AC: registry completeness)
- LLM adapter: FixtureAdapter reads fixture and returns content
- LLM adapter: XaiAdapter raises EnvironmentError without API key
- Each agent runs in fixture mode and produces expected state changes
- Contract validation passes at every stage transition in the full fixture run
- A stage that produces invalid state causes ValidationHaltError before the next stage
- Fixture mode / LLM mode selected solely by adapter configuration
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.threat_modeler.agents import build_default_agents, MockAgent
from src.threat_modeler.agents.base import BaseAgent
from src.threat_modeler.agents.deserialise import parse_graph_json
from src.threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from src.threat_modeler.llm.base import FixtureAdapter
from src.threat_modeler.llm.xai_adapter import XaiAdapter
from src.threat_modeler.models.canonical import CanonicalThreatModelGraph
from src.threat_modeler.orchestrator import FrameworkOrchestrator
from src.threat_modeler.state import FrameworkState
from src.threat_modeler.validation import ValidationHaltError

_FIXTURES = Path(__file__).parent.parent / "fixtures" / "agents"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestAgentRegistry:
    def test_all_nine_stages_registered(self):
        agents = build_default_agents()
        expected = {f"agent_0{i}" if i < 10 else f"agent_{i}" for i in range(1, 10)}
        assert set(agents.keys()) == expected

    def test_all_agents_have_run_method(self):
        for stage_id, agent in build_default_agents().items():
            assert callable(getattr(agent, "run", None)), f"{stage_id} missing run()"

    def test_all_agents_have_display_name(self):
        for stage_id, agent in build_default_agents().items():
            assert agent.display_name, f"{stage_id} missing display_name"


# ---------------------------------------------------------------------------
# LLM Adapters
# ---------------------------------------------------------------------------

class TestFixtureAdapter:
    def test_returns_fixture_contents(self, tmp_path):
        f = tmp_path / "out.json"
        f.write_text('{"hello": "world"}', encoding="utf-8")
        adapter = FixtureAdapter(f)
        result = adapter.complete("sys", "user")
        assert result == '{"hello": "world"}'

    def test_raises_if_fixture_missing(self, tmp_path):
        adapter = FixtureAdapter(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError):
            adapter.complete("sys", "user")


class TestXaiAdapter:
    def test_raises_without_api_key(self, monkeypatch):
        monkeypatch.delenv("GROK_API", raising=False)
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        adapter = XaiAdapter()
        with pytest.raises(EnvironmentError, match="GROK_API"):
            adapter.complete("sys", "user")


class TestPromptBudgeting:
    def test_base_agent_message_not_truncated_for_small_payload(self, monkeypatch):
        monkeypatch.setenv("THREAT_MODELER_MAX_USER_MESSAGE_CHARS", "5000")
        state = FrameworkState(raw_text="short input", tables=[])
        agent = BaseAgent(display_name="Test Agent", stage_id="agent_test")
        msg = agent._build_user_message(state)
        payload = json.loads(msg)
        assert payload["raw_text"] == "short input"
        assert "truncated" not in payload

    def test_base_agent_message_unbounded_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("THREAT_MODELER_MAX_USER_MESSAGE_CHARS", raising=False)
        state = FrameworkState(raw_text="short input", tables=[])
        agent = BaseAgent(display_name="Test Agent", stage_id="agent_test")
        msg = agent._build_user_message(state)
        payload = json.loads(msg)
        assert payload["raw_text"] == "short input"
        assert "truncated" not in payload

    def test_base_agent_message_truncated_for_large_payload(self, monkeypatch):
        monkeypatch.setenv("THREAT_MODELER_MAX_USER_MESSAGE_CHARS", "1200")
        state = FrameworkState()
        text = (_FIXTURES / "agent_01_output.json").read_text(encoding="utf-8")
        state.canonical_graph = parse_graph_json(text)
        assert state.canonical_graph is not None
        # Inflate payload to force prompt budget logic.
        state.canonical_graph.interfaces = state.canonical_graph.interfaces * 250

        agent = BaseAgent(display_name="Test Agent", stage_id="agent_test")
        msg = agent._build_user_message(state)
        parsed = json.loads(msg)

        assert len(msg) <= 1200
        assert parsed.get("truncated") is True
        assert "payload" in parsed


# ---------------------------------------------------------------------------
# Deserialiser
# ---------------------------------------------------------------------------

class TestParseGraphJson:
    def test_parses_fixture_01(self):
        text = (_FIXTURES / "agent_01_output.json").read_text(encoding="utf-8")
        graph = parse_graph_json(text)
        assert isinstance(graph, CanonicalThreatModelGraph)
        assert graph.system.name == "Multi-Agent LLM Threat Modeler"
        assert len(graph.interfaces) == 4

    def test_parses_avionics_fixture(self):
        """Avionics dataset retained as a compact quick-test fixture."""
        text = (_FIXTURES / "agent_01_avionics_output.json").read_text(encoding="utf-8")
        graph = parse_graph_json(text)
        assert isinstance(graph, CanonicalThreatModelGraph)
        assert graph.system.name == "Avionics Data Network"
        assert len(graph.interfaces) == 1

    def test_returns_none_for_invalid_json(self):
        assert parse_graph_json("not json at all") is None

    def test_strips_markdown_fences(self):
        text = (_FIXTURES / "agent_01_output.json").read_text(encoding="utf-8")
        fenced = f"```json\n{text}\n```"
        graph = parse_graph_json(fenced)
        assert graph is not None


# ---------------------------------------------------------------------------
# Individual agents — fixture mode
# ---------------------------------------------------------------------------

class TestAgentFixtureRuns:
    """Each agent runs against its fixture file and produces expected state changes."""

    def _state_with_graph(self) -> FrameworkState:
        state = FrameworkState()
        text = (_FIXTURES / "agent_01_output.json").read_text(encoding="utf-8")
        state.canonical_graph = parse_graph_json(text)
        return state

    def test_agent_01_sets_canonical_graph(self):
        from src.threat_modeler.agents.agent_01_input_normalizer import InputNormalizerAgent
        state = FrameworkState(raw_text="Sample avionics system description.")
        agent = InputNormalizerAgent()
        result = agent.run(state)
        assert isinstance(result.canonical_graph, CanonicalThreatModelGraph)

    def test_agent_02_sets_canonical_graph(self):
        from src.threat_modeler.agents.agent_02_context_builder import ContextBuilderAgent
        state = self._state_with_graph()
        agent = ContextBuilderAgent()
        result = agent.run(state)
        assert isinstance(result.canonical_graph, CanonicalThreatModelGraph)

    def test_agent_03_sets_canonical_graph(self):
        from src.threat_modeler.agents.agent_03_trust_boundary_validator import TrustBoundaryValidatorAgent
        state = self._state_with_graph()
        agent = TrustBoundaryValidatorAgent()
        result = agent.run(state)
        assert isinstance(result.canonical_graph, CanonicalThreatModelGraph)

    def test_agent_04_sets_stride_complete(self):
        from src.threat_modeler.agents.agent_04_stride_scorer import StrideScorer
        state = self._state_with_graph()
        agent = StrideScorer()
        result = agent.run(state)
        assert result.stride_complete is True

    def test_agent_05_sets_threats_generated(self):
        from src.threat_modeler.agents.agent_05_threat_generator import ThreatGeneratorAgent
        state = self._state_with_graph()
        agent = ThreatGeneratorAgent()
        result = agent.run(state)
        assert result.threats_generated is True
        assert len(result.canonical_graph.interfaces[0].threats) > 0

    def test_agent_06_sets_stix_bundle(self):
        from src.threat_modeler.agents.agent_06_stix_packager import StixPackagerAgent
        state = self._state_with_graph()
        agent = StixPackagerAgent()
        result = agent.run(state)
        assert isinstance(result.stix_bundle, dict)
        assert result.stix_bundle.get("type") == "bundle"

    def test_agent_07_maps_mitigations(self):
        from src.threat_modeler.agents.agent_07_mitigation_generator import MitigationGeneratorAgent
        state = self._state_with_graph()
        agent = MitigationGeneratorAgent()
        result = agent.run(state)
        threat = result.canonical_graph.interfaces[0].threats
        assert len(threat) > 0
        assert len(threat[0].mitigations_technical) > 0

    def test_agent_08_sets_mermaid_diagrams(self):
        from src.threat_modeler.agents.agent_08_diagram_generator import DiagramGeneratorAgent
        state = self._state_with_graph()
        agent = DiagramGeneratorAgent()
        result = agent.run(state)
        assert "level_0" in result.mermaid_diagrams
        assert "level_1" in result.mermaid_diagrams
        assert "level_2" in result.mermaid_diagrams

    def test_agent_09_sets_final_report(self):
        from src.threat_modeler.agents.agent_09_report_writer import ReportWriterAgent
        state = self._state_with_graph()
        agent = ReportWriterAgent()
        result = agent.run(state)
        assert result.final_report is not None
        assert "Executive Summary" in result.final_report


# ---------------------------------------------------------------------------
# Golden-path fixture run — all 9 stages
# ---------------------------------------------------------------------------

class TestGoldenPathFixtureRun:
    def _build_orchestrator(self) -> FrameworkOrchestrator:
        settings = RuntimeSettings(
            model=ModelSelection(provider="unconfigured", model_name="fixture", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="langgraph-compatible",
                require_hitl_gates=False,
            ),
        )
        return FrameworkOrchestrator(settings=settings, run_id="test-golden-path")

    def test_all_nine_stages_execute(self):
        orch = self._build_orchestrator()
        state = FrameworkState(raw_text="Sample avionics input.")
        result = orch.run_planned_stages(state)
        # All 9 stages should have posted a message
        stage_ids = {m["stage_id"] for m in result.messages}
        for i in range(1, 10):
            sid = f"agent_0{i}" if i < 10 else f"agent_{i}"
            assert sid in stage_ids, f"{sid} did not execute"

    def test_canonical_graph_non_empty_after_run(self):
        orch = self._build_orchestrator()
        state = FrameworkState(raw_text="Sample avionics input.")
        result = orch.run_planned_stages(state)
        assert result.canonical_graph is not None
        assert result.canonical_graph.system.name != ""

    def test_stix_bundle_present_after_run(self):
        orch = self._build_orchestrator()
        state = FrameworkState(raw_text="Sample avionics input.")
        result = orch.run_planned_stages(state)
        assert result.stix_bundle is not None

    def test_mermaid_diagrams_present_after_run(self):
        orch = self._build_orchestrator()
        state = FrameworkState(raw_text="Sample avionics input.")
        result = orch.run_planned_stages(state)
        assert result.mermaid_diagrams

    def test_final_report_present_after_run(self):
        orch = self._build_orchestrator()
        state = FrameworkState(raw_text="Sample avionics input.")
        result = orch.run_planned_stages(state)
        assert result.final_report is not None


# ---------------------------------------------------------------------------
# Contract validation at stage boundaries
# ---------------------------------------------------------------------------

class TestContractValidationAtBoundaries:
    def test_validation_runs_at_each_transition(self):
        """Orchestrator should not raise for valid fixture output at each stage."""
        settings = RuntimeSettings(
            model=ModelSelection(provider="unconfigured", model_name="fixture", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="linear",
                require_hitl_gates=False,
                stop_on_validation_error=True,
            ),
        )
        orch = FrameworkOrchestrator(settings=settings, run_id="test-contract")
        # Agent_01 fixture run produces a valid canonical graph; no halt expected
        state = FrameworkState(raw_text="Sample input.")
        result = orch.run_planned_stages(state)
        assert result.canonical_graph is not None

    def test_invalid_stage_output_halts_pipeline(self):
        """An agent that clears canonical_graph to None triggers ValidationHaltError."""
        from src.threat_modeler.agents.base import BaseAgent
        from src.threat_modeler.llm.base import LlmAdapter

        class _BadAdapter(LlmAdapter):
            def complete(self, system_prompt, user_message):
                return "NOT JSON"

        from src.threat_modeler.agents.agent_02_context_builder import ContextBuilderAgent
        bad_agent = ContextBuilderAgent(adapter=_BadAdapter())

        settings = RuntimeSettings(
            model=ModelSelection(provider="unconfigured", model_name="fixture", offline_only=True),
            pipeline=PipelineSettings(
                execution_mode="linear",
                enabled_stage_ids=["agent_01", "agent_02"],
                require_hitl_gates=False,
                stop_on_validation_error=True,
            ),
        )
        orch = FrameworkOrchestrator(settings=settings, run_id="test-halt")
        # Replace agent_02 with the bad one
        orch.agents["agent_02"] = bad_agent

        # agent_01 sets graph; agent_02 returns bad JSON → graph stays as agent_01 set it
        # To force a halt, use an agent that explicitly nulls the graph
        class _NullGraphAgent:
            display_name = "NullGraph"
            def run(self, state):
                state.canonical_graph = None
                return state

        orch.agents["agent_02"] = _NullGraphAgent()
        state = FrameworkState(raw_text="Sample input.")
        with pytest.raises(ValidationHaltError):
            orch.run_planned_stages(state)
