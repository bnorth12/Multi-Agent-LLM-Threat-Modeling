"""GUI-021 — STRIDE Threat Model Viewer screen."""

from __future__ import annotations

from typing import Any

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session


def _stride_rows(state: Any) -> list[dict[str, Any]]:
    """Build per-interface STRIDE rows with justifications and threat counts."""
    graph = getattr(state, "canonical_graph", None)
    if graph is None:
        return []

    rows: list[dict[str, Any]] = []
    for interface in graph.interfaces:
        rows.append(
            {
                "interface_id": interface.id,
                "interface_name": interface.name,
                "from_node": interface.from_node,
                "to_node": interface.to_node,
                "S": interface.stride.S,
                "T": interface.stride.T,
                "R": interface.stride.R,
                "I": interface.stride.I,
                "D": interface.stride.D,
                "E": interface.stride.E,
                "S_justification": interface.stride.S_justification,
                "T_justification": interface.stride.T_justification,
                "R_justification": interface.stride.R_justification,
                "I_justification": interface.stride.I_justification,
                "D_justification": interface.stride.D_justification,
                "E_justification": interface.stride.E_justification,
                "threat_count": len(interface.threats),
                "threat_names": ", ".join(threat.name for threat in interface.threats),
            }
        )
    return rows


def _sorted_rows(rows: list[dict[str, Any]], sort_by: str, ascending: bool) -> list[dict[str, Any]]:
    """Sort deterministic STRIDE rows by selected key."""
    return sorted(rows, key=lambda row: row.get(sort_by, ""), reverse=not ascending)


def render() -> None:
    st.header("STRIDE Threat Model Viewer")
    st.caption("GUI-021 — per-interface STRIDE scores, justifications, and linked threats")

    sync_execution_state_to_session()

    state = st.session_state.get("pipeline_state")
    if state is None:
        st.warning("No active pipeline state. Start and run the pipeline first.")
        return

    rows = _stride_rows(state)
    if not rows:
        st.warning("No STRIDE interface data available in this run.")
        return

    sort_options = ["interface_name", "S", "T", "R", "I", "D", "E", "threat_count"]
    col_sort, col_order = st.columns(2)
    with col_sort:
        sort_by = st.selectbox("Sort by", options=sort_options, index=0)
    with col_order:
        ascending = st.toggle("Ascending", value=True)

    sorted_rows = _sorted_rows(rows, sort_by, ascending)

    st.subheader("STRIDE Scores")
    st.dataframe(sorted_rows, use_container_width=True, hide_index=True)

    st.subheader("Interface Detail")
    selected_interface = st.selectbox(
        "Interface",
        options=[row["interface_name"] for row in sorted_rows],
        index=0,
    )
    selected = next(row for row in sorted_rows if row["interface_name"] == selected_interface)
    st.table(
        [
            {"Field": "Interface ID", "Value": selected["interface_id"]},
            {"Field": "S Justification", "Value": selected["S_justification"]},
            {"Field": "T Justification", "Value": selected["T_justification"]},
            {"Field": "R Justification", "Value": selected["R_justification"]},
            {"Field": "I Justification", "Value": selected["I_justification"]},
            {"Field": "D Justification", "Value": selected["D_justification"]},
            {"Field": "E Justification", "Value": selected["E_justification"]},
            {"Field": "Threat Names", "Value": selected["threat_names"]},
        ]
    )
