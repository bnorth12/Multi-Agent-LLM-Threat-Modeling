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
    LIVE_LLM_DEFAULT_MAX_ATTEMPTS,
    LIVE_LLM_DEFAULT_TIMEOUT_SECONDS,
    PROVIDER_MATRIX,
    ModelSelection,
    PipelineSettings,
    RuntimeSettings,
    build_default_settings,
)
from threat_modeler.backend.runtime_state import (
    get_last_settings,
    remember_settings,
    remember_validation_state,
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
    "xai": "GROK_API",
    "azure": "AZURE_OPENAI_API_KEY",
    "custom": "CUSTOM_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "fixture": "",
}

_API_KEY_ENV_CANDIDATES = {
    "xai": ("GROK_API", "XAI_API_KEY"),
}

_PROVIDER_MODEL_CATALOGS = {
    "fixture": ["fixture-placeholder"],
    "openai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini", "o4-mini", "o3"],
    "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-haiku-20241022"],
    "xai": [
        "grok-4",
        "grok-4.3",
        "grok-4.20-multi-agent-0309",
        "grok-4.20-0309-reasoning",
        "grok-4.20-0309-non-reasoning",
        "grok-4-1-fast-reasoning",
        "grok-4-1-fast-non-reasoning",
    ],
    "azure": ["gpt-4.1", "gpt-4o", "o4-mini"],
    "ollama": ["llama3.1:8b", "llama3.1:70b", "qwen2.5:14b", "mistral:latest"],
    "custom": ["<Custom model>"],
}

_ENDPOINT_MODES = ["chat_completions", "responses", "multi_agent"]


def _api_key_env_var(provider: str) -> str:
    return _API_KEY_ENV_VARS.get(provider, f"{provider.upper()}_API_KEY")


def _api_key_env_candidates(provider: str) -> tuple[str, ...]:
    return _API_KEY_ENV_CANDIDATES.get(provider, (_api_key_env_var(provider),))


def _defaults() -> RuntimeSettings:
    def _migrate_legacy_timeout_attempts(settings: RuntimeSettings) -> RuntimeSettings:
        # Migrate historical defaults (180s/3 attempts) to the new baseline (900s/2 attempts)
        # when the values appear untouched from older builds.
        timeout = int(getattr(settings.model, "request_timeout_seconds", LIVE_LLM_DEFAULT_TIMEOUT_SECONDS))
        attempts = int(getattr(settings.model, "request_max_attempts", LIVE_LLM_DEFAULT_MAX_ATTEMPTS))
        if timeout == 180 and attempts == 3:
            migrated_model = ModelSelection(
                provider=settings.model.provider,
                model_name=settings.model.model_name,
                offline_only=settings.model.offline_only,
                connection_url=settings.model.connection_url,
                endpoint_mode=getattr(settings.model, "endpoint_mode", "chat_completions"),
                request_timeout_seconds=LIVE_LLM_DEFAULT_TIMEOUT_SECONDS,
                request_max_attempts=LIVE_LLM_DEFAULT_MAX_ATTEMPTS,
            )
            return RuntimeSettings(model=migrated_model, pipeline=settings.pipeline)
        return settings

    override = st.session_state.get("settings_override")
    recovered = get_last_settings()
    if isinstance(override, RuntimeSettings):
        override = _migrate_legacy_timeout_attempts(override)
        st.session_state["settings_override"] = override
    if isinstance(recovered, RuntimeSettings):
        recovered = _migrate_legacy_timeout_attempts(recovered)
    if isinstance(override, RuntimeSettings):
        if isinstance(recovered, RuntimeSettings):
            override_live = not override.model.offline_only and override.model.provider != "fixture"
            recovered_live = not recovered.model.offline_only and recovered.model.provider != "fixture"
            if recovered_live and not override_live:
                st.session_state["settings_override"] = recovered
                return recovered
        return override
    if isinstance(recovered, RuntimeSettings):
        st.session_state["settings_override"] = recovered
        return recovered
    return build_default_settings()


