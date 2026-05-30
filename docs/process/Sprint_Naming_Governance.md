# Sprint Naming Governance

## Purpose

Define one stable sprint identifier policy for repository automation, planning artifacts, and contributor workflows.

## Why The Repository Shifted

The repository accumulated a mix of sprint forms such as `YYYY-MM`, `YYYY_MM`, and speculative future sprint labels like `2026_13` and `2026_14`.

That caused three recurring problems:

1. Automation scripts had to normalize multiple formats for the same sprint.
1. File naming and issue-tracker generation became brittle when prose naming drifted from script-facing naming.
1. Speculative planning work could be mistaken for active execution sprints and interfere with governance autoflow, portfolio planning, and remediation intake.

## Current Policy

- Canonical repository token: `YYYY_NN`
- Human-readable prose alias: `YYYY-NN`
- The trailing token `NN` is a sprint ordinal, not a calendar month
- Repository files, issue trackers, manifests, and script arguments should use `YYYY_NN`
- Human-facing narrative text may also mention the dashed alias when useful

## Legacy Acceptance Rule

Completed historical sprint artifacts that already use `YYYY-MM` or other legacy two-digit forms are accepted as-is.

- Do not renumber completed work only to conform to the new ordinal naming policy
- Historical records should preserve the identifier that existed when the work was executed
- Governance automation must continue to accept legacy dashed and underscored two-digit sprint inputs for existing completed work

## Why Underscore Instead Of Dash

- Filenames and glob patterns are simpler and more consistent with `YYYY_NN`
- Existing repository automation already normalizes to underscore-oriented file discovery
- Using one canonical file token reduces alias churn during planning, issue generation, and traceability verification

## Why `NN` Is Not A Month

Sprint cadence in this repository is not bound to calendar months.

- A sprint token identifies an ordered execution slot, not a month bucket
- Existing script variable names may still refer to `MM` for legacy reasons
- Contributors should treat the second token as an ordinal sprint number

## Parking-Lot Rule

`YYYY_99` is reserved for parking-lot or speculative work that must not collide with active remediation execution.

Use the parking-lot lane for:

- speculative concept work
- deferred non-remediation architecture ideas
- backlog items that should remain visible but must stay outside active sprint automation

## Automation Compatibility

Governance automation now accepts these sprint input forms:

- `YYYY-NN`
- `YYYY_NN`
- `YYYY-NNN`
- `YYYY_NNN`

This compatibility exists so the repository can preserve completed legacy work, operate current two-digit ordinal sprints, and grow into three-digit ordinals without blocking governance execution.

## Future Expansion

If the repository needs more than 99 sprint ordinals in a year, the preferred future scheme is `YYYY_NNN`.

Automation is now prepared to accept three-digit ordinals, but active repository naming should remain on `YYYY_NN` until a deliberate repository-wide migration is approved.

When that migration happens, it should still be executed as one explicit repository-wide change covering scripts, docs, file names, and validation tooling together.

## Current Transition Guidance

- Use `2026_01`, `2026_02`, and similar tokens for active remediation execution sprints
- Use `2026_99` for speculative or parked non-remediation work
- Do not create new active sprint artifacts using speculative labels that bypass the governed sequence
- When in doubt, prefer the restart manifest plus portfolio-planning flow before generating sprint issue trackers
