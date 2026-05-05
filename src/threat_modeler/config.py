"""Runtime configuration primitives for the framework skeleton."""

from dataclasses import dataclass, field
from typing import Sequence


# Provider enumeration for model selection UI
PROVIDER_MATRIX = {
    "fixture": {
        "label": "Local/Fixture",
        "description": "No LLM calls; uses deterministic fixture data",
        "requires_url": False,
        "requires_api_key": False,
        "default_model": "fixture-placeholder",
    },
    "openai": {
        "label": "OpenAI",
        "description": "OpenAI API (GPT-4, GPT-3.5)",
        "requires_url": False,
        "requires_api_key": True,
        "default_model": "gpt-4",
    },
    "anthropic": {
        "label": "Anthropic",
        "description": "Anthropic Claude API",
        "requires_url": False,
        "requires_api_key": True,
        "default_model": "claude-3-sonnet",
    },
    "xai": {
        "label": "xAI/Grok",
        "description": "xAI Grok API",
        "requires_url": False,
        "requires_api_key": True,
        "default_model": "grok-3-mini",
    },
    "azure": {
        "label": "Azure OpenAI",
        "description": "Azure OpenAI service",
        "requires_url": True,
        "requires_api_key": True,
        "default_model": "gpt-4",
    },
    "ollama": {
        "label": "Ollama",
        "description": "Local Ollama instance",
        "requires_url": True,
        "requires_api_key": False,
        "default_model": "llama2",
    },
    "custom": {
        "label": "Custom/Intranet",
        "description": "Self-hosted OpenAI-compatible endpoint",
        "requires_url": True,
        "requires_api_key": True,
        "default_model": "custom-model",
    },
}


@dataclass(frozen=True)
class ModelSelection:
    provider: str
    model_name: str
    offline_only: bool = True
    connection_url: str = ""  # For Azure, Ollama, Custom/Intranet providers


@dataclass(frozen=True)
class PipelineSettings:
    execution_mode: str = "linear"
    enabled_stage_ids: Sequence[str] = field(
        default_factory=lambda: (
            "agent_01",
            "agent_02",
            "agent_03",
            "agent_04",
            "agent_05",
            "agent_06",
            "agent_07",
            "agent_08",
            "agent_09",
        )
    )
    stop_on_validation_error: bool = True
    require_hitl_gates: bool = True


@dataclass(frozen=True)
class RuntimeSettings:
    model: ModelSelection
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)


def build_default_settings() -> RuntimeSettings:
    return RuntimeSettings(
        model=ModelSelection(
            provider="fixture",
            model_name="fixture-placeholder",
            offline_only=True,
            connection_url="",
        )
    )
