"""SCR-004 — Threat and Mitigation Review screen.

Allows users to inspect threats and mitigation coverage generated in the
canonical graph and record a lightweight review decision per threat.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from threat_modeler.config import RuntimeSettings, build_default_settings
from threat_modeler.hitl import GateAction, GateRejectedError
from threat_modeler.orchestrator import FrameworkOrchestrator
from threat_modeler.ui.execution import (
    sync_execution_state_to_session,
    resume_pipeline_execution,
    get_execution_status,
    get_paused_at_gate,
)


_GATE_LABELS = {
    "gate_0_input_integrity": "Gate 0 · Input Integrity",
    "gate_1_scope_confirmation": "Gate 1 · Scope Confirmation",
    "gate_2_boundary_approval": "Gate 2 · Trust Boundary Approval",
    "gate_3_stride_calibration": "Gate 3 · STRIDE Calibration",
    "gate_4_threat_plausibility": "Gate 4 · Threat Plausibility",
    "gate_5_mitigation_adequacy": "Gate 5 · Mitigation Adequacy",
    "gate_6_merge_conflict_resolution": "Gate 6 · Merge Conflict Resolution",
    "gate_7_export_consistency": "Gate 7 · Export Consistency",
}

_RAW_PREVIEW_CHAR_LIMIT = 20000
_RAW_PREVIEW_HEIGHT = 220


def _active_gate_ids(gate_states: dict[str, Any]) -> list[str]:
    active: list[str] = []
    for gate_id, gate in gate_states.items():
        status = str((gate or {}).get("status", "pending")).strip().lower()
        if status in {"open", "draft", "rejected", "accepted_as_is", "accepted_changes"}:
            active.append(gate_id)
    return active


def _review_gate_ids(gate_states: dict[str, Any], paused_gate: str | None) -> list[str]:
    """Build stable gate selector options, always including the current paused gate."""
    options: list[str] = []
    seen: set[str] = set()

    # Prefer canonical gate order for known gates.
    for gate_id in _GATE_LABELS.keys():
        if gate_id in gate_states or gate_id == paused_gate:
            options.append(gate_id)
            seen.add(gate_id)

    # Preserve any extra/non-standard gates recorded in state.
    for gate_id in gate_states.keys():
        if gate_id not in seen:
            options.append(gate_id)
            seen.add(gate_id)

    if paused_gate and paused_gate not in seen:
        options.append(paused_gate)

    return options


def _open_gate_ids(gate_states: dict[str, Any]) -> list[str]:
    open_ids: list[str] = []
    for gate_id, gate in gate_states.items():
        status = str((gate or {}).get("status", "pending")).strip().lower()
        if status in {"open", "draft", "rejected"}:
            open_ids.append(gate_id)
    return open_ids


def _runtime_settings() -> RuntimeSettings:
    settings = st.session_state.get("settings_override")
    if isinstance(settings, RuntimeSettings):
        return settings
    return build_default_settings()


def _restore_orchestrator() -> FrameworkOrchestrator:
    run_id = st.session_state.get("run_id") or "run-default"
    orchestrator = FrameworkOrchestrator(_runtime_settings(), run_id=run_id)
    pipeline_state = st.session_state.get("pipeline_state")
    checkpoint = getattr(pipeline_state, "hitl_gate_checkpoint", None) if pipeline_state else None
    if isinstance(checkpoint, dict) and checkpoint:
        orchestrator.hitl_service.restore_checkpoint_state(checkpoint)
    return orchestrator


def _update_session_from_state(orchestrator: FrameworkOrchestrator, pipeline_state: Any) -> None:
    checkpoint = orchestrator.hitl_service.checkpoint_state()
    pipeline_state.hitl_gate_checkpoint = checkpoint
    st.session_state["pipeline_state"] = pipeline_state
    st.session_state["gate_states"] = checkpoint.get("gates", {})


def _graph_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if "system" in snapshot or "subsystems" in snapshot or "interfaces" in snapshot:
        return snapshot
    return {}


def _render_graph_summary(snapshot: dict[str, Any]) -> None:
    graph = _graph_snapshot(snapshot)
    if not graph:
        st.caption("No canonical graph snapshot available for this gate.")
        return

    system = graph.get("system", {}) if isinstance(graph.get("system"), dict) else {}
    subsystems = graph.get("subsystems", []) if isinstance(graph.get("subsystems"), list) else []
    components = graph.get("components", []) if isinstance(graph.get("components"), list) else []
    interfaces = graph.get("interfaces", []) if isinstance(graph.get("interfaces"), list) else []
    trust_boundaries = [
        iface for iface in interfaces
        if isinstance(iface, dict) and iface.get("trust_boundary_crossing")
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("System", str(system.get("name", "Unknown")))
    col2.metric("Subsystems", len(subsystems))
    col3.metric("Components", len(components))
    col4.metric("Interfaces", len(interfaces))
    st.write(f"System under review: {system.get('name', 'Unknown')}")

    automated_checks = [
        {
            "Check": "System name present",
            "Status": "PASS" if system.get("name") else "FAIL",
            "Details": str(system.get("name", "Missing")),
        },
        {
            "Check": "At least one subsystem",
            "Status": "PASS" if subsystems else "FAIL",
            "Details": str(len(subsystems)),
        },
        {
            "Check": "At least one interface/data flow",
            "Status": "PASS" if interfaces else "FAIL",
            "Details": str(len(interfaces)),
        },
        {
            "Check": "Trust boundaries identified",
            "Status": "PASS" if trust_boundaries else "WARN",
            "Details": str(len(trust_boundaries)),
        },
    ]
    st.caption("Automated review checks")
    st.table(automated_checks)

    system_description = str(system.get("description", "")).strip()
    if system_description:
        st.caption("System context")
        st.write(system_description)

    subsystem_rows = []
    for subsystem in subsystems[:8]:
        if not isinstance(subsystem, dict):
            continue
        subsystem_rows.append(
            {
                "Subsystem": str(subsystem.get("name") or subsystem.get("id", "")),
                "Description": str(subsystem.get("description", "")),
            }
        )
    if subsystem_rows:
        st.caption("Subsystem summary")
        st.table(subsystem_rows)

    preview_rows = []
    for iface in interfaces[:8]:
        if not isinstance(iface, dict):
            continue
        preview_rows.append(
            {
                "Interface": str(iface.get("name") or iface.get("id", "")),
                "Protocol": str(iface.get("protocol", "")),
                "Boundary": str(iface.get("trust_boundary_name", "")) or "No",
            }
        )
    if preview_rows:
        st.caption("Interface preview")
        st.table(preview_rows)


def _render_gate_specific_summary(gate_id: str, snapshot: dict[str, Any]) -> None:
    if gate_id in {"gate_1_scope_confirmation", "gate_2_boundary_approval"}:
        _render_graph_summary(snapshot)
        return

    if gate_id == "gate_3_stride_calibration":
        interfaces = snapshot.get("interfaces", []) if isinstance(snapshot, dict) else []
        scored = 0
        for iface in interfaces:
            if isinstance(iface, dict) and isinstance(iface.get("stride"), dict):
                scored += 1
        st.metric("Interfaces with STRIDE payload", scored)
        st.caption("Automated check: STRIDE calibration data is human-reviewable when score payloads are attached per interface.")
        _render_graph_summary(snapshot)
        return

    if gate_id in {"gate_4_threat_plausibility", "gate_5_mitigation_adequacy"}:
        interfaces = snapshot.get("interfaces", []) if isinstance(snapshot, dict) else []
        threat_rows = []
        mitigation_count = 0
        for iface in interfaces:
            if not isinstance(iface, dict):
                continue
            for threat in iface.get("threats", [])[:10]:
                if not isinstance(threat, dict):
                    continue
                mitigation_count += len(threat.get("mitigations_technical", [])) + len(threat.get("mitigations_administrative", []))
                threat_rows.append(
                    {
                        "Interface": str(iface.get("name") or iface.get("id", "")),
                        "Threat": str(threat.get("name", "")),
                        "Likelihood": str(threat.get("likelihood", "")),
                        "Impact": str(threat.get("impact", "")),
                    }
                )
        st.metric("Visible threats", len(threat_rows))
        if gate_id == "gate_5_mitigation_adequacy":
            st.metric("Mitigation entries", mitigation_count)
        if threat_rows:
            st.caption("Threat preview")
            st.table(threat_rows[:8])
        else:
            st.caption("No threat payload is available yet for this gate snapshot.")
        return

    st.caption("No specialized renderer for this gate yet; raw snapshot remains available below.")


def _submit_gate_decision(gate_id: str, action: GateAction, rationale: str) -> None:
    pipeline_state = st.session_state.get("pipeline_state")
    if pipeline_state is None:
        st.error("No active pipeline state available.")
        return

    orchestrator = _restore_orchestrator()
    role = st.session_state.get("role") or "Reviewer"
    actor = str(role).lower().replace(" ", "_") or "reviewer"

    try:
        orchestrator.hitl_service.submit_decision(
            gate_id=gate_id,
            actor=actor,
            role=str(role),
            action=action,
            rationale=rationale.strip() or f"{action.value} during UI validation.",
        )
        _update_session_from_state(orchestrator, pipeline_state)
        st.success(f"Recorded {action.value} for {gate_id}.")
    except GateRejectedError as exc:
        pipeline_state.hitl_rejected_at_gate = exc.gate_record.gate_id
        _update_session_from_state(orchestrator, pipeline_state)
        st.session_state["pipeline_execution_error"] = str(exc)
        st.error(str(exc))


def _render_gate_review() -> None:
    gate_states: dict[str, Any] = st.session_state.get("gate_states", {})
    pipeline_state = st.session_state.get("pipeline_state")
    paused_gate = get_paused_at_gate()

    # Defensive hydration: after navigation/rerender, gate cache can be empty
    # even though the run is paused. Rebuild from checkpoint or paused gate id.
    if not gate_states:
        checkpoint = getattr(pipeline_state, "hitl_gate_checkpoint", None) if pipeline_state is not None else None
        if isinstance(checkpoint, dict):
            restored_gates = checkpoint.get("gates", {})
            if isinstance(restored_gates, dict) and restored_gates:
                gate_states = restored_gates
                st.session_state["gate_states"] = restored_gates

    if not gate_states and paused_gate:
        gate_states = {
            paused_gate: {
                "gate_id": paused_gate,
                "status": "open",
                "artifact_snapshot": {},
            }
        }
        st.session_state["gate_states"] = gate_states

    if not gate_states:
        st.caption("No HITL gates recorded for this run.")
        return

    active_default = pipeline_state
    default_gate = st.session_state.get("_execution_state", {}).get("pause_gate")
    if default_gate is None and active_default is not None:
        default_gate = getattr(active_default, "hitl_paused_at_gate", None)

    active_gate_ids = _review_gate_ids(gate_states, default_gate)
    if not active_gate_ids:
        st.caption("No actionable HITL gates are currently open or resolved for review.")
        return

    open_gate_ids = _open_gate_ids(gate_states)

    # Always bias selection toward the currently open gate so review controls
    # (including rationale text) align to the active checkpoint.
    selected_state = st.session_state.get("hitl_gate_select")
    preferred_gate = None
    if open_gate_ids:
        preferred_gate = open_gate_ids[0]
    elif default_gate in active_gate_ids:
        preferred_gate = default_gate
    elif selected_state in active_gate_ids:
        preferred_gate = selected_state
    elif active_gate_ids:
        preferred_gate = active_gate_ids[0]

    if preferred_gate is not None:
        if selected_state not in active_gate_ids or selected_state not in open_gate_ids and open_gate_ids:
            st.session_state["hitl_gate_select"] = preferred_gate

    selected_gate = st.selectbox(
        "Select gate",
        options=active_gate_ids,
        index=active_gate_ids.index(default_gate) if default_gate in active_gate_ids else 0,
        format_func=lambda gate_id: _GATE_LABELS.get(gate_id, gate_id),
        key="hitl_gate_select",
    )

    gate = gate_states.get(selected_gate, {}) or {}
    status = str(gate.get("status", "pending"))
    snapshot = gate.get("artifact_snapshot") if isinstance(gate.get("artifact_snapshot"), dict) else {}

    st.subheader(_GATE_LABELS.get(selected_gate, selected_gate))
    st.write(f"Status: **{status}**")

    _render_gate_specific_summary(selected_gate, snapshot)

    show_raw = st.toggle(
        "Show raw gate artifact",
        key=f"show_raw_gate_artifact_{selected_gate}",
        value=False,
        help="Scroll-safe raw payload preview. Toggle off to collapse.",
    )
    if show_raw:
        if not snapshot:
            st.info("No raw gate artifact data is available for this gate in the current run state.")
        else:
            raw_payload = json.dumps(snapshot, indent=2, ensure_ascii=False)
            st.text_area(
                "Raw gate artifact payload",
                value=raw_payload[:_RAW_PREVIEW_CHAR_LIMIT],
                height=_RAW_PREVIEW_HEIGHT,
                disabled=True,
                key=f"raw_gate_payload_{selected_gate}",
            )
            if len(raw_payload) > _RAW_PREVIEW_CHAR_LIMIT:
                st.caption(
                    f"Showing first {_RAW_PREVIEW_CHAR_LIMIT} characters of raw payload."
                )

    rationale_key = f"gate_rationale_{selected_gate}"
    if rationale_key not in st.session_state:
        st.session_state[rationale_key] = (
            f"Automated UI validation for {_GATE_LABELS.get(selected_gate, selected_gate)}."
        )

    rationale = st.text_area(
        "Gate rationale",
        key=rationale_key,
        height=100,
    )

    status_lower = status.strip().lower()
    can_decide = status_lower in {"open", "draft", "pending", "rejected"}
    paused_gate = get_paused_at_gate()
    execution_status = get_execution_status()
    can_resume = (
        status_lower in {"accepted_as_is", "accepted_changes"}
        and execution_status == "paused"
        and paused_gate == selected_gate
    )

    col1, col2, col3 = st.columns(3)
    if col1.button(
        "Approve Gate",
        key=f"approve_{selected_gate}",
        use_container_width=True,
        disabled=not can_decide,
    ):
        _submit_gate_decision(selected_gate, GateAction.ACCEPT_AS_IS, rationale)
        st.rerun()
    if col2.button(
        "Reject Gate",
        key=f"reject_{selected_gate}",
        use_container_width=True,
        disabled=not can_decide,
    ):
        _submit_gate_decision(selected_gate, GateAction.REJECT, rationale)
        st.rerun()
    if col3.button(
        "Resume Pipeline",
        key=f"resume_{selected_gate}",
        use_container_width=True,
        disabled=not can_resume,
    ):
        run_id = st.session_state.get("run_id") or "run-default"
        pipeline_state = st.session_state.get("pipeline_state")
        if pipeline_state is None:
            st.error("No active pipeline state available.")
        else:
            resume_pipeline_execution(run_id, pipeline_state, _runtime_settings(), selected_gate)
        st.rerun()

    if not can_decide and status_lower in {"accepted_as_is", "accepted_changes"}:
        st.caption("Gate already approved. Use Resume Pipeline when this gate is the active pause checkpoint.")


def _extract_threat_rows(pipeline_state: Any) -> list[dict[str, str]]:
    """Flatten interface threats into rows for display/filtering."""
    rows: list[dict[str, str]] = []
    graph = getattr(pipeline_state, "canonical_graph", None) if pipeline_state else None
    interfaces = getattr(graph, "interfaces", []) if graph else []

    for interface in interfaces:
        interface_id = getattr(interface, "id", "")
        interface_name = getattr(interface, "name", "")
        interface_desc = getattr(interface, "description", "")
        threats = getattr(interface, "threats", [])

        for threat in threats:
            technical = getattr(threat, "mitigations_technical", [])
            admin = getattr(threat, "mitigations_administrative", [])
            likelihood = int(getattr(threat, "likelihood", 1))
            impact = int(getattr(threat, "impact", 1))
            risk_score = likelihood * impact

            rows.append(
                {
                    "Threat Key": f"{interface_id}::{getattr(threat, 'name', '')}",
                    "Interface": interface_name or interface_id,
                    "Interface Description": interface_desc,
                    "Threat": str(getattr(threat, "name", "")),
                    "Description": str(getattr(threat, "description", "")),
                    "Likelihood": str(likelihood),
                    "Impact": str(impact),
                    "Risk Score": str(risk_score),
                    "Tech Mitigations": str(len(technical)),
                    "Admin Mitigations": str(len(admin)),
                }
            )

    return rows


def render() -> None:
    st.header("Threat Review")
    st.caption("SCR-004 — threat and mitigation review")

    sync_execution_state_to_session()

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")

    if run_id:
        st.info(f"Active run: {run_id}")
    else:
        st.warning("No active run yet. Start a run from Input Entry.")

    st.subheader("HITL Gate Review")
    _render_gate_review()

    st.divider()

    rows = _extract_threat_rows(pipeline_state)
    if not rows:
        st.caption("No threats available yet. Run through STRIDE/Threat stages first.")
        return

    # Review state (session only)
    if "threat_review_decisions" not in st.session_state:
        st.session_state["threat_review_decisions"] = {}

    st.subheader("Threat Table")

    min_risk = st.slider("Minimum risk score", min_value=1, max_value=25, value=1, step=1)
    filtered = [r for r in rows if int(r["Risk Score"]) >= min_risk]

    st.table(filtered)

    st.divider()
    st.subheader("Review Decisions")

    selected = st.selectbox(
        "Select threat",
        options=[r["Threat Key"] for r in filtered],
        key="threat_review_select",
    )

    decision = st.radio(
        "Decision",
        options=["accepted", "needs_attention", "defer"],
        horizontal=True,
        key="threat_decision_radio",
    )

    note = st.text_area("Review note", key="threat_review_note", height=100)

    if st.button("Save Decision", type="primary"):
        st.session_state["threat_review_decisions"][selected] = {
            "decision": decision,
            "note": note.strip(),
        }
        st.success("Review decision saved.")

    decisions = st.session_state.get("threat_review_decisions", {})
    if decisions:
        st.divider()
        st.subheader("Saved Decisions")
        table_rows = []
        for key, val in decisions.items():
            table_rows.append(
                {
                    "Threat Key": key,
                    "Decision": str(val.get("decision", "")),
                    "Note": str(val.get("note", "")),
                }
            )
        st.table(table_rows)
