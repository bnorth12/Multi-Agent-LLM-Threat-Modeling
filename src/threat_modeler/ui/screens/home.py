"""SCR-001 — Home / Run Dashboard.

Shows stage progress indicators for all nine pipeline stages and the
current HITL gate state. In this sprint the pipeline is not wired to a
live run, so placeholder progress is rendered from session state.
"""

import streamlit as st

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

_STATUS_ICON = {
    "pending":    "⬜",
    "running":    "🔄",
    "complete":   "✅",
    "halted":     "🛑",
    "awaiting":   "⏸️",
}


def render() -> None:
    """Render SCR-001 Home / Run Dashboard."""
    st.header("Run Dashboard")
    st.caption("SCR-001 — pipeline stage progress and HITL gate status")

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")
    gate_states: dict = st.session_state.get("gate_states", {})

    # Run metadata
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

    # Stage progress table
    st.subheader("Stage Progress")

    completed_stages: set[str] = set()
    if pipeline_state and hasattr(pipeline_state, "messages"):
        completed_stages = {m.get("stage_id") for m in pipeline_state.messages}

    rows = []
    for stage_id, label in _STAGE_LABELS.items():
        if stage_id in completed_stages:
            status = "complete"
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
