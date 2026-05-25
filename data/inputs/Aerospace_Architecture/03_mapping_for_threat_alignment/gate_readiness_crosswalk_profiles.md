# Gate-Readiness Crosswalk Profiles

## Purpose

Provide normalized gate-readiness profiles used by the interface governance matrix.

## Machine-Readable Artifact

- `gate_readiness_crosswalk_profiles.csv`

## How It Is Applied

- Every interface row in `interface_governance_matrix.csv` includes a `gate_crosswalk_id`.
- Every interface row also includes direct `evidence_artifact_refs` and `review_checkpoint_refs` values.
- The profile file defines the minimum gate, review owner, and profile intent for that ID.

## Evidence Artifact IDs

- `EA-ICD`: interface control definition
- `EA-SCHEMA`: data schema specification and version record
- `EA-TRUST-CONFIG`: trust/boundary policy configuration evidence
- `EA-THREAT-MODEL`: threat and misuse-case evidence
- `EA-SAFETY-CASE`: hazard and safety-argument evidence
- `EA-VV-TEST`: verification and validation test evidence
- `EA-SIM-RESULTS`: scenario simulation evidence
- `EA-LOGGING`: audit and logging evidence
- `EA-MONITORING`: runtime monitoring evidence
- `EA-ROUTE-RULES`: route/procedure integrity rule set
- `EA-SENSOR-VALIDATION`: sensor quality/integrity evidence
- `EA-CALIBRATION-RECORD`: calibration baseline and drift record
- `EA-HANDLING-RULES`: handling/classification policy evidence
- `EA-CHANGE-LOG`: change-control evidence
- `EA-CONOPS`: concept-of-operations evidence

## Review Checkpoint IDs

- `CP-G0-SCOPE`: scope and boundary definition check
- `CP-G1-OWNER`: ownership and accountability check
- `CP-G2-BOUNDARY`: trust-boundary definition and isolation check
- `CP-G3-INTEGRITY`: integrity/authenticity control check
- `CP-G4-VERIFICATION`: test and verification closure check
- `CP-G5-THREAT`: threat-model and misuse-case closure check
- `CP-G7-SAFETY`: hazard/safety argument closure check
- `CP-G9-READINESS`: gate readiness sign-off check
