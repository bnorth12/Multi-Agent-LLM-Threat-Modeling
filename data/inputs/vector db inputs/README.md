# Vector DB Inputs Taxonomy

## Purpose

This folder stores ingestion-ready artifacts for threat-model retrieval and reasoning.

## Required Separation

- `conference_inputs/`: conference-derived research and mappings.
- `standards_information/`: protocol, bus, and assurance standards references.
- `non_conference_threat_references/`: threat intelligence and case studies from non-conference sources.
- `Protocol Specifications/`: canonical protocol and bus behavior profiles used for threat modeling.
- `Inteface Specications/`: user-defined interface-specification landing zone aligned with existing taxonomy.
- `Aerospace CTI/`: canonical aerospace cyber-threat intelligence, advisory digests, and framework mappings.
- `stix_2_1_and_graph_modeling/`: STIX 2.1 schema guidance and threat-relationship diagram generation playbooks.
- `threat_modeling_methods/`: structured analysis methods for detailed threat and risk assessment.
- `taxonomy/`: cross-cutting gap analysis and corpus-level governance notes.
- `source_copies/`: captured source artifacts and extraction-ready text.
- `conference_research/`: legacy pointer-only folder retained for backward compatibility.

## Minimum Ingestion Contract

Each document should include:

- source URLs and retrieval date
- technical implementation details
- threat-model implications and controls
- confidence notes and caveats

## ISAC Public-Source Intake

When member-only ISAC feeds are not available, use:

- `taxonomy/isac_public_ingestion_playbook.md` for capture and gating workflow.
- `source_copies/manifests/isac_source_schema_extension.md` for extension field definitions.
- `source_copies/manifests/manifest_isac_extension.csv` for candidate-source tracking.

## Current Structure Status

- Conference content is canonical under `conference_inputs/`.
- Protocol and bus standards are canonical under `Protocol Specifications/`.
- Standards and partitioning assurance remain canonical under `standards_information/`.
- Aerospace CTI advisories and backlog are canonical under `Aerospace CTI/`.
- STIX and graph-modeling references are canonical under `stix_2_1_and_graph_modeling/`.
- Method references for detailed risk analysis are canonical under `threat_modeling_methods/`.
- Cross-cutting taxonomy artifacts are canonical under `taxonomy/`.
- `conference_research/` contains pointer stubs only (no canonical source content).
- `non_conference_threat_references/` is retained as compatibility entry points for CTI references.
- Non-conference threat references and source-copy captures are tracked in dedicated folders.

## Governance Crosswalk for HITL Stages

This crosswalk maps each top-level folder to Canonical versus Compatibility status and defines minimum evidence fields required for reliable use across HITL gates and downstream stage execution.

