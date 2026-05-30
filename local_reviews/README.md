# Local Independent Review Reports

This directory stores local-only independent review outputs.

Policy:
- Reports are generated on demand and by local hooks.
- Outputs remain local and are ignored by Git.
- Runtime application implementation is not modified by review generation.
- `local_reviews/latest/` is intentionally compact and keeps current per-context reports.
- `local_reviews/history/` stores long-term trend snapshots and archived timestamped reports.

Primary generator:
- `python scripts/independent_repo_review.py --sprint YYYY_MM --run-context manual --report-mode update`

Expected output files:
- `local_reviews/latest/independent_review_<sprint>_manual.md`
- `local_reviews/latest/independent_review_<sprint>_manual.json`
- `local_reviews/latest/independent_review_<sprint>_pre-commit.md`
- `local_reviews/latest/independent_review_<sprint>_pre-merge-commit.md`
- `local_reviews/latest/independent_review_<sprint>_pre-push.md`

Optional archive mode:
- `python scripts/independent_repo_review.py --sprint YYYY_MM --run-context manual --report-mode archive`
- Writes timestamped report files under `local_reviews/latest/` and compaction will move older timestamped files into `local_reviews/history/reports/`.

Report framing:
- The report uses a health score for remediation readiness.
- The final section provides remediation themes, trigger reasons, and sprint-intake guidance.
