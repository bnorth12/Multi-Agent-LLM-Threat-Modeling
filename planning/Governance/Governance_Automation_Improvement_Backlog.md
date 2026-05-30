# Governance Automation Improvement Backlog

Purpose: track governance automation debt and policy evolution items separately from product/application technical debt.

## Scope Boundaries

- Governance automation debt: issues in policy routing, enforcement behavior, evidence ledgers, exception handling, and governance reporting automation.
- Application technical debt: issues in runtime features, APIs, UI behavior, data models, or non-governance application architecture.

## Intake and Tracking Method

- New item source: independent review, governance autoflow, retrospectives, or policy audits.
- Each backlog item must include: owner, rationale, due sprint target, disposition recommendation, and evidence links.
- Status states: Proposed, Approved, In Progress, Deferred, Closed.
- Every deferred item requires an explicit review date and acceptance rationale.

## Backlog Items

| ID | Title | Category | Status | Owner | Target Sprint | Disposition | Notes |
|---|---|---|---|---|---|---|---|
| GOV-AUTO-001 | Governance ledger should surface latest remediation obligation count and source artifact links | Governance automation | Closed | Governance maintainers | 2026_01 | Include | Implemented in governance autoflow ledger summary and payload output. |
| GOV-AUTO-002 | Add formal historical debt disposition workflow (Reject/Defer/Include) with auditable decision records | Governance automation | Proposed | Governance maintainers | 2026_02 | Defer | Candidate future feature after baseline debt burn-down; should include approver, rationale, expiry, and escalation fields. |
| GOV-AUTO-003 | Add governance-debt queue analytics (age, due sprint drift, ownership gaps) | Governance automation | Proposed | Governance maintainers | 2026_02 | Include | Supports better burn-down sequencing and overdue detection for exception-backed debt. |
| GOV-AUTO-OBL-B20FE1CC | Triaged obligation (critical): Verification coverage ratio 0.22 is critically below threshold 0.75. | Governance automation | Proposed | Governance maintainers | 2026_01 | Include | Auto-triaged from C:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/independent_reviews/latest/remediation_obligations_2026-12_pre-push.json; rule=legacy-baseline-coverage-gap-2026-12; plan=planning/Sprint_2026_01_Remediation_Restart_Manifest.md. |
| GOV-AUTO-OBL-E1DECC8A | Triaged obligation (critical): Implementation coverage ratio 0.37 is critically below threshold 0.80. | Governance automation | Proposed | Governance maintainers | 2026_01 | Include | Auto-triaged from C:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/independent_reviews/latest/remediation_obligations_2026-12_pre-push.json; rule=legacy-baseline-coverage-gap-2026-12; plan=planning/Sprint_2026_01_Remediation_Restart_Manifest.md. |
| GOV-AUTO-OBL-F3B4A013 | Triaged obligation (major): Architecture/design trace ratio 0.47 is below threshold 0.80. | Governance automation | Proposed | Governance maintainers | 2026_01 | Include | Auto-triaged from C:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/independent_reviews/latest/remediation_obligations_2026-12_pre-push.json; rule=legacy-baseline-coverage-gap-2026-12; plan=planning/Sprint_2026_01_Remediation_Restart_Manifest.md. |
| GOV-AUTO-OBL-875E4C2D | Triaged obligation (major): Hierarchy governance fields are incomplete in sprint issue artifacts:... | Governance automation | Proposed | Governance maintainers | 2026_01 | Include | Auto-triaged from C:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/independent_reviews/latest/remediation_obligations_2026-12_pre-push.json; rule=legacy-baseline-coverage-gap-2026-12; plan=planning/Sprint_2026_01_Remediation_Restart_Manifest.md. |
| GOV-AUTO-OBL-8481C591 | Triaged obligation (major): Required traceability artifacts are present but not referenced by pla... | Governance automation | Proposed | Governance maintainers | 2026_01 | Include | Auto-triaged from C:/Users/brian/OneDrive/Documents/GitHubRepos/Multi Agent Threat Modeler/independent_reviews/latest/remediation_obligations_2026-12_pre-push.json; rule=legacy-baseline-coverage-gap-2026-12; plan=planning/Sprint_2026_01_Remediation_Restart_Manifest.md. |

## Decision Model (Future Concept)

This repository may later implement explicit disposition logic for historical governance debt with three outcomes:

- Reject: finding must be fixed before progressing.
- Include: finding accepted into active remediation scope with due sprint and owner.
- Defer: finding postponed with explicit justification, review date, and approval trail.

This logic is intentionally deferred until initial debt burn-down stabilizes.

## Related Artifacts

- independent_reviews/latest/remediation_obligations_2026-12_pre-push.md
- config/independent_review_exception_registry.json
- planning/work_items/Application_Tech_Debt_Backlog.md
