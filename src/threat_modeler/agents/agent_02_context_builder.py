from .base import FrameworkAgent


class Agent02HierarchicalContextBuilder(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_02",
            display_name="Hierarchical Context Builder",
            next_stage_id="agent_03",
        )
