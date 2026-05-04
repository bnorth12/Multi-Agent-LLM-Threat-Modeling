"""Gate engine: trigger evaluation and gate pause/resume logic for Gate Set 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import GateAction, GateStatus, HitlAuditLog, HitlDecision, HitlGateRecord


class GateRejectedError(Exception):
    """Raised when an analyst submits a REJECT decision at a gate."""

    def __init__(self, gate_record: HitlGateRecord) -> None:
        self.gate_record = gate_record
        super().__init__(
            f"Pipeline rejected at gate '{gate_record.gate_id}' "
            f"by '{gate_record.decision.actor}': {gate_record.decision.rationale}"
        )


class GatePausedError(Exception):
    """Raised when the pipeline hits an open gate with no decision yet."""

    def __init__(self, gate_record: HitlGateRecord) -> None:
        self.gate_record = gate_record
        super().__init__(
            f"Pipeline paused at gate '{gate_record.gate_id}' ({gate_record.gate_name}). "
            "Submit a decision to continue."
        )


@dataclass
class InputIntegrityMetrics:
    """Metrics evaluated by Gate 0 (Input Integrity, HITL-009)."""
    parse_error_count: int = 0
    required_field_missing_count: int = 0
    schema_validation_pass_rate: float = 1.0
    source_provenance_complete: bool = True

    def should_trigger(
        self,
        parse_error_count_gt: int = 0,
        required_field_missing_count_gt: int = 0,
        schema_validation_pass_rate_lt: float = 1.0,
        source_provenance_complete_required: bool = True,
    ) -> bool:
        if self.parse_error_count > parse_error_count_gt:
            return True
        if self.required_field_missing_count > required_field_missing_count_gt:
            return True
        if self.schema_validation_pass_rate < schema_validation_pass_rate_lt:
            return True
        if source_provenance_complete_required and not self.source_provenance_complete:
            return True
        return False


@dataclass
class GateEngine:
    """
    Manages the lifecycle of Gate Set 1 gates.

    Gate Set 1:
      gate_0_input_integrity    — before context merge (HITL-009)
      gate_1_scope_confirmation — after context merge (HITL-001)
      gate_2_boundary_approval  — after trust boundary validation (HITL-002)
    """

    run_id: str
    audit_log: HitlAuditLog = field(init=False)
    _gates: dict[str, HitlGateRecord] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.audit_log = HitlAuditLog(run_id=self.run_id)
        self._gates = {
            "gate_0_input_integrity": HitlGateRecord(
                gate_id="gate_0_input_integrity",
                gate_name="Input Integrity Gate",
                stage_id="agent_01",
            ),
            "gate_1_scope_confirmation": HitlGateRecord(
                gate_id="gate_1_scope_confirmation",
                gate_name="Scope Confirmation Gate",
                stage_id="agent_02",
            ),
            "gate_2_boundary_approval": HitlGateRecord(
                gate_id="gate_2_boundary_approval",
                gate_name="Trust Boundary Approval Gate",
                stage_id="agent_03",
            ),
        }

    # ------------------------------------------------------------------
    # Gate access
    # ------------------------------------------------------------------

    def gate(self, gate_id: str) -> HitlGateRecord:
        if gate_id not in self._gates:
            raise KeyError(f"Unknown gate id: '{gate_id}'")
        return self._gates[gate_id]

    def all_gates(self) -> list[HitlGateRecord]:
        return list(self._gates.values())

    # ------------------------------------------------------------------
    # Trigger evaluation
    # ------------------------------------------------------------------

    def evaluate_input_integrity(
        self,
        metrics: InputIntegrityMetrics,
        thresholds: dict[str, Any] | None = None,
    ) -> bool:
        """Return True if Gate 0 should trigger (pipeline should pause)."""
        t = thresholds or {}
        return metrics.should_trigger(
            parse_error_count_gt=t.get("parse_error_count_gt", 0),
            required_field_missing_count_gt=t.get("required_field_missing_count_gt", 0),
            schema_validation_pass_rate_lt=t.get("schema_validation_pass_rate_lt", 1.0),
            source_provenance_complete_required=t.get("source_provenance_complete_required", True),
        )

    # ------------------------------------------------------------------
    # Gate lifecycle
    # ------------------------------------------------------------------

    def open_gate(self, gate_id: str, artifact_snapshot: dict[str, Any] | None = None) -> HitlGateRecord:
        """Mark a gate as OPEN (pipeline paused). Returns the gate record."""
        record = self.gate(gate_id)
        record.open(artifact_snapshot=artifact_snapshot)
        return record

    def bypass_gate(self, gate_id: str) -> HitlGateRecord:
        """Mark a conditional gate as BYPASSED (trigger condition not met)."""
        record = self.gate(gate_id)
        record.status = GateStatus.BYPASSED
        return record

    def submit_decision(
        self,
        gate_id: str,
        actor: str,
        role: str,
        action: GateAction,
        rationale: str,
        edited_artifact: dict[str, Any] | None = None,
    ) -> HitlGateRecord:
        """
        Submit an analyst decision to a gate.

        - SAVE_DRAFT: persists edits, status → DRAFT, does NOT raise.
        - ACCEPT_AS_IS / ACCEPT_CHANGES: status → resolved, appends to audit log.
        - REJECT: status → REJECTED, appends to audit log, raises GateRejectedError.
        """
        record = self.gate(gate_id)

        if action == GateAction.SAVE_DRAFT:
            record.save_draft(draft=edited_artifact or {})
            return record

        # For accept/reject, rationale is mandatory
        if not rationale.strip():
            raise ValueError(
                f"Rationale is required for action '{action.value}' at gate '{gate_id}'."
            )

        diff: dict[str, Any] | None = None
        if action == GateAction.ACCEPT_CHANGES and edited_artifact is not None:
            diff = _compute_diff(record.artifact_snapshot or {}, edited_artifact)

        decision = HitlDecision(
            gate_id=gate_id,
            actor=actor,
            role=role,
            action=action,
            rationale=rationale,
            artifact_diff=diff,
        )
        record.apply_decision(decision)
        self.audit_log.record(decision)

        if record.is_rejected:
            raise GateRejectedError(record)

        return record

    # ------------------------------------------------------------------
    # Checkpoint / resume helpers
    # ------------------------------------------------------------------

    def first_open_or_draft_gate(self) -> HitlGateRecord | None:
        """Return the earliest gate still awaiting a final decision."""
        for record in self._gates.values():
            if record.status in (GateStatus.OPEN, GateStatus.DRAFT):
                return record
        return None

    def pending_gate_for_stage(self, stage_id: str) -> HitlGateRecord | None:
        """Return the gate guarding a stage if it is OPEN or DRAFT."""
        for record in self._gates.values():
            if record.stage_id == stage_id and record.status in (GateStatus.OPEN, GateStatus.DRAFT):
                return record
        return None

    def checkpoint_state(self) -> dict[str, Any]:
        """Serialisable snapshot of all gate states for run checkpointing."""
        return {
            "run_id": self.run_id,
            "gates": {gid: g.to_dict() for gid, g in self._gates.items()},
            "audit_log": self.audit_log.to_dict(),
        }


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _compute_diff(original: dict[str, Any], edited: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow diff of changed keys between original and edited."""
    diff: dict[str, Any] = {}
    all_keys = set(original) | set(edited)
    for key in all_keys:
        orig_val = original.get(key)
        edit_val = edited.get(key)
        if orig_val != edit_val:
            diff[key] = {"before": orig_val, "after": edit_val}
    return diff
