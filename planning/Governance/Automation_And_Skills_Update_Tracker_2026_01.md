# Governance Automation and Skills Update Tracker 2026_01

## Scope Boundary

This tracker captures governance automation and skill-definition updates only.

It is intentionally separate from remediation execution items (`R01-*`) so governance-tooling debt is auditable as an independent workstream.

## Current Automation and Skill Findings

| Governance ID | Type | Finding | Evidence | Impact | Required Update | Owner | Status |
|---|---|---|---|---|---|---|---|
| GOV-AUTO-001 | Automation | Sprint tracker status parsing uses wrong table cell index (`cells[5]`) and reads Requirement ID instead of Status. | scripts/verify_sprint_traceability.py; scripts/run_sprint_closeout_certification.py | False status distribution (`other` inflation) can mask residual active governance work. | Update parser to read actual status column index and add header-aware table parsing tests. | Governance Automation | Completed |
| GOV-AUTO-002 | Automation | Traceability verifier does not enforce presence/linkage of capability and function root artifacts. | scripts/verify_sprint_traceability.py | Chain can appear complete while root hierarchy artifacts drift or are missing. | Add explicit checks that capability/function IDs in sprint scope are defined in root hierarchy docs and linked through Requirements/15 registry. | Governance Automation | Completed |
| GOV-AUTO-003 | Automation | Closure evidence check is keyword-heuristic based and not schema-driven. | scripts/verify_sprint_traceability.py | Closeout pass/fail can be sensitive to wording rather than structural evidence quality. | Replace keyword heuristic with structured section parser and required evidence fields checklist. | Governance Automation | Completed |
| GOV-AUTO-004 | Automation | Closeout certifier certifies with `residual_active == 0` based on tracker parser that currently mis-parses status field. | scripts/run_sprint_closeout_certification.py | Certification confidence is reduced when issue status accounting is unreliable. | Correct parser and add certification precondition test vectors for mixed status datasets. | Governance Automation | Completed |
| GOV-AUTO-005 | Automation | Multi-sprint planner did not enforce governance-first remediation sequencing and baseline gating before implementation-focused remediation. | scripts/run_multi_sprint_portfolio_planning.py | Planning could prematurely schedule implementation work before governance and traceability baseline closure. | Add governance tracker parsing, non-implementation baseline readiness gate, and explicit governance-first portfolio sequence. | Governance Automation | Completed |
| GOV-SKILL-001 | Skill | Architecture/design authoring skill lacks explicit contract checks for root hierarchy artifacts and Requirements/15 linkage. | .github/skills/architecture-design-change-author/SKILL.md | Manual skill runs may omit mandatory root-to-evidence chain enforcement. | Add mandatory checklist fields for capability root, function root, Requirements/15 row, and verification artifact metadata references. | Governance Process | Completed |
| GOV-SKILL-002 | Skill | Source-to-evidence skill defines four-leg chain but does not require root capability/function artifact validation. | .github/skills/source-to-evidence-traceability/SKILL.md | Requirement chain can pass without validating capability/function roots. | Expand procedure to include root artifact coverage checks and fail conditions for missing root links. | Governance Process | Completed |
| GOV-SKILL-003 | Skill | Intake gatekeeper skill does not explicitly gate on root hierarchy integrity. | .github/skills/sprint-intake-gatekeeper/SKILL.md | Intake may admit scope with weak capability/function root lineage. | Add hard gate criterion requiring valid capability/function root lineage before intake readiness. | Governance Process | Completed |

## Execution Policy for Governance Updates

- Governance automation and skill updates must be tracked, implemented, reviewed, and closed under `GOV-*` IDs.
- Do not close `R01-*` remediation items using governance-tooling updates as substitute evidence.
- Governance updates require independent verification runs before they can influence remediation verdicts.

## Verification Requirements for GOV Updates

- Add parser unit tests for status extraction and closure evidence schema checks.
- Run sprint traceability verification in pre-push context after parser changes.
- Run sprint closeout certification with test fixtures that include mixed issue statuses.
- Produce before/after comparison in governance execution ledger.
