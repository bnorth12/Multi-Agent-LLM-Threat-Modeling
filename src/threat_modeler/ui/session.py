"""Session state initialisation for the Threat Modeler UI."""

import streamlit as st


_DEFAULTS: dict = {
    "role": "",                       # "Author" | "Reviewer" | "Approver"
    "run_id": None,                   # str UUID of the active pipeline run
    "pipeline_state": None,           # serialised FrameworkState for display
    "gate_states": {},                # gate_id -> {"status": "pending"|"approved"|"rejected"}
    "settings_override": None,        # RuntimeSettings built from the Config screen
    "model_connection_valid": False,  # Boolean: whether model connection has been validated (S07-02/03)
    "theme": "Default",               # "Default" | "Dark"
    "input_system_name": "",          # last system name entered on Input Entry
    "input_system_description": "",   # last description entered on Input Entry
    "input_raw_text_paste": "",       # last pasted raw text on Input Entry
}


def init_session_state() -> None:
    """Populate st.session_state with default values for any missing keys."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default
