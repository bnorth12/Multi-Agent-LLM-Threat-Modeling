"""HitlService: orchestrator-facing facade for Gate Set 1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .gate_engine import (
    ExportConsistencyMetrics,
    GateEngine,
    GatePausedError,
    GateRejectedError,
    InputIntegrityMetrics,
    MergeConflictMetrics,
)
from .models import GateAction, GateStatus, HitlAuditLog, HitlGateRecord


class HitlService:
    """
    Facade used by FrameworkOrchestrator to interact with HITL gates.

    One HitlService instance corresponds to one pipeline run.
    The run_id is set on first use via ``initialise(run_id)``.
    """

    def __init__(self) -> None:
        self._engine: GateEngine | None = None

    @staticmethod
    def _default_trigger_rules_path() -> Path:
        return Path(__file__).resolve().parents[3] / "Tests" / "fixtures" / "inputs" / "hitl" / "trigger_rules_default.json"

    def load_trigger_rules(self, rules_path: str | Path | None = None) -> dict[str, Any]:
        """Load HITL trigger rules JSON.

        If no path is provided, uses the default fixture-backed trigger rules.
        """
        path = Path(rules_path) if rules_path is not None else self._default_trigger_rules_path()
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialise(self, run_id: str) -> None:
        """Bind this service to a specific run. Must be called before any gate operations."""
        self._engine = GateEngine(run_id=run_id)

    @property
    def engine(self) -> GateEngine:
        if self._engine is None:
            raise RuntimeError(
                "HitlService has not been initialised. Call initialise(run_id) first."
            )
        return self._engine

    # ------------------------------------------------------------------
    # Gate 0 — Input Integrity (HITL-009)
    # ------------------------------------------------------------------

    def evaluate_and_open_input_integrity_gate(
        self,
        metrics: InputIntegrityMetrics,
        artifact_snapshot: dict[str, Any] | None = None,
        thresholds: dict[str, Any] | None = None,
    ) -> HitlGateRecord:
        """
        Evaluate Gate 0 trigger condition.

        - If triggered: opens the gate and raises GatePausedError.
        - If not triggered: bypasses the gate silently and returns the record.
        """
        should_trigger = self.engine.evaluate_input_integrity(metrics, thresholds)
        if should_trigger:
            record = self.engine.open_gate("gate_0_input_integrity", artifact_snapshot)
            raise GatePausedError(record)
        return self.engine.bypass_gate("gate_0_input_integrity")

    # ------------------------------------------------------------------
    # Gate 1 — Scope Confirmation (HITL-001)
    # ------------------------------------------------------------------

    def open_scope_confirmation_gate(
        self, artifact_snapshot: dict[str, Any] | None = None
    ) -> HitlGateRecord:
        """Open Gate 1. Always triggers (non-conditional). Raises GatePausedError."""
        record = self.engine.open_gate("gate_1_scope_confirmation", artifact_snapshot)
        raise GatePausedError(record)

    # ------------------------------------------------------------------
    # Gate 2 — Trust Boundary Approval (HITL-002)
    # ------------------------------------------------------------------

    def open_boundary_approval_gate(
        self, artifact_snapshot: dict[str, Any] | None = None
    ) -> HitlGateRecord:
        """Open Gate 2. Always triggers (non-conditional). Raises GatePausedError."""
        record = self.engine.open_gate("gate_2_boundary_approval", artifact_snapshot)
        raise GatePausedError(record)

    # ------------------------------------------------------------------
    # Gate 3/4/5 — Mandatory post-stage gates (HITL-003/004/005)
    # ------------------------------------------------------------------

    def open_stride_calibration_gate(
        self, artifact_snapshot: dict[str, Any] | None = None
    ) -> HitlGateRecord:
        """Open Gate 3. Always triggers (non-conditional). Raises GatePausedError."""
        record = self.engine.open_gate("gate_3_stride_calibration", artifact_snapshot)
        raise GatePausedError(record)

    def open_threat_plausibility_gate(
        self, artifact_snapshot: dict[str, Any] | None = None
    ) -> HitlGateRecord:
        """Open Gate 4. Always triggers (non-conditional). Raises GatePausedError."""
        record = self.engine.open_gate("gate_4_threat_plausibility", artifact_snapshot)
        raise GatePausedError(record)

    def open_mitigation_adequacy_gate(
        self, artifact_snapshot: dict[str, Any] | None = None
    ) -> HitlGateRecord:
        """Open Gate 5. Always triggers (non-conditional). Raises GatePausedError."""
        record = self.engine.open_gate("gate_5_mitigation_adequacy", artifact_snapshot)
        raise GatePausedError(record)

    # ------------------------------------------------------------------
    # Gate 6/7 — Conditional gates
    # ------------------------------------------------------------------

    def evaluate_and_open_merge_conflict_gate(
        self,
        metrics: MergeConflictMetrics,
        artifact_snapshot: dict[str, Any] | None = None,
        thresholds: dict[str, Any] | None = None,
        *,
        enabled: bool = True,
    ) -> HitlGateRecord:
        """Evaluate Gate 6 trigger condition.

        - If disabled or not triggered: bypasses gate and returns the record.
        - If triggered: opens the gate and raises GatePausedError.
        """
        if not enabled:
            return self.engine.bypass_gate("gate_6_merge_conflict_resolution")
        should_trigger = self.engine.evaluate_merge_conflict_resolution(metrics, thresholds)
        if should_trigger:
            record = self.engine.open_gate("gate_6_merge_conflict_resolution", artifact_snapshot)
            raise GatePausedError(record)
        return self.engine.bypass_gate("gate_6_merge_conflict_resolution")

    def evaluate_and_open_export_consistency_gate(
        self,
        metrics: ExportConsistencyMetrics,
        artifact_snapshot: dict[str, Any] | None = None,
        thresholds: dict[str, Any] | None = None,
        *,
        enabled: bool = True,
    ) -> HitlGateRecord:
        """Evaluate Gate 7 trigger condition.

        - If disabled or not triggered: bypasses gate and returns the record.
        - If triggered: opens the gate and raises GatePausedError.
        """
        if not enabled:
            return self.engine.bypass_gate("gate_7_export_consistency")
        should_trigger = self.engine.evaluate_export_consistency(metrics, thresholds)
        if should_trigger:
            record = self.engine.open_gate("gate_7_export_consistency", artifact_snapshot)
            raise GatePausedError(record)
        return self.engine.bypass_gate("gate_7_export_consistency")

    # ------------------------------------------------------------------
    # Decision submission (called by analyst UI or test harness)
    # ------------------------------------------------------------------

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
        Forward a decision to the gate engine.

        Raises GateRejectedError if action is REJECT.
        Returns the updated HitlGateRecord otherwise.
        """
        return self.engine.submit_decision(
            gate_id=gate_id,
            actor=actor,
            role=role,
            action=action,
            rationale=rationale,
            edited_artifact=edited_artifact,
        )

    # ------------------------------------------------------------------
    # Resume helpers
    # ------------------------------------------------------------------

    def resume_from_checkpoint(self, gate_id: str) -> None:
        """
        Assert that the named gate is resolved before the pipeline resumes.
        Raises GatePausedError if the gate is still open or in draft.
        """
        record = self.engine.gate(gate_id)
        if record.status in (GateStatus.OPEN, GateStatus.DRAFT):
            raise GatePausedError(record)

    # ------------------------------------------------------------------
    # Audit / inspection
    # ------------------------------------------------------------------

    @property
    def audit_log(self) -> HitlAuditLog:
        return self.engine.audit_log

    def gate_record(self, gate_id: str) -> HitlGateRecord:
        return self.engine.gate(gate_id)

    def checkpoint_state(self) -> dict[str, Any]:
        return self.engine.checkpoint_state()
