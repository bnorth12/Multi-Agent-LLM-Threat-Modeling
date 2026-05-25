# Detailed Risk Analysis Methods

## Purpose

Provide practical method guidance for producing detailed aerospace threat-risk analysis from ingestion evidence.

## Methods in Scope

### STRIDE

- Focus: threat categorization by spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege.
- Best use: early decomposition of interfaces, data flows, and trust boundaries.

### Attack Path Analysis

- Focus: multi-step adversary progression across systems and trust boundaries.
- Best use: identifying pivot sequences from enterprise to mission-critical components.

### Mission Thread Analysis

- Focus: mission-phase and operational-thread impact from cyber events.
- Best use: consequence-centered prioritization for aerospace operations.

### MBCRA (Mission-Based Cyber Risk Assessment)

- Focus: mission objective degradation under cyber threat conditions.
- Best use: aligning technical findings to mission outcomes and commander/operator decisions.

### MRAP-C

- Focus: structured risk assessment and prioritization for mission-relevant cyber controls.
- Best use: balancing mitigation coverage against operational constraints.

### CTT (Cyber Tabletop / Cyber Test and Training Context)

- Focus: exercise-driven validation of detection, response, and recovery assumptions.
- Best use: validating modeled attack paths and mitigations against realistic workflows.

## Integrated Workflow Recommendation

1. Use STRIDE for initial threat hypothesis generation.
1. Convert high-risk hypotheses into attack-path chains.
1. Evaluate mission impacts with mission-thread and MBCRA views.
1. Prioritize controls using MRAP-C framing.
1. Validate assumptions through CTT exercises and update residual risk.

## Data Contract Hooks

- `threat_or_control_summary`: method-tagged rationale (`STRIDE`, `AttackPath`, `MissionThread`, `MBCRA`, `MRAP-C`, `CTT`).
- `traceability_link`: link each conclusion to source captures and test evidence.
- `gate_readiness`: promote to gate 4 and gate 5 only when both plausibility and mitigation rationale are method-supported.

## Common Failure Modes

- STRIDE tags added without attack-path validation.
- Mission consequences asserted without mission-thread linkage.
- Mitigations proposed without MRAP-C tradeoff analysis.
- Tabletop conclusions not reflected back into model assumptions.
