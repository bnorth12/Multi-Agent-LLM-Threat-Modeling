"""SCR-001 — Home / Run Dashboard.

Shows stage progress indicators for all nine pipeline stages and the
current HITL gate state using the active session pipeline state.
"""

import html
import re

import streamlit as st
from threat_modeler.ui.execution import (
    sync_execution_state_to_session,
    is_execution_active,
    get_execution_status,
    get_execution_elapsed_seconds,
    get_heartbeat_age_seconds,
    get_paused_at_gate,
    get_execution_error,
    get_current_provider_status,
)

_STAGE_LABELS = {
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

_STATUS_ICON = {
    "pending":    "⬜",
    "running":    "🔄",
    "complete":   "✅",
    "halted":     "🛑",
    "awaiting":   "⏸️",
}

# Auto-refresh interval (seconds) while pipeline is active.
_POLL_INTERVAL = 3


def _render_execution_error_details(error_text: str) -> None:
    """Render execution error in readable and raw form."""
    raw_text = str(error_text)
    decoded_text = html.unescape(raw_text)
    st.error("Execution error detected.")
    st.code(decoded_text, language="text")
    if decoded_text != raw_text:
        with st.expander("Raw error payload"):
            st.code(raw_text, language="text")


def _extract_provider_http_status(error_text: str) -> str:
    """Extract an HTTP status code hint from provider/runtime error text."""
    if not error_text:
        return ""
    match = re.search(r"HTTP\s+(\d{3})", error_text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def _render_run_diagnostics_panel(
    *,
    run_id: str | None,
    current_stage_id: str | None,
    current_step: str,
    paused_gate: str | None,
    primary_error: str,
) -> None:
    """Render a dedicated diagnostics panel for run health and failure triage."""
    # Subheader first so the panel heading always appears even if data-fetching throws.
    st.subheader("Run Diagnostics")
    try:
        provider_label, provider_status = get_current_provider_status()
        status = get_execution_status()
        elapsed = get_execution_elapsed_seconds()
        heartbeat_age = get_heartbeat_age_seconds()
        heartbeat_timeout = st.session_state.get("_execution_state", {}).get("heartbeat_timeout_seconds")
        try:
            heartbeat_timeout_value = float(heartbeat_timeout) if heartbeat_timeout is not None else None
        except (TypeError, ValueError):
            heartbeat_timeout_value = None

        with st.container(border=True):
            row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
            row1_col1.metric("Execution Status", status.upper())
            row1_col2.metric("Elapsed", f"{elapsed:.0f}s")
            row1_col3.metric("Provider", provider_label)
            row1_col4.metric("Provider State", provider_status)

            row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
            row2_col1.metric("Run ID", (run_id[:8] + "...") if run_id else "N/A")
            row2_col2.metric("Current Stage", current_stage_id or "N/A")
            row2_col3.metric("Paused Gate", paused_gate or "N/A")
            if heartbeat_age is None:
                row2_col4.metric("Heartbeat Age", "N/A")
            else:
                row2_col4.metric("Heartbeat Age", f"{heartbeat_age:.1f}s")

            if heartbeat_timeout_value is not None:
                st.caption(f"Heartbeat timeout threshold: {heartbeat_timeout_value:.1f}s")
            st.caption(f"Current Step: {current_step}")

            http_code = _extract_provider_http_status(primary_error)
            if http_code:
                st.warning(f"Detected provider HTTP error code: {http_code}")
            if primary_error:
                st.caption("Decoded error details are shown above this panel.")
    except Exception as _exc:
        st.error(f"Diagnostics unavailable: {type(_exc).__name__}: {_exc}")


@st.fragment(run_every=_POLL_INTERVAL)
def _render_live_dashboard() -> None:
    """Auto-refreshing fragment: run status, stage table, gate states."""
    sync_execution_state_to_session()

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")
    gate_states: dict = st.session_state.get("gate_states", {})
    execution_summary = st.session_state.get("pipeline_execution_summary", "")
    execution_error = st.session_state.get("pipeline_execution_error", "")

    # Run metadata row
    col_left, col_right = st.columns([3, 1])
    with col_left:
        if run_id:
            st.info(f"Active run: `{run_id}`")
        else:
            st.info("No active run. Start a run from the Pipeline Configuration screen.")
    with col_right:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.divider()

    runtime_error = get_execution_error()
    primary_error = runtime_error or execution_error
    if execution_summary and not primary_error:
        st.success(execution_summary)
    if primary_error:
        _render_execution_error_details(primary_error)

    if is_execution_active():
        status = get_execution_status()
        elapsed = get_execution_elapsed_seconds()
        st.info(f"⏳ Pipeline execution is active ({status}) · elapsed {elapsed:.0f}s")
        heartbeat_age = get_heartbeat_age_seconds()
        heartbeat_timeout = st.session_state.get("_execution_state", {}).get("heartbeat_timeout_seconds")
        try:
            heartbeat_timeout_value = float(heartbeat_timeout) if heartbeat_timeout is not None else None
        except (TypeError, ValueError):
            heartbeat_timeout_value = None
        if heartbeat_age is not None:
            if heartbeat_timeout_value is not None and heartbeat_age > heartbeat_timeout_value:
                st.error(
                    f"Heartbeat stalled: last update {heartbeat_age:.1f}s ago "
                    f"(threshold {heartbeat_timeout_value:.1f}s)."
                )
            else:
                timeout_label = (
                    f" / timeout {heartbeat_timeout_value:.0f}s"
                    if heartbeat_timeout_value is not None
                    else ""
                )
                st.caption(f"Heartbeat age: {heartbeat_age:.1f}s{timeout_label}")

    paused_gate = get_paused_at_gate()
    if paused_gate:
        st.warning(f"Pipeline is paused at {paused_gate}. Open Threat Review to submit a gate decision.")

    # Explicit process pointer to reduce ambiguity about where the run is.
    current_stage_id = getattr(pipeline_state, "next_stage_id", None) if pipeline_state else None
    status = get_execution_status()
    if paused_gate:
        current_step = f"HITL Review · {_GATE_LABELS.get(paused_gate, paused_gate)}"
    elif current_stage_id:
        current_step = f"Running · {_STAGE_LABELS.get(current_stage_id, current_stage_id)}"
    elif status == "completed":
        current_step = "Completed · All stages and gate processing finished"
    elif run_id:
        current_step = "Waiting · No active stage currently reported"
    else:
        current_step = "Idle · Start a run from Input Entry"
    st.caption(f"Current Step: {current_step}")

    try:
        _render_run_diagnostics_panel(
            run_id=run_id,
            current_stage_id=current_stage_id,
            current_step=current_step,
            paused_gate=paused_gate,
            primary_error=str(primary_error or ""),
        )
    except Exception as _diag_exc:
        st.error(f"Run Diagnostics panel error: {type(_diag_exc).__name__}: {_diag_exc}")

    if primary_error:
        st.caption("Execution error is shown above with decoded and raw detail.")

    # Stage progress table
    st.subheader("Stage Progress")

    completed_stages: set[str] = set()
    if pipeline_state and hasattr(pipeline_state, "messages"):
        completed_stages = {m.get("stage_id") for m in pipeline_state.messages}

    rows = []
    for stage_id, label in _STAGE_LABELS.items():
        if stage_id in completed_stages:
            status = "complete"
        elif current_stage_id == stage_id and is_execution_active():
            status = "running"
        else:
            status = "pending"
        rows.append({"Stage": label, "Status": f"{_STATUS_ICON[status]} {status.title()}"})

    st.table(rows)

    # HITL gate status
    if gate_states:
        st.divider()
        st.subheader("HITL Gate States")
        for gate_id, gate in gate_states.items():
            gate_status = gate.get("status", "pending")
            icon = _STATUS_ICON.get(gate_status, "❓")
            st.write(f"{icon} **{gate_id}** — {gate_status.title()}")
    else:
        st.caption("No HITL gates recorded for this run.")


def render() -> None:
    """Render SCR-001 Home / Run Dashboard."""
    st.header("Run Dashboard")
    st.caption("SCR-001 — pipeline stage progress and HITL gate status")
    _render_live_dashboard()
