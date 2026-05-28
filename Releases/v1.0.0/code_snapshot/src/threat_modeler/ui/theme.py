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
/* ── Theme tokens (dark) ───────────────────────────────────────────── */
:root {
    --tm-bg: #0e1117;
    --tm-surface: #1e2029;
    --tm-surface-2: #262730;
    --tm-border: #3d4052;
    --tm-text: #fafafa;
    --tm-muted: #a3a8b8;
    --tm-accent: #1f6feb;
    --tm-accent-text: #ffffff;
}

/* ── Base app background ───────────────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    background-color: var(--tm-bg) !important;
    color: var(--tm-text) !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-text) !important;
}
[data-testid="stSidebar"] * {
    color: var(--tm-text) !important;
}

/* ── Headers and text ───────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6,
p, li, span, label,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * {
    color: var(--tm-text) !important;
}
.stCaption, .stCaption * {
    color: var(--tm-muted) !important;
}

/* ── Inputs ─────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stMultiSelect"] {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: var(--tm-muted) !important;
}

/* Streamlit selectbox/multiselect (BaseWeb) */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] [role="combobox"],
div[data-baseweb="select"] input {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="popover"] ul {
    background-color: var(--tm-surface) !important;
    border: 1px solid var(--tm-border) !important;
}
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] li {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
}
div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background-color: var(--tm-accent) !important;
    color: var(--tm-accent-text) !important;
}

/* ── Disabled text areas (preview blocks) ────────────────────────────── */
[data-testid="stTextArea"] textarea:disabled {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
    -webkit-text-fill-color: var(--tm-text) !important;
    opacity: 1 !important;
}

