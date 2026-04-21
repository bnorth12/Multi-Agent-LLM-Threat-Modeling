"""Shared base class for staged agent placeholders."""

from dataclasses import dataclass

from ..state import FrameworkState


@dataclass
class FrameworkAgent:
    stage_id: str
    display_name: str
    next_stage_id: str | None

    def run(self, state: FrameworkState) -> FrameworkState:
        state.record_message(self.stage_id, f"{self.display_name} placeholder executed.")
        state.next_stage_id = self.next_stage_id
        self._apply_placeholder_behavior(state)
        return state

    def _apply_placeholder_behavior(self, state: FrameworkState) -> None:
        # TODO: Replace placeholder stage behavior with real runtime logic.
        return None
