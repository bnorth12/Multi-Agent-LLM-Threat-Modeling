# Independent Reviews Reports

This directory stores independent review outputs produced by local governance automation.

Naming note:

- The path remains `independent_reviews/` for compatibility with existing scripts and hooks.
- The report program and documentation refer to these artifacts as Independent Reviews.

Policy:

- Reports are generated on demand and by local hooks (pre-commit / pre-merge / pre-push / closeout / manual).
- **Single canonical review file**: latest/ holds exactly one pair for the active context/sprint:
  `independent_review_<sprint>_<context>.md` + `.json`. This is the single independent review.
  Other outputs (remediation obligations, ledgers, blocker plans, etc.) are embedded as appendices
  inside the main review or compacted to history immediately. No large number of separate review files.
- The canonical pair in `independent_reviews/latest/` is tracked by Git (via the ! rules in .gitignore).
  Pre-push and push (local .githooks + CI) always execute governance autoflow + independent review,
  which updates these two files. This produces a dirty working tree by design. **These two files are the
  known exception** — we know why they are there (live independent review evidence). See also the
  is_allowed_generated_review_change filter and retention policy.
- High-churn historical artifacts are compacted into `independent_reviews/history/` ...
- Evaluation order implemented by the review (independent_repo_review.py):
  1. Content-based traceability **from source code** (implementation) to all other artifacts.
  2. Content-based traces **between SE artifacts** (capability, functional decomp, architecture,
     design, requirements, tests/verification) using actual document content, not matrices.
  3. Reconciliation of external traceability matrices against the verified ground truth.
  Reported in the single review file.
- The rest of the original policy (aggressive retention, appendices embedded, etc.) remains in force.
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
- Retention (independent_review_retention.py) moves the single canonical pair (and pre-push sidecars) into timestamped `history/reports/by_context/<context>/auto_compaction_YYYYMMDD_HHMMSS/` batches (retains newest 2 by default). Everything else is compacted.

IER (Independent Engineering Review) roll-up and mitigation trail:

- Each archived canonical `independent_review_<sprint>_<context>.md|.json` in an auto_compaction batch contains the full rich report per the Independent Engineering Review Model: per-class Engineering Artifact Class Scorecards (annex fidelity for Capability Hierarchy, Functional Decomposition, Architecture, Design, Requirements, Interfaces & ICDs, Verification & Evidence, etc.), Cross-Cutting Engineering Analyses (Documentation Relationship Health, Interface-to-Functional-Decomposition Mapping at L0–L4, Traceability Matrix Audit vs actual engineering docs/impl/tests), Overall Engineering Health Score, and the "Suggested Matrix Row Additions (from Annex + Source Analysis)" section with the exact gaps flagged at that run.
- This ensures previous findings and analysis (including what suggestions were present before a matrix sync commit) are not lost when rolling up into history/.
- In addition to the full reports, retention writes `ier_mitigation_snapshot.json` in the batch (lightweight extraction of scores, under-documented counts (impl/verify/arch), suggested row counts, and presence flags for scorecards/cross-cutting/audit). This supports quick historical queries of engineering health evolution and closed gaps without full-text reparse.
- Actioned mitigations from IER suggestions are durably recorded with provenance in the primary engineering artifacts:
  - Rows added/updated in `Requirements/15_End_To_End_Traceability_Attributes_Registry.md` (IER-GAP-*, IER-RESIDUAL-*, SUGGESTED-*, Notes containing "IER action on largest gap", "Added from IER annex+source suggestion", "Ground truth present in annex + source + test; was missing from matrix").
  - Corresponding entries and extended Governing Requirement IDs / Notes in `docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md`, `Requirements/04_Traceability_Matrix.md`, and `Requirements/17_Implementation_Trace_Normalization.md`.
- Future IER runs + human review can reconstruct: "at run T the IER (with 88.1% engineering score, 4 impl under-doc, these specific suggestions) flagged X; subsequent commit added rows Y; next run showed reduced counts."
- The two latest/ canonical files remain the explicit dirty-tree exception (documented in .gitignore and is_allowed_generated_review_change); history batches are the clean archive of prior states.

Report framing:

- The report uses a health score for remediation readiness.
- The final section provides remediation themes, trigger reasons, and sprint-intake guidance.
- Post-remediation (most governance now CI-enforced), minor "Ground Truth Present But Missing In Matrix" findings for meta items are expected and tracked via the exception registry + IER model rather than blocking. Feature-level gaps (GUI, PRJ, INT, etc.) continue to be driven to closure via the suggestions mechanism.
