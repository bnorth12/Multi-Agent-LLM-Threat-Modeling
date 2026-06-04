# Documentation Authority Matrix

## Purpose

Define the authoritative documentation path for each systems-engineering domain and identify non-authoritative references that should be treated as supporting context.

Primary ownership policy note: `docs/process/Artifact_Ownership_And_Evidence_Authority.md`.

## Scope

- Architecture
- Design
- Requirements
- Implementation and runtime
- Verification and evidence
- Sprint governance and closeout

## Authority Matrix

| Domain | Primary Authority | Secondary/Supporting | Typical Consumers | Update Gate |
|---|---|---|---|---|
| Project Concept and Big Picture | `README.md` | `docs/README.md`, `docs/INDEX.md` | New engineers, reviewers, leadership | Major architecture or process change |
| Architecture Baseline | `docs/architecture/Multi_Agent_Threat_Modeler_Architecture_Baseline.md` | `docs/architecture/framework_overview.md`, `docs/architecture/architecture_diagram.mermaid` | Architects, implementers | Architecture change approval |
| Design Authority | `docs/design/README.md` and `docs/design/system/*` plus `docs/design/software/*` | `planning/design_reviews/*` | Architects, implementers, reviewers | Design disposition complete |
| Requirements Baseline | `Requirements/README.md` and `Requirements/04_Traceability_Matrix.md` | `Requirements/Components/*`, `Requirements/appendices/*` | Product owner, implementers, QA | Requirement review and taxonomy check |
| End-to-End Traceability Registry | `Requirements/15_End_To_End_Traceability_Attributes_Registry.md` | `planning/Sprint_*_Traceability_Matrix.md` | Governance, release, audit | Sprint gate verification |
| Verification Strategy and Test Governance | `Requirements/05_Verification_Strategy.md` and `Tests/README.md` | `Tests/*_Verification_Backfill.md`, `planning/Test_Execution_Summary_*.md` | QA, implementers, release leads | Test lane governance check |
| Sprint Lifecycle Process | `docs/process/Governance_and_Traceability_Index.md` and `docs/process/Sprint_Lifecycle_and_Automated_Governance.md` | `docs/process/Definition_of_Done.md`, `docs/process/Requirements_and_Issues_Policy.md` | Sprint leads, engineers, reviewers | Retrospective process update |
| User and Operator Guidance | `docs/INDEX.md` to `docs/user_manual/index.html` | `docs/User_Manual.md`, `docs/screenshots/README.md` | Operators, test teams | UI release gate |
| Independent Review Evidence (Current) | `independent_reviews/latest/*_latest.md` and `independent_reviews/latest/independent_review_*_pre-push.md` | `independent_reviews/latest/*.json` | Governance and release certifiers | Hook/workflow completion |
| Historical and Archived Evidence | `planning/archives/`, `independent_reviews/history/`, `FQT/archive_dedup/` | planning historical sprint artifacts | Auditors, forensic review | Archive hygiene policy |

## Authoritative Navigation Rule

A new engineer should be able to start in any one of these anchors and move bidirectionally:

1. README.md for concept and system mission.
1. docs/INDEX.md for architecture, design, and operational docs.
1. Requirements/README.md for requirement taxonomy and evidence expectations.
1. docs/process/Governance_and_Traceability_Index.md for execution workflow.
1. Tests/README.md for verification lanes and evidence requirements.

## De-duplication Rule

If two active documents describe the same governance rule, keep one authoritative source and convert the other to a short pointer with rationale.

## Ownership

- Technical Lead: architecture, design, and process authority surfaces.
- Product Owner: requirement baseline and sprint issue linkage quality.
- QA Lead: verification strategy, test evidence lane policy, and closure evidence quality.
