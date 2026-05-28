"""SCR-003 — Stage Results Viewer.

Displays per-stage execution messages and canonical graph summary content from
the active FrameworkState in session state.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st
from threat_modeler.ui.execution import (
    sync_execution_state_to_session,
    get_execution_error,
    is_execution_active,
    get_execution_status,
    get_paused_at_gate,
)

_STAGE_LABELS: dict[str, str] = {
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


def _stage_rows(pipeline_state: Any) -> list[dict[str, str]]:
    """Build stage status rows from framework messages and live execution status."""
    rows: list[dict[str, str]] = []
    completed: set[str] = set()
    current_stage_id = getattr(pipeline_state, "next_stage_id", None) if pipeline_state else None
    paused_gate = get_paused_at_gate()
    execution_active = is_execution_active()
    execution_status = get_execution_status()

    messages = getattr(pipeline_state, "messages", []) if pipeline_state else []
    for msg in messages:
        stage_id = str(msg.get("stage_id", "")).strip()
        if stage_id:
            completed.add(stage_id)

    for stage_id, label in _STAGE_LABELS.items():
        if stage_id in completed:
            status = "Complete"
        elif paused_gate and current_stage_id == stage_id:
            status = "Awaiting HITL"
        elif execution_active and current_stage_id == stage_id:
            status = "Running"
        elif execution_status == "completed":
            status = "Skipped/Not Reached"
        else:
            status = "Pending"
        rows.append({"Stage": label, "Stage ID": stage_id, "Status": status})

    return rows


def _message_rows(pipeline_state: Any) -> list[dict[str, str]]:
    """Flatten state messages for table display."""
    rows: list[dict[str, str]] = []
    messages = getattr(pipeline_state, "messages", []) if pipeline_state else []
    for i, msg in enumerate(messages, start=1):
        rows.append(
            {
                "#": str(i),
                "Stage ID": str(msg.get("stage_id", "")),
                "Message": str(msg.get("text", "")),
            }
        )
    return rows


def render() -> None:
    sync_execution_state_to_session()

    st.header("Stage Results Viewer")
    st.caption("SCR-003 — stage-by-stage execution outputs")

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")

    if run_id:
        st.info(f"Active run: {run_id}")
    else:
        st.warning("No active run yet. Start a run from Input Entry.")

    execution_error = get_execution_error()
    if execution_error:
        raw_text = str(execution_error)
        decoded_text = html.unescape(raw_text)
        st.error("Execution error detected for this run.")
        st.code(decoded_text, language="text")
        if decoded_text != raw_text:
            with st.expander("Raw error payload"):
                st.code(raw_text, language="text")

    if pipeline_state is None:
        st.caption("No pipeline state available yet.")
        return

    # Stage completion grid
    st.subheader("Stage Completion")
    st.table(_stage_rows(pipeline_state))

    st.divider()
    st.subheader("Recorded Stage Messages")
    message_rows = _message_rows(pipeline_state)
    if message_rows:
        st.table(message_rows)
    else:
        st.caption("No messages recorded yet.")

    st.divider()
    st.subheader("Artifact Snapshot")

    graph = getattr(pipeline_state, "canonical_graph", None)
    interfaces = getattr(graph, "interfaces", []) if graph else []
    st.metric("Interfaces", len(interfaces))

    threat_count = 0
    for interface in interfaces:
        threat_count += len(getattr(interface, "threats", []))
    st.metric("Threats", threat_count)

    st.metric("STIX bundle present", "Yes" if getattr(pipeline_state, "stix_bundle", None) else "No")
    st.metric("Mermaid diagrams", len(getattr(pipeline_state, "mermaid_diagrams", {})))
    st.metric("Final report", "Yes" if getattr(pipeline_state, "final_report", None) else "No")
