# Independent Reviews Reports

This directory stores independent review outputs produced by local governance automation.

Naming note:
- The path remains `independent_reviews/` for compatibility with existing scripts and hooks.
- The report program and documentation refer to these artifacts as Independent Reviews.

Policy:
- Reports are generated on demand and by local hooks.
- Outputs remain local and are ignored by Git.
- Runtime application implementation is not modified by review generation.
- `independent_reviews/latest/` is intentionally compact and keeps current per-context reports.
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

Report framing:
- The report uses a health score for remediation readiness.
- The final section provides remediation themes, trigger reasons, and sprint-intake guidance.
