# Artifact Retention and Archive Policy

## Purpose

Keep active architecture, decomposition, and safety baselines easy to find while preserving governance evidence and analysis history for auditability.

## Decision Rule

Do not delete evidence by default.

Classify each artifact as one of the following:

- Canonical baseline: active source of truth used by runtime/governance checks.
- Active governance evidence: currently referenced by gate checklists or release evidence.
- Historical analysis evidence: useful for traceability but not used in active decision paths.
- Scratch/intermediate output: temporary files that can be regenerated.

## Retention Guidance

Keep in active folder:

- Canonical baseline artifacts.
- Any file directly consumed by validation scripts or CI checks.
- Any file referenced by current release/sprint governance checklists.

Move to archive:

- Historical analysis evidence that is no longer an active gate input.
- Superseded reports when a newer report exists and is authoritative.
- One-off reconciliation notes after closure has been recorded in canonical registers.

Delete (only if all conditions are true):

- File is scratch/intermediate.
- File is reproducible from scripts or source artifacts.
- File is not referenced by docs, scripts, CI, or release evidence.

## Archive Location

Use the local archive folder:

- `archive/`

Recommended structure:

- `archive/YYYY-MM/` for monthly batches
- include short migration notes in the archive index

## Required Metadata for Archived Files

When archiving, add an entry to `archive/README.md` with:

- original path
- archive date
- reason for archive
- replacement artifact (if any)
- whether regeneration is possible

## Governance Notes

- Prefer archive over deletion for auditability.
- Keep canonical files stable to avoid breaking validator and CI flows.
- If unsure, keep the file and mark it as historical in archive index.
