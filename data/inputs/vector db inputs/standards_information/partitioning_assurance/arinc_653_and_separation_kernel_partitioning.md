# ARINC 653 and Separation Kernel Information for Software Partitioning Threat Modeling

## Scope

This file provides ingestion-ready notes on ARINC 653 partitioning and separation-kernel isolation for aerospace and mixed-criticality threat modeling.

## Sources

- https://en.wikipedia.org/wiki/ARINC_653
- https://en.wikipedia.org/wiki/Integrated_modular_avionics
- https://en.wikipedia.org/wiki/Separation_kernel
- https://www.lynx.com/products/lynxsecure-separation-kernel-hypervisor

## Retrieval Date

- 2026-05-24

## ARINC 653 Essentials (Threat-Model Relevant)

- ARINC 653 defines an APEX API for partitioned avionics software execution.
- Each partition has isolated memory space and scheduled processor time windows.
- Platform model includes partition/process management, communication, timing, and error handling services.
- Typical execution is hierarchical:
- Level 1: fixed cyclic partition schedule (major frame with partition windows).
- Level 2: process scheduling inside a partition during its active window.
- Mixed-criticality systems use this model to host multiple applications on shared hardware.

## Separation Kernel Essentials (Threat-Model Relevant)

- A separation kernel enforces isolation and controlled information flow between partitions.
- Core intent is to make each partition behave as if on a separate machine, except for explicitly allowed channels.
- Practical assurance depends on more than kernel conformance claims; integration and configuration quality are critical.
- Common deployment context includes high-assurance and safety/security mixed systems.

## Critical Assets for Modeling

- Partition configuration artifacts and policy data.
- Major frame and partition window schedule tables.
- Inter-partition communication channels and quotas.
- Memory and I/O isolation boundaries.
- Error-handling and recovery pathways.
- Boot/update chain for core platform software.

## Representative Threat Scenarios

### Scenario 1: Partition Schedule Tampering

- Description: Adversary alters major-frame partition timing allocations.
- Likely effects:
- Starvation of safety-critical partition.
- Non-deterministic behavior and degraded control-loop guarantees.
- Primary controls:
- Signed configuration updates.
- Runtime integrity checks of schedule tables.
- Dual-control approval for timing changes.

### Scenario 2: Inter-Partition Policy Drift

- Description: Communication policy changes permit unintended flow between partitions.
- Likely effects:
- Data leakage from high-criticality function to lower-criticality domain.
- Cross-domain command influence.
- Primary controls:
- Explicit information-flow matrix.
- Policy diff review in CI/CD.
- Runtime auditing of channel usage versus approved intent.

### Scenario 3: Error-Handler Abuse or Misbehavior

- Description: Fault handling loops or weak recovery logic can be triggered repeatedly.
- Likely effects:
- Local denial of service within partition.
- Cascading timing pressure on shared resources.
- Primary controls:
- Bounded recovery logic and watchdog integration.
- Failure-mode testing under adversarial inputs.

### Scenario 4: Isolation Bypass via Kernel or Integration Weakness

- Description: Mediation path or isolation boundary is bypassed through defect or incorrect integration assumptions.
- Likely effects:
- Privilege escalation across criticality domains.
- Unauthorized access to protected memory/device resources.
- Primary controls:
- Defense-in-depth beyond kernel claims.
- Independent penetration testing for boundary bypass.
- Strong least-privilege mapping of exported resources.

## Threat-Model Mapping Hints

- STRIDE emphasis:
- Tampering: policy/schedule/config manipulation.
- Information Disclosure: unintended cross-partition flows.
- Denial of Service: partition starvation and fault-loop effects.
- Elevation of Privilege: boundary bypass into higher criticality partition.
- ATT&CK ICS style alignment:
- Modify Program/Parameter patterns.
- Exploitation of remote or maintenance service paths.

## Governance and Assurance Hooks

- Maintain requirement-to-partition traceability for all safety and security claims.
- Add HITL gate for partition policy/schedule changes before release.
- Record independent verification evidence per release:
- configuration signature checks
- partition communication conformance tests
- adversarial fault-injection and resilience test summaries

## Confidence Notes

- Conceptual technical points: Medium-High confidence.
- Certification-grade decisions should use controlled ARINC and certification authority documents in addition to these public summaries.
