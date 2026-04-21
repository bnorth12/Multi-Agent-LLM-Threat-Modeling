from .base import FrameworkAgent


class Agent09HumanReportWriter(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_09",
            display_name="Human Report Writer",
            next_stage_id=None,
        )
