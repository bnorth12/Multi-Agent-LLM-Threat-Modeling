# Issue: S11-018 — Agent Prompt Loading Silently Falls Back on Any Exception

**Sprint**: 2026-11
**Type**: Critical Defect / Architectural Bypass
**Priority**: P0 Blocker
**Severity**: Critical
**Status**: Open
**Owner**: Backend Architecture / Agents Engineer
**Estimated Effort**: 1–2 points (refactor exception handling to be explicit)

---

## Problem Statement

In `src/threat_modeler/agents/base.py`, the `_load_system_prompt()` and `_load_expected_output()` methods contain blanket exception handlers that silently fall back to hardcoded/file-based prompts if **any exception occurs**, including:

- Import errors (if backend module isn't available)
- Network/IO errors (if persistent store file is inaccessible)
- Logic errors (if `get_prompt()` fails for any reason)
- Validation errors

**Result**: If the backend prompt persistence system has any issue at all, agents execute with defaults and the failure is completely invisible. No logging, no error state propagation, no user visibility.

### Current Code (Problematic)

```python
# agents/base.py lines 45-56

def _load_system_prompt(self) -> str:
    try:
        from ..backend.prompt_store import get_prompt
        return get_prompt(self.stage_id)
    except Exception:  # <-- BLANKET CATCH: swallows ALL exceptions silently
        return self._load_system_prompt_from_file()

def _load_expected_output(self) -> str:
    try:
        from ..backend.prompt_store import get_expected_output
        return get_expected_output(self.stage_id)
    except Exception:  # <-- BLANKET CATCH: silently returns ""
        return ""
```

### Impact Chain

1. **User edits prompt in UI** → Saves to backend store (after S11-017 fix)
2. **Agent executes** → Calls `_load_system_prompt()`
3. **If ANY error occurs** (store file missing, corrupted, import fails, etc.):
   - Exception is silently caught
   - Fallback prompt is loaded from `docs/agents/*.txt` file
   - Agent uses default prompt, not user edits
   - No error logged, no state recorded, no UI notification
4. **User has no idea their edits weren't used**

### Combined with S11-017

- **S11-017**: UI edits not saved to backend at all (bridge not wired).
- **S11-018**: Even if S11-017 is fixed and edits ARE saved, S11-018 means agents silently fall back to defaults if the backend store is ever inaccessible.

**Both must be fixed together to make prompt persistence reliable.**

---

## Root Causes

1. **Over-broad exception handling**: Used `except Exception` instead of specific exception types.
2. **No explicit fallback policy**: Fallback mechanism is implicit and invisible.
3. **No logging/observability**: No way to know if a fallback occurred.
4. **No error state propagation**: Errors are swallowed instead of surfaced to the execution state.

---

## Solution

### Explicit Exception Handling with Logging and Observability

Replace blanket handlers with specific exception types and clear fallback rules:

```python
import logging

logger = logging.getLogger(__name__)

def _load_system_prompt(self) -> str:
    try:
        from ..backend.prompt_store import get_prompt
        return get_prompt(self.stage_id)
    except ImportError as e:
        logger.error(
            f"Agent {self.stage_id}: failed to import backend.prompt_store; "
            f"falling back to file-based prompt. Error: {e}"
        )
        return self._load_system_prompt_from_file()
    except KeyError as e:
        logger.warning(
            f"Agent {self.stage_id}: prompt not found in backend store; "
            f"falling back to file-based prompt. Error: {e}"
        )
        return self._load_system_prompt_from_file()
    except Exception as e:
        # Catch-all for unexpected errors, but log them explicitly
        logger.critical(
            f"Agent {self.stage_id}: unexpected error loading prompt from backend store; "
            f"falling back to file-based prompt. Error type: {type(e).__name__}, Message: {e}"
        )
        return self._load_system_prompt_from_file()

def _load_expected_output(self) -> str:
    try:
        from ..backend.prompt_store import get_expected_output
        return get_expected_output(self.stage_id)
    except (ImportError, KeyError) as e:
        # Expected errors (missing store, missing key) → return empty string
        logger.debug(
            f"Agent {self.stage_id}: expected output not found in backend store "
            f"(this is normal if not configured); returning empty. Error: {e}"
        )
        return ""
    except Exception as e:
        # Unexpected errors → log and return empty
        logger.warning(
            f"Agent {self.stage_id}: unexpected error loading expected output from backend store; "
            f"returning empty. Error type: {type(e).__name__}, Message: {e}"
        )
        return ""
```

### Observability Option (Advanced)

Optionally record fallback events in execution state:

```python
def _load_system_prompt(self) -> str:
    try:
        from ..backend.prompt_store import get_prompt
        prompt = get_prompt(self.stage_id)
        # Log success
        logger.debug(f"Agent {self.stage_id}: loaded system prompt from backend store (user-edited)")
        return prompt
    except (ImportError, KeyError, Exception) as e:
        logger.warning(f"Agent {self.stage_id}: prompt loading failed, using fallback")
        # Optional: record fallback in execution state for observability
        # state.record_message(self.stage_id, f"Prompt fallback: {type(e).__name__}")
        return self._load_system_prompt_from_file()
```

---

## Acceptance Criteria

1. Replace blanket `except Exception` handlers with specific exception types (ImportError, KeyError) and explicit catch-alls with logging.
2. All fallback paths log at appropriate level (ERROR, WARNING, or DEBUG as applicable).
3. A unit test verifies:
   - When backend store is available, prompts are loaded from store (not file).
   - When backend store raises ImportError, error is logged and file fallback is used.
   - When backend store raises KeyError, error is logged and file fallback is used.
   - When backend store raises unexpected exception, error is logged at CRITICAL and file fallback is used.
4. Integration test confirms that edited prompts reach agents without fallback when both S11-017 and S11-018 are fixed.
5. No change to existing fallback behavior (still falls back to file); only adds visibility.

---

## Files to Change

- `src/threat_modeler/agents/base.py` — Add specific exception handling and logging.
- `Tests/unit/test_agent_base_prompt_loading.py` — New unit test for exception handling.
- `Tests/integration/test_end_to_end_prompt_persistence.py` — New integration test for S11-017 + S11-018 together.

---

## Relationship to S11-017

- **S11-017** fixes: UI edits not saved to backend (UI → backend bridge).
- **S11-018** fixes: Agents silently fall back if backend is unavailable (visibility + explicit policy).
- **Together**: Prompts edited in UI → persisted to backend → loaded by agents with full observability of any fallback.

---

## Related Findings

Similar patterns exist elsewhere:

- `src/threat_modeler/agents/base.py` line 75–80: `_get_adapter()` has explicit exception handling for missing live adapter, but fixture fallback is still implicit.
- `src/threat_modeler/exports/report_exporter.py` line 38: Fallback report generation if LLM report is missing — this is intentional and should be logged/tracked similarly.

Recommend audit of all fallback paths after S11-018 closure to identify any other silent failures.
