"""Runtime theme injection for the Threat Modeler UI.

Streamlit does not support switching themes at runtime via st.set_page_config,
so we inject a <style> block on every render.  The CSS targets Streamlit's
internal DOM structure with !important overrides so the chosen palette
supersedes the framework defaults.

Supported themes
----------------
- "Default"  — Streamlit's built-in light palette (no overrides injected).
- "Dark"     — Explicit dark palette matching Streamlit's own dark-mode spec.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Palette constants
# ---------------------------------------------------------------------------

_DARK_CSS = """
<style>
/* ── Base app background ───────────────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    background-color: #0e1117 !important;
    color: #fafafa !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: #262730 !important;
    color: #fafafa !important;
}
[data-testid="stSidebar"] * {
    color: #fafafa !important;
}

/* ── Headers and text ───────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6,
p, li, span, label,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * {
    color: #fafafa !important;
}
.stCaption, .stCaption * {
    color: #a3a8b8 !important;
}

/* ── Inputs ─────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
.stSelectbox select,
[data-testid="stMultiSelect"] {
    background-color: #1e2029 !important;
    color: #fafafa !important;
    border-color: #3d4052 !important;
}

/* ── Buttons ────────────────────────────────────────────────────────── */
[data-testid="stBaseButton-primary"] {
    background-color: #1f6feb !important;
    color: #ffffff !important;
    border-color: #1f6feb !important;
}
[data-testid="stBaseButton-secondary"] {
    background-color: #262730 !important;
    color: #fafafa !important;
    border-color: #3d4052 !important;
}

/* ── Tables ─────────────────────────────────────────────────────────── */
[data-testid="stTable"] table {
    background-color: #1e2029 !important;
    color: #fafafa !important;
}
[data-testid="stTable"] th {
    background-color: #262730 !important;
    color: #a3a8b8 !important;
}
[data-testid="stTable"] td {
    color: #fafafa !important;
    border-color: #3d4052 !important;
}

/* ── Info / alert boxes ─────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background-color: #1e2029 !important;
    color: #fafafa !important;
}

/* ── Dividers ────────────────────────────────────────────────────────── */
hr {
    border-color: #3d4052 !important;
}

/* ── Radio groups ────────────────────────────────────────────────────── */
[data-testid="stRadio"] label {
    color: #fafafa !important;
}
[data-testid="stRadio"] div {
    color: #fafafa !important;
}

/* ── Checkbox ────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    color: #fafafa !important;
}

/* ── Multiselect tags ────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] span {
    background-color: #1f6feb !important;
    color: #ffffff !important;
}

/* ── Metric / column headers ─────────────────────────────────────────── */
[data-testid="stMetricLabel"] {
    color: #a3a8b8 !important;
}
[data-testid="stMetricValue"] {
    color: #fafafa !important;
}
</style>
"""

# No CSS injected for Default — let Streamlit's own light theme apply.
_DEFAULT_CSS = ""


def apply_theme() -> None:
    """Read ``st.session_state['theme']`` and inject the matching CSS.

    Must be called once per render cycle, before any page content is rendered,
    so the styles are present in the page from the start of the DOM.
    """
    theme: str = st.session_state.get("theme", "Default")
    css = _DARK_CSS if theme == "Dark" else _DEFAULT_CSS
    if css:
        st.markdown(css, unsafe_allow_html=True)
