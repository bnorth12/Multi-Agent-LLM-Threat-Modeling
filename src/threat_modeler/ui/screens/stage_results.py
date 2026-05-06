"""SCR-003 — Stage Results Viewer.

Displays per-stage execution messages and canonical graph summary content from
the active FrameworkState in session state.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

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
    """Build stage status rows from FrameworkState.messages."""
    rows: list[dict[str, str]] = []
    completed: set[str] = set()

    messages = getattr(pipeline_state, "messages", []) if pipeline_state else []
    for msg in messages:
        stage_id = str(msg.get("stage_id", "")).strip()
        if stage_id:
            completed.add(stage_id)

    for stage_id, label in _STAGE_LABELS.items():
        status = "Complete" if stage_id in completed else "Pending"
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
    st.header("Stage Results Viewer")
    st.caption("SCR-003 — stage-by-stage execution outputs")

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")

    if run_id:
        st.info(f"Active run: {run_id}")
    else:
        st.warning("No active run yet. Start a run from Input Entry.")

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
        st.dataframe(message_rows, use_container_width=True, hide_index=True)
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
