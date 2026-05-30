# Sprint 2026-01 Planning

Date: 2026-05-30
Status: Restart planning baseline
Source of truth: planning/Sprint_2026_01_Remediation_Restart_Manifest.md

## Objective

Execute Phase 1 of the remediation restart under the governance automation suite while preserving complete allocation of all 42 selected items across the portfolio.

## In Scope

- Intake source: the 42-item restart manifest.
- Execution slice for this sprint: Phase 1 items `R01-001` through `R01-030`.
- Governance sequence to exercise before implementation work:
  - `portfolio` context to stage the restart set across execution and parking-lot lanes
  - `planning` context to validate planning readiness and intake quality
  - `blocker-planning` context to emit any recurring traceability blocker backlog
  - `design-authoring` context only after intake is accepted and issue artifacts are generated

## Allocation Rule

- Sprint 2026_01 owns the 30 Phase 1 remediation items.
- Sprint 2026_02 reserves the 12 Phase 2 remediation items.
- Parking Lot 2026_99 owns non-remediation speculative work previously labeled as S13/S14.

## Exit Condition

- Every Phase 1 item is represented in the generated sprint tracker and issue set.
- No speculative non-remediation work is mixed into the remediation tracker.
- The planning and portfolio governance outputs reference only `2026_01`, `2026_02`, and `2026_99` for this restart sequence.
