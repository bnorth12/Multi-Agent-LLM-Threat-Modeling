# STIX 2.1 Schema and Relationship Mapping

## Purpose

Strengthen STIX detail generation by explicitly mapping threats to threat actors, vulnerabilities, attack patterns, assets, and mitigations using STIX 2.1 object and relationship semantics.

## Core STIX 2.1 Objects for Aerospace Threat Modeling

- `threat-actor`
- `intrusion-set`
- `campaign`
- `attack-pattern`
- `vulnerability`
- `malware`
- `tool`
- `indicator`
- `observed-data`
- `identity` (organization/operator/manufacturer)
- `location` (airspace, ground segment, mission center context)
- `infrastructure` (C2, relay, staging)
- `course-of-action` (mitigation/control)
- `relationship`
- `sighting`

## Minimum Relationship Coverage

For each high-priority threat case, model the following relationship chain where evidence exists:

1. `threat-actor` `uses` `attack-pattern`
1. `attack-pattern` `targets` `identity` or `infrastructure`
1. `attack-pattern` `exploits` `vulnerability`
1. `campaign` `attributed-to` `threat-actor` (if supported)
1. `course-of-action` `mitigates` `attack-pattern`
1. `course-of-action` `remediates` `vulnerability` (if represented)

## Recommended Extended Relationships

- `indicator` `indicates` `malware` or `attack-pattern`
- `malware` `uses` `infrastructure`
- `tool` `targets` `infrastructure`
- `intrusion-set` `uses` `malware`/`tool`
- `identity` `located-at` `location`

## Mapping Contract from Internal Artifacts to STIX

| Internal Field | STIX Object/Property | Notes |
| --- | --- | --- |
| `threat_or_control_summary` | `attack-pattern.description` or `course-of-action.description` | Split threat vs mitigation semantics before export. |
| `source_url` | `external_references.url` | Preserve source attribution for each generated object. |
| `confidence` | `confidence` | Keep normalized confidence scale and transformation notes. |
| `retrieval_timestamp_utc` | `created`/`modified` provenance note | Preserve ingestion timeline traceability. |
| `artifact_id` | `external_references.external_id` | Stable crosswalk between manifest and STIX package. |

## Coverage Gaps to Track

- Missing actor attribution despite strong attack-pattern evidence.
- Vulnerabilities captured without linked mitigation objects.
- Mitigations captured as prose only without explicit `course-of-action` object.
- Incomplete relationship graph (objects generated but not connected).

## Gate Alignment

- `gate_4_threat_plausibility`: require actor-pattern-target plausibility graph.
- `gate_5_mitigation_adequacy`: require at least one mitigation relationship per high-risk pattern.
- `gate_9_stix_packaging_review`: require graph integrity checks (no orphaned high-priority objects).