/* ── Buttons ────────────────────────────────────────────────────────── */
[data-testid="stBaseButton-primary"] {
    background-color: var(--tm-accent) !important;
    color: var(--tm-accent-text) !important;
    border-color: var(--tm-accent) !important;
}
[data-testid="stBaseButton-secondary"] {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* ── Tables ─────────────────────────────────────────────────────────── */
[data-testid="stTable"] table {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
}
[data-testid="stTable"] th {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-muted) !important;
}
[data-testid="stTable"] td {
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* Dataframe (glide grid) */
[data-testid="stDataFrame"] * {
    color: var(--tm-text) !important;
}
[data-testid="stDataFrame"] {
    background-color: var(--tm-surface) !important;
    border: 1px solid var(--tm-border) !important;
}

/* ── Info / alert boxes ─────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* ── Dividers ────────────────────────────────────────────────────────── */
hr {
    border-color: var(--tm-border) !important;
}

/* ── Radio groups ────────────────────────────────────────────────────── */
[data-testid="stRadio"] label {
    color: var(--tm-text) !important;
}
[data-testid="stRadio"] div {
    color: var(--tm-text) !important;
}

/* ── Checkbox ────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    color: var(--tm-text) !important;
}

/* ── Multiselect tags ────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] span {
    background-color: var(--tm-accent) !important;
    color: var(--tm-accent-text) !important;
}

/* ── File uploader ───────────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--tm-surface) !important;
    border-color: var(--tm-border) !important;
    color: var(--tm-text) !important;
}
[data-testid="stFileUploaderDropzone"] * {
    color: var(--tm-text) !important;
}

/* ── Tabs / expanders / code blocks ─────────────────────────────────── */
button[data-baseweb="tab"] {
    color: var(--tm-text) !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stCodeBlock"] pre,
[data-testid="stCode"] pre,
pre,
code {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* ── Metric / column headers ─────────────────────────────────────────── */
[data-testid="stMetricLabel"] {
    color: var(--tm-muted) !important;
}
[data-testid="stMetricValue"] {
    color: var(--tm-text) !important;
}

/* ── Number inputs ───────────────────────────────────────────────────── */
[data-testid="stNumberInput"] input {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stNumberInput"] > div {
    background-color: var(--tm-surface) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stNumberInput"] button {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* ── Slider ──────────────────────────────────────────────────────────── */
[data-testid="stSlider"] label {
    color: var(--tm-text) !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: var(--tm-muted) !important;
}

/* ── Form container ──────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background-color: var(--tm-surface) !important;
    border: 1px solid var(--tm-border) !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background-color: var(--tm-surface-2) !important;
    border-bottom: 1px solid var(--tm-border) !important;
}
[data-baseweb="tab-panel"] {
    background-color: var(--tm-bg) !important;
}
button[data-baseweb="tab"][aria-selected="false"] {
    color: var(--tm-muted) !important;
}

/* ── JSON viewer ─────────────────────────────────────────────────────── */
[data-testid="stJson"],
[data-testid="stJson"] * {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
}
</style>
"""

_DEFAULT_CSS = """
<style>
/* ── Theme tokens (default/light) ───────────────────────────────────── */
:root {
    --tm-bg: #ffffff;
    --tm-surface: #f7f8fc;
    --tm-surface-2: #eef2f7;
    --tm-border: #b0bbd0;
    --tm-text: #0f172a;
    --tm-muted: #4b5563;
    --tm-accent: #1d4ed8;
    --tm-accent-text: #ffffff;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    background-color: var(--tm-bg) !important;
    color: var(--tm-text) !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-text) !important;
}

h1, h2, h3, h4, h5, h6,
p, li, span, label,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * {
    color: var(--tm-text) !important;
}
.stCaption, .stCaption * {
    color: var(--tm-muted) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stMultiSelect"] {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stTextArea"] textarea:disabled {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
    -webkit-text-fill-color: var(--tm-text) !important;
    opacity: 1 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="select"] [role="combobox"],
div[data-baseweb="select"] input {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="popover"] ul {
    background-color: var(--tm-surface) !important;
    border: 1px solid var(--tm-border) !important;
}
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] li {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
}
div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background-color: var(--tm-accent) !important;
    color: var(--tm-accent-text) !important;
}

[data-testid="stBaseButton-secondary"] {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stTable"] table,
[data-testid="stDataFrame"] {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stTable"] th {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-muted) !important;
}
[data-testid="stTable"] td,
[data-testid="stDataFrame"] * {
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: var(--tm-surface) !important;
    border-color: var(--tm-border) !important;
    color: var(--tm-text) !important;
}
[data-testid="stFileUploaderDropzone"] * {
    color: var(--tm-text) !important;
}

[data-testid="stCodeBlock"] pre,
[data-testid="stCode"] pre,
pre,
code {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* ── Number inputs ───────────────────────────────────────────────────── */
[data-testid="stNumberInput"] input {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stNumberInput"] > div {
    background-color: var(--tm-surface) !important;
    border-color: var(--tm-border) !important;
}
[data-testid="stNumberInput"] button {
    background-color: var(--tm-surface-2) !important;
    color: var(--tm-text) !important;
    border-color: var(--tm-border) !important;
}

/* ── Slider ──────────────────────────────────────────────────────────── */
[data-testid="stSlider"] label {
    color: var(--tm-text) !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: var(--tm-muted) !important;
}

/* ── Form container ──────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background-color: var(--tm-surface) !important;
    border: 1px solid var(--tm-border) !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background-color: var(--tm-surface-2) !important;
    border-bottom: 1px solid var(--tm-border) !important;
}
[data-baseweb="tab-panel"] {
    background-color: var(--tm-bg) !important;
}
button[data-baseweb="tab"][aria-selected="false"] {
    color: var(--tm-muted) !important;
}

/* ── JSON viewer ─────────────────────────────────────────────────────── */
[data-testid="stJson"],
[data-testid="stJson"] * {
    background-color: var(--tm-surface) !important;
    color: var(--tm-text) !important;
}
</style>
"""


def apply_theme() -> None:
    """Read ``st.session_state['theme']`` and inject the matching CSS.

    Must be called once per render cycle, before any page content is rendered,
    so the styles are present in the page from the start of the DOM.
    """
    theme: str = st.session_state.get("theme", "Default")
    css = _DARK_CSS if theme == "Dark" else _DEFAULT_CSS
    if css:
        st.markdown(css, unsafe_allow_html=True)
