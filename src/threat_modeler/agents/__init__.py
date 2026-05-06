"""Agent registry and builder for orchestrator pipeline."""

from dataclasses import dataclass

from threat_modeler.config import RuntimeSettings
from threat_modeler.llm import OpenAiCompatibleAdapter

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


def _build_live_adapter(settings: RuntimeSettings):
    model = settings.model
    provider = model.provider

    model_name = model.model_name
    if provider == "xai" and model_name.strip().lower() == "grok-beta":
        # Backward-compatible alias retained for existing tests/configs.
        model_name = "grok-3-mini"

    env_map = {
        "openai": ("OPENAI_API_KEY",),
        "anthropic": ("ANTHROPIC_API_KEY",),
        "xai": ("GROK_API", "XAI_API_KEY"),
        "azure": ("AZURE_OPENAI_API_KEY",),
        "custom": ("CUSTOM_API_KEY", f"{provider.upper()}_API_KEY"),
        "ollama": ("OLLAMA_API_KEY",),
    }

    # Base URLs for providers that use hosted default endpoints
    base_url_map = {
        "openai": "https://api.openai.com/v1",
        "xai": "https://api.x.ai/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }

    base_url = model.connection_url.strip() or base_url_map.get(provider, "")
    api_key_candidates = env_map.get(provider, (f"{provider.upper()}_API_KEY",))

    return OpenAiCompatibleAdapter(
        model=model_name,
        endpoint_mode=model.endpoint_mode,
        base_url=base_url,
        api_key_env_candidates=api_key_candidates,
    )


def build_default_agents(settings: RuntimeSettings | None = None):
    """Return a mapping of stage IDs to agent instances.

    All agents default to fixture mode (no LLM API key required).
    Pass a configured LlmAdapter to each agent constructor to use a live provider.
    """
    adapter = None
    if settings is not None and not settings.model.offline_only and settings.model.provider != "fixture":
        adapter = _build_live_adapter(settings)

    return {
        "agent_01": InputNormalizerAgent(adapter=adapter),
        "agent_02": ContextBuilderAgent(adapter=adapter),
        "agent_03": TrustBoundaryValidatorAgent(adapter=adapter),
        "agent_04": StrideScorer(adapter=adapter),
        "agent_05": ThreatGeneratorAgent(adapter=adapter),
        "agent_06": StixPackagerAgent(adapter=adapter),
        "agent_07": MitigationGeneratorAgent(adapter=adapter),
        "agent_08": DiagramGeneratorAgent(adapter=adapter),
        "agent_09": ReportWriterAgent(adapter=adapter),
    }

