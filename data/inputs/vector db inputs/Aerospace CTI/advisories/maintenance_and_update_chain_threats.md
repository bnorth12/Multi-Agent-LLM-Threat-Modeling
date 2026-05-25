# Maintenance and Update Chain Threats for Aviation and ICS

- created_utc: 2026-05-24
- objective: capture CTI patterns specific to maintenance, update, and configuration-control pathways
- canonical_folder: Aerospace CTI/advisories
- linked_source_copies:
  - ../../source_copies/raw/SC-011.md
  - ../../source_copies/raw/SC-012.md
  - ../../source_copies/raw/SC-013.md
  - ../../source_copies/raw/SC-014.md
  - ../../source_copies/raw/SC-015.md
  - ../../source_copies/raw/SC-016.md

## Scope

This document focuses on compromise paths where adversaries abuse software update mechanisms, maintenance tools, engineering interfaces, or configuration authorities in aerospace and ICS-adjacent environments.

## Threat Patterns

### Pattern 1: Firmware/Project Update Mode Abuse

- reference: MITRE ATT&CK ICS matrix includes `Activate Firmware Update Mode` and `Program Download` behavior.
- attack logic:
  - Gain access to maintenance or engineering channel.
  - Force update mode or deliver unauthorized program package.
  - Persist modified logic or firmware beyond session.
- likely impacts:
  - deterministic behavior regression
  - latent unsafe control actions
  - integrity loss in trust baseline
- priority controls:
  - signed updates, anti-rollback, dual-approval release gates
  - strict maintenance role separation and session recording

### Pattern 2: Remote Service Pivot into Maintenance Plane

- references: ATT&CK ICS remote service techniques and EASA exposed-interface risk framing.
- attack logic:
  - exploit reachable remote service or weakly isolated support interface.
  - pivot into maintenance toolchains or update orchestration components.
  - alter configuration artifacts or push malicious updates.
- likely impacts:
  - unauthorized policy/config drift
  - broad fleet or platform propagation risk
- priority controls:
  - management-plane segmentation
  - strong MFA for maintenance operators
  - continuous integrity checks on deployed configuration

### Pattern 3: Safety-Security Tradeoff Misconfiguration During Patching

- reference: NIST ICS guidance on balancing safety/reliability with security controls.
- attack logic:
  - exploit deferred patch windows and emergency-change procedures.
  - induce risky maintenance shortcuts under operational pressure.
- likely impacts:
  - persistent known-vulnerability exposure
  - unvalidated emergency changes in high-impact domains
- priority controls:
  - risk-tiered emergency change process
  - compensating controls during patch deferral
  - auditable rollback and post-change validation

## Governance and HITL Evidence Fields

Each promoted maintenance/update-chain threat entry should include:

- artifact_id
- source_url
- retrieval_timestamp_utc
- affected_asset_or_interface
- update_or_maintenance_step
- attack_preconditions
- plausible_attack_path
- candidate_controls
- confidence
- linked_source_copy
- traceability_link
- gate_readiness

## HITL Gate Readiness Mapping

- gate_2_boundary_approval: requires explicit maintenance interface boundary mapping.
- gate_3_stride_calibration: requires tampering/elevation pathways scored for update channels.
- gate_4_threat_plausibility: requires source-backed attack path references.
- gate_5_mitigation_adequacy: requires control evidence for signing, authorization, and rollback.

## Open Items

- Add targeted KEV-to-asset mapping slices for in-scope aviation and supporting ground-system products.
- Add FAA program-specific implementation artifacts (service-level policy, integration guidance, and operational test evidence) as available.
