"""Agent registry and builder for orchestrator pipeline."""

from dataclasses import dataclass


@dataclass
class MockAgent:
    """Minimal agent for testing validation gates."""
    display_name: str

    def run(self, state):
        """Execute the agent (no-op for testing)."""
        return state


def build_default_agents():
    """Return a mapping of stage IDs to agent instances (mock for now)."""
    return {
        "agent_01": MockAgent(display_name="Input Normalizer"),
        "agent_02": MockAgent(display_name="Context Builder"),
        "agent_03": MockAgent(display_name="Trust Boundary Validator"),
        "agent_04": MockAgent(display_name="STRIDE Scorer"),
    }

