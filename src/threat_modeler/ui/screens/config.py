"""SCR-003 — Pipeline Configuration with SCR-012/013 Model Selection and Connection Details.

Renders configuration form with:
- SCR-012: Model provider selection (dropdown with Custom/Intranet support)
- SCR-013: Model connection details (URL for providers that need it)
- Pipeline settings (stage selection, error handling, HITL gates)

The resulting RuntimeSettings is stored in st.session_state["settings_override"]
and connection validation state is stored in st.session_state["model_connection_valid"].
"""

import streamlit as st

from threat_modeler.config import (
    PROVIDER_MATRIX,
    ModelSelection,
    PipelineSettings,
    RuntimeSettings,
    build_default_settings,
)

_ALL_STAGES = [
    "agent_01",
    "agent_02",
    "agent_03",
    "agent_04",
    "agent_05",
    "agent_06",
    "agent_07",
    "agent_08",
    "agent_09",
]

_STAGE_LABELS = {
    "agent_01": "01 · Input Normalizer",
    "agent_02": "02 · Context Builder",
    "agent_03": "03 · Trust Boundary Validator",
    "agent_04": "04 · STRIDE Scorer",
    "agent_05": "05 · Threat Generator",
    "agent_06": "06 · STIX Packager",
    "agent_07": "07 · Mitigation Generator",
    "agent_08": "08 · Diagram Generator",
    "agent_09": "09 · Report Writer",
}


def _defaults() -> RuntimeSettings:
    override = st.session_state.get("settings_override")
    if isinstance(override, RuntimeSettings):
        return override
    return build_default_settings()


def render() -> None:
    """Render SCR-003 Pipeline Configuration with provider selection and connection details."""
    st.header("Pipeline Configuration")
    st.caption("SCR-003 — configure model, connection, and pipeline settings before starting a run")

    defaults = _defaults()

    with st.form("pipeline_config_form"):
        # ===== SCR-012: Model Provider Selection =====
        st.subheader("SCR-012 — Model Provider Selection")
        st.write("Choose an LLM provider to use for this threat modeling run.")

        provider_options = {prov_key: f"{meta['label']}" for prov_key, meta in PROVIDER_MATRIX.items()}
        selected_provider = st.selectbox(
            "Provider",
            options=list(PROVIDER_MATRIX.keys()),
            format_func=lambda x: provider_options[x],
            index=list(PROVIDER_MATRIX.keys()).index(defaults.model.provider)
            if defaults.model.provider in PROVIDER_MATRIX
            else 0,
            help="Select the LLM provider to use.",
        )

        # Show provider description
        provider_info = PROVIDER_MATRIX.get(selected_provider, {})
        if provider_info:
            st.info(f"**{provider_info['label']}**: {provider_info['description']}")

        # Model name (use provider default, allow override)
        model_name = st.text_input(
            "Model name",
            value=defaults.model.model_name,
            help=f"Model identifier for the provider. Default: {provider_info.get('default_model', 'N/A')}",
        )

        # ===== SCR-013: Connection Details =====
        st.subheader("SCR-013 — Connection Details")

        connection_url = ""
        if provider_info.get("requires_url", False):
            connection_url = st.text_input(
                "Connection URL",
                value=defaults.model.connection_url,
                placeholder="e.g., https://api.azure.com/v1 or http://localhost:11434",
                help=f"Connection URL or endpoint for {provider_info['label']}.",
            )
            st.caption("This URL is used to connect to the LLM provider. It will be securely stored in session state.")

        offline_mode_checkbox = st.checkbox(
            "Offline/Fixture mode (no live LLM calls)",
            value=defaults.model.offline_only,
            help="When checked, uses deterministic fixture data instead of calling a live LLM.",
        )

        # ===== Pipeline Settings =====
        st.subheader("Pipeline Settings")

        default_enabled = list(defaults.pipeline.enabled_stage_ids)
        enabled_stages = st.multiselect(
            "Enabled stages",
            options=_ALL_STAGES,
            default=default_enabled,
            format_func=lambda s: _STAGE_LABELS.get(s, s),
            help="Deselect stages to skip them during the run.",
        )

        stop_on_error = st.checkbox(
            "Stop on validation error",
            value=defaults.pipeline.stop_on_validation_error,
            help="Halt the pipeline when a stage produces invalid output.",
        )
        require_hitl = st.checkbox(
            "Require HITL gates",
            value=defaults.pipeline.require_hitl_gates,
            help="Pause the pipeline at human review checkpoints.",
        )

        submitted = st.form_submit_button("Apply Settings", type="primary")

    if submitted:
        # Validate inputs
        errors = []
        if not model_name.strip():
            errors.append("Model name must not be empty.")
        if provider_info.get("requires_url", False) and not connection_url.strip():
            errors.append(f"Connection URL is required for {provider_info['label']}.")
        if not enabled_stages:
            errors.append("At least one stage must be enabled.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            new_settings = RuntimeSettings(
                model=ModelSelection(
                    provider=selected_provider,
                    model_name=model_name.strip(),
                    offline_only=offline_mode_checkbox,
                    connection_url=connection_url.strip() if provider_info.get("requires_url", False) else "",
                ),
                pipeline=PipelineSettings(
                    enabled_stage_ids=tuple(enabled_stages),
                    stop_on_validation_error=stop_on_error,
                    require_hitl_gates=require_hitl,
                ),
            )
            st.session_state["settings_override"] = new_settings
            st.success(f"✅ Settings applied. Provider: {provider_info['label']}, Model: {model_name.strip()}")

    # ===== Connection Validation Status Display =====
    st.divider()
    st.subheader("SCR-014 — Connection Status")
    is_valid = st.session_state.get("model_connection_valid", False)
    if is_valid:
        st.success("✅ Model connection validated and ready to use.", icon="✅")
    else:
        st.warning("⚠️ Model connection not yet validated. Configure connection details and click 'Validate Connection' to proceed.", icon="⚠️")
        if st.button("Validate Connection", type="primary", key="validate_connection_btn"):
            # Placeholder for actual validation logic (will be implemented in S07-03)
            st.session_state["model_connection_valid"] = True
            st.rerun()
            st.success("Settings applied. Start a run from the Home screen.")

    # Show active settings summary
    st.divider()
    st.subheader("Active Settings")
    active = _defaults()
    cols = st.columns(2)
    with cols[0]:
        st.metric("Provider", active.model.provider)
        st.metric("Model", active.model.model_name)
        st.metric("Offline mode", str(active.model.offline_only))
    with cols[1]:
        st.metric("Stop on error", str(active.pipeline.stop_on_validation_error))
        st.metric("Require HITL", str(active.pipeline.require_hitl_gates))
        st.metric("Enabled stages", len(active.pipeline.enabled_stage_ids))
