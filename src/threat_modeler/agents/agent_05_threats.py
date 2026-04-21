from .base import FrameworkAgent


class Agent05ConcreteThreatGenerator(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_05",
            display_name="Concrete Threat Generator",
            next_stage_id="agent_06",
        )

    def _apply_placeholder_behavior(self, state):
        state.threats_generated = True
