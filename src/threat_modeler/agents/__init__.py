"""Agent registry and builder for orchestrator pipeline."""

from dataclasses import dataclass

from .agent_01_input_normalizer import InputNormalizerAgent
from .agent_02_context_builder import ContextBuilderAgent
from .agent_03_trust_boundary_validator import TrustBoundaryValidatorAgent
from .agent_04_stride_scorer import StrideScorer
from .agent_05_threat_generator import ThreatGeneratorAgent
from .agent_06_stix_packager import StixPackagerAgent
from .agent_07_mitigation_generator import MitigationGeneratorAgent
from .agent_08_diagram_generator import DiagramGeneratorAgent
from .agent_09_report_writer import ReportWriterAgent


@dataclass
class MockAgent:
    """Minimal agent for testing validation gates (no fixture I/O)."""
    display_name: str

    def run(self, state):
        """Execute the agent (no-op for testing)."""
        return state


def build_default_agents():
    """Return a mapping of stage IDs to agent instances.

    All agents default to fixture mode (no LLM API key required).
    Pass a configured LlmAdapter to each agent constructor to use a live provider.
    """
    return {
        "agent_01": InputNormalizerAgent(),
        "agent_02": ContextBuilderAgent(),
        "agent_03": TrustBoundaryValidatorAgent(),
        "agent_04": StrideScorer(),
        "agent_05": ThreatGeneratorAgent(),
        "agent_06": StixPackagerAgent(),
        "agent_07": MitigationGeneratorAgent(),
        "agent_08": DiagramGeneratorAgent(),
        "agent_09": ReportWriterAgent(),
    }

