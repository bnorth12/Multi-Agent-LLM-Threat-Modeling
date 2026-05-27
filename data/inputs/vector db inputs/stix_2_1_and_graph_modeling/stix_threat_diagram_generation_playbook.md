# STIX Threat Diagram Generation Playbook

## Purpose

Provide repeatable steps for converting STIX 2.1 objects and relationships into readable threat diagrams that preserve analytical correctness.

## Diagram Goals

- Show who (`threat-actor`, `intrusion-set`) does what (`attack-pattern`, `malware`, `tool`).
- Show what is affected (`identity`, `infrastructure`, `location`).
- Show what mitigates risk (`course-of-action`) and where evidence exists (`indicator`, `observed-data`).

## Minimal Diagram Node Set

1. Actor nodes: `threat-actor`, `intrusion-set`
1. Behavior nodes: `attack-pattern`, `campaign`
1. Exposure nodes: `vulnerability`
1. Asset nodes: `identity`, `infrastructure`
1. Control nodes: `course-of-action`

## Edge Semantics

- `uses`
- `targets`
- `exploits`
- `attributed-to`
- `mitigates`
- `indicates`

## Rendering Guidance

1. Group nodes by layer: actor, behavior, exposure, asset, mitigation.
1. Use confidence-based styling (for example dotted edges for low confidence).
1. Label each edge with STIX relationship type.
1. Include source reference IDs on nodes for audit traceability.

## Recommended Output Views

- **Plausibility View**: actor to attack-pattern to asset chain (gate 4 emphasis).
- **Mitigation View**: attack-pattern/vulnerability to course-of-action chain (gate 5 emphasis).
- **Export Integrity View**: full connected graph with provenance markers (gate 9 emphasis).

## Quality Checks Before Export

1. No orphaned high-priority attack-pattern nodes.
1. Every promoted vulnerability has at least one relationship to pattern or mitigation.
1. Every mitigation in report text maps to a STIX `course-of-action` object.
1. Diagram node and edge counts match STIX bundle object/relationship counts.
