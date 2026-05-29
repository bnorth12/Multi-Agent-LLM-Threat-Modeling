# FQT Evidence Retention Policy

## Purpose

Define a repeatable, audit-safe retention policy for Frontend Qualification Test (FQT) artifacts so that:

- successful evidence remains fully preserved,
- duplicate failure evidence is reduced without losing traceability,
- every archive action is reversible and non-destructive.

## Scope

Applies to run folders under `FQT/` that follow the `fqt_*` naming pattern.

## Retention Classes

- Keep Full:
  - Any run with `test_report.json` status `LIVE_BROWSER_SMOKE_OK`.
  - Any failure run marked canonical for a unique failure signature.
  - Any run with unknown format that cannot be safely classified.
- Summarize Only:
  - Runs with duplicate failure signatures where canonical evidence already exists.
  - Empty or screenshots-only folders that add no unique diagnostics.

## Signature Rules

Failure signatures are normalized by stable indicators in failure artifacts:

- `Provider HTTP error 429` capacity exhaustion
- Playwright timeout waiting for `Verified`
- `Live adapter required ... adapter is missing`
- fallback `raw_failure_evidence` when no known pattern matches

If no failure evidence is present, signatures may be:

- `NO_REPORT_SCREENSHOTS_ONLY`
- `NO_REPORT_EMPTY`
- `NO_REPORT_UNKNOWN`

## Canonical Selection

For each failure signature, keep full evidence for:

- first observed run in timestamp order,
- latest observed run in timestamp order.

All other runs with that signature are summarize-only candidates.

## Non-Destructive Archival

Summarize-only candidates are handled non-destructively:

1. Move original run folder to `FQT/archive_dedup/YYYY-MM-DD/<run_name>/`.
1. Recreate original run folder at `FQT/<run_name>/`.
1. Write `MANIFEST_POINTER.json` at original path with:
   - original run name,
   - archived location,
   - classification and signature,
   - archive timestamp.
1. Preserve a global manifest in `FQT/retention/`.

This preserves path-level references while reducing active evidence clutter.

## Deliverables Per Run

Each retention pass produces:

- `FQT/retention/fqt_retention_matrix_<date>.md`
- `FQT/retention/fqt_retention_matrix_<date>.csv`
- `FQT/retention/fqt_retention_manifest_<date>.json`
- `FQT/retention/fqt_archive_actions_<date>.json` (when apply mode is used)

## Governance Controls

- Default mode is dry-run.
- Apply mode is opt-in (`--apply`) and only archives summarize-only candidates.
- Keep-full runs are never moved by the script.
- Every move is recorded in a machine-readable action log.

## Review Cadence

Run at sprint close and prior to release evidence freeze.

Suggested command:

```powershell
"c:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/.venv/Scripts/python.exe" scripts/fqt_retention_manager.py --fqt-root FQT --retention-dir FQT/retention
```

Apply archival pass:

```powershell
"c:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/.venv/Scripts/python.exe" scripts/fqt_retention_manager.py --fqt-root FQT --retention-dir FQT/retention --apply
```
