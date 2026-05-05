"""Integration tests for S06-02 HITL Gate Set 2.

Covers:
- Mandatory gates 3/4/5 open at their mapped stages.
- Conditional gates 6/7 trigger based on thresholded metrics.
- Gate actions (accept-as-is, accept-changes, save-draft, reject) semantics.
- Audit records include actor, timestamp, rationale, and diff for edited decisions.
- Selective resume skips prior approved stages.
"""

from __future__ import annotations

import pytest

from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings
from threat_modeler.hitl import (
    ExportConsistencyMetrics,
    GateAction,
    GatePausedError,
    GateRejectedError,
    GateStatus,
    HitlService,
    MergeConflictMetrics,
)
from threat_modeler.hitl.gate_engine import GateEngine
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.state import FrameworkState


ANALYST = {"actor": "analyst_2", "role": "Reviewer"}


def _make_service(run_id: str = "run-s06-02") -> HitlService:
    svc = HitlService()
    svc.initialise(run_id)
    return svc


def _make_engine(run_id: str = "run-s06-02") -> GateEngine:
    return GateEngine(run_id=run_id)


def _settings(require_hitl_gates: bool = True, stop_on_validation_error: bool = True) -> RuntimeSettings:
    return RuntimeSettings(
        model=ModelSelection(provider="unconfigured", model_name="fixture", offline_only=True),
        pipeline=PipelineSettings(
            execution_mode="langgraph-compatible",
            require_hitl_gates=require_hitl_gates,
            stop_on_validation_error=stop_on_validation_error,
        ),
    )


class TestMandatoryGateSet2:
    def test_gate_3_always_pauses(self):
        svc = _make_service()
        with pytest.raises(GatePausedError) as exc_info:
            svc.open_stride_calibration_gate(artifact_snapshot={"stride": "scored"})
        assert exc_info.value.gate_record.gate_id == "gate_3_stride_calibration"
        assert exc_info.value.gate_record.status == GateStatus.OPEN

    def test_gate_4_always_pauses(self):
        svc = _make_service()
        with pytest.raises(GatePausedError) as exc_info:
            svc.open_threat_plausibility_gate(artifact_snapshot={"threat_count": 3})
        assert exc_info.value.gate_record.gate_id == "gate_4_threat_plausibility"
        assert exc_info.value.gate_record.status == GateStatus.OPEN

    def test_gate_5_always_pauses(self):
        svc = _make_service()
        with pytest.raises(GatePausedError) as exc_info:
            svc.open_mitigation_adequacy_gate(artifact_snapshot={"mitigation_count": 6})
        assert exc_info.value.gate_record.gate_id == "gate_5_mitigation_adequacy"
        assert exc_info.value.gate_record.status == GateStatus.OPEN


class TestConditionalGateSet2:
    def test_gate_6_bypassed_on_clean_merge(self):
        svc = _make_service()
        metrics = MergeConflictMetrics(
            merge_conflict_count=0,
            approved_artifact_conflict_count=0,
            critical_field_conflict_count=0,
            conflict_severity_max="low",
        )
        record = svc.evaluate_and_open_merge_conflict_gate(
            metrics=metrics,
            enabled=True,
            thresholds={
                "merge_conflict_count_gte": 5,
                "approved_artifact_conflict_count_gte": 1,
                "critical_field_conflict_count_gte": 1,
                "conflict_severity_max_gte": "high",
            },
        )
        assert record.gate_id == "gate_6_merge_conflict_resolution"
        assert record.status == GateStatus.BYPASSED

    def test_gate_6_opens_when_conflict_threshold_exceeded(self):
        svc = _make_service()
        metrics = MergeConflictMetrics(
            merge_conflict_count=5,
            approved_artifact_conflict_count=1,
            critical_field_conflict_count=0,
            conflict_severity_max="medium",
        )
        with pytest.raises(GatePausedError) as exc_info:
            svc.evaluate_and_open_merge_conflict_gate(
                metrics=metrics,
                enabled=True,
                thresholds={
                    "merge_conflict_count_gte": 5,
                    "approved_artifact_conflict_count_gte": 1,
                    "critical_field_conflict_count_gte": 1,
                    "conflict_severity_max_gte": "high",
                },
                artifact_snapshot={"merge_conflict_count": 5},
            )
        assert exc_info.value.gate_record.gate_id == "gate_6_merge_conflict_resolution"
        assert exc_info.value.gate_record.status == GateStatus.OPEN

    def test_gate_7_bypassed_when_consistent(self):
        svc = _make_service()
        metrics = ExportConsistencyMetrics(
            canonical_stix_error_count=0,
            canonical_report_error_count=0,
            diagram_reference_error_count=0,
            consistency_warning_count=2,
        )
        record = svc.evaluate_and_open_export_consistency_gate(
            metrics=metrics,
            enabled=True,
            thresholds={
                "canonical_stix_error_count_gt": 0,
                "canonical_report_error_count_gt": 0,
                "diagram_reference_error_count_gt": 0,
                "consistency_warning_count_gt": 10,
            },
        )
        assert record.gate_id == "gate_7_export_consistency"
        assert record.status == GateStatus.BYPASSED

    def test_gate_7_opens_when_consistency_errors_present(self):
        svc = _make_service()
        metrics = ExportConsistencyMetrics(
            canonical_stix_error_count=1,
            canonical_report_error_count=0,
            diagram_reference_error_count=0,
            consistency_warning_count=0,
        )
        with pytest.raises(GatePausedError) as exc_info:
            svc.evaluate_and_open_export_consistency_gate(
                metrics=metrics,
                enabled=True,
                thresholds={
                    "canonical_stix_error_count_gt": 0,
                    "canonical_report_error_count_gt": 0,
                    "diagram_reference_error_count_gt": 0,
                    "consistency_warning_count_gt": 10,
                },
                artifact_snapshot={"canonical_stix_error_count": 1},
            )
        assert exc_info.value.gate_record.gate_id == "gate_7_export_consistency"
        assert exc_info.value.gate_record.status == GateStatus.OPEN


