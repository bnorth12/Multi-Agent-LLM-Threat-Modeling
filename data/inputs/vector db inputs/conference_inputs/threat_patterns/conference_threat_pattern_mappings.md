# Conference-Derived Threat Pattern Mappings

## Purpose

Translate conference presentation content into reusable threat patterns for aerospace and interface-centric threat models.

## Pattern Set

### Pattern A: Firmware Trust-Chain Bypass via Physical Faults

- Representative conference source:
- Black Hat USA 2022, Starlink terminal fault injection research.
- Typical target assets:
- Boot ROM trust logic.
- eFuse/key material.
- Firmware update authorization path.
- Preconditions:
- Physical access and specialized fault-injection setup.
- Primary impacts:
- Persistent compromise of trusted boot flow.
- Capability to run unauthorized firmware code.
- Suggested controls:
- Fault-aware secure boot validation.
- Hardware tamper response and secure element hardening.
- Deployment risk zoning for unattended terminals.
- Framework tags:
- STRIDE: `Tampering`, `Elevation of Privilege`.
- ATT&CK ICS: `Modify Program`, `Firmware Modification`.

### Pattern B: Protocol Framework Weakness in Industrial Controllers

- Representative conference source:
- Black Hat USA 2023, CoDe16 (CODESYS).
- Typical target assets:
- PLC protocol handlers.
- Runtime execution environment.
- Engineering and management channels.
- Preconditions:
- Reachable vulnerable service and exploit chain feasibility.
- Primary impacts:
- Remote code execution.
- Persistent malicious control logic.
- Process and safety degradation.
- Suggested controls:
- Minimize controller exposure.
- Segment engineering channels.
- Validate control logic integrity and enforce change approval.
- Framework tags:
- STRIDE: `Tampering`, `Denial of Service`, `Elevation of Privilege`.
- ATT&CK ICS: `Program Download`, `Modify Controller Tasking`.

### Pattern C: Satellite Terminal Campaign Combining Malware and Network Denial

- Representative conference source:
- Black Hat USA 2023, KA-SAT response and mitigation session.
- Typical target assets:
- Terminal flash and firmware state.
- Service continuity and network control functions.
- Incident coordination channels.
- Preconditions:
- Initial compromise path and ability to sustain follow-on denial pressure.
- Primary impacts:
- Wide-area service interruption.
- Long-duration operational degradation.
- Elevated response burden across operators and agencies.
- Suggested controls:
- Pre-authorized information-sharing playbooks.
- Rapid terminal forensic triage capability.
- Joint tabletop exercises for blended campaigns.
- Framework tags:
- STRIDE: `Denial of Service`, `Tampering`.
- NIST CSF: `Respond`, `Recover`, `Detect`.

### Pattern D: Wireless Bridge Exploitation Across Vehicle and Aviation Adjacent Systems

- Representative conference source:
- DEF CON 32, Bluetooth exploitation across cars and aircraft-adjacent systems.
- Typical target assets:
- Bluetooth pairing channels.
- Companion account-linked services.
- Embedded infotainment and auxiliary avionics-adjacent endpoints.
- Preconditions:
- Proximity and protocol exploit chain.
- Primary impacts:
- Data extraction.
- Session/account hijacking support.
- Lateral movement into broader trusted ecosystems.
- Suggested controls:
- Hardened pairing policy and cryptographic agility.
- Strong separation between convenience and safety-critical domains.
- Continuous telemetry on wireless negotiation anomalies.
- Framework tags:
- STRIDE: `Spoofing`, `Information Disclosure`.
- ATT&CK ICS: `Wireless Compromise`, `Modify Authentication Process`.

### Pattern E: RF Injection Against SATCOM Ground Equipment

