"""Debug utilities for Streamlit UI - exception logging and state tracing."""

import traceback
from typing import Any, Callable, Optional

import streamlit as st


def log_exception(
    error: Exception,
    context: str = "",
    show_traceback: bool = True,
    severity: str = "error",
) -> str:
    """Log exception with context and optionally show traceback to user.

    Args:
        error: The exception to log
        context: Context description for the error
        show_traceback: Whether to display full traceback
        severity: 'error', 'warning', or 'info'

    Returns:
        Formatted error message
    """
    tb_str = traceback.format_exc()
    error_msg = f"{context}\n\n**Error:** {type(error).__name__}: {str(error)}"

    if show_traceback:
        error_msg += f"\n\n```\n{tb_str}\n```"

    if severity == "error":
        st.error(error_msg)
    elif severity == "warning":
        st.warning(error_msg)
    else:
        st.info(error_msg)

    return error_msg


def validate_settings(settings: Any, stage: str = "") -> tuple[bool, str]:
    """Validate RuntimeSettings and return (is_valid, message).

    Args:
        settings: The RuntimeSettings object to validate
        stage: Description of what stage we're in

    Returns:
        Tuple of (is_valid, message)
    """
    if settings is None:
        return False, f"❌ {stage} - Settings are None"

    try:
        model = getattr(settings, "model", None)
        if model is None:
            return False, f"❌ {stage} - Model settings missing"

        provider = getattr(model, "provider", None)
        model_name = getattr(model, "model_name", None)
        offline = getattr(model, "offline_only", True)

        if not provider:
            return False, f"❌ {stage} - Provider not set"
        if not model_name:
            return False, f"❌ {stage} - Model name not set"

        return True, f"✅ {stage} - Settings valid (provider={provider}, model={model_name}, offline={offline})"
    except Exception as e:
        return False, f"❌ {stage} - Settings validation failed: {str(e)}"


def log_state_change(key: str, value: Any, action: str = "set") -> None:
    """Log a session state change (stored in debug history).

    Args:
        key: Session state key
        value: New value
        action: 'set', 'update', or 'delete'
    """
    if "_debug_history" not in st.session_state:
        st.session_state["_debug_history"] = []

    history_entry = {
        "action": action,
        "key": key,
        "value": str(value)[:100],  # Truncate for readability
        "timestamp": len(st.session_state["_debug_history"]),
    }
    st.session_state["_debug_history"].append(history_entry)


def show_debug_panel() -> None:
    """Display debug panel with history and current state."""
    with st.expander("🐛 Debug Info (Dev Only)", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Run ID", st.session_state.get("run_id", "none")[:8])
        with col2:
            st.metric("Settings Applied", "✅" if st.session_state.get("settings_override") else "❌")
        with col3:
            st.metric("Model Validated", "✅" if st.session_state.get("model_connection_valid") else "❌")

        st.subheader("Session State Keys")
        state_summary = {
            k: f"{str(v)[:50]}..." if len(str(v)) > 50 else str(v)
            for k, v in st.session_state.items()
            if not k.startswith("_")
        }
        st.json(state_summary)

        if "_debug_history" in st.session_state:
            st.subheader("State Changes History")
            st.dataframe(st.session_state["_debug_history"], use_container_width=True)


def wrap_execution(
    func: Callable,
    context: str = "",
    show_debug: bool = True,
) -> Any:
    """Wrap a function call with exception logging and state tracking.

    Args:
        func: Function to execute
        context: Context description
        show_debug: Whether to show debug panel on error

    Returns:
        Function result or None if error
    """
    try:
        return func()
    except Exception as e:
        error_msg = log_exception(e, context=context, show_traceback=True)
        st.session_state["last_error"] = error_msg
        if show_debug:
            show_debug_panel()
        return None
