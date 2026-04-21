from .base import FrameworkAgent


class Agent06StixPackager(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_06",
            display_name="STIX Packager",
            next_stage_id="agent_07",
        )
