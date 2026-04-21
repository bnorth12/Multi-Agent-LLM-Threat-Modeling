"""Runtime configuration primitives for the framework skeleton."""

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class ModelSelection:
    provider: str
    model_name: str
    offline_only: bool = True


@dataclass(frozen=True)
class PipelineSettings:
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
            provider="unconfigured",
            model_name="placeholder",
            offline_only=True,
        )
    )
