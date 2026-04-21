from .base import FrameworkAgent


class Agent08DiagramGenerator(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_08",
            display_name="Diagram Generator",
            next_stage_id="agent_09",
        )
