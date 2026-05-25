# Threat Analysis Method Overlay

## Purpose

Describe how major threat-analysis methods apply to the aircraft functional decomposition baseline.

## Methods and Application Points

### STRIDE

- Apply at L1, L2, L3, and L4 functions with internal to trust boundaries and across explicit trust boundaries.
- Use as initial threat hypothesis generator for each function and inter-function flow.

### Attack Path Analysis

- Build multi-step paths across Aviate, Navigate, Communicate, and Operate transitions.
- Focus on pivots across control, data, and maintenance/service boundaries.

### Mission Thread Analysis

- Evaluate how function degradation affects mission phase outcomes.
- Prioritize functions with mission-critical timing or decision impact.

### MBCRA

- Translate function compromise into mission objective degradation.
- Quantify mission impact severity and recovery constraints.

### MRAP-C

- Compare mitigation options for each high-risk function and path.
- Capture operational tradeoffs and residual risk rationale.

### CTT

- Validate modeled threat paths through exercise/test scenarios.
- Feed observed gaps back into function-to-threat mappings.

## Suggested Execution Order

1. STRIDE baseline.
1. Attack-path expansion.
1. Mission-thread and MBCRA impact analysis.
1. MRAP-C mitigation prioritization.
1. CTT validation and update cycle.

## Output Expectation

Every high-priority function should include:

- At least one STRIDE-labeled threat scenario.
- At least one attack path with mission impact narrative.
- At least one mitigation decision record with residual risk note.
