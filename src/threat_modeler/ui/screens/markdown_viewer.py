"""SCR-GUI-025 — Markdown Viewer and Editor screen.

Provides in-app markdown display, editing, and preview with save-state feedback
and edit safeguards for analyst-driven documentation updates.
"""

from __future__ import annotations

import streamlit as st
from markdown import markdown

from threat_modeler.ui.execution import sync_execution_state_to_session
from threat_modeler.ui.runtime_io import export_report_markdown


def render() -> None:
    st.header("Markdown Viewer and Editor")
    st.caption("GUI-025 — view, edit, and save markdown artifacts")

    sync_execution_state_to_session()

    run_id = st.session_state.get("run_id") or "no-run"
    state = st.session_state.get("pipeline_state")

    if state is None:
        st.warning("No active pipeline state. Start and run the pipeline first.")
        return

    if not state.final_report:
        st.warning("No generated report available. Complete a pipeline run to generate markdown.")
        return

    # Initialize session state for markdown editing
    if "markdown_edits" not in st.session_state:
        st.session_state["markdown_edits"] = {}

    if run_id not in st.session_state["markdown_edits"]:
        st.session_state["markdown_edits"][run_id] = state.final_report

    # Get current markdown content (from edits or original)
    current_markdown = st.session_state["markdown_edits"][run_id]

    # UI tabs for view, edit, and preview
    tab_view, tab_edit, tab_preview = st.tabs(["📖 View", "✏️ Edit", "👁️ Preview"])

    # -----------------------------------------------------------------------
    # VIEW TAB: Read-only display of markdown
    # -----------------------------------------------------------------------
    with tab_view:
        st.markdown("### Generated Report")
        st.markdown(current_markdown)

    # -----------------------------------------------------------------------
    # EDIT TAB: Edit markdown content
    # -----------------------------------------------------------------------
    with tab_edit:
        st.markdown("### Edit Markdown Content")

        # Display edit safeguards info
        col_info, col_reset = st.columns([0.8, 0.2])
        with col_info:
            st.info(
                "Edit the markdown content below. Changes are tracked but not automatically saved. "
                "Use 'Save Changes' to persist edits to the snapshot."
            )

        with col_reset:
            if st.button("Reset to Original", use_container_width=True, help="Discard all edits"):
                st.session_state["markdown_edits"][run_id] = state.final_report
                st.success("Reset to original report.")
                st.rerun()

        # Markdown editor textarea
        edited_markdown = st.text_area(
            "Markdown content",
            value=current_markdown,
            height=400,
            key=f"md_editor_{run_id}",
            label_visibility="collapsed",
        )

        # Track changes
        has_changes = edited_markdown != state.final_report

        # Save button with visual feedback
        col_save, col_discard = st.columns(2)

        with col_save:
            if st.button(
                "💾 Save Changes",
                type="primary" if has_changes else "secondary",
                use_container_width=True,
                disabled=not has_changes,
                help="Save edits to snapshot state"
            ):
                st.session_state["markdown_edits"][run_id] = edited_markdown
                st.success("✓ Markdown changes saved to snapshot state.")

        with col_discard:
            if st.button(
                "🔄 Discard Changes",
                use_container_width=True,
                disabled=not has_changes,
                help="Revert to last saved version"
            ):
                st.session_state["markdown_edits"][run_id] = state.final_report
                st.info("Changes discarded. Editor reset to last saved version.")
                st.rerun()

        # Display save state indicator
        if has_changes:
            st.warning("⚠️ Unsaved changes detected. Click 'Save Changes' to persist edits.")
        else:
            st.success("✓ All changes saved.")

    # -----------------------------------------------------------------------
    # PREVIEW TAB: Rendered HTML preview
    # -----------------------------------------------------------------------
    with tab_preview:
        st.markdown("### Markdown Preview")

        if not current_markdown.strip():
            st.info("No markdown content to preview.")
        else:
            try:
                # Convert markdown to HTML and display
                html_content = markdown(current_markdown)
                st.markdown(current_markdown)

                # Show character and line count
                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    st.metric("Characters", len(current_markdown))
                with col_stats2:
                    st.metric("Lines", len(current_markdown.split("\n")))

            except Exception as e:
                st.error(f"Preview error: {e}")

    # -----------------------------------------------------------------------
    # EXPORT SECTION: Download edited markdown
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Export")

    col_download_original, col_download_edited = st.columns(2)

    with col_download_original:
        original_md = export_report_markdown(state)
        st.download_button(
            "Download Original Report",
            data=original_md,
            file_name=f"{run_id}_report_original.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_download_edited:
        st.download_button(
            "Download Edited Report",
            data=current_markdown,
            file_name=f"{run_id}_report_edited.md",
            mime="text/markdown",
            use_container_width=True,
        )
