# Interface Governance Matrix

## Purpose

Provide a machine-readable interface catalog that pairs canonical architecture flows with governance evidence requirements.

## Machine-Readable Artifact

- `interface_governance_matrix.csv`
- `gate_readiness_crosswalk_profiles.csv`
- `function_catalog.csv`

## Required Columns

- `interface_id`
- `producer`
- `producer_function_id`
- `consumer`
- `consumer_function_id`
- `data_object`
- `rate_trigger`
- `assurance_level`
- `gate_evidence_fields`
- `evidence_artifact_refs`
- `review_checkpoint_refs`
- `gate_crosswalk_id`
- `source_doc`

## Assurance-Level Intent

- `very_high`: safety-critical control or authority-bearing data.
- `high`: mission-critical or route-critical data that can alter flight intent.
- `moderate`: operational/service data requiring integrity but not direct flight control authority.

## Gate Evidence Fields

Store the following field names in `gate_evidence_fields` as a semicolon-delimited list:

- `interface_owner`
- `data_schema_ref`
- `trust_boundary`
- `integrity_control`
- `authenticity_control`
- `rate_limit_or_trigger_rule`
- `verification_evidence_ref`
- `gate_readiness`

## Usage Rule

Update the CSV whenever a new canonical producer-consumer flow is introduced, split, or reassigned.

Every interface row must include direct evidence/checkpoint references and a `gate_crosswalk_id` that resolves to an approved evidence/checkpoint profile in `gate_readiness_crosswalk_profiles.csv`.
