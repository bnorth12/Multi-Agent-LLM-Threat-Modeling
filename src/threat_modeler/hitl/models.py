"""HITL data model: gate records, decisions, and audit log."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GateStatus(str, Enum):
    """Lifecycle state of a single gate instance."""
    PENDING = "pending"       # not yet reached
    OPEN = "open"             # pipeline paused, awaiting analyst decision
    DRAFT = "draft"           # analyst has saved edits but not submitted
    ACCEPTED_AS_IS = "accepted_as_is"    # pipeline advanced with original artifact
    ACCEPTED_CHANGES = "accepted_changes"  # pipeline advanced with edited artifact
    REJECTED = "rejected"     # pipeline halted by analyst rejection
    BYPASSED = "bypassed"     # conditional gate whose trigger condition was not met


class GateAction(str, Enum):
    ACCEPT_AS_IS = "accept_as_is"
    ACCEPT_CHANGES = "accept_changes"
    REJECT = "reject"
    SAVE_DRAFT = "save_draft"


@dataclass
class HitlDecision:
    """A single analyst decision submitted at a gate."""
    gate_id: str
    actor: str
    role: str
    action: GateAction
    rationale: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    artifact_diff: dict[str, Any] | None = None  # populated when action == ACCEPT_CHANGES

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "actor": self.actor,
            "role": self.role,
            "action": self.action.value,
            "rationale": self.rationale,
            "timestamp": self.timestamp.isoformat(),
            "artifact_diff": self.artifact_diff,
        }


@dataclass
class HitlGateRecord:
    """Persistent record for one gate instance in a run."""
    gate_id: str
    gate_name: str
    stage_id: str               # pipeline stage this gate guards
    status: GateStatus = GateStatus.PENDING
    artifact_snapshot: dict[str, Any] | None = None   # artifact at time gate opened
    draft_artifact: dict[str, Any] | None = None       # analyst in-progress edits
    decision: HitlDecision | None = None

    def open(self, artifact_snapshot: dict[str, Any] | None = None) -> None:
        self.status = GateStatus.OPEN
        self.artifact_snapshot = artifact_snapshot

    def save_draft(self, draft: dict[str, Any]) -> None:
        self.status = GateStatus.DRAFT
        self.draft_artifact = draft

    def apply_decision(self, decision: HitlDecision) -> None:
        self.decision = decision
        if decision.action == GateAction.SAVE_DRAFT:
            self.status = GateStatus.DRAFT
        elif decision.action == GateAction.ACCEPT_AS_IS:
            self.status = GateStatus.ACCEPTED_AS_IS
        elif decision.action == GateAction.ACCEPT_CHANGES:
            self.status = GateStatus.ACCEPTED_CHANGES
        elif decision.action == GateAction.REJECT:
            self.status = GateStatus.REJECTED

    @property
    def is_resolved(self) -> bool:
        return self.status in (
            GateStatus.ACCEPTED_AS_IS,
            GateStatus.ACCEPTED_CHANGES,
            GateStatus.BYPASSED,
        )

    @property
    def is_rejected(self) -> bool:
        return self.status == GateStatus.REJECTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "gate_name": self.gate_name,
            "stage_id": self.stage_id,
            "status": self.status.value,
            "artifact_snapshot": self.artifact_snapshot,
            "draft_artifact": self.draft_artifact,
            "decision": self.decision.to_dict() if self.decision else None,
        }


@dataclass
class HitlAuditLog:
    """Ordered, append-only record of all gate decisions for a run."""
    run_id: str
    entries: list[HitlDecision] = field(default_factory=list)

    def record(self, decision: HitlDecision) -> None:
        """Append a decision. Existing entries are never modified (immutable audit trail)."""
        self.entries.append(decision)

    def decisions_for_gate(self, gate_id: str) -> list[HitlDecision]:
        return [e for e in self.entries if e.gate_id == gate_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "entries": [e.to_dict() for e in self.entries],
        }
