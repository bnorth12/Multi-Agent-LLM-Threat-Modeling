# Mapping for Threat Alignment

## Scope

Templates and guidance to align functional architecture to threat, impact, and mitigation analysis.

## Current Files

- `function_to_threat_impact_mapping_template.md`
- `function_to_stix_mapping_guidance.md`
- `threat_analysis_method_overlay.md`
- `interface_governance_matrix.md`
- `interface_governance_matrix.csv`
- `gate_readiness_crosswalk_profiles.md`
- `gate_readiness_crosswalk_profiles.csv`
- `function_catalog.md`
- `function_catalog.csv`
- `bottom_up_hazard_effect_rollup_method.md`
- `l3_l4_l5_inference_matrix.csv`
- `l2_l1_rollup_gap_register.csv`
- `control_loop_closure_matrix.csv`
- `logical_component_specialization_matrix.csv`
- `interface_boundary_classification_register.csv`
- `cross_domain_interface_exception_register.csv`
- `cross_domain_interface_exception_register.md`
- `orphan_trace_register.csv`
- `orphan_closure_tranche_register.csv`
- `orphan_closure_governance_checklist.md`
- `ARTIFACT_RETENTION_AND_ARCHIVE_POLICY.md`
- `archive/README.md`
- `archive/2026-05/README.md`

## Intended Use

Use these files to map architecture decomposition outputs into threat-model artifacts and STIX-ready graph structures.

The interface-governance matrix provides a machine-readable producer-consumer catalog with assurance expectations and required gate evidence fields.

The function catalog assigns canonical IDs to all documented L1/L2 functions to support stable traceability across architecture, interfaces, threat analysis, and gate evidence.

The bottom-up rollup artifacts define how hazard and failure evidence is mapped from L3 inferred functions and implied L4/L5 implementation elements up to L2 and L1, with explicit gap closure tracking.

In this repository, Aviate/Navigate/Communicate/Operate are treated as L0 mission-function domains.

## Canonical vs Analysis Artifacts

Keep canonical architecture and safety baselines in place for active modeling and stage execution.

Canonical baseline artifacts include:

- `function_catalog.csv`
- `interface_governance_matrix.csv`
- `l3_l4_l5_inference_matrix.csv`
- `cross_domain_interface_exception_register.csv`
- `orphan_trace_register.csv`
- `orphan_closure_tranche_register.csv`

Analysis and governance evidence artifacts should be retained, but moved to archive when they are no longer active decision inputs.

Examples of archive candidates:

- one-off execution reports
- temporary reconciliation notes
- superseded audit snapshots
- stale intermediate matrices replaced by newer baselines

Use `ARTIFACT_RETENTION_AND_ARCHIVE_POLICY.md` for move criteria and archive process.

Current archived batch:

- `archive/2026-05/wave_A_to_E_execution_report.md`
- `archive/2026-05/cross_entrypoint_traceability_audit.md`
