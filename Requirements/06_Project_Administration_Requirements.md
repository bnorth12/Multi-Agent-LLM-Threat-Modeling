# Project Administration Requirements

|ID|Name|Requirement Text|Requirement Rationale|Verification Method|Verification Statement|
|---|---|---|---|---|---|
|ADM-001|Branch Planning Linkage|Project Management Process SHALL require each feature branch to reference a planning issue before development starts.|Planning linkage ensures scope and ownership clarity.|Inspection|Verified by branch registry review showing linked issue ID for each active feature branch.|
|ADM-002|PR-Issue Synchronization|Pull Request Process SHALL require each feature pull request to reference at least one tracked issue and update issue status on merge.|Sync between implementation and planning prevents tracking drift.|Test|Verified by PR template and automation checks rejecting PRs without issue references and confirming status updates on merge.|
|ADM-003|Checklist Completion Gate|Release Process SHALL require a completed feature branch checklist before pull request approval.|Checklist gating improves consistency and quality.|Inspection|Verified by PR review evidence showing completed checklist entries prior to approval.|
|ADM-004|Branch Completion Evidence|Feature Branch Workflow SHALL store completed checklist artifacts for each merged feature branch.|Stored evidence supports release audits and retrospectives.|Inspection|Verified by repository audit showing one completed checklist artifact per merged branch.|
|ADM-005|Release Readiness Review|Release Management Process SHALL conduct release readiness review using aggregated branch checklist evidence.|Release review reduces unresolved integration risk.|Demonstration|Verified by release meeting record containing checklist evidence and sign-off decision.|
|ADM-006|Change Control Cadence|Project Governance Process SHALL schedule recurring backlog, branch, and release sync reviews at defined cadence.|Regular governance cadence keeps plans and implementation aligned.|Inspection|Verified by calendar and meeting records demonstrating recurring sync execution.|

## Traceability Annex

Relationship definitions and placement policy: Requirements/18_Traceability_Governance_Operating_Model.md.

### Derived From

- ADM-001 through ADM-006 derived from C18-ADM-001 (Administration Governance Control Plane) in Capability_Hierarchy_Baseline.md and the L1/L2 administration governance control functions (F-ADM-GOV-CONTROLS-L1/L2)

### Allocated To

- ADM-00x allocated to C18-ADM-001 and the executable governance automation (scripts/governance_autoflow.py, verify_administration_controls.py, run_governance_*.ps1/sh, sprint-intake-gatekeeper, etc.) plus config/governance_autoflow_routing.json and independent_review_policy/exception files

### Refines

- Sprint planning/closeout checklists, feature branch templates (08_), and release process (07_) refine the high-level ADM governance obligations
- Per-sprint remediation and issue artifacts (planning/issues/, planning/governance_rounds/) add concrete instances of the ADM controls

### Satisfied By

- ADM-001 (branch-planning linkage) satisfied by planning/ artifacts, scripts/sprint_naming.py, run_traceability_blocker_planning.py, and governance_autoflow routing
- ADM-002 (PR issue synchronization) satisfied by .github/pull_request_template.md, scripts that reconcile GitHub issues, and independent review GitHub reconciliation (when enabled)
- ADM-003/004 (checklist gating and retention) satisfied by 08_Feature_Branch_Checklist_Template.md usage in feature branches, archive_hygiene.py, and retention policies
- ADM-005 (release-readiness review) satisfied by sprint closeout certifiers, verify_architecture_design_surface_coverage.py, independent_repo_review outputs, and Releases/ artifacts
- ADM-006 (cadence and review controls) satisfied by governance_autoflow.py, pre-push/pre-commit hooks, sprint execution compliance monitor, and independent review history rollup
- Primary implementation: scripts/verify_administration_controls.py :: evaluate_controls and the full set of governance_*.py / run_governance_*.sh scripts + config/ governance files
- 15_End_To_End rows (S13-002 ADM-001..006) cite scripts/verify_administration_controls.py + Tests/unit/test_administration_controls.py + Runtime_And_Orchestration_Design_Specification.md as the design anchor

### Verified By

- Tests/unit/test_administration_controls.py (TST-S13-002-ADM-00x)
- Governance execution ledger and independent review outputs (independent_reviews/latest/ and history) that record ADM control execution
- Sprint closeout certification, remediation readiness, and multi-sprint portfolio artifacts
- FQT and sprint test execution summaries that include administration/governance workflow checks where applicable
- C18-ADM-001 verification anchors in Capability_Hierarchy_Baseline.md and Function_Hierarchy_Registry.md

### Depends On

- 07_Release_Process.md, 08_Feature_Branch_Checklist_Template.md, and sprint planning/closeout templates for concrete checklist and release obligations
- config/governance_autoflow_routing.json, independent_review_policy_profiles.json, independent_review_exception_registry.json, sprint_defaults.env
- All design and capability docs for the governance surfaces they define (especially Runtime_And_Orchestration for ADM execution paths)
- 15_End_To_End_Traceability_Attributes_Registry.md (S13-002 and related ADM rows)
- planning/ issues, governance_rounds, and sprint artifacts for the planning linkage side of ADM-001
- 18_Traceability_Governance_Operating_Model.md (defines the administration governance control plane as a first-class capability) and the independent review mechanism (the primary evidence producer for ADM compliance)
