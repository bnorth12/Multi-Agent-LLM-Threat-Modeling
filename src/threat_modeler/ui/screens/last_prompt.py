"""SCR-015 — Last Prompt screen.

Displays the last prompt payload submitted to an LLM call so operators can
troubleshoot timeout and provider failures.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session

_STAGE_LABELS: dict[str, str] = {
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


def _request_payload(prompt: dict[str, Any]) -> dict[str, Any]:
    mode = str(prompt.get("endpoint_mode", "")).strip().lower()
    base = {"model": str(prompt.get("model", "")).strip()}

    if mode in ("responses", "multi_agent"):
        base["input"] = [
            {"role": "system", "content": prompt.get("system_prompt", "")},
            {"role": "user", "content": prompt.get("user_message", "")},
        ]
        return base

    base["messages"] = [
        {"role": "system", "content": prompt.get("system_prompt", "")},
        {"role": "user", "content": prompt.get("user_message", "")},
    ]
    return base


def _prompt_for_selection(state: Any, selection: str) -> dict[str, Any] | None:
    if selection == "Latest across all stages":
        if hasattr(state, "latest_llm_prompt"):
            return state.latest_llm_prompt()
        history = getattr(state, "llm_prompt_history", []) or []
        return dict(history[-1]) if history else None

    stage_id = selection.split(" ", 1)[0]
    if hasattr(state, "latest_llm_prompt"):
        return state.latest_llm_prompt(stage_id)

    by_stage = getattr(state, "llm_prompts_by_stage", {}) or {}
    entries = by_stage.get(stage_id, [])
    return dict(entries[-1]) if entries else None


def _latest_attempt_for_prompt(state: Any, selected_prompt: dict[str, Any]) -> dict[str, Any] | None:
    stage_id = str(selected_prompt.get("stage_id", "")).strip()
    prompt_record_id = str(selected_prompt.get("prompt_record_id", "")).strip()
    if not stage_id or not prompt_record_id:
        return None
    by_stage = getattr(state, "llm_attempts_by_stage", {}) or {}
    entries = by_stage.get(stage_id, [])
    if not entries:
        return None
    for entry in reversed(entries):
        if str(entry.get("prompt_record_id", "")).strip() == prompt_record_id:
            return dict(entry)
    return None


def render() -> None:
    sync_execution_state_to_session()

    st.header("Last Prompt")
    st.caption("SCR-015 — Prompt payload diagnostics for timeout troubleshooting")

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")

    if run_id:
        st.info(f"Active run: {run_id}")

    if pipeline_state is None:
        st.warning("No active pipeline state. Run the pipeline first.")
        return

    prompts_by_stage = getattr(pipeline_state, "llm_prompts_by_stage", {}) or {}
    prompt_history = getattr(pipeline_state, "llm_prompt_history", []) or []
    if not prompts_by_stage and not prompt_history:
        st.caption("No prompt payloads have been recorded yet.")
        return

    stage_options = ["Latest across all stages"]
    for stage_id in sorted(prompts_by_stage.keys()):
        stage_options.append(f"{stage_id} · {_STAGE_LABELS.get(stage_id, stage_id)}")

    selection = st.selectbox("Prompt scope", options=stage_options, index=0)
    selected_prompt = _prompt_for_selection(pipeline_state, selection)
    if not selected_prompt:
        st.caption("No prompt data available for the selected scope.")
        return

    stage_id = str(selected_prompt.get("stage_id", ""))
    st.subheader(_STAGE_LABELS.get(stage_id, stage_id or "Unknown Stage"))

    col1, col2, col3 = st.columns(3)
    col1.metric("Provider", str(selected_prompt.get("provider", "-")) or "-")
    col2.metric("Endpoint Mode", str(selected_prompt.get("endpoint_mode", "-")) or "-")
    col3.metric("Model", str(selected_prompt.get("model", "-")) or "-")

    col4, col5 = st.columns(2)
    col4.metric("System Prompt Chars", int(selected_prompt.get("system_prompt_chars", 0) or 0))
    col5.metric("User Message Chars", int(selected_prompt.get("user_message_chars", 0) or 0))

    st.divider()
    st.subheader("System Prompt")
    st.text_area(
        "System prompt body",
        value=str(selected_prompt.get("system_prompt", "")),
        height=260,
        disabled=True,
        label_visibility="collapsed",
    )

    st.subheader("User Message")
    st.text_area(
        "User message body",
        value=str(selected_prompt.get("user_message", "")),
        height=320,
        disabled=True,
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("Reconstructed Request Payload")
    st.code(
        json.dumps(_request_payload(selected_prompt), indent=2, ensure_ascii=False),
        language="json",
    )

    latest_attempt = _latest_attempt_for_prompt(pipeline_state, selected_prompt)
    if latest_attempt:
        st.divider()
        st.subheader("Model Result")

        status = str(latest_attempt.get("status", "unknown")).upper()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Attempt Status", status)
        col_b.metric("Provider", str(latest_attempt.get("provider", "-")) or "-")
        col_c.metric("Model", str(latest_attempt.get("model", "-")) or "-")

        response_text = str(latest_attempt.get("response_text", "") or "")
        response_preview = str(latest_attempt.get("response_preview", "") or "")
        if response_text or response_preview:
            st.caption("Latest response captured from this stage.")
            st.text_area(
                "LLM response",
                value=response_text or response_preview,
                height=320,
                disabled=True,
            )

        error_text = str(latest_attempt.get("error", "") or "")
        if error_text:
            st.error("Latest provider error for this stage")
            st.text_area(
                "Provider error",
                value=error_text,
                height=140,
                disabled=True,
            )
