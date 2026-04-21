from .base import FrameworkAgent


class Agent03TrustBoundaryValidator(FrameworkAgent):
    def __init__(self) -> None:
        super().__init__(
            stage_id="agent_03",
            display_name="Trust Boundary Validator",
            next_stage_id="agent_04",
        )

    def _apply_placeholder_behavior(self, state):
        state.trust_boundary_review_needed = True