- Representative conference source:
- DEF CON 32, VSAT signal injection and modem exploitation.
- Typical target assets:
- RF ingress paths.
- Modem network stack and update trust boundaries.
- Ground terminal management interfaces.
- Preconditions:
- SDR capability and protocol-specific attack knowledge.
- Primary impacts:
- Unauthorized firmware or command execution.
- Remote root-level compromise paths.
- Integrity loss in communication services.
- Suggested controls:
- End-to-end cryptographic validation of updates and control commands.
- RF anomaly detection and signal integrity monitoring.
- Security review of modem software plus protocol implementation.
- Framework tags:
- STRIDE: `Tampering`, `Elevation of Privilege`.
- ATT&CK ICS: `Modify Firmware`, `Exploitation of Remote Services`.

### Pattern F: Legacy Transportation Signaling and Embedded Device Exposure

- Representative conference sources:
- DEF CON 32 railroad signaling and ELD/truck wormability sessions.
- Typical target assets:
- Legacy control signals and transport telematics stacks.
- Certification and default configuration baselines.
- Fleet or network management channels.
- Preconditions:
- Legacy protocol assumptions and weak defaults.
- Primary impacts:
- Disruption propagation across fleets or corridors.
- Unsafe operational states and reliability degradation.
- Suggested controls:
- Secure-by-default procurement requirements.
- Signed updates, hardening baselines, and continuous compliance scans.
- Segmented operations and incident containment drills.
- Framework tags:
- STRIDE: `Tampering`, `Denial of Service`.
- NIST CSF: `Protect`, `Detect`, `Recover`.

### Pattern G: ARINC 653 Partition Configuration Abuse

- Representative source set:
- ARINC 653 platform and APEX service model references.
- Typical target assets:
- Partition configuration data.
- Major Time Frame and Partition Time Window schedule.
- Inter-partition communication objects and quotas.
- Preconditions:
- Misconfiguration, weak change control, or unauthorized config deployment path.
- Primary impacts:
- Partition starvation or degraded determinism.
- Cross-partition data exposure through misrouted communication channels.
- Safety function timing regression.
- Suggested controls:
- Signed configuration artifacts and strict release governance.
- Runtime schedule integrity verification against approved baseline.
- Independent review of inter-partition communication policy.
- Framework tags:
- STRIDE: `Tampering`, `Denial of Service`, `Information Disclosure`.
- ATT&CK ICS: `Modify Parameter`, `Modify Program`.

### Pattern H: Separation-Kernel Mediation or Isolation Weakness

- Representative source set:
- Separation-kernel architectural definitions and assurance guidance.
- Typical target assets:
- Kernel mediation path for memory, CPU, and I/O resources.
- Allowed information-flow policy and partition boundary enforcement.
- Audit and trusted computing base functions.
- Preconditions:
- Kernel defect, incomplete assurance argument for integrated system context, or misbound trust assumptions.
- Primary impacts:
- Unauthorized information flow between isolated partitions.
- Privilege escalation from low-criticality partition to higher-criticality domain.
- Loss of high-assurance isolation claims.
- Suggested controls:
- Defense-in-depth beyond kernel conformance claims.
- Formal or semi-formal policy validation for information-flow constraints.
- Independent red-team testing of bypass and covert-channel hypotheses.
- Framework tags:
- STRIDE: `Elevation of Privilege`, `Information Disclosure`, `Tampering`.
- NIST CSF: `Protect`, `Detect`, `Govern`.

## Query Fragments for Vector Retrieval

- `satellite terminal firmware flash overwrite incident response lessons`
- `fault injection secure boot aerospace terminal risk`
- `CODESYS remote code execution PLC mitigation segmentation`
- `Bluetooth exploit car aircraft accessory trust boundary`
- `VSAT signal injection firmware update trust chain`
- `legacy railway signaling cyber vulnerability controls`
- `ARINC 653 partition schedule tampering threat model`
- `separation kernel information flow bypass avionics`

## Governance Linkage

For each pattern promoted to formal risk register entries, create:

- A traceability record to requirements and control owners.
- HITL decision gates for residual-risk acceptance.
- Validation evidence references (test report IDs, simulation artifacts, exercise logs).
