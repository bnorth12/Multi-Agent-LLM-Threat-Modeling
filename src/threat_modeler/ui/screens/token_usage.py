"""SCR-014 — Token Usage screen.

Displays per-stage token usage and aggregate run totals for live LLM calls.
Also shows gate-to-stage mapping so analysts can inspect guarded-stage usage.
"""

from __future__ import annotations

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


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _stage_usage_rows(state: Any) -> list[dict[str, Any]]:
    usage_by_stage = getattr(state, "llm_usage_by_stage", {}) or {}
    attempts_by_stage = getattr(state, "llm_attempts_by_stage", {}) or {}
    rows: list[dict[str, Any]] = []

    stage_ids = sorted(set(list(usage_by_stage.keys()) + list(attempts_by_stage.keys())))
    for stage_id in stage_ids:
        entries = usage_by_stage.get(stage_id, [])
        attempts = attempts_by_stage.get(stage_id, [])
        prompt_tokens = 0
        completion_tokens = 0
        reasoning_tokens = 0
        cached_tokens = 0
        total_tokens = 0
        models: set[str] = set()
        modes: set[str] = set()

        for entry in entries or []:
            prompt_tokens += _safe_int(entry.get("prompt_tokens", 0))
            completion_tokens += _safe_int(entry.get("completion_tokens", 0))
            reasoning_tokens += _safe_int(entry.get("reasoning_tokens", 0))
            cached_tokens += _safe_int(entry.get("cached_tokens", 0))
            total_tokens += _safe_int(entry.get("total_tokens", 0))
            model = str(entry.get("model", "")).strip()
            if model:
                models.add(model)
            mode = str(entry.get("endpoint_mode", "")).strip()
            if mode:
                modes.add(mode)

        rows.append(
            {
                "Stage": _STAGE_LABELS.get(stage_id, stage_id),
                "Stage ID": stage_id,
                "Attempts": len(attempts or []),
                "Requests": len(entries or []),
                "Prompt Tokens": prompt_tokens,
                "Completion Tokens": completion_tokens,
                "Reasoning Tokens": reasoning_tokens,
                "Cached Tokens": cached_tokens,
                "Total Tokens": total_tokens,
                "Model(s)": ", ".join(sorted(models)) or "-",
                "Endpoint Mode(s)": ", ".join(sorted(modes)) or "-",
            }
        )

    rows.sort(key=lambda r: r["Stage ID"])
    return rows


def _gate_usage_rows(state: Any) -> list[dict[str, Any]]:
    checkpoint = getattr(state, "hitl_gate_checkpoint", {}) or {}
    gates = checkpoint.get("gates", {}) if isinstance(checkpoint, dict) else {}
    usage_by_stage = getattr(state, "llm_usage_by_stage", {}) or {}

    rows: list[dict[str, Any]] = []
    for gate_id, gate in gates.items():
        if not isinstance(gate, dict):
            continue
        stage_id = str(gate.get("stage_id", "")).strip()
        entries = usage_by_stage.get(stage_id, []) if stage_id else []
        total_tokens = sum(_safe_int(e.get("total_tokens", 0)) for e in entries)
        rows.append(
            {
                "Gate": gate_id,
                "Status": str(gate.get("status", "pending")),
                "Guarded Stage": _STAGE_LABELS.get(stage_id, stage_id or "-"),
                "Stage Requests": len(entries),
                "Stage Total Tokens": total_tokens,
            }
        )

    rows.sort(key=lambda r: r["Gate"])
    return rows


def render() -> None:
    sync_execution_state_to_session()

    st.header("Token Usage")
    st.caption("SCR-014 — LLM token usage by stage and gate context")

    run_id = st.session_state.get("run_id")
    pipeline_state = st.session_state.get("pipeline_state")

    if run_id:
        st.info(f"Active run: {run_id}")

    if pipeline_state is None:
        st.warning("No active pipeline state. Run the pipeline first.")
        return

    totals = pipeline_state.llm_usage_totals() if hasattr(pipeline_state, "llm_usage_totals") else {}
    attempt_totals = pipeline_state.llm_attempt_totals() if hasattr(pipeline_state, "llm_attempt_totals") else {}
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tokens", _safe_int(totals.get("total_tokens", 0)))
    col2.metric("Prompt Tokens", _safe_int(totals.get("prompt_tokens", 0)))
    col3.metric("Completion Tokens", _safe_int(totals.get("completion_tokens", 0)))

    col4, col5, col6 = st.columns(3)
    col4.metric("Reasoning Tokens", _safe_int(totals.get("reasoning_tokens", 0)))
    col5.metric("Cached Tokens", _safe_int(totals.get("cached_tokens", 0)))
    col6.metric("LLM Requests", _safe_int(totals.get("request_count", 0)))

    col7, col8, col9 = st.columns(3)
    col7.metric("Attempted Requests", _safe_int(attempt_totals.get("submitted", 0)))
    col8.metric("Completed Attempts", _safe_int(attempt_totals.get("completed", 0)))
    col9.metric("Failed Attempts", _safe_int(attempt_totals.get("failed", 0)))

    st.divider()
    st.subheader("Usage by Stage")
    stage_rows = _stage_usage_rows(pipeline_state)
    if stage_rows:
        st.dataframe(stage_rows, use_container_width=False, width=1400, hide_index=True)
    else:
        st.caption("No live token usage has been recorded yet. Run a live provider pipeline to populate this table.")

    st.divider()
    st.subheader("Gate Context")
    gate_rows = _gate_usage_rows(pipeline_state)
    if gate_rows:
        st.dataframe(gate_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No gate checkpoint data available for this run.")
