"""Streamlit application entry point.

Launch with:
    streamlit run src/threat_modeler/ui/app.py

Requires the venv to be active and the package installed (or run from the
project root so src/ is on sys.path via pyproject.toml / editable install).
"""

import streamlit as st

from threat_modeler.ui.screens.home import render as render_home
from threat_modeler.ui.screens.role_select import render as render_role_select
from threat_modeler.ui.screens.config import render as render_config
from threat_modeler.ui.screens.input_entry import render as render_input_entry
from threat_modeler.ui.session import init_session_state
from threat_modeler.ui.theme import apply_theme

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

# Inject theme CSS (must run before any page content)
apply_theme()

# ---------------------------------------------------------------------------
# Navigation registry — order determines sidebar display order
# ---------------------------------------------------------------------------
_PAGES = {
    "Home": render_home,
    "Input Entry": render_input_entry,
    "Role Selection": render_role_select,
    "Pipeline Configuration": render_config,
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

    selected_page = st.radio(
        "Navigate",
        options=list(_PAGES.keys()),
        key="nav_selection",
        label_visibility="collapsed",
    )

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
