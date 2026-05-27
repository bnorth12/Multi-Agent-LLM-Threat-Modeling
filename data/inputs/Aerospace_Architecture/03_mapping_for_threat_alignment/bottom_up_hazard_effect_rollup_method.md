# Bottom-Up Hazard/Effect Rollup Method

## Purpose

Define the formal method for rolling bottom-up hazard and failure evidence upward through architecture levels.

## Level Semantics

1. L0: Aviate, Navigate, Communicate, Operate.
1. L1: subsystem function families.
1. L2: specific functions from `function_catalog.csv`.
1. L3: inferred functional behaviors derived from effects and hazards.
1. L4: implied component realization points (where identifiable).
1. L5: implied hardware or software implementation anchors.

## Abstraction Rule

Every upward level is a higher abstraction that aggregates multiple lower-level items:

1. L3 to L2: one L2 function should generally cover multiple L3 inferred behaviors.
1. L2 to L1: one L1 family should aggregate multiple L2 functions.
1. L1 to L0: one L0 domain should aggregate multiple L1 families.

Flow rollup follows the same rule: higher-level flow intent must summarize multiple lower-level producer-consumer flows.

## Current State

- Structured catalog exists for L1 and L2 (`function_catalog.csv`).
- L3 exists as prose examples in decomposition docs, not yet in structured trace tables.
- L4 and L5 are not explicitly modeled as architecture truth today; they are inferred from evidence.

## Required Mapping Sequence

1. Start at effects and hazards (`fmea_hazard_register.csv`).
1. Infer L3 behavior nodes using evidence and affected function context.
1. Map each L3 node to one or more L2 function IDs.
1. Roll mapped L2 nodes up to L1 families.
1. Roll mapped L1 families up to L0 domains.
1. Record unresolved nodes as explicit gaps at L2 and L1.

## Gap Rules

- L2 gap: no valid L2 function can be linked from L3 evidence.
- L1 gap: L2 links exist, but no complete L1 family covers behavior/effect intent.
- Flow gap: L2 function exists but required producer-consumer edge is missing from `interface_governance_matrix.csv`.
- Endpoint gap: flow exists but source or sink endpoint cannot be identified to function, and to component where possible.
- Abstraction gap: rollup is one-to-one where many-to-one aggregation is expected, indicating over-fragmented or under-modeled hierarchy.

## Output Artifacts

- `l3_l4_l5_inference_matrix.csv`
- `l2_l1_rollup_gap_register.csv`

## Acceptance Criteria

1. Every high-severity hazard chain has at least one mapped L2 function.
1. Every mapped L2 function has at least one flow edge or a documented exception.
1. Every unresolved mapping is captured in the gap register with closure owner and plan.
1. Every L1 family mapped for comparison demonstrates aggregation of at least two L2 functions unless explicitly justified.
1. Every L0 domain used in gap analysis demonstrates aggregation of at least two L1 families unless explicitly justified.
