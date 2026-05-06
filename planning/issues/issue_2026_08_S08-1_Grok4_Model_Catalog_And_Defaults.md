# Issue: Sprint 2026-08 xAI Grok-4 Model Catalog and Defaults

## Sprint

2026-08

## Issue ID

S08-1

## GitHub Issue

GH #36

## Owner Role

HMI Architect and Orchestrator Engineer

## Description

Upgrade xAI model configuration from Grok-3-era defaults/catalog values to Grok-4-aligned values for Sprint 2026-08 live execution readiness. Ensure runtime and UI are consistent, maintain backward compatibility for legacy values where practical, and keep documentation/tests synchronized.

## Background

Sprint 2026-07 introduced provider model catalogs, editable model override controls, endpoint mode selection, and OpenAI-compatible live adapter wiring. During closeout, a follow-on gap was identified: xAI defaults and catalog values still include Grok-3 references. This issue formalizes the Sprint 2026-08 update and links it 1:1 with GH #36.

## Scope

- Update xAI provider catalog entries to Grok-4 options in Pipeline Configuration.
- Update xAI default model selection to Grok-4 baseline.
- Preserve compatibility mapping for legacy model aliases still present in existing tests/configs.
- Validate live adapter path remains functional for xAI endpoint modes used by Sprint 8.
- Update user documentation (Markdown and HTML manuals) with Grok-4 wording and examples.
- Update/extend tests that assert xAI model options/defaults.

## Acceptance Criteria

- xAI catalog in configuration UI no longer defaults to Grok-3-only options.
- xAI default model resolves to an approved Grok-4 baseline.
- Legacy xAI model aliases continue to run without hard failure (or are migrated with explicit handling and tests).
- Unit tests for configuration/runtime model selection pass.
- Relevant e2e live validation path remains passing when API key and endpoint are available.
- `docs/User_Manual.md` and `docs/user_manual/index.html` both reflect Grok-4 model guidance.

## Requirement Links

- PRJ-003
- PRJ-004
- PRJ-009
- PRJ-016

## Dependencies

- Depends on Sprint 2026-07 runtime/provider wiring baseline in PR #34.

## Status

- [x] Not started
- [ ] In progress
- [ ] Completed

## Notes

- Created to align local planning issue tracking 1:1 with GH #36.
- Disposition from Sprint 2026-07 discovered issue log: deferred-to-sprint-2026-08 S08-1.
