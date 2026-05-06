"""SCR-003 — Pipeline Configuration with SCR-012/013 Model Selection and Connection Details.

Renders configuration form with:
- SCR-012: Model provider selection (dropdown with Custom/Intranet support)
- SCR-013: Model connection details (URL for providers that need it)
- Pipeline settings (stage selection, error handling, HITL gates)

The resulting RuntimeSettings is stored in st.session_state["settings_override"]
and connection validation state is stored in st.session_state["model_connection_valid"].
"""

import os

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

_API_KEY_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "xai": "XAI_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "custom": "CUSTOM_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "fixture": "",
}

_PROVIDER_MODEL_CATALOGS = {
    "fixture": ["fixture-placeholder"],
    "openai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini", "o4-mini", "o3"],
    "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-haiku-20241022"],
    "xai": ["grok-3", "grok-3-mini", "grok-3-reasoning"],
    "azure": ["gpt-4.1", "gpt-4o", "o4-mini"],
    "ollama": ["llama3.1:8b", "llama3.1:70b", "qwen2.5:14b", "mistral:latest"],
    "custom": ["<Custom model>"],
}

_ENDPOINT_MODES = ["chat_completions", "responses", "multi_agent"]


def _api_key_env_var(provider: str) -> str:
    return _API_KEY_ENV_VARS.get(provider, f"{provider.upper()}_API_KEY")


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

    # ===== SCR-012: Model Provider Selection =====
    st.subheader("SCR-012 — Model Provider Selection")
    st.write("Choose an LLM provider to use for this threat modeling run.")

    provider_options = {prov_key: f"{meta['label']}" for prov_key, meta in PROVIDER_MATRIX.items()}
    provider_keys = list(PROVIDER_MATRIX.keys())
    default_provider = st.session_state.get("config_selected_provider", defaults.model.provider)
    if default_provider not in PROVIDER_MATRIX:
        default_provider = provider_keys[0]

    selected_provider = st.selectbox(
        "Provider",
        options=provider_keys,
        key="config_selected_provider",
        format_func=lambda x: provider_options[x],
        index=provider_keys.index(default_provider),
        help="Select the LLM provider to use.",
    )

    # Show provider description
    provider_info = PROVIDER_MATRIX.get(selected_provider, {})
    if provider_info:
        st.info(f"**{provider_info['label']}**: {provider_info['description']}")

    api_key_input = ""
    with st.form("pipeline_config_form"):
        # Model name selector + editable override
        model_catalog = list(_PROVIDER_MODEL_CATALOGS.get(selected_provider, []))
        default_model = defaults.model.model_name.strip() or provider_info.get("default_model", "")

        if default_model and default_model not in model_catalog and "<Custom model>" not in model_catalog:
            model_catalog.append("<Custom model>")

        if not model_catalog:
            model_catalog = [default_model or provider_info.get("default_model", ""), "<Custom model>"]

        model_select_options = model_catalog
        if default_model in model_select_options:
            model_index = model_select_options.index(default_model)
        elif "<Custom model>" in model_select_options:
            model_index = model_select_options.index("<Custom model>")
        else:
            model_index = 0

        selected_model_catalog = st.selectbox(
            "Model catalog",
            options=model_select_options,
            index=model_index,
            help="Select a known model for this provider or choose <Custom model>.",
        )

        model_name = selected_model_catalog
        if selected_model_catalog == "<Custom model>":
            model_name = st.text_input(
                "Custom model name",
                value=default_model if default_model not in ("", "<Custom model>") else "",
                placeholder="e.g., grok-3-reasoning or intranet-agent-v2",
                help="Editable override for custom/intranet or newly released models.",
            )

        # ===== SCR-013: Connection Details =====
        st.subheader("SCR-013 — Connection Details")

        connection_url = defaults.model.connection_url
        if selected_provider != "fixture":
            connection_url = st.text_input(
                "Connection URL",
                value=defaults.model.connection_url,
                placeholder=(
                    "Required endpoint URL"
                    if provider_info.get("requires_url", False)
                    else "Optional base URL override (leave blank for provider default)"
                ),
                help=f"Connection URL or endpoint for {provider_info['label']} (including intranet endpoints).",
            )
            st.caption("This URL is used to connect to the LLM provider. It will be securely stored in session state.")

        endpoint_mode = st.selectbox(
            "Endpoint mode",
            options=_ENDPOINT_MODES,
            index=_ENDPOINT_MODES.index(getattr(defaults.model, "endpoint_mode", "chat_completions"))
            if getattr(defaults.model, "endpoint_mode", "chat_completions") in _ENDPOINT_MODES
            else 0,
            help=(
                "chat_completions: OpenAI-style /chat/completions. "
                "responses: modern reasoning endpoint. "
                "multi_agent: non-completions orchestration endpoint (mapped via Responses API flow)."
            ),
        )

        api_key_required = provider_info.get("requires_api_key", False)
        api_key_input = st.text_input(
            "API key",
            value=st.session_state.get("model_api_key", ""),
            type="password",
            placeholder=(
                "Enter API key for the selected provider"
                if api_key_required
                else "Not required for selected provider"
            ),
            disabled=not api_key_required,
            help="Session-only secret used for live LLM calls and connection validation.",
        )
        if api_key_required:
            st.caption(
                "API key is kept in session state only (never written to repository files). "
                "You may also provide the key via environment variable."
            )
        else:
            st.caption("API key is optional/not required for the selected provider.")

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
                    connection_url=connection_url.strip(),
                    endpoint_mode=endpoint_mode,
                ),
                pipeline=PipelineSettings(
                    enabled_stage_ids=tuple(enabled_stages),
                    stop_on_validation_error=stop_on_error,
                    require_hitl_gates=require_hitl,
                ),
            )
            st.session_state["settings_override"] = new_settings
            st.session_state["model_connection_valid"] = False
            st.session_state["offline_override_active"] = False

            if provider_info.get("requires_api_key", False):
                key_value = api_key_input.strip()
                st.session_state["model_api_key"] = key_value
                if key_value:
                    env_var = _api_key_env_var(selected_provider)
                    if env_var:
                        os.environ[env_var] = key_value

            st.success(f"✅ Settings applied. Provider: {provider_info['label']}, Model: {model_name.strip()}")

    # ===== SCR-014: Connection Validation =====
    st.divider()
    st.subheader("SCR-014 — Connection Validation")

    active = _defaults()
    is_fixture = active.model.offline_only or active.model.provider == "fixture"
    is_valid = st.session_state.get("model_connection_valid", False)

    if is_fixture:
        st.info(
            "**Offline/Fixture mode** — no connection validation required. "
            "The pipeline will use deterministic fixture data."
        )
        # Fixture mode is always considered valid
        st.session_state["model_connection_valid"] = True
    elif is_valid:
        active_info = PROVIDER_MATRIX.get(active.model.provider, {})
        st.success(
            f"✅ **Validated**: {active_info.get('label', active.model.provider)} / "
            f"{active.model.model_name} — connection is ready."
        )
        if st.button("Re-validate", key="revalidate_btn"):
            st.session_state["model_connection_valid"] = False
            st.rerun()
    else:
        st.warning(
            "⚠️ Model connection not yet validated. Apply settings above, then click "
            "**Validate Connection** to confirm the endpoint is reachable before running."
        )

        stored_key = st.session_state.get("model_api_key", "")
        active_provider_info = PROVIDER_MATRIX.get(active.model.provider, {})
        if active_provider_info.get("requires_api_key", False):
            if stored_key.strip():
                st.caption("API key found in current session for selected provider.")
            else:
                st.caption(
                    "No API key stored in session. Set it in SCR-013 or via environment variable."
                )

        col_validate, col_override = st.columns(2)
        with col_validate:
            if st.button("Validate Connection", type="primary", key="validate_connection_btn"):
                from threat_modeler.ui.connection_validator import validate_connection  # noqa: PLC0415

                # Resolve API key: UI input first, then environment
                env_var = _api_key_env_var(active.model.provider)
                resolved_key = stored_key.strip() or os.environ.get(env_var, "")

                with st.spinner("Checking connection…"):
                    result = validate_connection(active.model, api_key=resolved_key)

                if result.ok:
                    st.session_state["model_connection_valid"] = True
                    st.rerun()
                else:
                    st.error(f"❌ {result.message}")
                    if result.detail:
                        st.caption(result.detail)

        with col_override:
            if st.button(
                "Use Offline Override",
                key="offline_override_btn",
                help="Mark connection valid for offline/testing use without a live API key.",
            ):
                st.session_state["model_connection_valid"] = True
                st.session_state["offline_override_active"] = True
                st.rerun()

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
        st.metric("Endpoint mode", getattr(active.model, "endpoint_mode", "chat_completions"))
        st.metric("Stop on error", str(active.pipeline.stop_on_validation_error))
        st.metric("Require HITL", str(active.pipeline.require_hitl_gates))
    st.metric("Enabled stages", len(active.pipeline.enabled_stage_ids))
