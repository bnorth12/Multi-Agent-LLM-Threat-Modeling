# D-S13-001: STIX 2.1 Visualizer License Review and Deferred Integration

## Issue Summary

Evaluate and optionally integrate an external STIX 2.1 visualization capability (for example, the OASIS/Open GitHub visualizer or a functionally similar alternative) so analysts can inspect STIX bundles in richer graph-oriented views.

This issue is explicitly deferred to a later sprint and must not be implemented until licensing, security, and compatibility checks pass.

## Related Requirements

- GUI-018
- PRJ-016
- GOV-TRACE-001

## Severity

Medium - Analyst usability enhancement with licensing/compliance impact.

## Deferred Scope

- Perform OSS license due diligence on candidate STIX visualizer repositories.
- Determine compatibility with this repository's MIT license distribution model.
- If compatible, define integration architecture (embed, wrapper, or generated static visualization).
- If not compatible, implement a similar in-house or MIT-compatible visualization path.

## Acceptance Criteria

- [ ] Candidate visualizer(s) identified and documented with repository URLs and commit pin strategy.
- [ ] License analysis completed (SPDX identifier, obligations, attribution, copyleft constraints, redistribution constraints).
- [ ] Legal/compliance decision recorded: approved, approved-with-conditions, or rejected.
- [ ] Security review completed for third-party JS/dependency footprint and offline operation constraints.
- [ ] Integration design note produced with one selected approach:
  - Embed external visualizer safely, or
  - Implement similar native STIX graph visualization in MTM UI.
- [ ] If external visualizer is rejected, fallback capability backlog item is created and linked.
- [ ] Traceability links added to sprint matrix and release checklist before implementation starts.

## Verification Evidence

### Planned Review Commands

```powershell
# License metadata and dependency inspection (final commands selected in implementation sprint)
Get-Content LICENSE
npx --yes license-checker --summary
```

### Expected Result

- Clear go/no-go decision on external visualizer usage.
- Documented compliance posture compatible with MIT repository policy.
- Actionable implementation plan for a future sprint.

## Status

Deferred

## Metadata

- Sprint: 2026-99 parking lot (or next explicitly activated visualization sprint)
- Created: 2026-05-21
- Source: Deferred enhancement request from STIX visualization roadmap discussion
- Dependency: License and compliance review gate must pass before coding starts

## Notes

- Do not import or bundle external visualizer code in the current sprint.
- Prefer deterministic builds and pinned versions for any approved dependency.
- Preserve an internal fallback path so visualization capability does not depend on uncertain third-party licensing outcomes.
