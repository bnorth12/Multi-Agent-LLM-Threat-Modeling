"""SCR-004 — Threat and Mitigation Review screen.

Allows users to inspect threats and mitigation coverage generated in the
canonical graph and record a lightweight review decision per threat.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


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

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")

    if run_id:
        st.info(f"Active run: {run_id}")
    else:
        st.warning("No active run yet. Start a run from Input Entry.")

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

    st.dataframe(filtered, use_container_width=True, hide_index=True)

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
