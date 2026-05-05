"""SCR-004 — Input Entry Form.

The primary entry point for a new threat model run.  The analyst:

  1. Enters a system name and optional description.
  2. Uploads one or more architecture files (CSV/XLSX ICD spreadsheets or
     MD/TXT narrative documents).
  3. Optionally pastes raw architecture text directly.
  4. Clicks "Start Threat Model Run" to kick off the pipeline.

The screen respects the model-connection-valid banner requirement from the HMI
Blueprint: when the provider is "unconfigured" a warning banner is shown but
the run is still permitted (offline / fixture mode).  When a live provider is
configured the banner confirms the connection.

After submitting the form the parsed content is written to session state and the
navigation switches to the Home (Run Dashboard) screen so the analyst can monitor
progress.
"""

from __future__ import annotations

import io
import uuid
from typing import Any

import streamlit as st

# Accepted MIME types / extensions for the file uploader.
_ACCEPTED_EXTENSIONS = ["csv", "xlsx", "md", "txt", "yaml", "yml"]

# Maximum number of files the analyst can upload at once.
_MAX_FILES = 10


def _parse_uploaded_files(uploaded_files: list[Any]) -> tuple[str, list[dict]]:
    """Return (raw_text, tables) from a list of UploadedFile objects.

    - MD / TXT / YAML / YML files are read as text and concatenated into raw_text.
    - CSV / XLSX files are parsed with the ICD parser and their rows appended to tables.

    Returns a tuple of (raw_text: str, tables: list[dict]).
    """
    raw_parts: list[str] = []
    tables: list[dict] = []

    for uf in uploaded_files:
        name: str = uf.name.lower()
        ext = name.rsplit(".", 1)[-1] if "." in name else ""

        if ext in ("md", "txt", "yaml", "yml"):
            content = uf.read().decode("utf-8", errors="replace")
            raw_parts.append(f"# --- {uf.name} ---\n{content}")

        elif ext == "csv":
            import csv as csv_mod

            content = uf.read().decode("utf-8", errors="replace")
            reader = csv_mod.DictReader(io.StringIO(content))
            for row in reader:
                tables.append(dict(row))

        elif ext == "xlsx":
            try:
                import openpyxl  # noqa: PLC0415

                wb = openpyxl.load_workbook(io.BytesIO(uf.read()), read_only=True, data_only=True)
                for ws in wb.worksheets:
                    headers: list[str] = []
                    for i, row in enumerate(ws.iter_rows(values_only=True)):
                        if i == 0:
                            headers = [str(c) if c is not None else f"col_{j}" for j, c in enumerate(row)]
                        else:
                            tables.append({headers[j]: str(v) if v is not None else "" for j, v in enumerate(row)})
            except ImportError:
                st.warning(
                    f"⚠️ openpyxl is required to parse XLSX files.  "
                    f"Install it with `pip install openpyxl`.  '{uf.name}' was skipped."
                )

    return "\n\n".join(raw_parts), tables


def _model_connection_banner() -> bool:
    """Render the model-connection banner.  Returns True if model is configured."""
    settings = st.session_state.get("settings_override")
    if settings is not None:
        provider = getattr(getattr(settings, "model", None), "provider", "unconfigured")
        offline = getattr(getattr(settings, "model", None), "offline_only", True)
    else:
        provider = "unconfigured"
        offline = True

    if provider == "unconfigured" or offline:
        st.info(
            "ℹ️ **Offline / fixture mode** — the pipeline will use pre-recorded agent "
            "outputs (no live LLM calls).  To switch to a live model, go to "
            "**Pipeline Configuration** and set Provider and Model Name.",
            icon=None,
        )
        return False
    else:
        st.success(
            f"✅ **Connected:** {provider} / "
            f"{getattr(getattr(settings, 'model', None), 'model_name', '—')}  "
            f"— Live LLM calls will be made during the run.",
            icon=None,
        )
        return True


