"""Agent registry for the initial framework skeleton."""

from .agent_01_input_normalizer import Agent01InputNormalizer
from .agent_02_context_builder import Agent02HierarchicalContextBuilder
from .agent_03_trust_boundary import Agent03TrustBoundaryValidator
from .agent_04_stride import Agent04StrideScorer
from .agent_05_threats import Agent05ConcreteThreatGenerator
from .agent_06_stix import Agent06StixPackager
from .agent_07_mitigations import Agent07MitigationGenerator
from .agent_08_diagrams import Agent08DiagramGenerator
from .agent_09_report import Agent09HumanReportWriter
from .base import FrameworkAgent


def build_default_agents() -> dict[str, FrameworkAgent]:
    agents: list[FrameworkAgent] = [
        Agent01InputNormalizer(),
        Agent02HierarchicalContextBuilder(),
        Agent03TrustBoundaryValidator(),
        Agent04StrideScorer(),
        Agent05ConcreteThreatGenerator(),
        Agent06StixPackager(),
        Agent07MitigationGenerator(),
        Agent08DiagramGenerator(),
        Agent09HumanReportWriter(),
    ]
    return {agent.stage_id: agent for agent in agents}


__all__ = ["FrameworkAgent", "build_default_agents"]
