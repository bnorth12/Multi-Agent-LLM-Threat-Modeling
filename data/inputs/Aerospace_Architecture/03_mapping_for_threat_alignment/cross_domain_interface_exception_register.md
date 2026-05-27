# Cross-Domain Interface Exception Register

## Purpose

Records decomposition exceptions where interface linkages cross L0 domain boundaries for same-level pairs (L1->L1 and L2->L2).
Each exception includes explicit rationale, trust-boundary class, and gate evidence references.

## Summary

- Total flagged exceptions: 30
- L1->L1 cross-domain bridges: 21
- L2->L2 cross-domain bridges: 9
- Schema version: v2.0

## Gate Linkage

- L1->L1 exceptions default gate path: G5-THREAT and G4-VERIFICATION
- L2->L2 exceptions default gate path: G4-VERIFICATION and G9-READINESS

## Evidence Requirements (minimum)

- EA-ICD
- EA-SCHEMA
- EA-TRUST-BOUNDARY-ANALYSIS
- EA-VV-TEST
- EA-THREAT-MODEL-TRACE (L1->L1)
- EA-LOGGING (L2->L2)

## Controlled Taxonomy

### Trust Boundary Classification Enum

- TB-CONTROL-INTERDOMAIN
- TB-DATA-INTERDOMAIN
- TB-MAINTENANCE-OFFBOARD
- TB-PASSENGER-SERVICE

### Disposition State Enum

- proposed
- under_review
- accepted
- mitigated
- waived
- rejected
- closed

### State Transition Guardrails

- accepted, waived, rejected, and closed require approved_by and approval_date.
- mitigated requires mitigation_due_date.
- status=closed is only valid with disposition in accepted, mitigated, waived, or closed.

## Schema v2.0 Fields

The CSV includes these governance and traceability columns in addition to the original baseline:

- disposition
- risk_acceptance_id
- mitigation_due_date
- approved_by
- approval_date
- threat_model_row_id
- vv_test_case_ids
- icd_section_ref
- schema_version

## Automation

- Validation script: scripts/validate_cross_domain_exception_policy.py
- Strict gate command:
  - python scripts/validate_cross_domain_exception_policy.py
- Auto-remediation proposal command:
  - python scripts/validate_cross_domain_exception_policy.py --proposal-only --propose-missing --proposal-out test_reports/cross_domain_exception_proposals.csv
- Policy checks:
  - Complete coverage for all cross-domain same-level interfaces detected from interface_governance_matrix.csv and function_catalog.csv
  - Required field population for governance and evidence metadata
  - Enum validation for trust_boundary_classification, disposition, status, and level_pair
  - Gate evidence token presence (EA-ICD, EA-SCHEMA, EA-TRUST-BOUNDARY-ANALYSIS, EA-VV-TEST)

CI wiring:

- Workflow: .github/workflows/ci.yml
- Non-live suite gate executes proposal generation first, then strict policy validation.

## Artifact

- cross_domain_interface_exception_register.csv
