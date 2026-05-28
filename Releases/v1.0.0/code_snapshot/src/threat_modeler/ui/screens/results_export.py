"""SCR-007 — Results Export screen."""

from __future__ import annotations

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session
from threat_modeler.ui.runtime_io import (
    export_canonical_json,
    export_mermaid_markdown,
    export_report_markdown,
    export_stride_csv,
    export_stride_json,
    export_stix_json,
    export_token_usage_json,
)
from threat_modeler.ui.version_governance import (
    generate_component_file_inventory,
    generate_component_version_manifest,
    inventory_to_json,
    manifest_to_json,
)


_PREVIEW_CHAR_LIMIT = 20000
_PREVIEW_HEIGHT = 220


def _render_preview_block(label: str, content: str, key_suffix: str) -> None:
    show = st.toggle(
        f"Show {label}",
        key=f"preview_toggle_{key_suffix}",
        value=False,
        help="Scroll-safe quick preview. Toggle off to collapse.",
    )
    if not show:
        return

    st.text_area(
        f"{label} preview",
        value=(content or "")[:_PREVIEW_CHAR_LIMIT],
        height=_PREVIEW_HEIGHT,
        disabled=True,
        key=f"preview_text_{key_suffix}",
    )
    if content and len(content) > _PREVIEW_CHAR_LIMIT:
        st.caption(f"Showing first {_PREVIEW_CHAR_LIMIT} characters.")


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
    col1, col2, col3, col4 = st.columns(4)

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

    with col4:
        stride_json = export_stride_json(state)
        st.download_button(
            "Download STRIDE JSON",
            data=stride_json,
            file_name=f"{run_id}_stride.json",
            mime="application/json",
            use_container_width=True,
        )

        stride_csv = export_stride_csv(state)
        st.download_button(
            "Download STRIDE CSV",
            data=stride_csv,
            file_name=f"{run_id}_stride.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.subheader("Version Governance Artifacts")
    version_manifest = generate_component_version_manifest()
    file_inventory = generate_component_file_inventory()
    version_manifest_json = manifest_to_json(version_manifest)
    file_inventory_json = inventory_to_json(file_inventory)

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.download_button(
            "Download Component Version Manifest",
            data=version_manifest_json,
            file_name=f"{run_id}_component_version_manifest.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_v2:
        st.download_button(
            "Download Component File Inventory",
            data=file_inventory_json,
            file_name=f"{run_id}_component_file_inventory.json",
            mime="application/json",
            use_container_width=True,
        )

    st.caption(
        f"Component manifest entries: {len(version_manifest.get('components', []))} | "
        f"File inventory rows: {file_inventory.get('row_count', 0)}"
    )

    st.divider()
    st.subheader("Quick Preview")
    _render_preview_block("Canonical Graph JSON", canonical_json, "canonical_graph")
    _render_preview_block("STIX Bundle JSON", stix_json, "stix_bundle")
    _render_preview_block("Final Report Markdown", report_md, "final_report")
    _render_preview_block("Mermaid Markdown", mermaid_md, "mermaid")
    _render_preview_block("Token Usage JSON", token_usage_json, "token_usage")
    _render_preview_block("STRIDE JSON", stride_json, "stride")
    _render_preview_block("Component Version Manifest", version_manifest_json, "version_manifest")
    _render_preview_block("Component File Inventory", file_inventory_json, "file_inventory")
