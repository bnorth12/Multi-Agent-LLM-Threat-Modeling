---
name: independent-repo-review
description: "Run a full-scope local independent repository review with specialized agent workflow and generate local ignored reports. Use for governance health checks before commits, merges, and branch integration decisions."
---
# Independent Repo Review Skill

## Purpose
Run a holistic Independent Engineering Review (per docs/process/Independent_Engineering_Review_Model.md) that assesses maturity, health, and quality of each engineering artifact class (Capability Hierarchy, Functional Decomposition, Architecture, Design, Requirements, Interfaces/ICDs, Implementation, Verification & Evidence, Configuration). 

It evaluates actual documentation relationships (INCOSE annexes), implementation fidelity, verification substantiation, interface-to-functional-decomposition (L0–L4) mappings, and audits traceability matrices for correctness/completeness against the underlying engineering reality (or gaps in the docs/impl/tests themselves). 

This is a comprehensive, content-based review of the Multi-Agent Threat Modeler engineering, not just repo hygiene or basic traceability accounting.

## Inputs
- Sprint ID (YYYY-MM or YYYY_MM)
- Enforcement mode (auto/off/manual)
- Severity policy profile (optional)
- Severity threshold overrides (optional)
- GitHub reconciliation mode (optional, explicit opt-in)

## Procedure
1. Execute:
```bash
python scripts/independent_repo_review.py --sprint <SPRINT> --run-context manual --report-mode update
```
2. Select a checked-in policy profile:
```bash
python scripts/independent_repo_review.py --sprint <SPRINT> --run-context manual --report-mode update --policy-profile strict
```
3. For profile-based enforcement, execute:
```bash
python scripts/independent_repo_review.py --sprint <SPRINT> --run-context manual --report-mode update --policy-profile strict --enforcement-mode auto
```
Manual enforcement levels:
```bash
python scripts/independent_repo_review.py --sprint <SPRINT> --enforcement-mode manual --enforce-on critical,major
```
4. Optional threshold policy override:
```bash
python scripts/independent_repo_review.py \
	--sprint <SPRINT> \
	--run-context manual \
	--report-mode update \
	--policy-profile default \
	--req-impl-threshold 0.75 \
	--req-verify-threshold 0.70 \
	--req-arch-threshold 0.75 \
	--issue-quality-threshold 0.95 \
	--max-planned-missing-requirement 0
```
5. Read generated markdown/json in independent_reviews/latest/.
6. Report using the Independent Engineering Review Model structure:
- Per-class maturity/health/quality scorecards (Capability Hierarchy, Functional Decomposition, Architecture, Design, Requirements, Interfaces & ICDs, Implementation, Verification & Evidence, Configuration).
- Documentation relationship health (INCOSE annex fidelity: Satisfies, Realizes, Provides/Requires, Implemented By, Verified By, etc.).
- Interface-to-Functional-Decomposition mapping (explicit L0–L4 abstraction linkages from ICD / data-flow package / annexes).
- Cross-cutting fidelity of implementation and verification.
- Traceability Matrix Audit: correctness and completeness vs. actual annex content, implementation, tests, and test artifacts (gaps in matrices *or* in the engineering artifacts themselves).
- Overall Engineering Health Score + trends.
- Consolidated findings distinguishing matrix issues from engineering documentation/impl/verification gaps.
- Actionable recommendations for engineering improvement.

7. Treat architecture/design, requirements, implementation, and verification as a single governed chain for the Multi-Agent Threat Modeler application, and note when any of those concepts appear in data-flow modeling or interface boundaries.

8. Explicitly capture where agents and skills are acting as implementation or governance participants, especially when they enforce traceability, boundary validation, or review readiness.

9. Enforce hierarchical decomposition checks in sprint artifacts so each requirement can be traced L0 -> L1 -> L2 with explicit parent-child relationships and code-level allocation.

10. Run hierarchy governance sub-workflows:
- hierarchy-taxonomy-steward for decomposition taxonomy normalization and drift control
- hierarchy-conformance-auditor for enforceable hierarchy conformance findings and metrics

11. Optional local GitHub reconciliation:
```bash
python scripts/independent_repo_review.py \
	--sprint <SPRINT> \
	--run-context manual \
	--report-mode update \
	--policy-profile default \
	--trend-window 5 \
	--github-reconcile \
	--github-repo <OWNER/REPO>
```

12. Optional archival snapshot mode:
```bash
python scripts/independent_repo_review.py --sprint <SPRINT> --run-context manual --report-mode archive
```

## Expected Outputs
- independent_reviews/latest/independent_review_<sprint>_<context>.md
- independent_reviews/latest/independent_review_<sprint>_<context>.json
- independent_reviews/history/reports/independent_review_<sprint>_<context>_<timestamp>.* (when archived)

## Health Metric
- The report uses "health" rather than "goodness" as the primary remediation readiness framing.
- A remediation health floor is read from the active policy profile and drives the final readiness verdict.

## Guardrails
- Local-only evidence execution.
- Do not depend on GitHub Actions or remote CI status.
- Do not edit runtime implementation as part of review reporting.
- GitHub reconciliation is opt-in only and must remain non-blocking unless enforce policy is explicitly chosen.
- Chain completeness must be evaluated with explicit evidence refs, not first-level ID presence.