def render() -> None:
    """Render SCR-004 Input Entry Form."""
    st.header("Input Entry Form")
    st.caption("SCR-004 — upload architecture files and start a threat model run")

    _model_connection_banner()

    st.divider()

    # ── System identification ────────────────────────────────────────────
    st.subheader("System Identification")

    system_name = st.text_input(
        "System name",
        value=st.session_state.get("input_system_name", ""),
        placeholder="e.g. Avionics Data Bus Network",
        help="A short, unique name for the system being threat modelled.  "
             "This appears in all output artifacts.",
    )

    system_description = st.text_area(
        "System description (optional)",
        value=st.session_state.get("input_system_description", ""),
        placeholder="Brief description of the system's purpose and operational context …",
        height=90,
        help="Supplementary context shown to agents during analysis.  "
             "Not required when a narrative document is uploaded.",
    )

    st.divider()

    # ── File upload ──────────────────────────────────────────────────────
    st.subheader("Architecture Files")
    st.markdown(
        "Upload one or more files that describe the system architecture.  "
        "Accepted formats:"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "**ICD / Spreadsheet**\n"
            "- `.csv` — interface control document (flat entity-per-row)\n"
            "- `.xlsx` — ICD workbook (first row = column headers)"
        )
    with col2:
        st.markdown(
            "**Narrative / Description**\n"
            "- `.md` — Markdown architecture description\n"
            "- `.txt` — plain text description\n"
            "- `.yaml` / `.yml` — YAML-structured description"
        )

    uploaded_files = st.file_uploader(
        "Upload architecture files",
        type=_ACCEPTED_EXTENSIONS,
        accept_multiple_files=True,
        label_visibility="collapsed",
        help=f"Up to {_MAX_FILES} files.  Drag-and-drop or click Browse.",
    )

    if uploaded_files and len(uploaded_files) > _MAX_FILES:
        st.error(f"Too many files — maximum is {_MAX_FILES}.  Please remove some and try again.")
        uploaded_files = uploaded_files[:_MAX_FILES]

    # File summary
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        for uf in uploaded_files:
            size_kb = uf.size / 1024 if uf.size else 0
            st.markdown(f"- `{uf.name}` ({size_kb:.1f} KB)")

    st.divider()

    # ── Optional raw text paste ──────────────────────────────────────────
    raw_text_paste = st.session_state.get("input_raw_text_paste", "")
    with st.expander("Paste raw architecture text (optional)", expanded=False):
        raw_text_paste = st.text_area(
            "Raw text",
            value=raw_text_paste,
            placeholder="Paste architecture description text here …\n"
                        "This is concatenated with any uploaded narrative files.",
            height=180,
            label_visibility="collapsed",
            help="Use this when you cannot upload a file (e.g. copy-paste from a document).",
        )

    st.divider()

    # ── Validation and submit ────────────────────────────────────────────
    can_submit = bool(system_name.strip()) and (bool(uploaded_files) or bool(raw_text_paste.strip()))

    # SCR-011: Check model connection validation gate
    model_valid = st.session_state.get("model_connection_valid", False)
    settings = st.session_state.get("settings_override")
    is_fixture_mode = (
        settings is None or 
        getattr(getattr(settings, "model", None), "offline_only", True) or 
        getattr(getattr(settings, "model", None), "provider", "unconfigured") == "unconfigured"
    )

    # Allow submit if: (1) inputs valid AND (2) either fixture mode OR live mode with validation
    can_submit = can_submit and (is_fixture_mode or model_valid)

    if not system_name.strip():
        st.warning("⚠️ Enter a **System name** before starting a run.")
    elif not uploaded_files and not raw_text_paste.strip():
        st.warning("⚠️ Upload at least one architecture file **or** paste raw text before starting a run.")
    elif not is_fixture_mode and not model_valid:
        st.error(
            "🔒 **Model connection required** — Go to **Pipeline Configuration** to configure and validate your LLM connection before starting a run.",
            icon="🔒"
        )

    col_btn, col_clear = st.columns([3, 1])
    with col_btn:
        start_clicked = st.button(
            "▶ Start Threat Model Run",
            type="primary",
            disabled=not can_submit,
            use_container_width=True,
        )
    with col_clear:
        clear_clicked = st.button(
            "Clear",
            type="secondary",
            use_container_width=True,
            help="Clear all inputs and start over.",
        )

    # ── Handle clear ────────────────────────────────────────────────────
    if clear_clicked:
        for key in ("input_system_name", "input_system_description", "input_raw_text_paste",
                    "run_id", "pipeline_state", "gate_states"):
            st.session_state[key] = "" if key.startswith("input") else None
        st.session_state["gate_states"] = {}
        st.rerun()

    # ── Handle submit ────────────────────────────────────────────────────
    if start_clicked and can_submit:
        # Persist inputs in session state
        st.session_state["input_system_name"] = system_name.strip()
        st.session_state["input_system_description"] = system_description.strip()
        st.session_state["input_raw_text_paste"] = raw_text_paste.strip()

        # Parse uploaded files
        file_raw_text, file_tables = _parse_uploaded_files(list(uploaded_files or []))

        # Merge raw text: pasted + uploaded narrative
        combined_raw = "\n\n".join(
            part for part in [
                f"# {system_name.strip()}",
                system_description.strip(),
                raw_text_paste.strip(),
                file_raw_text,
            ]
            if part.strip()
        )

        # Build initial FrameworkState and persist to session
        from threat_modeler.state import FrameworkState  # noqa: PLC0415

        initial_state = FrameworkState(
            raw_text=combined_raw,
            tables=file_tables,
        )

        run_id = str(uuid.uuid4())
        st.session_state["run_id"] = run_id
        st.session_state["pipeline_state"] = initial_state
        st.session_state["gate_states"] = {}

        # Switch nav to Home / Run Dashboard
        st.session_state["nav_selection"] = "Home"

        st.success(
            f"✅ Run **{run_id[:8]}…** initialised with {len(file_tables)} ICD rows "
            f"and {len(combined_raw.split())} words of narrative text.  "
            "Navigate to **Home** to monitor pipeline progress."
        )
        st.rerun()
