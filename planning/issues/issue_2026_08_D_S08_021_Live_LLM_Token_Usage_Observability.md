# D-S08-021: Live LLM Token Usage Observability and Export

## Issue Summary

Implement explicit token-usage telemetry for live provider runs so analysts can verify that requests are sent to and returned from the live LLM provider, and export usage metrics as test evidence artifacts.

## Related Requirements

- GUI-015: Token Usage Telemetry Dashboard and Export
- PRJ-008: Runtime model/provider integration and observability
- PRJ-016: GUI operational monitoring behavior

## Severity

**Medium** - Observability/verification feature; does not change threat logic but is required to prove live provider usage.

## Acceptance Criteria

- [x] LLM adapter captures provider usage metrics from response payloads
- [x] Framework state stores token usage by stage for each live request
- [x] Aggregate totals available for prompt/completion/reasoning/cached/total tokens and request count
- [x] Results Export provides downloadable token usage JSON artifact
- [x] New Token Usage screen displays per-stage and aggregate usage in GUI
- [x] Unit regression tests added for adapter usage capture and runtime serialization/export
- [x] Live verification run confirms non-zero token totals for a 9-stage live run

## Implementation Scope

### Code Changes

- `src/threat_modeler/llm/base.py`
  - Added `usage_snapshot()` API on adapters.
- `src/threat_modeler/llm/openai_compatible_adapter.py`
  - Captures and normalizes usage from provider responses for both `chat_completions` and `responses` endpoint modes.
- `src/threat_modeler/state.py`
  - Added `llm_usage_by_stage`, `record_llm_usage()`, and `llm_usage_totals()`.
- `src/threat_modeler/agents/base.py`
  - Records per-stage token usage immediately after adapter completion.
- `src/threat_modeler/ui/runtime_io.py`
  - Added serialization support and `export_token_usage_json()`.
- `src/threat_modeler/ui/screens/results_export.py`
  - Added token usage artifact download and preview.
- `src/threat_modeler/ui/screens/token_usage.py`
  - New screen with aggregate and per-stage usage telemetry, including gate context view.
- `src/threat_modeler/ui/app.py`
  - Registered Token Usage screen in navigation.

### Tests

- `Tests/unit/test_openai_compatible_adapter.py`
  - Added usage snapshot tests for `chat_completions` and `responses` payloads.
- `Tests/unit/test_token_usage_runtime.py`
  - Added tests for state aggregation, serialization/restore, and token usage export JSON.

## Verification Evidence

### Regression Tests

Command:

```powershell
.venv\Scripts\pytest.exe Tests/unit/test_openai_compatible_adapter.py Tests/unit/test_token_usage_runtime.py -q
```

Result:

- 24 passed in 1.88s

### Live Provider Verification

Command:

```powershell
$env:GROK_API = "<set in environment>"
.venv\Scripts\python.exe -c "from threat_modeler.config import ModelSelection, PipelineSettings, RuntimeSettings; from threat_modeler.orchestrator import FrameworkOrchestrator; settings=RuntimeSettings(model=ModelSelection(provider='xai', model_name='grok-4-1-fast-non-reasoning', offline_only=False, endpoint_mode='chat_completions'), pipeline=PipelineSettings(execution_mode='langgraph-compatible', require_hitl_gates=False, stop_on_validation_error=False)); orch=FrameworkOrchestrator(settings=settings, run_id='live-token-usage-check'); state=orch.initialize_state(); state.raw_text='System: Payment API over HTTPS. Component: CardProcessor. Assets: PAN and auth token.'; result=orch.run_planned_stages(state); print('TOTALS', result.llm_usage_totals()); print('STAGES', sorted(result.llm_usage_by_stage.keys()));"
```

Observed output:

- TOTALS: `{'prompt_tokens': 8720, 'completion_tokens': 2937, 'reasoning_tokens': 0, 'cached_tokens': 1425, 'total_tokens': 11657, 'request_count': 9}`
- STAGES: `['agent_01', 'agent_02', 'agent_03', 'agent_04', 'agent_05', 'agent_06', 'agent_07', 'agent_08', 'agent_09']`

## Notes

- Fixture/offline runs intentionally report no live provider usage.
- If a provider omits usage fields, totals may be partial but request-level telemetry remains recorded where present.

---

**Status**: Resolved
**Assigned**: Engineering
**Sprint**: 2026-08

## Closure Evidence Template

Use this block for future closure updates.

- Resolution date:
- Implementation commit or PR:
- Verification command(s):
- Verification result summary (include pass counts):
- Evidence artifact path(s):
- Reviewer or approver initials:
