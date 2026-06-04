# Independent Reviews Reports

This directory stores independent review outputs produced by local governance automation.

Naming note:

- The path remains `independent_reviews/` for compatibility with existing scripts and hooks.
- The report program and documentation refer to these artifacts as Independent Reviews.

Policy:

- Reports are generated on demand and by local hooks.
- Current operational snapshots in `independent_reviews/latest/` are tracked by Git via selective allowlist rules.
- High-churn historical artifacts are compacted into `independent_reviews/history/` and remain ignored to prevent uncontrolled repository growth.
- Runtime application implementation is not modified by review generation.
- `independent_reviews/latest/` is intentionally compact and keeps current per-context reports.
- High-churn iterative artifacts (for example timestamped one-off planning snapshots and legacy round-run batches) should be compacted into `independent_reviews/history/reports/` after active triage or closeout.
- For sprint-specific independent review pre-context outputs (`pre-commit`, `pre-merge-commit`, `pre-push`), keep one canonical latest set per run-context in `latest/` and archive older sprint-specific variants under `history/reports/`.
- The independent review report now carries remediation obligations as Appendix A and governance execution telemetry as Appendix B, so `latest/` can stay to a single canonical review pair.
- One-time KPI backfill outputs and superseded remediation planning artifacts should be archived to `history/reports/` once their guidance is absorbed into the embedded review appendices.
- Governance autoflow routes a first-class independent review history-rollup stage before review execution in the contexts that need latest-output compaction.
- Retention is aggressive by design: `latest/` keeps only the canonical review pair for the active context, while manual and historical context reports are moved to `history/reports/`.
- Auto-compaction history retention policy keeps the two most recent `history/reports/auto_compaction_*` batches and writes a rollup summary for older batches before removing those older auto batches.
- `independent_reviews/history/` stores long-term trend snapshots and archived timestamped reports.
- GitHub issue reconciliation is default-on in the review engine when `gh` is available (not opt-in).
- Reconciliation outcomes are informational unless a separate explicit enforcement control is chosen.

Primary generator:

- `python scripts/independent_repo_review.py --sprint YYYY_MM --run-context manual --report-mode update`

Expected output files:

- `independent_reviews/latest/independent_review_<sprint>_manual.md`
- `independent_reviews/latest/independent_review_<sprint>_manual.json`
- `independent_reviews/latest/independent_review_<sprint>_pre-commit.md`
- `independent_reviews/latest/independent_review_<sprint>_pre-merge-commit.md`
- `independent_reviews/latest/independent_review_<sprint>_pre-push.md`

Optional archive mode:

- `python scripts/independent_repo_review.py --sprint YYYY_MM --run-context manual --report-mode archive`
- Writes timestamped report files under `independent_reviews/latest/` and compaction will move older timestamped files into `independent_reviews/history/reports/`.

Routed history rollup:

- `python scripts/governance_autoflow.py --context pre-push --sprint YYYY_MM --out-dir independent_reviews/latest`
- The routed history-rollup stage archives stale latest artifacts and updates the history compaction summary before the review stage runs.

Report framing:

- The report uses a health score for remediation readiness.
- The final section provides remediation themes, trigger reasons, and sprint-intake guidance.
