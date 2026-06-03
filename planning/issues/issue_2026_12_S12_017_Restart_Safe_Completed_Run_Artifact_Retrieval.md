# S12-017: Restart-Safe Completed-Run Artifact Retrieval

Sprint: 2026-12
Requirement ID: RHMI-016
Parent Capability ID: C13-UI-001
Parent Function ID: F-RHMI-TRACEABILITY-L1
Child Function ID: F-S12-017-RHMI_016-L2
Decomposition Level: L2
Allocated Component/Module: planning/issues/issue_2026_12_S12_017_Restart_Safe_Completed_Run_Artifact_Retrieval.md
Verification Method: Sprint traceability verification
Status: In Review

## Issue Summary

Completed and paused runs could remain visible in run history after backend restart while
artifact endpoints failed with `Unknown or incomplete run_id`. This created a misleading
operator state where runs appeared complete but canonical/STIX/mermaid/report artifacts
were inaccessible.

## Related Requirements

- RHMI-016
- S12-REQ-017

## Severity

High - operational evidence access and post-run review continuity

## Implemented Scope

1. Persist a restorable runtime-state projection for completed and paused runs in
   `~/.multi_agent_threat_modeler_runs.json`.
1. Restore persisted state projection into run registry entries during checkpoint load.
1. Rehydrate `FrameworkState` in API artifact resolution when in-memory runtime state is absent.
1. Maintain normal 404 behavior only for truly unknown or incomplete runs.

## Acceptance Criteria

- [x] Completed/paused historical runs listed by `GET /runs` remain artifact-addressable after restart.
- [x] `GET /runs/{run_id}/artifacts/canonical` is restart-safe for restorable historical runs.
- [x] `GET /runs/{run_id}/artifacts/mermaid` is restart-safe for restorable historical runs.
- [x] `GET /runs/{run_id}/artifacts/stix` is restart-safe for restorable historical runs.
- [x] `GET /runs/{run_id}/artifacts/report` is restart-safe for restorable historical runs.
- [x] Sprint 2026-12 governance docs updated with requirement and traceability coverage.

## Verification

- `PYTHONPATH=src .venv\Scripts\python.exe -m pytest Tests/test_hmi_backend_api.py -q` -> `18 passed`
- Manual backend restart probe with `/health` validation and completed-run artifact retrieval checks.

## Status

In Review

## GitHub Tracking

- Repository issue: #70

## Owner Guidance

- If historical run records predate `persisted_state` checkpoints, rerun or regenerate artifacts once
  so future restarts have complete recovery state.
- Keep issue open until a GitHub issue number is assigned and closure evidence is linked.
