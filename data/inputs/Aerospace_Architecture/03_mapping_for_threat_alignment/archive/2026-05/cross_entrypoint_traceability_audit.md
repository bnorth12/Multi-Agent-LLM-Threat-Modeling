# Cross-Entrypoint Traceability Audit

## Scope

Cross-compare of architecture evidence from all primary entry points:

- Hazards and failure modes to decomposition
- Hazards and failure modes to functions and flows
- Functions to flows and back to hazards
- Top-down L0 to L1 to L2 to flow coverage
- Bottom-up loop and boundary consistency

## Core Counts

- FMEA register rows: 266
- Decomposition rows: 12
- Function catalog rows: 145
- Interface rows: 54
- Inference rows: 4
- Gap rows: 4
- Control-loop rows: 5
- Boundary rows: 7

## Entrypoint Cross-Compare

### 1) Hazards and Failures to Decomposition

- Uncovered failure-mode IDs: 0
- Uncovered hazard IDs: 0
- Result: full decomposition range coverage is present for FM and HZ IDs.

### 2) Hazards and Failures to Functions and Flows

- FMEA entries linked in inference matrix: 4
- FMEA entries not yet linked in inference matrix: 262
- Inference entry IDs missing in FMEA register: 0
- Inference L2 function IDs missing in function catalog: 0
- Inference flow interface IDs missing in interface matrix: 0
- Result: inference rows are internally consistent but only a small subset of FMEA is currently bottom-up linked.

### 3) Functions to Flows to Hazards

- Interface function references missing in function catalog: 0
- Function IDs with no interface reference: 99
- Result: function-flow referential integrity is clean, but many functions are flow-orphaned.

### 4) Decomposition and Hierarchy Integrity

- L1 count: 27
- L2 count: 118
- L1 functions with zero L2 children: 1
- L1 without L2: AVI.VSYS.001
- Domain coverage:
  - AVIATE: total=46, referenced=14, unreferenced=32
  - COMMUNICATE: total=19, referenced=6, unreferenced=13
  - NAVIGATE: total=20, referenced=6, unreferenced=14
  - OPERATE: total=60, referenced=20, unreferenced=40

### 5) Control Loop and Boundary Cross-Checks

- Control-loop required interface refs missing in interface matrix: 0
- Control-loop function refs missing in function catalog: 0
- Control-loop hazard refs missing in FMEA register: 0
- Boundary interface refs missing in interface matrix: 0
- Boundary control-loop refs missing in loop matrix: 0
- Result: control-loop and boundary datasets are referentially consistent.

### 6) Gap Register Consistency

- Gap function refs missing in function catalog: 0
- Gap status counts:
  - closed: 3
  - in_progress: 1

## Primary Findings

1. Decomposition coverage is complete for seeded FM and HZ IDs.
1. Function-flow referential integrity is good, but flow coverage is incomplete (orphaned functions remain high).
1. Bottom-up hazard-to-function inference is coherent but sparse relative to full FMEA corpus.
1. One hierarchy orphan exists at L1 with no L2 children.
1. Control-loop and boundary artifacts are structurally consistent.

## Recommended Next Closure Actions

1. Expand inference mapping from seeded rows to broader FM and HZ coverage.
1. Prioritize interface additions for unreferenced L2 functions by hazard criticality and control-loop relevance.
1. Resolve the L1 hierarchy orphan by defining L2 children or explicitly retiring/reclassifying the L1 node.
1. Continue closing in-progress gap-register items with endpoint-typed flow evidence.