class TestGateActionsAndAudit:
    def test_save_draft_does_not_advance_or_audit(self):
        engine = _make_engine()
        engine.open_gate("gate_4_threat_plausibility", artifact_snapshot={"threat_count": 3})
        record = engine.submit_decision(
            gate_id="gate_4_threat_plausibility",
            **ANALYST,
            action=GateAction.SAVE_DRAFT,
            rationale="",
            edited_artifact={"threat_count": 4},
        )
        assert record.status == GateStatus.DRAFT
        assert record.draft_artifact == {"threat_count": 4}
        assert len(engine.audit_log.entries) == 0

    def test_accept_as_is_advances(self):
        engine = _make_engine()
        engine.open_gate("gate_3_stride_calibration", artifact_snapshot={"S": 3})
        record = engine.submit_decision(
            gate_id="gate_3_stride_calibration",
            **ANALYST,
            action=GateAction.ACCEPT_AS_IS,
            rationale="STRIDE calibration accepted.",
        )
        assert record.status == GateStatus.ACCEPTED_AS_IS
        assert record.is_resolved

    def test_accept_changes_records_diff_and_audits(self):
        engine = _make_engine()
        engine.open_gate("gate_5_mitigation_adequacy", artifact_snapshot={"mitigation_count": 2, "high_risk_left": 1})
        record = engine.submit_decision(
            gate_id="gate_5_mitigation_adequacy",
            **ANALYST,
            action=GateAction.ACCEPT_CHANGES,
            rationale="Added one mitigation and reduced residual risk.",
            edited_artifact={"mitigation_count": 3, "high_risk_left": 0},
        )
        assert record.status == GateStatus.ACCEPTED_CHANGES
        assert record.decision is not None
        assert record.decision.artifact_diff is not None
        assert "mitigation_count" in record.decision.artifact_diff
        assert len(engine.audit_log.decisions_for_gate("gate_5_mitigation_adequacy")) == 1

    def test_reject_halts_and_sets_rejected_status(self):
        engine = _make_engine()
        engine.open_gate("gate_7_export_consistency", artifact_snapshot={"canonical_stix_error_count": 2})
        with pytest.raises(GateRejectedError):
            engine.submit_decision(
                gate_id="gate_7_export_consistency",
                **ANALYST,
                action=GateAction.REJECT,
                rationale="Export consistency unacceptable for release.",
            )
        assert engine.gate("gate_7_export_consistency").status == GateStatus.REJECTED

    def test_all_gate_set_2_final_decisions_are_audited(self):
        engine = _make_engine()
        gate_ids = [
            "gate_3_stride_calibration",
            "gate_4_threat_plausibility",
            "gate_5_mitigation_adequacy",
            "gate_6_merge_conflict_resolution",
            "gate_7_export_consistency",
        ]

        for gate_id in gate_ids:
            engine.open_gate(gate_id, artifact_snapshot={"gate": gate_id, "value": 1})
            engine.submit_decision(
                gate_id=gate_id,
                **ANALYST,
                action=GateAction.ACCEPT_AS_IS,
                rationale=f"Approved {gate_id}",
            )

        assert len(engine.audit_log.entries) == 5
        for entry in engine.audit_log.entries:
            assert entry.actor == ANALYST["actor"]
            assert entry.rationale
            assert entry.timestamp is not None


class TestSelectiveResume:
    def test_resume_from_gate_skips_prior_stages(self, monkeypatch):
        orch = FrameworkOrchestrator(
            settings=_settings(require_hitl_gates=False, stop_on_validation_error=False),
            run_id="run-resume-01",
        )

        # Mark gate_1 resolved so resume is allowed.
        orch.hitl_service.engine.open_gate("gate_1_scope_confirmation", artifact_snapshot={"scope": "ok"})
        orch.hitl_service.submit_decision(
            gate_id="gate_1_scope_confirmation",
            actor="analyst_2",
            role="Reviewer",
            action=GateAction.ACCEPT_AS_IS,
            rationale="Scope approved.",
        )

        called: list[str] = []

        def fake_run_stage(state: FrameworkState, stage_id: str):
            called.append(stage_id)
            return None

        monkeypatch.setattr(orch, "run_stage", fake_run_stage)

        state = FrameworkState(raw_text="resume input")
        orch.resume_from_checkpoint(state, "gate_1_scope_confirmation")

        # gate_1 is associated with agent_02, so resume should continue at agent_03.
        assert "agent_01" not in called
        assert "agent_02" not in called
        assert called[0] == "agent_03"
        assert "agent_09" in called
