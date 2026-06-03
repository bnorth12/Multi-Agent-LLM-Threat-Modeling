# Working Artifact Segregation and Archive Plan (2026-06-02)

## Purpose

Reduce readability drag from high-churn working artifacts while preserving auditability and evidence lineage.

## Current Working-Set Pressure Points

- planning/ has high tracked artifact density and mixed active/historical narratives.
- FQT/ contains many generated run folders and dedup archives.
- independent_reviews/latest is active and must remain concise while history is retained elsewhere.

## Segregation Policy

1. Keep active governance surfaces small and pointer-based.
1. Archive time-bound sprint and run evidence under dated archive folders.
1. Maintain one latest summary per automation lane in independent_reviews/latest.
1. Keep generated retention reports in dedicated retention/archive folders, not active process indexes.

## Cleanup Tranches

### Tranche A: Planning Surface

- Move superseded execution logs and completion summaries into planning/archives/YYYY-MM/.
- Keep only current sprint planning, active issue tracker, and active traceability matrix in top-level planning/.
- Update planning/README.md pointers after each tranche.

### Tranche B: FQT Surface

- Run scripts/fqt_retention_manager.py without --apply for classification preview.
- Run scripts/fqt_retention_summary.py for executive rollup.
- Apply archive moves only when pointer integrity checks pass.

### Tranche C: Independent Review Surface

- Keep *_latest artifacts and current pre-push/pre-commit snapshots in independent_reviews/latest.
- Keep historical trend and round-run outputs under independent_reviews/history.
- Use run_phase4_maintenance.py to flag active-doc drift and tracked-volume growth.

## Acceptance Criteria

- Active top-level planning pages focus on current sprint execution and required references.
- Archive index and batch notes document movement rationale.
- FQT archive pointer integrity remains valid after each archive apply pass.
- Phase 4 scheduled reminders capture unresolved cleanup items.

## Operating Commands

1. python scripts/archive_hygiene.py check --staged --enforce
1. python scripts/fqt_retention_manager.py
1. python scripts/fqt_retention_summary.py --manifest FQT/retention/fqt_retention_manifest_YYYY-MM-DD.json --out FQT/retention/fqt_retention_executive_summary_YYYY-MM-DD.md
1. python scripts/run_phase4_maintenance.py --enforce
