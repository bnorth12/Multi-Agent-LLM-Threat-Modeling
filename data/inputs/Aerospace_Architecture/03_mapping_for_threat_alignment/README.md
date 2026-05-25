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

## Intended Use

Use these files to map architecture decomposition outputs into threat-model artifacts and STIX-ready graph structures.

The interface-governance matrix provides a machine-readable producer-consumer catalog with assurance expectations and required gate evidence fields.

The function catalog assigns canonical IDs to all documented L1/L2 functions to support stable traceability across architecture, interfaces, threat analysis, and gate evidence.

The bottom-up rollup artifacts define how hazard and failure evidence is mapped from L3 inferred functions and implied L4/L5 implementation elements up to L2 and L1, with explicit gap closure tracking.

In this repository, Aviate/Navigate/Communicate/Operate are treated as L0 mission-function domains.

- `cross_domain_interface_exception_register.csv`r
- `cross_domain_interface_exception_register.md`
