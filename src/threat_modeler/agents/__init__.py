"""Agent registry and builder for orchestrator pipeline."""

from dataclasses import dataclass

from threat_modeler.config import RuntimeSettings
from threat_modeler.llm import OpenAiCompatibleAdapter


@dataclass
class MockAgent:
    """Minimal agent for testing validation gates (no fixture I/O)."""
    display_name: str

    def run(self, state):
        """Execute the agent (no-op for testing)."""
        return state


def _build_live_adapter(settings: RuntimeSettings):
    model = settings.model
    provider = model.provider

    model_name = model.model_name
    if provider == "xai":
        # Backward-compatible aliases retained for existing tests/configs.
        xai_aliases = {
            "grok-beta",
            "grok-3",
            "grok-3-mini",
            "grok-3-reasoning",
        }
        if model_name.strip().lower() in xai_aliases:
            model_name = "grok-4"

    # Base URLs for providers that use hosted default endpoints
    base_url_map = {
        "openai": "https://api.openai.com/v1",
        "xai": "https://api.x.ai/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }

    base_url = model.connection_url.strip() or base_url_map.get(provider, "")

    return OpenAiCompatibleAdapter(
        model=model_name,
        api_key=model.api_key,
        endpoint_mode=model.endpoint_mode,
        base_url=base_url,
        timeout_seconds=model.request_timeout_seconds,
        max_attempts=model.request_max_attempts,
    )


def build_default_agents(settings: RuntimeSettings | None = None):
    """Return a mapping of stage IDs to agent instances.

    All agents default to fixture mode (no LLM API key required).
    Pass a configured LlmAdapter to each agent constructor to use a live provider.
    """
    # Lazy imports avoid transient circular-import races during Streamlit hot reload.
    from .agent_01_input_normalizer import InputNormalizerAgent
    from .agent_02_context_builder import ContextBuilderAgent
    from .agent_03_trust_boundary_validator import TrustBoundaryValidatorAgent
    from .agent_04_stride_scorer import StrideScorer
    from .agent_05_threat_generator import ThreatGeneratorAgent
    from .agent_06_stix_packager import StixPackagerAgent
    from .agent_07_mitigation_generator import MitigationGeneratorAgent
    from .agent_08_diagram_generator import DiagramGeneratorAgent
    from .agent_09_report_writer import ReportWriterAgent

    adapter = None
    require_live_adapter = False
    if settings is not None and not settings.model.offline_only and settings.model.provider != "fixture":
        require_live_adapter = True
        adapter = _build_live_adapter(settings)

    return {
        "agent_01": InputNormalizerAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_02": ContextBuilderAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_03": TrustBoundaryValidatorAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_04": StrideScorer(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_05": ThreatGeneratorAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_06": StixPackagerAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_07": MitigationGeneratorAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_08": DiagramGeneratorAgent(adapter=adapter, require_live_adapter=require_live_adapter),
        "agent_09": ReportWriterAgent(adapter=adapter, require_live_adapter=require_live_adapter),
    }