| Top-Level Folder | Status | Primary Content Role | HITL Gate Scope Enabled | Required HITL Evidence Fields | Stage Usability Notes |
| --- | --- | --- | --- | --- | --- |
| `conference_inputs/` | Canonical | Conference-derived source details and threat pattern mappings | `gate_1_normalization_review`, `gate_4_threat_plausibility` | `source_url`, `retrieval_date`, `threat_pattern_id`, `affected_assets`, `confidence`, `linked_source_copy` | Supports threat-seed quality for stages 01, 04, 05 and improves explainability in stage 09 reporting. |
| `standards_information/` | Canonical | Assurance-oriented standards, especially partitioning and separation-kernel baseline | `gate_2_boundary_approval`, `gate_3_stride_calibration`, `gate_5_mitigation_adequacy` | `standard_name`, `version_or_revision`, `control_objective`, `boundary_assumption`, `verification_reference`, `confidence` | Provides safety-security assumptions for stages 02, 03, 04, 07 and evidence context for stage 09. |
| `non_conference_threat_references/` | Compatibility | Legacy entry points to Aerospace CTI advisories and backlog | `gate_4_threat_plausibility` (reference only) | `canonical_target_path`, `pointer_validated_date`, `source_authority`, `linked_source_copy` | Do not use as sole source for decisions; resolve to canonical Aerospace CTI artifact before stage 05/07 output promotion. |
| `Protocol Specifications/` | Canonical | Protocol and bus behavior with threat implications and controls | `gate_2_boundary_approval`, `gate_3_stride_calibration`, `gate_4_threat_plausibility` | `protocol_or_bus`, `implementation_context`, `threat_scenarios`, `control_candidates`, `confidence`, `linked_source_copy` | Core technical baseline for stages 02 to 05 and mitigation shaping in stage 07. |
| `Inteface Specications/` | Canonical (staging) | Interface-specific intake zone pending normalization into protocol/assurance corpora | `gate_1_normalization_review`, `gate_2_boundary_approval` | `interface_name`, `producer_consumer`, `trust_boundary_crossing`, `data_classification`, `normalization_status`, `review_owner` | Valid for stage 01/02 intake only until normalized and cross-linked to canonical technical artifacts. |
| `Aerospace CTI/` | Canonical | Aerospace CTI advisories, backlog, and framework mappings including SPARTA baseline | `gate_4_threat_plausibility`, `gate_5_mitigation_adequacy` | `source_url`, `retrieval_date`, `sparta_mapping`, `attack_or_incident_summary`, `mitigation_status`, `confidence`, `linked_source_copy` | Primary CTI corpus for stages 05 and 07; required for high-confidence threat realism in stage 09 exports. |
| `stix_2_1_and_graph_modeling/` | Canonical | STIX object/relationship mapping and graph/diagram generation guidance | `gate_7_export_consistency`, `gate_9_stix_packaging_review` | `stix_object_type`, `relationship_type`, `source_reference_ids`, `confidence`, `graph_integrity_check`, `packaging_notes` | Strengthens stage 09 export quality and prevents under-modeled STIX relationship output. |
| `threat_modeling_methods/` | Canonical | Method library for STRIDE, attack path, mission thread, MBCRA, MRAP-C, and CTT workflows | `gate_3_stride_calibration`, `gate_4_threat_plausibility`, `gate_5_mitigation_adequacy` | `method_name`, `assumptions`, `risk_rationale`, `mitigation_tradeoff`, `validation_evidence`, `traceability_link` | Improves analytical rigor and consistency for stage 03 to stage 07 decision quality. |
| `taxonomy/` | Canonical | Gap analysis, corpus governance, and completeness controls | `gate_1_normalization_review`, `gate_7_export_consistency` | `coverage_domain`, `gap_statement`, `priority`, `owner`, `target_sprint`, `traceability_link` | Drives governance readiness and release-quality checks for stages 01 and 09. |
| `source_copies/` | Canonical | Raw and extracted provenance artifacts with queue and manifest tracking | `gate_0_input_integrity`, `gate_1_normalization_review`, `gate_7_export_consistency`, `gate_9_stix_packaging_review` | `source_id`, `source_url`, `retrieval_timestamp_utc`, `capture_method`, `raw_path`, `extracted_path`, `manifest_row_id`, `hash_or_integrity_note` | Mandatory provenance substrate for stages 01 through 09; absence should block acceptance at gate 0 or gate 7. |
| `conference_research/` | Compatibility | Pointer-only backward compatibility to canonical conference and standards assets | `gate_1_normalization_review` (pointer validation only) | `canonical_target_path`, `pointer_validated_date`, `no_canonical_payload=true` | Legacy compatibility only; artifacts must be dereferenced to canonical folders before stage decisions. |

## HITL Evidence Field Contract (Minimum)

To ensure ingestion data is executable across HITL stages, each candidate artifact should expose or derive the following contract fields:

- `artifact_id`
- `canonical_folder`
- `status` (`canonical` or `compatibility`)
- `source_url`
- `retrieval_timestamp_utc`
- `threat_or_control_summary`
- `confidence`
- `linked_source_copy`
- `traceability_link` (requirement, issue, or test reference)
- `gate_readiness` (list of gate IDs artifact can support)

Artifacts missing `source_url` + `retrieval_timestamp_utc` + `linked_source_copy` should be treated as non-approvable at `gate_0_input_integrity` and non-exportable at `gate_7_export_consistency`.
