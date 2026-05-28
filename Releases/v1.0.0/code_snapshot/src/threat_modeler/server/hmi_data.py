"""HMI data extraction helpers for serving threat modeling state to web frontends.

Provides serializable views of framework state, gates, threats, and metrics
optimized for React/web consumption.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from threat_modeler.hitl.models import HitlGateRecord, GateStatus
from threat_modeler.state import FrameworkState


def serialize_threat(
    threat: Any,
    component_id: str = "",
    interface_id: str = "",
    review_decisions: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Serialize a threat to a frontend-consumable dict."""
    threat_id = f"{interface_id}_{threat.name.replace(' ', '_')}"
    return {
        "id": threat_id,
        "name": threat.name,
        "description": threat.description,
        "component_id": component_id,
        "interface_id": interface_id,
        "mitre_attack_techniques": threat.mitre_attack_technique,
        "capec_id": threat.capec_id,
        "cwe_id": threat.cwe_id,
        "likelihood": threat.likelihood,
        "impact": threat.impact,
        "risk_score": threat.likelihood * threat.impact,
        "technical_mitigations": [
            {
                "control_id": m.control_id,
                "title": m.title,
                "description": m.description,
                "residual_risk": m.residual_risk_after_control,
            }
            for m in threat.mitigations_technical
        ],
        "administrative_mitigations": [
            {
                "control_id": m.control_id,
                "title": m.title,
                "description": m.description,
                "residual_risk": m.residual_risk_after_control,
            }
            for m in threat.mitigations_administrative
        ],
        "decision": (review_decisions or {}).get(threat_id),
    }


def extract_threats_from_state(state: FrameworkState) -> list[dict[str, Any]]:
    """Extract all threats from canonical graph with serialization."""
    threats: list[dict[str, Any]] = []

    if not state.canonical_graph:
        return threats

    graph = state.canonical_graph
    review_decisions = state.threat_review_decisions or {}

    # Extract threats from interfaces (formerly data flows)
    for interface in getattr(graph, "interfaces", []) or []:
        for threat in getattr(interface, "threats", []) or []:
            threats.append(serialize_threat(threat, interface_id=interface.id, review_decisions=review_decisions))

    return threats


def serialize_gate(gate: HitlGateRecord) -> dict[str, Any]:
    """Serialize a gate record to frontend-consumable dict."""
    return {
        "gate_id": gate.gate_id,
        "gate_name": gate.gate_name,
        "stage_id": gate.stage_id,
        "status": gate.status.value,
        "artifact_snapshot": gate.artifact_snapshot,
        "draft_artifact": gate.draft_artifact,
        "decision": gate.decision.to_dict() if gate.decision else None,
        "is_resolved": gate.is_resolved,
        "is_rejected": gate.is_rejected,
    }


def extract_stages_from_messages(
    messages: list[dict[str, Any]],
    *,
    run_status: str | None = None,
    next_stage_id: str | None = None,
) -> list[dict[str, Any]]:
    """Extract stage execution status from messages and reconcile with live run state."""
    stage_ids_seen: dict[str, bool] = {}
    stages: list[dict[str, Any]] = []

    stage_labels = {
        "agent_01": "01 · Input Normalizer",
        "agent_02": "02 · Context Builder",
        "agent_03": "03 · Trust Boundary Validator",
        "agent_04": "04 · STRIDE Scorer",
        "agent_05": "05 · Threat Generator",
        "agent_06": "06 · STIX Packager",
        "agent_07": "07 · Mitigation Generator",
        "agent_08": "08 · Diagram Generator",
        "agent_09": "09 · Report Writer",
    }

    for msg in messages:
        stage_id = str(msg.get("stage_id", "")).strip()
        if stage_id and stage_id not in stage_ids_seen:
            stage_ids_seen[stage_id] = True
    normalized_run_status = str(run_status or "").strip().lower()
    active_statuses = {"queued", "running", "paused"}
    terminal_completed_statuses = {"completed", "complete", "succeeded", "success"}
    terminal_failed_statuses = {"failed", "error", "provider_throttled"}
    raw_current_stage_id = str(next_stage_id or "").strip()
    current_stage_id = raw_current_stage_id
    if normalized_run_status not in active_statuses:
        current_stage_id = ""

    failed_stage_id = ""
    if normalized_run_status in terminal_failed_statuses:
        for msg in reversed(messages):
            stage_id = str(msg.get("stage_id", "")).strip()
            text = str(msg.get("text", "")).strip().lower()
            if stage_id and " failed:" in text:
                failed_stage_id = stage_id
                break

        # Fallback to live next_stage projection when no explicit failure message exists.
        if not failed_stage_id and raw_current_stage_id:
            failed_stage_id = raw_current_stage_id

    stage_order = list(stage_labels.keys())
    stage_index_by_id = {stage_id: index for index, stage_id in enumerate(stage_order)}
    current_stage_index = stage_index_by_id.get(current_stage_id)

    for stage_id, label in stage_labels.items():
        status = "pending"
        if failed_stage_id and stage_id == failed_stage_id:
            status = "failed"
        elif normalized_run_status in terminal_completed_statuses:
            status = "complete"
        elif stage_id in stage_ids_seen:
            status = "complete"
        elif current_stage_index is not None:
            stage_index = stage_index_by_id.get(stage_id, -1)
            if stage_index == current_stage_index:
                status = "running"
            elif stage_index < current_stage_index:
                status = "complete"

        stages.append({
            "stage_id": stage_id,
            "label": label,
            "status": status,
        })

    return stages


def extract_llm_metrics(state: FrameworkState) -> dict[str, Any]:
    """Extract LLM usage and cost metrics."""
    totals = state.llm_usage_totals()

    return {
        "total_tokens": totals.get("total_tokens", 0),
        "prompt_tokens": totals.get("prompt_tokens", 0),
        "completion_tokens": totals.get("completion_tokens", 0),
        "reasoning_tokens": totals.get("reasoning_tokens", 0),
        "cached_tokens": totals.get("cached_tokens", 0),
        "request_count": totals.get("request_count", 0),
        "by_stage": {
            stage_id: {
                "request_count": len(entries),
                "total_tokens": sum(int(e.get("total_tokens", 0) or 0) for e in entries),
                "prompt_tokens": sum(int(e.get("prompt_tokens", 0) or 0) for e in entries),
                "completion_tokens": sum(int(e.get("completion_tokens", 0) or 0) for e in entries),
            }
            for stage_id, entries in state.llm_usage_by_stage.items()
        },
    }
