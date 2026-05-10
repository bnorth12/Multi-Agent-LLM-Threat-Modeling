"""SCR-007 — Results Export screen."""

from __future__ import annotations

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session
from threat_modeler.ui.runtime_io import (
    export_canonical_json,
    export_mermaid_markdown,
    export_report_markdown,
    export_stix_json,
    export_token_usage_json,
)


def render() -> None:
    st.header("Results Export")
    st.caption("SCR-007 — export generated artifacts")

    sync_execution_state_to_session()

    run_id = st.session_state.get("run_id") or "no-run"
    state = st.session_state.get("pipeline_state")

    if state is None:
        st.warning("No active pipeline state. Start and run the pipeline first.")
        return

    st.subheader("Export Artifacts")
    col1, col2, col3 = st.columns(3)

    with col1:
        canonical_json = export_canonical_json(state)
        st.download_button(
            "Download Canonical Graph JSON",
            data=canonical_json,
            file_name=f"{run_id}_canonical_graph.json",
            mime="application/json",
            use_container_width=True,
        )

        stix_json = export_stix_json(state)
        st.download_button(
            "Download STIX Bundle JSON",
            data=stix_json,
            file_name=f"{run_id}_stix_bundle.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        report_md = export_report_markdown(state)
        st.download_button(
            "Download Final Report (Markdown)",
            data=report_md,
            file_name=f"{run_id}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

        mermaid_md = export_mermaid_markdown(state)
        st.download_button(
            "Download Mermaid Diagrams (Markdown)",
            data=mermaid_md,
            file_name=f"{run_id}_diagrams.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col3:
        token_usage_json = export_token_usage_json(state)
        st.download_button(
            "Download Token Usage JSON",
            data=token_usage_json,
            file_name=f"{run_id}_token_usage.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    st.subheader("Quick Preview")

    with st.expander("Canonical Graph JSON", expanded=False):
        st.code(canonical_json[:20000], language="json")

    with st.expander("STIX Bundle JSON", expanded=False):
        st.code(stix_json[:20000], language="json")

    with st.expander("Final Report Markdown", expanded=False):
        st.code(report_md[:20000], language="markdown")

    with st.expander("Mermaid Markdown", expanded=False):
        st.code(mermaid_md[:20000], language="markdown")

    with st.expander("Token Usage JSON", expanded=False):
        st.code(token_usage_json[:20000], language="json")
