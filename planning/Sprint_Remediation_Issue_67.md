# Sprint Remediation: Issue #67 / S12-013 Gate 0 Input Integrity

Branch: `remediation/issue-67-gate-0-input-integrity`

## Purpose

Run a short remediation sprint around the issue itself, not the issue filename. This slice is intentionally narrow and uses the GitHub issue as the planning key.

## Sprint Objective

Restore Gate 0 input-integrity behavior as a fully traced change set that is planned, implemented, and verified against the same issue key.

## Planning Summary

| Phase | Goal | Primary Output |
|---|---|---|
| 1. Intake and traceability sync | Confirm the issue key, requirement IDs, and evidence targets are aligned | Updated sprint tracker and traceability references |
| 2. Architecture/design update | Capture the Gate 0 preflight boundary and readiness-coupled behavior | HMI blueprint and gate-flow design notes |
| 3. Implementation change | Make the Gate 0 preflight path and summary presentation coherent | Orchestrator, HITL service, and gate ledger updates |
| 4. Verification closure | Prove the branch behavior with automated and manual checks | Backend tests, frontend tests, walkthrough notes |
| 5. Governance closeout | Tie the issue key to the branch, evidence, and merge decision | Execution log and closeout-ready traceability artifacts |

## Selected Issue

- GitHub issue: #67
- Sprint tracker key: S12-013
- Title: Sprint Remediation: Issue #67 - Enforce Gate 0 input integrity preflight review

## Scope by Evidence Layer

### Architecture / Design

- Update the gate-flow architecture notes to describe the Gate 0 preflight boundary, the human-readable parsed input summary, and the readiness-coupled pause/resume behavior.
- Keep the design aligned with the existing HMI blueprint and the runtime state contract.

### Requirements

- Confirm GUI-032 remains the governing requirement for this slice.
- Update the traceability matrix so the issue is traceable from requirement to design to implementation to verification.
- Keep the issue body and sprint tracker synchronized with the active requirement IDs.

### Implementation

- Review the orchestrator and HITL service path that opens Gate 0.
- Review the gate ledger rendering path in the HMI so the preflight summary is visible before Stage 1 execution.
- Keep the implementation change set small and focused on the single issue key.

### Verification

- Require a backend test pass for the Gate 0 preflight path.
- Require a frontend test pass for the gate ledger / summary presentation path.
- Require a manual walkthrough that confirms Stage 1 does not begin until the Gate 0 decision is recorded.

### Governance / Traceability

- Update the sprint issue tracker so the issue key is the authoritative planning reference for the remediation branch.
- Keep the sprint traceability matrix and execution log synchronized with the issue key and with the concrete implementation/verification evidence.
- Ensure the governance autoflow and review artifacts can point back to the same issue without relying on filename-based selection.

## Execution Sequence

1. Intake and confirm the four-layer evidence path for issue #67.
1. Update design and traceability references so Gate 0 preflight behavior is described consistently.
1. Implement the smallest possible change set in the orchestrator, HITL service, and gate ledger rendering path.
1. Run the backend and frontend checks, then perform a manual pause/resume walkthrough.
1. Record closure evidence and keep the tracker, execution log, and issue body synchronized.

## Governance Checkpoints

- Checkpoint A: issue key and requirement IDs confirmed before code changes begin.
- Checkpoint B: architecture/design references updated before the implementation branch is considered complete.
- Checkpoint C: tests and walkthrough evidence collected before closeout.
- Checkpoint D: issue tracker and execution log updated before merge.

## Focused Replan Addendum (Architecture/Design-First Enforcement)

This remediation sprint keeps the same scope and issue key. The replan is limited to workflow enforcement so architecture and design disposition happens before implementation closure.

### Mandatory Disposition Gate

- A disposition decision is required whenever implementation and architecture/design are not aligned.
- The decision must select exactly one path.
- Path A: update architecture/design artifacts to reflect the implemented behavior.
- Path B: update implementation to conform to architecture/design intent.
- The selected path must include rationale and approval evidence in the execution log.

### In-Flight Governance Invocation

- Planning/intake checkpoint: requirements-baseline-steward, architecture-design-traceability-auditor, sprint-intake-gatekeeper.
- Development checkpoints: architecture-design-traceability-auditor and requirements-implementation-auditor must run in pre-commit and pre-merge-commit governance flow.
- Independent review checkpoint: source-to-evidence-traceability-auditor confirms the final disposition path remains complete through verification evidence.

### Closure Rules for Disposition Cases

- If architecture/design is updated to match implementation, closeout must include revised architecture/design references plus conformance verification evidence.
- If implementation is updated to match architecture/design, closeout must include rerun verification on the new implementation baseline.
- Existing verification evidence from the superseded path is historical context only and does not satisfy final closeout evidence.
- Closeout certification requires a complete Requirement -> Architecture/Design -> Implementation -> Verification traceability chain for the final chosen state.

## Risks and Controls

| Risk | Control |
|---|---|
| Scope expands beyond Gate 0 input integrity | Split follow-on work into a new issue key and keep this branch narrow |
| Implementation changes without design/traceability updates | Require architecture and traceability updates before merge |
| Verification evidence is incomplete | Block closeout until backend, frontend, and manual walkthrough evidence are recorded |
| Planning drifts back to filename-based selection | Use issue #67 as the only branch planning key |

## Acceptance Criteria

- The issue is the planning key for the remediation branch.
- The remediation slice covers architecture/design, requirements, implementation, and verification together.
- The sprint tracker and evidence artifacts can point back to the same issue key.
- The branch can be closed and merged only after the four-layer evidence is complete.
- The branch also carries the traceability-governance artifacts required to prove the remediation was planned and closed against the issue itself.

## Evidence Targets

- Requirements/10_GUI_Requirements.md
- planning/Sprint_2026_12_Traceability_Matrix.md
- planning/Sprint_2026_12_Execution_Log.md
- planning/issues/Sprint_2026_12_Issue_Tracker.md
- local_reviews/latest/governance_execution_ledger_latest.md
- local_reviews/latest/remediation_readiness_latest.md
- docs/architecture/HMI_Architecture_Blueprint.md
- src/threat_modeler/orchestrator.py
- src/threat_modeler/hitl/service.py
- frontend/src/components/HITLGateManager.tsx
- Tests/integration/test_avionics_expected_results.py
- Tests/test_hmi_backend_api.py

## Notes

- This is the only selected remediation slice for the short branch.
- If the issue expands, split follow-on work into a separate issue key rather than broadening this branch.

## Exit Criteria

- The Gate 0 preflight behavior is documented, implemented, and verified.
- The traceability matrix and execution log reference the same issue key as the branch.
- The branch can be merged only after the four-layer evidence set is complete.
- Any residual gaps are converted into new issues rather than widening this one.
