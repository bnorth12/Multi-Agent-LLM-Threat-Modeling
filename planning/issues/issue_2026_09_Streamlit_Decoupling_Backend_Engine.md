# Issue: LangGraph Sprint — Streamlit Decoupling and Backend Execution Engine

**Sprint**: 2026-09 (LangGraph / Backend Architecture sprint)
**Status**: In Progress
**Priority**: High
**Author**: Copilot

---

## Problem Statement

The pipeline execution engine (`ui/execution.py`) currently imports and depends
on `streamlit` to manage background thread execution, run registry, and state
propagation.  This tightly couples the core business logic (orchestration,
HITL gates, agent pipeline) to a web-UI framework, preventing:

1. **CLI / headless execution** — running threat models from the command line
   or CI without a running Streamlit server.
1. **Future LangGraph migration** — LangGraph's `StateGraph` execution engine
   has no Streamlit concept; embedding `st.*` calls in the execution path
   blocks a clean migration.
1. **Testability without mocking** — tests must patch `streamlit` at module
   level before business logic can be exercised.
1. **JSON-backed persistence** — the current in-memory-only `_RUN_REGISTRY`
   is lost on process restart; run metadata is not checkpointed.

**Design rule**: Streamlit is permitted only in the `ui/` layer (screens,
session sync, rendering helpers).  All execution engines, prompt stores, and
backend services must be importable and usable without Streamlit.

---

## Workstreams

### WS-1: Backend Execution Engine (`backend/run_manager.py`)

| Item | Detail |
|------|--------|
| File | `src/threat_modeler/backend/run_manager.py` |
| Status | **DONE** |
| Imports streamlit? | **No** |

- Moves `_RUN_REGISTRY`, `_REGISTRY_LOCK`, `_execute()`, and
  `_resume_execute()` out of `ui/execution.py`.
- Exposes `submit_run()`, `resume_run()`, `cancel_run()`, `wait_for_run()`,
  `get_run_status()`, `is_run_active()`, `any_run_active()`.
- Persists run metadata (status, timing, gate, error, settings) to
  `~/.multi_agent_threat_modeler_runs.json` for reload recovery.
- `FrameworkState` objects remain in-memory only (use snapshot helpers in
  `ui/runtime_io` for durable persistence).

### WS-2: File-Backed Prompt Store (`backend/prompt_store.py`)

| Item | Detail |
|------|--------|
| File | `src/threat_modeler/backend/prompt_store.py` |
| Status | **DONE** |
| Imports streamlit? | **No** |

- Thread-safe `PromptStore` class with optional JSON file backing.
- Same public API as `ui/prompt_store.py` (drop-in for agent callers):
  `get_prompt`, `set_prompt`, `get_history`, `revert_to`, `get_temperature`,
  `set_temperature`, `reset_to_default`, `is_modified`, `get_default_prompt`.
- Default persistence path: `~/.multi_agent_threat_modeler_prompts.json`.
- Accepts `store_path=None` for in-memory-only tests.

### WS-3: UI Adapter Cleanup (`ui/execution.py`)

| Item | Detail |
|------|--------|
| File | `src/threat_modeler/ui/execution.py` |
| Status | **DONE** |

- `start_pipeline_execution()` → delegates to `backend.run_manager.submit_run()`.
- `resume_pipeline_execution()` → delegates to `backend.run_manager.resume_run()`.
- `cancel_execution()` → delegates to `backend.run_manager.cancel_run()`.
- `wait_for_execution_complete()` → delegates to `backend.run_manager.wait_for_run()`.
- `sync_execution_state_to_session()` reads from `backend.run_manager.get_run_status()`.
- Retains all `st.*` UI calls (session sync, URL params, rendering) — correct
  for the adapter layer.

### WS-4: CLI Entry Point (`__main__.py`)

| Item | Detail |
|------|--------|
| File | `src/threat_modeler/__main__.py` |
| Status | **DONE** |

Enables `python -m threat_modeler [--port N] [--open-browser]` to start the
Streamlit web server without installing a shell-script wrapper.

### WS-5: Backend Tests

| Test file | Covers |
|-----------|--------|
| `Tests/unit/test_run_manager.py` | `ExecutionStatus`, registry accessors, cancel, wait, submit_run with fixture settings, no-Streamlit guard |
| `Tests/unit/test_backend_prompt_store.py` | `PromptStore` CRUD, history, revert, temperature, JSON persistence, thread safety, no-Streamlit guard |

### WS-6: JSON Storage Format

Run metadata checkpoint: `~/.multi_agent_threat_modeler_runs.json`

```json
{
  "<run-uuid>": {
    "run_id": "<run-uuid>",
    "status": "completed|paused|failed|running|queued",
    "start_time": 1748000000.0,
    "end_time": 1748000045.2,
    "pause_gate": null,
    "error": null,
    "settings": { ... }
  }
}
```

Prompt store: `~/.multi_agent_threat_modeler_prompts.json`

```json
{
  "prompts": { "agent_01": "..." },
  "histories": { "agent_01": [ { "version": 1, "text": "...", "actor": "system", "timestamp": "..." } ] },
  "temperatures": { "agent_01": 0.2 }
}
```

---

## Acceptance Criteria

- [x] `backend/run_manager.py` imports no `streamlit` symbol.
- [x] `backend/prompt_store.py` imports no `streamlit` symbol.
- [x] `ui/execution.py` no longer contains `threading.Thread`, `FrameworkOrchestrator`,
      or `_RUN_REGISTRY` — all live in the backend module.
- [x] `python -m threat_modeler` starts the application.
- [x] All 199 existing unit tests continue to pass.
- [x] New `test_run_manager.py` and `test_backend_prompt_store.py` tests pass.
- [ ] (Future) LangGraph `StateGraph` can be swapped in to `run_manager.submit_run()`
      without changing any UI code.

---

## Related Issues

- `issue_LangGraph_integration.md` — LangGraph state-graph migration roadmap
- `issue_2026_09_EDR_03_Execution_Worker_Queue.md` — async worker queue for
  scalable multi-run support
- `issue_2026_09_EDR_05_UI_Run_Event_Stream.md` — event-driven dashboard polling
