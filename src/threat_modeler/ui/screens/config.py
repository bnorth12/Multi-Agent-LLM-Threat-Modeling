"""SCR-003 — Pipeline Configuration.

Renders a form pre-populated from build_default_settings() that lets the
analyst override ModelSelection fields and the enabled stage list. The
resulting RuntimeSettings is stored in st.session_state["settings_override"]
for use when a run is started.
"""

import streamlit as st

from threat_modeler.config import (
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
    """Render SCR-003 Pipeline Configuration."""
    st.header("Pipeline Configuration")
    st.caption("SCR-003 — configure model and pipeline settings before starting a run")

    defaults = _defaults()

    with st.form("pipeline_config_form"):
        st.subheader("Model Selection")

        provider = st.text_input(
            "Provider",
            value=defaults.model.provider,
            help="LLM provider identifier, e.g. 'xai' or 'unconfigured' for fixture mode.",
        )
        model_name = st.text_input(
            "Model name",
            value=defaults.model.model_name,
            help="Model name passed to the provider, e.g. 'grok-3-mini'.",
        )
        offline_only = st.checkbox(
            "Offline / fixture mode (no live LLM calls)",
            value=defaults.model.offline_only,
            help="When checked, FixtureAdapter is used and no API key is required.",
        )

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
        if not provider.strip():
            st.error("Provider must not be empty.")
        elif not model_name.strip():
            st.error("Model name must not be empty.")
        elif not enabled_stages:
            st.error("At least one stage must be enabled.")
        else:
            new_settings = RuntimeSettings(
                model=ModelSelection(
                    provider=provider.strip(),
                    model_name=model_name.strip(),
                    offline_only=offline_only,
                ),
                pipeline=PipelineSettings(
                    enabled_stage_ids=tuple(enabled_stages),
                    stop_on_validation_error=stop_on_error,
                    require_hitl_gates=require_hitl,
                ),
            )
            st.session_state["settings_override"] = new_settings
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
