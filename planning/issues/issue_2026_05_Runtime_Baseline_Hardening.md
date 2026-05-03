# Issue: Sprint 2026-05 Runtime Baseline Hardening

## Sprint
2026-05

## Owner Role
Technical Lead and Orchestrator Engineer

## Description
Consolidate the runtime into one authoritative execution path and remove duplicate legacy blocks that can cause drift.

## Scope
- Remove duplicate class and function blocks in core runtime modules.
- Keep one authoritative orchestrator and state model path.
- Align enabled stage IDs with implemented stage registry.

## Acceptance Criteria
- Core runtime modules no longer contain duplicate active definitions.
- Orchestrator executes deterministic linear stage flow.
- Review notes confirm deprecated compatibility seams are not used in active path.

## Requirement Links
- PRJ-003
- PRJ-004
- PRJ-015

## Status
- [ ] Not started
- [x] In progress
- [ ] Completed
