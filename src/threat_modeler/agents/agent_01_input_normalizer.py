from .base import FrameworkAgent
from ..parsing import ParserInput, ParserInterface


class Agent01InputNormalizer(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_01",
            display_name="Input Normalizer and Graph Builder",
            next_stage_id="agent_02",
        )
        self.parser = ParserInterface()

    def _apply_placeholder_behavior(self, state):
        if state.canonical_graph is None:
            payload = ParserInput(raw_text=state.raw_text, tables=state.tables)
            state.canonical_graph = self.parser.normalize(payload)
