from .base import FrameworkAgent
from ..models import build_placeholder_graph


class Agent01InputNormalizer(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_01",
            display_name="Input Normalizer and Graph Builder",
            next_stage_id="agent_02",
        )

    def _apply_placeholder_behavior(self, state):
        if state.canonical_graph is None:
            state.canonical_graph = build_placeholder_graph()
