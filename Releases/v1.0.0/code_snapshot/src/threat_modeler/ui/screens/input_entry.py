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
import traceback
import uuid
from typing import Any

import streamlit as st

from threat_modeler.ui.debug import log_exception, validate_settings, log_state_change, show_debug_panel
from threat_modeler.ui.execution import start_pipeline_execution, is_execution_active, get_active_run_id

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

            try:
                content = uf.read().decode("utf-8", errors="replace")
                reader = csv_mod.DictReader(io.StringIO(content))
                for row in reader:
                    tables.append(dict(row))
            except Exception as e:
                st.warning(f"⚠️ Failed to parse CSV '{uf.name}': {str(e)}")
                continue

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


def _model_connection_banner() -> None:
    """Render the model-connection status banner (informational only)."""
    settings = st.session_state.get("settings_override")
    provider = getattr(getattr(settings, "model", None), "provider", "fixture")
    offline = getattr(getattr(settings, "model", None), "offline_only", True)
    model_name = getattr(getattr(settings, "model", None), "model_name", "—")
    is_validated = st.session_state.get("model_connection_valid", False)
    offline_override = st.session_state.get("offline_override_active", False)

    if offline or provider == "fixture":
        st.info(
            "ℹ️ **Offline / Fixture mode** — pipeline uses deterministic fixture data "
            "(no live LLM calls). Go to **Pipeline Configuration** to select a live provider."
        )
    elif offline_override:
        st.warning(
            "⚠️ **Offline Override active** — connection was not validated against a live "
            f"endpoint. Provider: `{provider}` / `{model_name}`. Results may not reflect "
            "live model behaviour."
        )
    elif is_validated:
        st.success(
            f"✅ **Validated:** `{provider}` / `{model_name}` — live LLM calls will be "
            "made during the run."
        )
    else:
        st.error(
            "🔒 **Connection not validated** — go to **Pipeline Configuration → "
            "SCR-014 Connection Validation** to validate before starting a run."
        )


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
        settings is None
        or getattr(getattr(settings, "model", None), "offline_only", True)
        or getattr(getattr(settings, "model", None), "provider", "fixture") in ("unconfigured", "fixture")
        or st.session_state.get("offline_override_active", False)
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
        # Disable button if a run is already active
        is_run_active = is_execution_active()
        btn_label = "⏳ Running — see Run Dashboard" if is_run_active else "▶ Start Threat Model Run"
        start_clicked = st.button(
            btn_label,
            type="primary",
            disabled=not can_submit or is_run_active,
            use_container_width=True,
            help="A run is already in progress — navigate to Home to monitor" if is_run_active else None,
        )
    with col_clear:
        clear_clicked = st.button(
            "Clear",
            type="secondary",
            use_container_width=True,
            help="Clear all inputs and start over.",
        )

    # Show warning if run is active
    if is_run_active:
        active_run = get_active_run_id()
        st.warning(f"⏳ A run is already in progress: **{active_run[:8]}…**\n\nNavigate to **Home** or **Stage Results** to monitor progress.")

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
        try:
            file_raw_text, file_tables = _parse_uploaded_files(list(uploaded_files or []))
            log_state_change("file_tables", f"{len(file_tables)} rows parsed")
        except Exception as e:
            log_exception(e, context="File parsing failed", show_traceback=True)
            st.stop()

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

        # Execute pipeline immediately after form submission (GUI-001A requirement)
        try:
            from threat_modeler.orchestrator import FrameworkOrchestrator  # noqa: PLC0415
            from threat_modeler.config import RuntimeSettings  # noqa: PLC0415
            from threat_modeler.backend.runtime_state import get_last_settings  # noqa: PLC0415

            # Get runtime settings from session (SCR-003), fall back to backend store if missing.
            # This ensures settings persist across session resets and browser navigation.
            settings = st.session_state.get("settings_override")
            if not isinstance(settings, RuntimeSettings):
                settings = get_last_settings()
                if isinstance(settings, RuntimeSettings):
                    st.session_state["settings_override"] = settings
                else:
                    st.error(
                        "❌ Runtime settings are missing. Run halted to prevent implicit fallback to Local/Fixture mode. "
                        "Open Pipeline Configuration and configure an LLM provider."
                    )
                    st.stop()

            # Validate settings before pipeline execution
            is_valid, validation_msg = validate_settings(settings, "Pre-pipeline validation")
            st.info(validation_msg)
            if not is_valid:
                st.error("Cannot start pipeline with invalid settings.")
                st.stop()

            log_state_change("settings", f"provider={settings.model.provider}, model={settings.model.model_name}")

            # Start pipeline execution in background thread (non-blocking)
            # This allows user to navigate to monitoring screens while pipeline runs
            start_pipeline_execution(
                run_id=run_id,
                initial_state=initial_state,
                settings=settings,
            )
            log_state_change("execution", "started in background")

        except Exception as e:
            # Error during pipeline startup (not during execution)
            error_context = f"Failed to start pipeline execution"
            log_exception(e, context=error_context, show_traceback=True, severity="error")
            st.session_state["pipeline_execution_error"] = f"{type(e).__name__}: {str(e)}"
            show_debug_panel()
            st.stop()

        # Flag to navigate after rerun (avoid modifying session_state after widget instantiation)
        st.session_state["_navigate_to_home_after_rerun"] = True

        st.success(
            f"✅ Run **{run_id[:8]}…** initialised with {len(file_tables)} ICD rows "
            f"and {len(combined_raw.split())} words of narrative text.  "
            "Navigate to **Home** to monitor pipeline progress."
        )
        st.rerun()
