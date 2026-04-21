from .base import FrameworkAgent


class Agent07MitigationGenerator(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_07",
            display_name="Mitigation Generator",
            next_stage_id="agent_08",
        )
