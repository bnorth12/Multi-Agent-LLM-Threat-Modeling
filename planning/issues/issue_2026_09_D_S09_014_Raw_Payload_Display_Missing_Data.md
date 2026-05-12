# D-S09-014: Raw Payload Display Shows No Data in Gate/Related Controls

## Issue Summary

During manual review in Threat Review, selecting raw payload display for a gate can open a section that contains no useful data. Similar raw preview controls may show empty payloads on related screens depending on current run state.

This issue tracks the **data content** gap only. Scroll/collapse interaction blockers are addressed separately in the current fix set.

## Related Requirements

- GUI-002A
- GUI-021
- GUI-023

## Severity

Medium - does not always block control interaction, but reduces analyst ability to inspect evidence payloads during review.

## Reproduction

1. Open `Threat Review`.
2. Select a gate in HITL Gate Review.
3. Open raw payload display control.
4. Observe payload area shows empty/no useful content for the selected gate.

## Scope

1. Diagnose payload source for gate raw artifact snapshots across run lifecycle.
2. Ensure gate-specific raw payload controls render non-empty source data when available.
3. Provide explicit user message for true empty-state vs. missing-state conditions.
4. Add automated coverage for payload-present and payload-empty behaviors.

## Acceptance Criteria

- [ ] Gate raw payload control displays actual gate snapshot content when data exists.
- [ ] Empty payload states are explicitly labeled and distinguishable from loading/missing state.
- [ ] Related raw preview controls on affected screens behave consistently.
- [ ] Automated tests validate both non-empty and empty-state rendering paths.

## Status

Deferred

## Deferral Rationale (2026-05-10)

- Current immediate blocker was page interaction (collapse/scroll lock), which is fixed in active work.
- Data-content rendering gap is tracked for follow-up implementation before release sign-off.
