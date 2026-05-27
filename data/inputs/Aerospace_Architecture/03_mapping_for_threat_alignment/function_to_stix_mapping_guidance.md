# Function to STIX Mapping Guidance

## Purpose

Guide conversion from architecture functions and threat mappings into STIX 2.1 objects and relationships.

## Recommended Mapping Pattern

1. Represent function-relevant adversary behavior as `attack-pattern`.
1. Represent exploiting parties as `threat-actor` or `intrusion-set`.
1. Represent weak points as `vulnerability` where applicable.
1. Represent protections as `course-of-action`.
1. Link with explicit `relationship` objects.

## Suggested Relationship Set

- `threat-actor` `uses` `attack-pattern`
- `attack-pattern` `targets` `infrastructure` or `identity`
- `attack-pattern` `exploits` `vulnerability`
- `course-of-action` `mitigates` `attack-pattern`

## Functional Traceability Fields

- Function ID in `external_references.external_id`
- Variant tags in labels
- Safety/mission impact tags in object labels or custom properties

## Completeness Check

For high-priority functions, avoid generating isolated STIX objects without relationships.
