# Subsystem-by-Subsystem Research Execution Plan

## Objective

Maximize failure-mode and hazard discovery by executing deep research one subsystem at a time, with strict source and normalization controls.

## Execution Sequence

1. P1 subsystems first: SS-01, SS-02, SS-03, SS-06, SS-08, SS-09.
1. P2 subsystems next: SS-04, SS-05, SS-07, SS-10.
1. Close with cross-subsystem coupling pass for interaction hazards.

## Per-Subsystem Work Package

For each subsystem:

1. Build a function map from `function_catalog.csv` (all relevant L1 and L2 functions).
1. Generate candidate failure-pattern combinations across lifecycle and authority states.
1. Retain only source-backed candidates with clear local and system effects.
1. Convert retained candidates into normalized `FM-*` and `HZ-*` entries.
1. Append machine-readable rows to `fmea_hazard_register.csv`.
1. Add representative human-readable rows to `fmea_and_hazard_baseline.md`.
1. Run integrity checks and update `consistency_assessment.md`.

## Gate Criteria Per Subsystem

- No duplicate IDs and no duplicate normalized titles.
- All source IDs resolve in `public_source_index.md`.
- At least one hazard chain mapped to each major function cluster in the subsystem.
- At least one detectability/mitigation narrative captured for each new failure family.

## Throughput Targets

- P1 subsystem tranche: 20 to 25 new failure modes and 12 to 15 hazards each.
- P2 subsystem tranche: 12 to 20 new failure modes and 8 to 12 hazards each.
- Cross-subsystem coupling tranche: at least 30 interaction-driven entries.

## Why This Increases Yield

- Focused subsystem sweeps reduce missed patterns caused by mixed-domain context switching.
- Repeated per-subsystem templates improve comparability and deduplication quality.
- Priority ordering aligns the largest known operational risk surfaces to earliest expansion.

## Tranche 1 Completion Snapshot

- Executed subsystems: `SS-01`, `SS-02`, `SS-03`.
- New tranche-1 additions: `18` failure modes (`FM-031` through `FM-048`) and `9` hazards (`HZ-027` through `HZ-035`).
- Tranche-1 objective outcome: guidance/route/communications clusters now include richer mode-transition, integrity, and channel-divergence patterns.

## Tranche 2 Plan

### Tranche 05-11 Scope

1. `SS-06` Hydraulic and braking systems.
1. `SS-08` Ice protection and weather response.
1. `SS-09` Mission systems and authority arbitration.

### Expansion Targets

- `SS-06`: add 18 failure modes and 10 hazards.
- `SS-08`: add 16 failure modes and 9 hazards.
- `SS-09`: add 16 failure modes and 10 hazards.
- Tranche-2 subtotal: `50` failure modes and `29` hazards.

### Execution Order

1. Start with `SS-06` because high-energy ground-phase consequences require early runway-risk closure.
1. Continue with `SS-08` to capture weather-coupled and icing-coupled control degradations.
1. Finish with `SS-09` to bind mission authority conflicts to already-expanded aviate/navigate/communicate failures.

### Tranche-2 Gate Exit Criteria

- Every new row includes source-backed evidence IDs from `public_source_index.md`.
- No duplicate IDs or duplicate normalized titles.
- At least three cross-subsystem interaction hazards linking tranche-1 and tranche-2 functions.
- Updated count and integrity snapshot captured in `consistency_assessment.md`.

## Tranche 2 Execution Result

- Executed subsystems: `SS-06`, `SS-08`, `SS-09`.
- New additions: `30` failure modes (`FM-049` through `FM-078`) and `17` hazards (`HZ-036` through `HZ-052`).
- Outcome: braking/hydraulic, icing/weather, and mission-authority domains are no longer thinly seeded.

## Tranche 3 Plan and Execution Result

### Tranche 3 Planned Scope

1. `SS-04` Propulsion and fuel systems.
1. `SS-05` Electrical power and distribution.
1. `SS-07` Environmental and pressurization.
1. `SS-10` Ground operations and human proximity.

### Tranche 3 Executed Outcome

- New additions: `32` failure modes (`FM-079` through `FM-110`) and `16` hazards (`HZ-053` through `HZ-068`).
- Outcome: P2 subsystem baseline is now broad enough to support cross-subsystem coupling analysis.

## Tranche 4 Plan and Execution Result

### Tranche 4 Planned Scope

1. Cross-subsystem interaction failures across aviate, navigate, communicate, and operate.
1. Latent-assurance and multi-fault coordination hazards.

### Tranche 4 Executed Outcome

- New additions: `20` failure modes (`FM-111` through `FM-130`) and `12` hazards (`HZ-069` through `HZ-080`).
- Outcome: coupling hazards and recovery deadlock families are now explicitly represented.

## Current Coverage Assessment

- All planned subsystem tranches (`SS-01` through `SS-11`) have at least one deep execution pass.
- Register now includes complete contiguous ID ranges through `FM-130` and `HZ-080`.
- Coverage is assessed as satisfactory for seeded decomposition-gap analysis, with residual expansion reserved for aircraft-program-specific tailoring.

## Tranche 05 Through Tranche 11 Plan and Execution

### Scope

1. Tranche 05: `SS-12` Flight deck HMI and alerting.
1. Tranche 06: `SS-13` Data networking and cyber resilience.
1. Tranche 07: `SS-14` Maintenance diagnostics and prognostics.
1. Tranche 08: `SS-15` External CNS and ATM integration.
1. Tranche 09: `SS-16` Autonomy decision support and policy control.
1. Tranche 10: `SS-17` Human factors and procedural controls.
1. Tranche 11: `SS-18` Assurance config and release governance.

### Executed Outcome

- New additions: `35` failure modes (`FM-131` through `FM-165`) and `21` hazards (`HZ-081` through `HZ-101`).
- Allocation pattern: `5` failure modes and `3` hazards per tranche for deterministic decomposition mapping.
- Outcome: coverage now includes HMI, networking trust/timing, maintenance/prognostics, external ATM interfaces, autonomy governance, procedural-human factors, and release-assurance controls.

### Tranche 11 Adequacy Gate

- Subsystem coverage status: all `SS-01` through `SS-18` seeded with dedicated tranche execution.
- Cross-domain coupling: represented through `SS-11` and extended governance tranches (`SS-13`, `SS-16`, `SS-18`).
- Readiness decision: baseline coverage is satisfactory for architecture comparison and formal decomposition gap analysis.
