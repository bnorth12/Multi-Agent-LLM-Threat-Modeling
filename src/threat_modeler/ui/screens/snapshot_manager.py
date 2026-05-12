"""SCR-008/009 — Snapshot save and restore screen."""

from __future__ import annotations

import datetime

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session
from threat_modeler.ui.runtime_io import (
    build_snapshot_payload,
    framework_state_from_dict,
    snapshot_payload_from_json,
    snapshot_payload_to_json,
)
from threat_modeler.ui.version_governance import (
    generate_component_file_inventory,
    generate_component_version_manifest,
)


def render() -> None:
    st.header("Snapshot Manager")
    st.caption("SCR-008/009 — save and restore run snapshots")

    sync_execution_state_to_session()

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")
    gate_states = st.session_state.get("gate_states", {})
    markdown_edits = st.session_state.get("markdown_edits", {})

    if "saved_snapshots" not in st.session_state:
        st.session_state["saved_snapshots"] = {}

    st.subheader("Save Snapshot")

    snapshot_name = st.text_input(
        "Snapshot name",
        value=f"snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        key="snapshot_name_input",
    )

    payload = build_snapshot_payload(run_id, pipeline_state, gate_states, markdown_edits)
    payload_json = snapshot_payload_to_json(payload)

    col_save, col_download = st.columns(2)

    with col_save:
        if st.button("Save Snapshot In Session", type="primary", use_container_width=True):
            st.session_state["saved_snapshots"][snapshot_name] = payload
            st.success(f"Snapshot '{snapshot_name}' saved in session memory.")

    with col_download:
        st.download_button(
            "Download Snapshot JSON",
            data=payload_json,
            file_name=f"{snapshot_name}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    st.subheader("Version Governance Visibility")
    manifest = generate_component_version_manifest()
    inventory = generate_component_file_inventory()
    st.table(manifest.get("components", []))
    st.caption(f"Component file inventory rows: {inventory.get('row_count', 0)}")

    st.divider()
    st.subheader("Restore Snapshot")

    upload = st.file_uploader("Upload snapshot JSON", type=["json"], key="snapshot_upload")
    if upload is not None:
        try:
            raw = upload.read().decode("utf-8")
            restored = snapshot_payload_from_json(raw)
            st.success("Snapshot file parsed successfully. Click restore to apply.")

            if st.button("Apply Uploaded Snapshot", key="apply_uploaded_snapshot"):
                _apply_snapshot_payload(restored)
                st.success("Uploaded snapshot applied.")
                st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Invalid snapshot file: {exc}")

    saved = st.session_state.get("saved_snapshots", {})
    if saved:
        st.divider()
        st.subheader("Session Snapshots")
        selected = st.selectbox("Saved snapshots", options=list(saved.keys()), key="saved_snapshot_select")
        col_restore, col_delete = st.columns(2)
        with col_restore:
            if st.button("Restore Selected Snapshot", use_container_width=True):
                _apply_snapshot_payload(saved[selected])
                st.success(f"Restored snapshot '{selected}'.")
                st.rerun()
        with col_delete:
            if st.button("Delete Selected Snapshot", use_container_width=True):
                del st.session_state["saved_snapshots"][selected]
                st.success(f"Deleted snapshot '{selected}'.")
                st.rerun()


def _apply_snapshot_payload(payload: dict) -> None:
    """Mutate session state from snapshot payload."""
    st.session_state["run_id"] = payload.get("run_id")
    st.session_state["pipeline_state"] = framework_state_from_dict(payload.get("pipeline_state", {}))
    st.session_state["gate_states"] = payload.get("gate_states", {})
    st.session_state["markdown_edits"] = payload.get("markdown_edits", {})
