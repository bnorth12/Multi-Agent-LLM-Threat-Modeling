# Artifact Ownership and Evidence Authority

## Purpose

Prevent active governance and traceability drift by defining authoritative homes for requirements, architecture/design, and verification evidence.

## Policy

1. Active requirement traceability SHALL be authored and maintained in `Requirements/`.
1. Architecture, design, and process governance SHALL be authored and maintained in `docs/`.
1. Verification execution summaries SHALL be authored and maintained in `docs/verification/sprint_test_execution/`.
1. `planning/` artifacts SHALL be treated as operational sprint workflow records and historical context, not system-of-record authority.
1. If an active document references `planning/` for authoritative content, the owner SHALL either:
   - move the authoritative content to the correct authority surface, or
   - replace the active reference with a pointer to an existing authoritative artifact.

## Enforcement

- During documentation changes, run `scripts/verify_sprint_traceability.py` for affected sprint scope.
- Run `npx --yes markdownlint-cli **/*.md` on changed markdown files.
- Record relocation events in `planning/archives/` with a move manifest.
