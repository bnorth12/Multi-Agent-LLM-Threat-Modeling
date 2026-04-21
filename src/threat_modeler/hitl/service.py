"""HITL scaffolding for approval and override gates."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HitlDecision:
    action: str
    rationale: str
    actor: str
    role: str


class HitlService:
    def requires_review(self, stage_id: str) -> bool:
        return stage_id in {"agent_03", "agent_04", "agent_05", "agent_07", "agent_09"}

    def record_decision(self, decision: HitlDecision) -> dict[str, str]:
        # TODO: Persist signed gate decisions and audit diffs in a durable store.
        return {
            "action": decision.action,
            "actor": decision.actor,
            "role": decision.role,
        }
