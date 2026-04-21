"""Stage orchestration skeleton for the threat modeler framework."""

from dataclasses import dataclass

from .agents import build_default_agents
from .config import RuntimeSettings
from .hitl import HitlService
from .state import FrameworkState
from .validation import CanonicalGraphValidator


@dataclass
class StageExecutionResult:
    stage_id: str
    success: bool


class FrameworkOrchestrator:
    def __init__(
        self,
        settings: RuntimeSettings,
        *,
        validator: CanonicalGraphValidator | None = None,
        hitl_service: HitlService | None = None,
    ) -> None:
        self.settings = settings
        self.validator = validator or CanonicalGraphValidator()
        self.hitl_service = hitl_service or HitlService()
        self.agents = build_default_agents()

    def planned_stage_ids(self) -> list[str]:
        return [stage_id for stage_id in self.settings.pipeline.enabled_stage_ids if stage_id in self.agents]

    def initialize_state(self) -> FrameworkState:
        state = FrameworkState()
        stage_ids = self.planned_stage_ids()
        state.next_stage_id = stage_ids[0] if stage_ids else None
        return state

    def run_stage(self, state: FrameworkState, stage_id: str) -> StageExecutionResult:
        agent = self.agents[stage_id]
        updated_state = agent.run(state)
        state.next_stage_id = updated_state.next_stage_id
        return StageExecutionResult(stage_id=stage_id, success=True)

    def run_planned_stages(self, state: FrameworkState | None = None) -> FrameworkState:
        active_state = state or self.initialize_state()

        for index, stage_id in enumerate(self.planned_stage_ids()):
            active_state.next_stage_id = stage_id
            self.run_stage(active_state, stage_id)

            if index > 0:
                result = self.validator.validate(active_state)
                if not result.is_valid and self.settings.pipeline.stop_on_validation_error:
                    raise ValueError(result.issues[0].message)

        # TODO: Replace linear execution with LangGraph routing and checkpointing.
        return active_state
