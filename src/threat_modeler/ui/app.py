"""Streamlit application entry point.

Launch with:
    streamlit run src/threat_modeler/ui/app.py

Requires the venv to be active and the package installed (or run from the
project root so src/ is on sys.path via pyproject.toml / editable install).
"""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from threat_modeler.ui.screens.home import render as render_home
from threat_modeler.ui.screens.role_select import render as render_role_select
from threat_modeler.ui.screens.config import render as render_config
from threat_modeler.ui.screens.input_entry import render as render_input_entry
from threat_modeler.ui.screens.prompt_editor import render as render_prompt_editor
from threat_modeler.ui.screens.stage_results import render as render_stage_results
from threat_modeler.ui.screens.threat_review import render as render_threat_review
from threat_modeler.ui.screens.results_export import render as render_results_export
from threat_modeler.ui.screens.stix_viewer import render as render_stix_viewer
from threat_modeler.ui.screens.canonical_graph_viewer import render as render_canonical_graph_viewer
from threat_modeler.ui.screens.mermaid_viewer import render as render_mermaid_viewer
from threat_modeler.ui.screens.stride_viewer import render as render_stride_viewer
from threat_modeler.ui.screens.markdown_viewer import render as render_markdown_viewer
from threat_modeler.ui.screens.token_usage import render as render_token_usage
from threat_modeler.ui.screens.last_prompt import render as render_last_prompt
from threat_modeler.ui.screens.snapshot_manager import render as render_snapshot_manager
from threat_modeler.ui.session import init_session_state
from threat_modeler.ui.theme import apply_theme
from threat_modeler.ui.execution import (
    sync_execution_state_to_session,
    render_execution_status_badge,
    verify_provider_not_fallen_back,
)

load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)

# ---------------------------------------------------------------------------
# Page-level Streamlit config — must be the first st call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Agent LLM Threat Modeler",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
init_session_state()

# Keep active execution and run state coherent across reruns/reloads.
sync_execution_state_to_session()

# Inject theme CSS (must run before any page content)
apply_theme()

# ---------------------------------------------------------------------------
# Navigation registry — order determines sidebar display order
# Ordered by typical user workflow: setup → input → analysis → review → export → tools
# ---------------------------------------------------------------------------
_PAGES = {
    "Home": render_home,
    "Role Selection": render_role_select,
    "Pipeline Configuration": render_config,
    "Input Entry": render_input_entry,
    "Stage Results": render_stage_results,
    "Threat Review": render_threat_review,
    "STIX Viewer": render_stix_viewer,
    "Canonical Graph Viewer": render_canonical_graph_viewer,
    "Mermaid Viewer": render_mermaid_viewer,
    "STRIDE Viewer": render_stride_viewer,
    "Token Usage": render_token_usage,
    "Last Prompt": render_last_prompt,
    "Results Export": render_results_export,
    "Snapshot Manager": render_snapshot_manager,
    "Markdown Viewer": render_markdown_viewer,
    "Prompt Editor": render_prompt_editor,
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🔐 Threat Modeler")

    role = st.session_state.get("role", "")
    if role:
        st.caption(f"Signed in as: **{role}**")
    else:
        st.caption("No role selected")

    st.divider()

    # Handle navigation flag set by other screens (before rendering the radio widget)
    if st.session_state.get("_navigate_to_home_after_rerun", False):
        st.session_state["nav_selection"] = "Home"
        st.session_state["_navigate_to_home_after_rerun"] = False

    selected_page = st.radio(
        "Navigate",
        options=list(_PAGES.keys()),
        key="nav_selection",
        label_visibility="collapsed",
    )

    # Show current background execution status for operators.
    render_execution_status_badge()

    st.divider()

    # Theme toggle
    current_theme = st.session_state.get("theme", "Default")
    new_theme = st.radio(
        "Appearance",
        options=["Default", "Dark"],
        index=0 if current_theme == "Default" else 1,
        horizontal=True,
        key="theme_radio",
    )
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        st.rerun()

    st.divider()
    st.caption("Sprint 2026-06 · S06-07")

# ---------------------------------------------------------------------------
# Render selected page
# ---------------------------------------------------------------------------
_PAGES[selected_page]()

# Verify provider hasn't fallen back (logs fallback if detected)
verify_provider_not_fallen_back()
