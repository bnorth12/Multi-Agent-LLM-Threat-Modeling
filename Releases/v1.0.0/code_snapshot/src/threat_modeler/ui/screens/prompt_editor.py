"""SCR-010/011 — Prompt Editor and Version History screen.

SCR-010: Per-agent system prompt editor with temperature configuration.
SCR-011: Prompt version history, diff view, and rollback.

Access is controlled by role: only the "Author" role may edit and save prompts.
Reviewers and Approvers have read-only access.
"""

from __future__ import annotations

import streamlit as st

from threat_modeler.ui.prompt_store import (
    AGENT_IDS,
    AGENT_LABELS,
    get_default_prompt,
    get_history,
    get_prompt,
    get_temperature,
    is_modified,
    reset_to_default,
    revert_to,
    set_prompt,
    set_temperature,
)


def render() -> None:
    """Entry point called by app.py."""
    st.header("Prompt Editor")
    st.caption("SCR-010 — Per-agent prompt editor  ·  SCR-011 — Version history & rollback")

    role = st.session_state.get("role", "")
    can_edit = role == "Author"

    if not role:
        st.warning(
            "⚠️ No role selected — go to **Role Selection** first. "
            "Prompt editing requires the **Author** role."
        )
        return

    if not can_edit:
        st.info(
            f"ℹ️ Signed in as **{role}** — prompts are read-only. "
            "Only the **Author** role may edit and save prompts."
        )

    # ── Agent selector ────────────────────────────────────────────────────
    st.divider()

    agent_options = {AGENT_LABELS[a]: a for a in AGENT_IDS}
    selected_label = st.selectbox(
        "Select agent",
        options=list(agent_options.keys()),
        key="prompt_editor_agent_select",
    )
    selected_agent = agent_options[selected_label]
    modified_badge = " ✏️ modified" if is_modified(selected_agent) else ""
    st.caption(f"Agent ID: `{selected_agent}`{modified_badge}")

    tab_editor, tab_history = st.tabs(["SCR-010 — Prompt Editor", "SCR-011 — Version History"])

    # =========================================================================
    # SCR-010 — Prompt Editor
    # =========================================================================
    with tab_editor:
        _render_editor(selected_agent, can_edit, role)

    # =========================================================================
    # SCR-011 — Version History
    # =========================================================================
    with tab_history:
        _render_history(selected_agent, can_edit, role)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _render_editor(agent_id: str, can_edit: bool, role: str) -> None:
    """SCR-010: Prompt text area + temperature slider + save/reset controls."""
    from threat_modeler.ui.prompt_store import get_expected_output, set_expected_output

    current_prompt = get_prompt(agent_id)
    default_prompt = get_default_prompt(agent_id)
    # If default_prompt is a dict (from _DEFAULT_PROMPTS), extract the 'prompt' field
    if isinstance(default_prompt, dict):
        default_prompt = default_prompt.get("prompt", "")
    current_temp = get_temperature(agent_id)
    current_expected = get_expected_output(agent_id)

    st.subheader("System Prompt")
    edited_text = st.text_area(
        "System prompt text",
        value=current_prompt,
        height=260,
        disabled=not can_edit,
        key=f"prompt_text_{agent_id}",
        label_visibility="collapsed",
        help=(
            "The system prompt sent to the LLM for this agent on every invocation. "
            "Changes are recorded in the version history."
        ),
    )

    st.subheader("Expected Output Example")
    edited_expected = st.text_area(
        "Expected output example",
        value=current_expected,
        height=180,
        disabled=not can_edit,
        key=f"expected_output_{agent_id}",
        label_visibility="collapsed",
        help=(
            "A canonical example output for this agent's prompt. "
            "Used for LLM validation, debugging, and prompt engineering."
        ),
    )

    # ── Temperature ────────────────────────────────────────────────────────
    st.subheader("Temperature")
    st.caption("Controls LLM randomness. 0.0 = deterministic, 2.0 = most creative.")
    new_temp = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=current_temp,
        step=0.05,
        disabled=not can_edit,
        key=f"temp_slider_{agent_id}",
        label_visibility="collapsed",
    )

    col_save, col_reset, col_diff = st.columns([2, 2, 3])

    with col_save:
        save_clicked = st.button(
            "💾 Save Changes",
            key=f"save_prompt_{agent_id}",
            disabled=not can_edit,
            type="primary",
            use_container_width=True,
            help="Save the current prompt, expected output, and temperature as a new version.",
        )

    with col_reset:
        reset_clicked = st.button(
            "↺ Reset to Default",
            key=f"reset_prompt_{agent_id}",
            disabled=not can_edit,
            use_container_width=True,
            help="Restore the built-in default prompt, expected output, and temperature.",
        )

    with col_diff:
        if is_modified(agent_id):
            with st.expander("Show diff vs. default"):
                _render_diff(default_prompt, get_prompt(agent_id))
        else:
            st.caption("No changes from default.")

    # ── Handle actions ─────────────────────────────────────────────────────
    if save_clicked and can_edit:
        text_changed = edited_text.strip() != current_prompt.strip()
        temp_changed = abs(new_temp - current_temp) > 0.001
        expected_changed = edited_expected.strip() != current_expected.strip()

        if text_changed:
            set_prompt(agent_id, edited_text.strip(), actor=role)
        if temp_changed:
            set_temperature(agent_id, new_temp)
        if expected_changed:
            set_expected_output(agent_id, edited_expected.strip())

        if text_changed or temp_changed or expected_changed:
            st.success(f"✅ Changes saved for **{AGENT_LABELS[agent_id]}**.")
            st.rerun()
        else:
            st.info("No changes detected.")

    if reset_clicked and can_edit:
        reset_to_default(agent_id, actor=role)
        set_expected_output(agent_id, get_expected_output(agent_id))
        st.success(f"↺ **{AGENT_LABELS[agent_id]}** reset to default prompt, expected output, and temperature.")
        st.rerun()


