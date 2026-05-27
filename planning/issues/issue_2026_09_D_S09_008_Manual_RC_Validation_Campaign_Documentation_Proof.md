# D-S09-008: Manual RC Validation Campaign and Documentation Proof

## Issue Summary

S09 RC1 requires a full manual release-candidate validation campaign after a clean automated pass across all RC-included features. The campaign must include documentation verification for user manual, product documentation set, and deployment guide.

## Related Requirements

- VS-008
- PRJ-011
- PRJ-016

## Severity

Medium - RC publication control and release evidence requirement.

## Scope

1. Execute full manual end-to-end functional validation for RC1.
2. Validate S09 UI feature set and export behavior.
3. Validate documentation accuracy and operational usability:
   - User manual markdown and HTML.
   - Product documentation set used for release operations.
   - Deployment guide walkthrough in clean environment.
4. Produce release evidence bundle and decision record input.
5. Apply bounded validation-loop policy (target <=2 loops).

## Acceptance Criteria

- [ ] Full manual RC checklist executed with pass/fail results captured.
- [ ] Functionality validated for all release-critical workflows.
- [ ] Documentation checks completed and findings resolved or accepted.
- [ ] Evidence bundle archived with release artifacts.
- [ ] Validation completed within target loop count or escalated per policy.

## Verification Evidence

### Planned Evidence Artifacts

- `planning/archives/2026-05/Test_Execution_Summary_Sprint_2026_09.md`
- `Releases/Deployment_Guide_v1.0.0-rc1.md`
- RC decision record with manual validation references

### Expected Result

- RC1 decision is backed by complete manual functional and documentation validation evidence executed after clean automated validation of RC-included features.

## Status

In Progress

## Metadata

- Sprint: 2026-09
- Created: 2026-05-09
- Source: RC sequencing policy requiring automated clean pass before manual validation, plus documentation-proof requirement

## Progress Notes (2026-05-10)

- Automated prerequisite completed and recorded in `planning/archives/2026-05/Test_Execution_Summary_Sprint_2026_09.md`.
- Sweep evidence: `406 passed, 11 deselected` for `pytest Tests/unit Tests/integration Tests/e2e -m "not llm_live"`.
- Manual RC campaign execution remains pending user-driven test run and evidence capture.
