# ISAC Source Schema Extension

## Purpose

Extend source metadata for ISAC and ISAC-adjacent public intelligence intake without breaking the existing canonical manifest schema in `manifest.csv`.

## Design

- Base manifest remains authoritative for ingestion execution.
- Extension rows are keyed separately and can be joined by `planned_artifact_id` after capture.
- Supports public-only acquisition workflows where membership feeds are not accessible.

## Extension File

- `manifest_isac_extension.csv`

## Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `candidate_id` | string | yes | Stable identifier for candidate public source (`P-ISAC-###`). |
| `community_scope` | string | yes | Source community (`aviation_isac`, `space_isac`, `regulator`, `cert`, `cross_sector`). |
| `source_url` | string | yes | Public URL used for retrieval. |
| `source_type` | string | yes | `landing_page`, `newsroom`, `publication`, `advisory_feed`, `schema_repo`, `program_page`. |
| `access_tier` | string | yes | `public`, `member_restricted`, `unknown`. |
| `handling_constraint` | string | yes | `public_releasable`, `attribution_required`, `restricted_republication`. |
| `aerospace_domain` | string | yes | `aviation`, `space`, `both`, `adjacent`. |
| `threat_surface_tags` | string | yes | Pipe-separated tags (for example `supply_chain\|ground_segment\|atm_data_exchange`). |
| `mitigation_signal_type` | string | yes | `governance`, `technical_control`, `incident_lesson`, `detection_signal`, `mixed`. |
| `retrieval_status` | string | yes | `captured`, `queued`, `failed`, `blocked_membership`, `redirected`. |
| `last_checked_utc` | string | yes | Date or datetime of latest verification. |
| `coverage_gap_reason` | string | no | Gap explanation, including `membership_required` where applicable. |
| `planned_artifact_id` | string | no | Intended `SC-###` target when capture is scheduled. |
| `next_action` | string | yes | Immediate operator action to advance readiness. |
| `notes` | string | no | Provenance or caveat notes. |

## Gate Relevance

- `gate_4_threat_plausibility`: enabled by `threat_surface_tags`, `community_scope`, and corroborated `source_type`.
- `gate_5_mitigation_adequacy`: enabled by `mitigation_signal_type` and `handling_constraint`.
- `gate_7_export_consistency`: enabled by `access_tier`, `retrieval_status`, and reproducible provenance fields.
