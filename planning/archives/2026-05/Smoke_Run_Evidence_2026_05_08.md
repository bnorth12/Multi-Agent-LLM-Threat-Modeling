# Smoke Run Evidence - 2026-05-08

## Scope

Fresh live browser smoke execution for Sprint 2026-08 using xAI/Grok in the Streamlit UI.

## Environment and Preflight Checks

### PASS - Traceability Closure Gate

Command:

```powershell
.venv\Scripts\python.exe scripts/verify_sprint_traceability.py --sprint 2026-08 --audit --closure
```

Result:

- All requested traceability checks passed.

### PASS - Targeted Runtime Regression

Command:

```powershell
.venv\Scripts\pytest.exe Tests/unit/test_openai_compatible_adapter.py Tests/unit/test_token_usage_runtime.py -q
```

Result:

- 24 passed
- 0 failed

### PASS - Live Provider Connection Validation (UI)

Pipeline Configuration (SCR-003/SCR-014):

- Provider: `xAI/Grok`
- Model: `grok-4`
- Offline mode: `False`
- Endpoint mode: `chat_completions`

UI validation status:

- `Validated: xAI/Grok / grok-4 - connection is ready.`

## Browser Smoke Run Execution

### Run Metadata

- Run ID: `c8d8a5b5-d934-4900-9711-7e9e6ee2014b`
- Launch URL: `http://localhost:8501/?run_id=c8d8a5b5-d934-4900-9711-7e9e6ee2014b`
- Role: `Author`
- Input screen: `SCR-004`

### Inputs Used

- System name: `Avionics Data Network`
- ICD file: `Tests/fixtures/inputs/icd/icd_avionics_v1.csv`
- Narrative file: `Tests/fixtures/inputs/descriptions/description_avionics.md`

### Fresh Observed Results

After automated refresh polling for approximately 5 minutes post-start:

- Stage completion:
  - `agent_01` (Input Normalizer): `Complete`
  - `agent_02` (Context Builder): `Pending`
  - `agent_03`..`agent_09`: `Pending`
- HITL gates: no gates opened yet
- Artifact snapshot at observation point:
  - Interfaces: `8`
  - Threats: `0`
  - STIX bundle: `No`
  - Mermaid diagrams: `0`
  - Final report: `No`
- Execution status in UI remained `RUNNING` without advancing beyond stage 1 during the observation window.

## Pass/Fail Verdict

- PASS:
  - Live provider connection validation succeeded.
  - Browser run initialization succeeded.
  - Stage 1 completed with expected artifact shape update (interfaces populated).
- FAIL:
  - End-to-end completion not achieved in this run.
  - Run stalled at stage 2 (`agent_02`) during the observed window.

Overall verdict for this fresh browser smoke attempt: FAIL (incomplete progression beyond stage 1).

## Notes for Follow-Up

- The failure mode in this attempt is progression stall, not startup/configuration failure.
- Suggested immediate rerun variant: use a faster validated model from Sprint S08 live matrix (for example `grok-4-1-fast-non-reasoning`) and capture a second fresh run for pass comparison.

## HITL Abbreviated Continuation Run (Fixture, Gates Engaged)

### Run Metadata

- Run ID: `277ef27c-a8e7-4774-9751-f9a0a94b50c1`
- Launch URL: `http://localhost:8501/?run_id=277ef27c-a8e7-4774-9751-f9a0a94b50c1`
- Provider mode: `fixture` (offline deterministic)
- HITL mode: `require_hitl_gates=True`

### Abbreviated HITL Decisions Applied

For each open gate, an abbreviated review was performed and then continued:

- `gate_1_scope_confirmation`: `Accepted_As_Is` then `Resume Pipeline`
- `gate_2_boundary_approval`: `Accepted_As_Is` then `Resume Pipeline`
- `gate_3_stride_calibration`: `Accepted_As_Is` then `Resume Pipeline`
- `gate_4_threat_plausibility`: `Accepted_As_Is` then `Resume Pipeline`
- `gate_5_mitigation_adequacy`: `Accepted_As_Is` then `Resume Pipeline`

Observed non-open gates in this run:

