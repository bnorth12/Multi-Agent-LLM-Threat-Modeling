# Issue S12-020: Stage Latency and Token Telemetry Persistence

Status: Proposed (Post-Run)
Priority: P1
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

Track and persist stage-level latency telemetry for LLM calls, measured from prompt dispatch
until model response completion, and store these data points with stage token usage metrics
inside run records.

This enables evidence-based timeout tuning, stage performance trend analysis, and improved
triage when live runs stall or degrade.

## Why This Matters

- Current token telemetry is useful but incomplete without stage timing context.
- Prompt-to-response latency by stage helps distinguish provider slowness from orchestration issues.
- Persisted timing plus token data creates durable operational evidence for governance reporting.

## Scope (No Implementation During Active Run)

1. Define canonical per-stage latency fields and semantics.
1. Instrument LLM call path to capture prompt-sent and response-received timing.
1. Persist telemetry with run state and expose via run/API/export surfaces.
1. Add tests for schema, persistence, and edge cases (timeouts, retries, skipped stages).

## Proposed Telemetry Fields

- stage_id
- prompt_sent_at_utc
- response_received_at_utc
- llm_round_trip_ms
- attempt_count
- timeout_seconds
- token_usage: prompt, completion, reasoning, cached, total, request_count
- telemetry_status: completed, timeout, failed, skipped

## Acceptance Criteria

- [ ] Each LLM-backed stage records latency data from prompt send to response receive.
- [ ] Per-stage latency and token usage are persisted with run records.
- [ ] Telemetry remains available after backend restart for completed/paused runs.
- [ ] Timeouts/retries are represented explicitly so durations are interpretable.
- [ ] Traceability and execution-log documents include final requirement IDs and verification evidence.

## Related Requirements

- GUI-015 in Requirements/10_GUI_Requirements.md
- GUI-027 in Requirements/10_GUI_Requirements.md
- INT-005 in Requirements/02_Interface_Requirements.md
- Pending requirement ID for persisted stage latency metrics

## Expected Files

- src/threat_modeler/services/openai_compatible_adapter.py
- src/threat_modeler/backend/run_manager.py
- src/threat_modeler/server/api.py
- frontend/src/components/TokenUsageView.tsx
- Requirements/10_GUI_Requirements.md
- Requirements/02_Interface_Requirements.md

## Validation Plan

- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q
- PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/unit Tests/integration -q
- manual: run a live pipeline and verify stage latency plus tokens are present in run telemetry payloads

## GitHub Tracking

- Repository issue: TBD

## Deferment Note

- Implementation is intentionally deferred until the current active run is complete.

## Sprint Deferment Language (2026-05-26)

- Defer Decision: Deferred from Sprint 2026-12 closure scope into Sprint 2026-13 intake unless elevated by governance review.
- Rationale: Minor-to-moderate scope expansion relative to current Sprint 2026-12 critical-path closure work.
- Risk Level: Controlled and acceptable for defer with explicit tracking.
- Verification Impact: No Sprint 2026-12 blocking verification lane is invalidated by deferment.
- Next Sprint Owner: bnorth12
- Intake Linkage: planning/Sprint_2026_13_Skills_Layer_and_Avionics_Specialization.md
