# Issue: S11-017 — Prompt Editor Modifications Not Persisted To Agent Execution Path

**Sprint**: 2026-11
**Type**: Critical Defect / Feature Gap
**Priority**: P0 Blocker
**Severity**: Critical
**Status**: Open
**Owner**: Backend/UI Integration Engineer
**Estimated Effort**: 1–2 points (fix is straightforward)

---

## Problem Statement

The prompt editor (GUI-009, SCR-010) in the UI allows users to edit prompts and save them. However, the saved edits are stored **only in Streamlit session state** and are **never persisted to disk or used by the backend execution path**.

When agents execute, they load prompts via `backend.prompt_store.get_prompt()`, which reads from the persistent JSON file `~/.multi_agent_threat_modeler_prompts.json`. Since the UI editor does not write to this backend store, any prompt edits (including single/multi-shot examples) are lost and agents continue to use the original hardcoded or file-based prompts.

### Current Flow (Broken)

```
User edits prompt in UI
       ↓
st.session_state[prompt] = edited_text
       ↓
(session ends)
       ↓
Edits are lost; agent execution still uses original prompt from backend/prompt_store.py
```

### Expected Flow

```
User edits prompt in UI
       ↓
backend.prompt_store.set_prompt(agent_id, edited_text)
       ↓
Persists to ~/.multi_agent_threat_modeler_prompts.json
       ↓
Agent execution calls backend.prompt_store.get_prompt(agent_id)
       ↓
Edited prompt (with examples) is used
```

---

## Impact

1. **Broken Feature**: GUI-009 (Agent Prompt Editor) appears functional but is non-operational.
2. **Single/Multi-Shot Examples Lost**: Users edit prompts with examples to improve agent output quality, but these edits are never used.
3. **User Trust**: Release documentation claims prompts are editable, but edits don't affect execution.
4. **RC Sign-Off Risk**: This is a critical quality gap that must be resolved before RC1 release.

---

## Root Cause

- `src/threat_modeler/ui/prompt_store.py` is a standalone Streamlit session-state wrapper.
- `src/threat_modeler/backend/prompt_store.py` is the authoritative file-backed store.
- `ui/prompt_store.set_prompt()` updates session state but does **not call** `backend.prompt_store.set_prompt()`.
- No synchronization or bridge exists between the two stores.

---

## Solution Options

### Option A: Bridge UI Store to Backend (Recommended)

Modify `ui/prompt_store.set_prompt()` to delegate to `backend.prompt_store.set_prompt()`:

```python
# In ui/prompt_store.py
from threat_modeler.backend.prompt_store import PromptStore

def set_prompt(agent_id: str, text: str, actor: str = "user") -> None:
    """Save to both session state and backend persistent store."""
    _validate_agent(agent_id)
    _ensure_initialised()

    # Update session state
    st.session_state[_KEY_PROMPTS][agent_id] = text
    history: list[VersionEntry] = st.session_state[_KEY_HISTORIES][agent_id]
    next_version = history[-1].version + 1 if history else 1
    history.append(
        VersionEntry(version=next_version, text=text, actor=actor, timestamp=_utc_now())
    )

    # Persist to backend store
    from threat_modeler.backend.prompt_store import _default_store
    _default_store.set_prompt(agent_id, text, actor=actor)
```

**Pros**:
- Simple, no new dependencies.
- UI session state and backend file stay in sync.
- No agent code changes needed.

**Cons**:
- Creates a cross-module dependency (UI → Backend).

### Option B: Load Backend Store at UI Session Init

Initialize `ui/prompt_store` by loading persisted prompts from backend on session start.

**Pros**:
- Cleaner separation of concerns.

**Cons**:
- Requires syncing session state back to backend on save, which is Option A anyway.

---

## Acceptance Criteria

1. When user edits a prompt in the UI and clicks "Save Changes", the edit is persisted to `~/.multi_agent_threat_modeler_prompts.json`.
2. When an agent executes after the prompt edit, it loads and uses the edited prompt (not the original).
3. Single/multi-shot examples in edited prompts are included in the system prompt sent to the LLM.
4. A regression test confirms that prompt edits persist across UI sessions and are used by agent execution.
5. Issue closure note references the test and commit.

---

## Test Plan

### Unit Test

Create `Tests/unit/test_ui_backend_prompt_sync.py`:

```python
def test_ui_set_prompt_persists_to_backend(tmp_path):
    """Verify that UI prompt edits are persisted to backend store."""
    # Create a backend store with a temp file
    store_path = tmp_path / "prompts.json"
    backend_store = PromptStore(store_path=store_path)

    # Mock UI session state and call set_prompt()
    # Then verify that the backend file contains the edited prompt
    edited_text = "New prompt with examples"
    backend_store.set_prompt("agent_01", edited_text)

    # Verify persistence
    backend_store_2 = PromptStore(store_path=store_path)
    assert backend_store_2.get_prompt("agent_01") == edited_text
```

### Integration Test

Create `Tests/integration/test_prompt_edit_to_execution.py`:

```python
def test_agent_uses_edited_prompt_on_execution():
    """Verify that agents execute with edited prompts."""
    # Edit a prompt in UI → backend store
    # Execute an agent
    # Verify that the agent's LLM call used the edited prompt (not the default)
    # Check state.llm_prompts_by_stage contains the edited text
```

---

## Files to Change

- `src/threat_modeler/ui/prompt_store.py` — Add delegation to backend store.
- `Tests/unit/test_ui_backend_prompt_sync.py` — New unit test.
- `Tests/integration/test_prompt_edit_to_execution.py` — New integration test.
- [Optional] `src/threat_modeler/ui/screens/prompt_editor.py` — Add user feedback confirming persistence.

---

## Blocking Dependencies

- None. This is a standalone fix.
- Must be resolved before RC1 sign-off (part of S11 closeout).

---

## Evidence Notes

- Root cause verified via code inspection of `ui/prompt_store.py` and `backend/prompt_store.py`.
- Feature gap confirmed in Sprint 2026-11 review: prompt edits exist in UI but are not used by agents.