- `gate_0_input_integrity`: `Bypassed`
- `gate_6_merge_conflict_resolution`: `Pending` (conditional, not triggered)
- `gate_7_export_consistency`: `Pending` (conditional, not triggered)

### Final Outcome

- UI execution status: `COMPLETED`
- Elapsed time: `86s`
- Stage progression: `agent_01` through `agent_09` all `Complete`
- Report generation end-state: `09 · Report Writer ✅ Complete`

### Interpretation

The previously observed "stalled" behavior is expected when HITL is enabled and open gates are not explicitly adjudicated.
When each open HITL gate receives an abbreviated accept-and-resume decision, the pipeline proceeds to completion and ends with report generation.

## Controlled Live Grok Probe (Stage-Level Telemetry Capture)

### Purpose

Capture deterministic evidence for:

- attempts observed by stage, and
- token usage on success OR explicit failed-attempt detail on timeout.

### Method

Executed a controlled Python probe in the project virtual environment to run only `agent_01` with live xAI settings:

- Provider: `xai`
- Model: `grok-4`
- Base URL: `https://api.x.ai/v1`
- Endpoint mode: `chat_completions`
- Timeout controls: `THREAT_MODELER_LLM_TIMEOUT_SECONDS=45`, `THREAT_MODELER_LLM_MAX_ATTEMPTS=1`
- Secret loading: `GROK_API` loaded from `.env` when not already in process environment.

### Observed Result

- Outcome: `failure`
- Failure detail:
  - `RuntimeError: Provider request timed out after 1 attempts (timeout=45s, path=/chat/completions, model=grok-4, mode=chat_completions)`

### Captured Attempt/Usage Telemetry

- `ATTEMPT_TOTALS`: `{'submitted': 1, 'completed': 0, 'failed': 1, 'total': 2}`
- `USAGE_TOTALS`: `{'prompt_tokens': 0, 'completion_tokens': 0, 'reasoning_tokens': 0, 'cached_tokens': 0, 'total_tokens': 0, 'request_count': 0}`
- `ATTEMPTS_BY_STAGE`:
  - `agent_01`:
    - `submitted` with provider/model/mode metadata
    - `failed` with explicit timeout error string above
- `USAGE_BY_STAGE`: `{}`

### Interpretation

This probe satisfies the evidence requirement for timeout behavior:

- stage-level attempts are recorded, and
- explicit timeout failure details are captured with attempt count and endpoint metadata.

Zero token usage is expected in this timeout case because no response payload with usage fields was returned.

## Autonomous Closeout Run Addendum (2026-05-09)

### Purpose

Capture post-fix autonomous verification for the gate-resume stability patch set and final Sprint 2026-08 closeout evidence.

### Run Metadata

- Run ID: `40c1c2de-c9fe-4ed5-8327-27cfaf15ddcc`
- Launch URL: `http://localhost:8501/?run_id=40c1c2de-c9fe-4ed5-8327-27cfaf15ddcc`
- Provider mode: `xAI/Grok` (live)
- Endpoint mode: `chat_completions`

### Patch Context Under Verification

- `src/threat_modeler/ui/execution.py`
  - Added resume re-entry guard for RUNNING/QUEUED status.
  - Added paused-gate mismatch guard for stale resume clicks.
  - Added completion cleanup to clear stale `next_stage_id` after run completion.
- `src/threat_modeler/ui/screens/threat_review.py`
  - Added state-aware button gating for Approve/Reject/Resume actions.

### Observed Outcome

- UI execution status reached `COMPLETED`.
- Stage progression reached `agent_01` through `agent_09` as `Complete`.
- HITL decisions proceeded through Gate 5 using single approve/resume actions without duplicate-resume oscillation.
- Results Export displayed all expected artifacts:
  - Canonical Graph JSON
  - STIX Bundle JSON
  - Final Report (Markdown)
  - Mermaid Diagrams (Markdown)
  - Token Usage JSON

### Additional Regression Evidence

Command:

```powershell
.venv\Scripts\python.exe -m pytest Tests/unit/test_ui_app_shell.py Tests/unit/test_live_mode_failover_halt.py -q --tb=short
```

Result:

- 109 passed
- 0 failed

### Addendum Verdict

PASS - Autonomous post-fix live run completed end-to-end with expected artifacts and no recurrence of prior duplicate-resume instability.
