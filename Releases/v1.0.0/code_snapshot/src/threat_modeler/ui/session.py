"""Session state initialisation for the Threat Modeler UI."""

import streamlit as st
from threat_modeler.config import RuntimeSettings
from threat_modeler.backend.runtime_state import (
    get_last_settings,
    get_validation_state,
    remember_settings,
)


_DEFAULTS: dict = {
    "role": "",                       # "Author" | "Reviewer" | "Approver"
    "run_id": None,                   # str UUID of the active pipeline run
    "pipeline_state": None,           # serialised FrameworkState for display
    "gate_states": {},                # gate_id -> {"status": "pending"|"approved"|"rejected"}
    "settings_override": None,        # RuntimeSettings built from the Config screen
    "model_api_key": "",             # Session-only API key for selected provider (SCR-013)
    "model_connection_valid": False,  # Boolean: whether model connection has been validated (S07-02/03)
    "offline_override_active": False, # Boolean: user explicitly chose offline override (S07-03)
    "theme": "Dark",                  # "Default" | "Dark"
    "input_system_name": "",          # last system name entered on Input Entry
    "input_system_description": "",   # last description entered on Input Entry
    "input_raw_text_paste": "",       # last pasted raw text on Input Entry
    "markdown_edits": {},             # run_id -> edited markdown content (GUI-025)
}


def init_session_state() -> None:
    """Populate st.session_state with default values for any missing keys."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default

    current_settings = st.session_state.get("settings_override")
    last_settings = get_last_settings()

    if isinstance(last_settings, RuntimeSettings):
        if not isinstance(current_settings, RuntimeSettings):
            st.session_state["settings_override"] = last_settings
            current_settings = last_settings
        else:
            current_live = (
                not current_settings.model.offline_only
                and current_settings.model.provider != "fixture"
            )
            last_live = (
                not last_settings.model.offline_only
                and last_settings.model.provider != "fixture"
            )
            # If session state drifted to fixture while backend has live settings,
            # trust backend to preserve continuity across reruns/windows.
            if last_live and not current_live:
                st.session_state["settings_override"] = last_settings
                current_settings = last_settings

    if isinstance(current_settings, RuntimeSettings):
        remember_settings(current_settings)

    # Keep validation and offline override aligned with backend state.
    valid, offline_override = get_validation_state()
    if valid:
        st.session_state["model_connection_valid"] = True
    if offline_override:
        st.session_state["offline_override_active"] = True
