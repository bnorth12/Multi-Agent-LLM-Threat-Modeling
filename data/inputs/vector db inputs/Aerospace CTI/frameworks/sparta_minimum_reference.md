# SPARTA Minimum Reference for Aerospace CTI

## Purpose

Define the minimum SPARTA coverage expected in this repository so aerospace CTI entries can be normalized for threat-model retrieval.

## Minimum Required Fields

- SPARTA tactic or category label.
- Threat event summary in aerospace mission context.
- Affected assets or functions (vehicle, payload, ground segment, communications).
- Preconditions and attacker assumptions.
- Observable indicators or telemetry cues.
- Candidate mitigations or resilience controls.
- Source URL and retrieval date.
- Confidence rating with caveats.

## Minimum Mapping Rule

Each new aerospace CTI document should include at least one explicit SPARTA mapping statement or include a short rationale for why SPARTA mapping is not applicable.

## Integration Notes

- Use this baseline together with ATT&CK ICS and internal threat-model schema mappings.
- Prefer stable SPARTA terminology across all documents to support deterministic retrieval and cross-document joins.
