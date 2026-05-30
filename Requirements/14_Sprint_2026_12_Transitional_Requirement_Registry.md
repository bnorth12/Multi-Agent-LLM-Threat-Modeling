# Sprint 2026-12 Transitional Requirement Registry

## Purpose

This registry captures requirement identifiers already referenced by Sprint 2026-12 planning and issue artifacts so intake validation can resolve those IDs to a controlled requirement record.

These entries are transitional governance records. They must be migrated into canonical domain requirement specifications or retired through an approved deferment path.

## Transitional Requirement IDs

### Deferred Requirement IDs

- DEF-001: GraphQL endpoint implementation deferred under REST-first Sprint 2026-12 policy.

### Sprint Execution Requirement IDs

- EXEC-001: Expose backend operational endpoints in REST-first mode.
- EXEC-002: Publish frontend-consumable API contract for Sprint 2026-12.
- EXEC-003: Provide standalone React + MUI shell with frame layout.
- EXEC-004: Wire frontend flows to backend run/config/prompt/artifact surfaces.
- EXEC-005: Provide page and footer HITL controls for operator actions.
- EXEC-006: Implement staged bearer-token auth gate handling.
- EXEC-007: Provide unauthorized browser-lane guidance and UX handling.
- EXEC-008: Enforce dependency boundary separation for runtime vs test tooling.
- EXEC-009: Maintain explicit browser test lanes for shell and full workflow paths.
- EXEC-010: Maintain split-hosting runtime integration hardening.
- EXEC-011: Maintain ordered HITL gate ledger and lifecycle summary behavior.
- EXEC-012: Maintain runtime monitoring continuity and status telemetry behavior.
- EXEC-013: Enforce Gate 0 preflight review before Stage 1 execution.
- EXEC-014: Enforce post-Stage-1 normalization gate before Stage 2 execution.
- EXEC-015: Provide Mermaid reviewer with multi-diagram navigation.
- EXEC-016: Preserve wizard-created run auto-selection pin and badge behavior.
- EXEC-017: Preserve restart-safe completed-run artifact retrieval behavior.
- EXEC-018: Preserve React input file parsing parity and binary injection guard behavior.

### Traceability Requirement IDs

- REQ-001: REST-first endpoint exposure is traceable to implementation and verification evidence.
- REQ-002: API contract publication is traceable to implementation and verification evidence.
- REQ-003: React + MUI shell behavior is traceable to implementation and verification evidence.
- REQ-004: Frontend-to-backend wiring behavior is traceable to implementation and verification evidence.
- REQ-005: HITL control-path behavior is traceable to implementation and verification evidence.
- REQ-006: Auth gate behavior is traceable to implementation and verification evidence.
- REQ-007: Unauthorized browser-lane behavior is traceable to implementation and verification evidence.
- REQ-008: Dependency boundary hardening is traceable to implementation and verification evidence.
- REQ-009: Browser test-lane policy is traceable to implementation and verification evidence.
- REQ-010: Split-hosting integration behavior is traceable to implementation and verification evidence.
- REQ-011: HITL ledger behavior is traceable to implementation and verification evidence.
- REQ-012: Runtime monitoring continuity is traceable to implementation and verification evidence.
- REQ-013: Gate 0 preflight behavior is traceable to implementation and verification evidence.
- REQ-014: Normalization-gate behavior is traceable to implementation and verification evidence.
- REQ-015: Mermaid reviewer behavior is traceable to implementation and verification evidence.
- REQ-016: Wizard run-selection behavior is traceable to implementation and verification evidence.
- REQ-017: Restart-safe artifact retrieval behavior is traceable to implementation and verification evidence.
- REQ-018: Input parsing parity and binary guard behavior is traceable to implementation and verification evidence.

### Open Sprint 2026-12 Post-Run Requirement IDs

- GUI-038: Standalone mitigations artifact-viewer capability.
- GUI-039: Optional prior-canonical-graph setup input capability.
- GUI-040: Dual-surface threat artifact and mitigation-review viewer capability.
- HITL-00X: Legacy placeholder HITL gate requirement identifier retained for tracker compatibility until normalized ID replacement is approved.

### Legacy Identifier Compatibility Aliases

- LLM-004: Legacy alias for `C11-LLM-004` retained for Sprint 2026_01 remediation tracker compatibility.

## Governance Notes

- This file is authoritative for identifier existence only.
- Requirement content maturity remains controlled by the canonical requirement sets in `Requirements/` and active sprint issue records.
- Each transitional ID must either migrate to a canonical requirement artifact or be retired with explicit governance disposition.