def _provider_scoped_model_defaults(
    defaults: RuntimeSettings,
    selected_provider: str,
) -> tuple[str, str, str, bool, int, int]:
    if defaults.model.provider == selected_provider:
        return (
            defaults.model.model_name.strip(),
            defaults.model.connection_url,
            getattr(defaults.model, "endpoint_mode", "chat_completions"),
            defaults.model.offline_only,
            max(1, int(getattr(defaults.model, "request_timeout_seconds", LIVE_LLM_DEFAULT_TIMEOUT_SECONDS))),
            max(1, int(getattr(defaults.model, "request_max_attempts", LIVE_LLM_DEFAULT_MAX_ATTEMPTS))),
        )
    return (
        str(PROVIDER_MATRIX.get(selected_provider, {}).get("default_model", "")).strip(),
        "",
        "chat_completions",
        False,
        LIVE_LLM_DEFAULT_TIMEOUT_SECONDS,
        LIVE_LLM_DEFAULT_MAX_ATTEMPTS,
    )


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
    provider_widget_key = "config_selected_provider"
    desired_provider = defaults.model.provider if defaults.model.provider in PROVIDER_MATRIX else provider_keys[0]
    current_provider = st.session_state.get(provider_widget_key)
    if current_provider not in PROVIDER_MATRIX:
        st.session_state[provider_widget_key] = desired_provider

    default_provider = st.session_state.get(provider_widget_key, desired_provider)

    selected_provider = st.selectbox(
        "Provider",
        options=provider_keys,
        key=provider_widget_key,
        format_func=lambda x: provider_options[x],
        index=provider_keys.index(default_provider),
        help="Select the LLM provider to use.",
    )
    st.caption(
        "Provider selection updates the draft form immediately. Click Apply Settings to commit changes to backend state."
    )

    # Show provider description
    provider_info = PROVIDER_MATRIX.get(selected_provider, {})
    if provider_info:
        st.info(f"**{provider_info['label']}**: {provider_info['description']}")

    api_key_input = ""
    (
        scoped_model_name,
        scoped_connection_url,
        scoped_endpoint_mode,
        scoped_offline_only,
        scoped_timeout_seconds,
        scoped_max_attempts,
    ) = _provider_scoped_model_defaults(
        defaults,
        selected_provider,
    )
    with st.form("pipeline_config_form"):
        # Model name selector + editable override
        model_catalog = list(_PROVIDER_MODEL_CATALOGS.get(selected_provider, []))
        default_model = scoped_model_name or provider_info.get("default_model", "")

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
                placeholder="e.g., grok-4-reasoning or intranet-agent-v2",
                help="Editable override for custom/intranet or newly released models.",
            )

        # ===== SCR-013: Connection Details =====
        st.subheader("SCR-013 — Connection Details")

        connection_url = scoped_connection_url
        if selected_provider != "fixture":
            connection_url = st.text_input(
                "Connection URL",
                value=scoped_connection_url,
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
            index=_ENDPOINT_MODES.index(scoped_endpoint_mode)
            if scoped_endpoint_mode in _ENDPOINT_MODES
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

        force_offline_fixture = selected_provider == "fixture"
        offline_mode_checkbox = st.checkbox(
            "Offline/Fixture mode (no live LLM calls)",
            value=True if force_offline_fixture else scoped_offline_only,
            disabled=force_offline_fixture,
            help=(
                "Local/Fixture provider always runs offline. Select a live provider above to enable live LLM mode."
                if force_offline_fixture
                else "When checked, uses deterministic fixture data instead of calling a live LLM."
            ),
        )
        if force_offline_fixture:
            st.caption("Local/Fixture is always offline. Choose a live provider above, then click Apply Settings.")

        st.subheader("Live Request Reliability")
        request_timeout_seconds = st.number_input(
            "Request timeout per attempt (seconds)",
            min_value=30,
            max_value=900,
            step=30,
            value=int(scoped_timeout_seconds),
            help="Maximum wait time for one provider request attempt before retry/failure.",
            disabled=selected_provider == "fixture",
        )
        request_max_attempts = st.number_input(
            "Max retry attempts",
            min_value=1,
            max_value=6,
            step=1,
            value=int(scoped_max_attempts),
            help="How many total attempts are made before failing a stage request.",
            disabled=selected_provider == "fixture",
        )

        # ===== Pipeline Settings =====
        st.subheader("Pipeline Settings")

        # Always show all stages enabled by default in the form
        default_enabled = list(_ALL_STAGES)
        st.write("**Enabled stages** — Check which pipeline stages to execute:")
        st.caption("All stages are enabled by default. Uncheck to skip any stage during the run.")

        # Display stages in 3-column layout for better readability
        cols = st.columns(3)
        stage_checkboxes = {}
        for idx, stage_id in enumerate(_ALL_STAGES):
            col = cols[idx % 3]
            stage_label = _STAGE_LABELS.get(stage_id, stage_id)
            with col:
                stage_checkboxes[stage_id] = st.checkbox(
                    stage_label,
                    value=stage_id in default_enabled,
                    key=f"stage_checkbox_{stage_id}",
                    help=f"Enable/disable {stage_label}",
                )

        # Collect enabled stages from checkboxes
        enabled_stages = [stage_id for stage_id, is_checked in stage_checkboxes.items() if is_checked]

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
        if selected_provider == "fixture" and not offline_mode_checkbox:
            errors.append("Local/Fixture provider must run in offline mode. Select a live provider to enable live LLM mode.")

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
                    request_timeout_seconds=int(request_timeout_seconds),
                    request_max_attempts=int(request_max_attempts),
                ),
                pipeline=PipelineSettings(
                    execution_mode="langgraph-compatible",
                    enabled_stage_ids=tuple(enabled_stages),
                    stop_on_validation_error=stop_on_error,
                    require_hitl_gates=require_hitl,
                ),
            )
            st.session_state["settings_override"] = new_settings
            remember_settings(new_settings)
            st.session_state["model_connection_valid"] = False
            st.session_state["offline_override_active"] = False
            remember_validation_state(False, offline_override=False)

            if provider_info.get("requires_api_key", False):
                key_value = api_key_input.strip()
                st.session_state["model_api_key"] = key_value
                if key_value:
                    for env_var in _api_key_env_candidates(selected_provider):
                        if env_var:
                            os.environ[env_var] = key_value

            st.success(f"✅ Settings applied. Provider: {provider_info['label']}, Model: {model_name.strip()}")

    # ===== SCR-014: Connection Validation =====
    st.divider()
    st.subheader("SCR-014 — Connection Validation")

    if selected_provider != defaults.model.provider:
        st.info(
            f"Pending draft provider: {provider_options.get(selected_provider, selected_provider)}. "
            "Click Apply Settings before validating or starting a run."
        )

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
        st.session_state["offline_override_active"] = False
        remember_validation_state(True, offline_override=False)
    elif is_valid:
        active_info = PROVIDER_MATRIX.get(active.model.provider, {})
        st.success(
            f"✅ **Validated**: {active_info.get('label', active.model.provider)} / "
            f"{active.model.model_name} — connection is ready."
        )
        if st.button("Re-validate", key="revalidate_btn"):
            st.session_state["model_connection_valid"] = False
            st.session_state["offline_override_active"] = False
            remember_validation_state(False, offline_override=False)
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

                # Resolve API key: UI input first, then environment.
                resolved_key = stored_key.strip()
                if not resolved_key:
                    for env_var in _api_key_env_candidates(active.model.provider):
                        resolved_key = os.environ.get(env_var, "").strip()
                        if resolved_key:
                            break

                with st.spinner("Checking connection…"):
                    result = validate_connection(active.model, api_key=resolved_key)

                if result.ok:
                    st.session_state["model_connection_valid"] = True
                    st.session_state["offline_override_active"] = False
                    remember_validation_state(True, offline_override=False)
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
                remember_validation_state(True, offline_override=True)
                st.rerun()

    # Show active settings summary
    st.divider()
    st.subheader("Applied Backend Settings")
    st.caption("These values show the settings currently committed to backend state.")
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
