from .base import FrameworkAgent


class Agent01InputNormalizer(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_01",
            display_name="Input Normalizer and Graph Builder",
            next_stage_id="agent_02",
        )

    def _apply_placeholder_behavior(self, state):
        if not state.canonical_graph:
            state.canonical_graph = {"metadata": {"status": "placeholder"}, "data_flows": []}
