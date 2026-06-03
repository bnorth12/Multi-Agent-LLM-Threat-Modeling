# Independent Change-Set Separation 2026_01

## Purpose

Maintain two independently governable change sets so governance/automation work does not get mixed with Multi Agent Threat Modeler remediation implementation work.

## Change-Set Lanes

| Lane | Scope | Primary IDs | Canonical Artifacts | Closure Authority |
|---|---|---|---|---|
| Lane A: Governance and Automation | Policy rules, automation scripts, quality gates, governance trackers, skill contracts | GOV-*, GOV-AUTO-*, GOV-SKILL-* | planning/Governance/Automation_And_Skills_Update_Tracker_2026_01.md; planning/issues/issue_2026_01_GOV-001_Automation_Skill_Traceability_Contract_Enforcement.md; scripts/verify_sprint_traceability.py; scripts/run_sprint_closeout_certification.py; scripts/run_traceability_blocker_planning.py; scripts/run_multi_sprint_portfolio_planning.py | Governance closeout artifacts and governance execution ledger |
| Lane B: Multi Agent Threat Modeler Remediation | Requirement, architecture/design, implementation, verification remediation slices | R01-* (and linked requirement IDs) | planning/issues/Sprint_2026_01_Issue_Tracker.md; planning/issues/issue_2026_01_R01-003_C11_LLM_004_Architecture_Traceability_Remediation.md; Requirements/15_End_To_End_Traceability_Attributes_Registry.md; docs/architecture/Capability_Function_Architecture_Traceability_Matrix.md | Sprint closeout certification and remediation readiness |

## Hard Separation Rules

1. Do not close any R01 item using only GOV evidence.
1. Do not mark GOV items complete based on R01 implementation-only evidence.
1. Commit and review by lane where feasible:
   - Lane A commit set: governance scripts, governance trackers, skills, policy docs.
   - Lane B commit set: remediation issue files, requirement rows, architecture/design rows, verification evidence links.
1. Run automation for both lanes, but report outcomes independently.

## Independent Reporting Contract

### Lane A Required Outputs

- governance execution ledger
- governance automation tracker status
- traceability verifier parser and gate behavior status

### Lane B Required Outputs

- sprint closeout certification verdict
- residual active remediation issue count
- traceability blocker backlog counts by category
- pre/post KPI drift for remediation sprint

## Current Separation Status (2026_01)

- Lane A status: active and tracked in GOV artifacts.
- Lane B status: active with conditional closeout and residual backlog.
- Cross-lane dependency: Lane B implementation-focused work remains deferred until governance and non-implementation baseline gates are satisfied.

## Independent Management Commands

### Lane A (Governance)

```powershell
& ".\\.venv\\Scripts\\python.exe" scripts/verify_sprint_traceability.py --sprint 2026_01 --audit
& ".\\.venv\\Scripts\\python.exe" scripts/run_multi_sprint_portfolio_planning.py --sprint 2026_01
```

### Lane B (Remediation)

```powershell
& ".\\.venv\\Scripts\\python.exe" scripts/run_traceability_blocker_planning.py --sprint 2026_01
& ".\\.venv\\Scripts\\python.exe" scripts/run_sprint_closeout_certification.py --sprint 2026_01
```