def _render_history(agent_id: str, can_edit: bool, role: str) -> None:
    """SCR-011: Version history table with rollback controls."""
    history = get_history(agent_id)

    st.subheader(f"Version History — {AGENT_LABELS[agent_id]}")
    st.caption(
        f"{len(history)} version(s) recorded. "
        "Most recent version is always the active prompt."
    )

    if not history:
        st.info("No versions recorded yet.")
        return

    # Display newest first
    for idx in range(len(history) - 1, -1, -1):
        entry = history[idx]
        is_current = idx == len(history) - 1

        label = f"v{entry.version} — {entry.timestamp}  ·  actor: {entry.actor}"
        if is_current:
            label += "  🟢 current"

        with st.expander(label, expanded=is_current):
            st.code(entry.text, language="text")

            col_revert, _ = st.columns([2, 5])
            with col_revert:
                if not is_current:
                    revert_clicked = st.button(
                        f"↩ Revert to v{entry.version}",
                        key=f"revert_{agent_id}_v{entry.version}",
                        disabled=not can_edit,
                        help="Restore this version as the active prompt (creates a new history entry).",
                    )
                    if revert_clicked and can_edit:
                        revert_to(agent_id, idx, actor=role)
                        st.success(
                            f"↩ Reverted **{AGENT_LABELS[agent_id]}** to v{entry.version}."
                        )
                        st.rerun()
                else:
                    st.caption("Active version — no rollback needed.")


def _render_diff(old: str, new: str) -> None:
    """Show a simple line-level diff between default and current prompt."""
    import difflib  # stdlib

    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(old_lines, new_lines, fromfile="default", tofile="current", lineterm="")
    )
    if diff:
        diff_text = "\n".join(diff)
        st.code(diff_text, language="diff")
    else:
        st.caption("No diff (prompts are identical).")
