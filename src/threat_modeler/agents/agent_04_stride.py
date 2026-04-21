from .base import FrameworkAgent


class Agent04StrideScorer(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_04",
            display_name="STRIDE Scorer",
            next_stage_id="agent_05",
        )

    def _apply_placeholder_behavior(self, state):
        state.stride_complete = True
