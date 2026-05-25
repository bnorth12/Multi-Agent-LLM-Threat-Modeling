# System-Wide Deep Research Phase for Functional Failure Modes and Hazards

## Purpose

Define a repeatable method to deepen failure mode effects and hazard coverage across all system domains:

- Aviate
- Navigate
- Communicate
- Operate
- Cross-domain integrity and authority management

Communication-specific failures were used as an initial example only; this phase expands uniformly across all systems.

## Research Objective

Scale from seeded entries to a broad, evidence-backed corpus (eventually thousands of normalized functional modes and hazards) suitable for decomposition coverage analysis.

## Expansion Axes

1. Functional axis: every L1 and L2 function in `function_catalog.csv`.
1. Lifecycle axis: ground, taxi, takeoff, climb, cruise, descent, approach, landing, turnaround, maintenance.
1. Authority axis: manual, augmented, automated, mission-constrained.
1. Environment axis: nominal, adverse weather, high-traffic, degraded infrastructure, contested electromagnetic conditions.
1. Failure-pattern axis: unavailable, incorrect, delayed, intermittent, conflicting, unsafe default, unsafe recovery.

## Method

1. Build a candidate mode list per function using the five expansion axes.
1. Normalize each mode into: functional failure mode, local effect, aircraft/system effect, detectability, mitigations.
1. Map each mode to at least one public source reference.
1. Deduplicate by effect-equivalence and source-supported semantics.
1. Classify into hazard pathways and assign preliminary severity tier.
1. Store in machine-readable register with stable IDs.

## Data Quality Rules

- Every entry must have non-empty source references.
- No duplicate IDs or duplicate normalized titles.
- Every added source ID must exist in `public_source_index.md`.
- Cross-domain effects must identify boundary/control implications.

## Immediate Backlog Focus

1. Flight-control and guidance mode-transition failures.
1. Navigation database/constraint integrity failures.
1. Vehicle systems service degradation modes (power, hydraulic, pneumatic/environmental, propulsion).
1. Passenger and mission operation conflict and prioritization failures.
1. Ground-operation human-proximity hazards (including RF exposure near active antennas).

## Output Contract

- Add entries to `fmea_hazard_register.csv`.
- Reflect representative entries in `fmea_and_hazard_baseline.md`.
- Record periodic integrity snapshots in `consistency_assessment.md`.
