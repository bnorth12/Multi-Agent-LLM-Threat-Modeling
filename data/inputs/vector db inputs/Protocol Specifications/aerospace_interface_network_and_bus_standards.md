# Aerospace Interface, Network, and Bus Standards

## Scope

This file provides ingestion-ready protocol and bus behavior notes for aerospace and mixed ICS environments, with threat implications and baseline controls.

## Retrieval Date

- 2026-05-24

## Protocols and Security Layers

### IP (Internet Protocol)

- How it works: connectionless packet delivery with routing across networks.
- Threats: spoofed source addresses, route manipulation, and reconnaissance via exposed services.
- Controls: strict segmentation, ingress/egress filtering, and route-policy hardening.

### TCP (Transmission Control Protocol)

- How it works: stateful, reliable byte-stream transport using a three-way handshake and ordered delivery.
- Threats: session hijack attempts, reset injection, and SYN-flood resource exhaustion.
- Controls: authenticated higher-layer protocols, anti-spoofing controls, and rate-limiting/DoS protections.

### UDP (User Datagram Protocol)

- How it works: connectionless datagram transport with no built-in reliability or ordering.
- Threats: amplification abuse, spoofed telemetry/control traffic, and weak integrity assumptions in custom protocols.
- Controls: authenticated payloads, replay windows, and ACL-based source restriction.

### TLS 1.3

- How it works: encrypted channel establishment with modern key exchange and record protection.
- Threats: weak certificate lifecycle management, downgrade misconfiguration, and trust-store abuse.
- Controls: strict certificate validation, approved cipher suites, and managed key rotation.

### mTLS (Mutual TLS)

- How it works: both client and server authenticate with certificates during TLS handshake.
- Threats: stolen client certs, incomplete revocation handling, and identity over-permissioning.
- Controls: short-lived certs, revocation checks, hardware-backed key storage, and identity-to-role least privilege.

### DTLS 1.3

- How it works: TLS-equivalent security adapted to unreliable datagram transport.
- Threats: replay and reordering abuse if anti-replay windows are weakly implemented.
- Controls: anti-replay enforcement, robust session/key update handling, and strict endpoint authentication.

## Aerospace and Industrial Buses

### ARINC 664 Part 7 (AFDX)

- How it works: switched full-duplex deterministic avionics Ethernet profile using pre-defined Virtual Links (VLs), BAG (Bandwidth Allocation Gap), and policing to enforce bounded latency and jitter.
- Implementation notes:
- End systems transmit only on assigned VLs with configured maximum frame size and BAG constraints.
- Switches enforce VL contract behavior and isolate traffic paths across the deterministic backbone.
- Redundancy is typically implemented with dual independent networks and receive-side integrity checking.
- Threats:
- Virtual-link misconfiguration that violates bandwidth and timing assumptions for safety-critical flows.
- Policer bypass or weak enforcement leading to deterministic-service degradation and congestion bleed-through.
- Unauthorized endpoint attachment or management-plane abuse to alter VL definitions or forwarding policy.
- Controls:
- Signed and review-gated configuration baselines for VL, BAG, and maximum frame constraints.
- Runtime conformance monitoring for latency, jitter, dropped-frame ratio, and BAG violations.
- Strict endpoint admission control, management-plane segmentation, and dual-network consistency checks.

### IEEE 802.1DP (Aerospace TSN Profile)

- How it works: profile guidance for applying TSN mechanisms to aerospace use cases, emphasizing deterministic transport behavior, bounded latency, time synchronization assurance, and interoperable profile constraints.
- Implementation notes:
- Uses profile-constrained TSN feature selections to avoid unsafe optionality across vendors.
- Depends on accurate time distribution and schedule integrity for time-aware forwarding and traffic shaping.
- Integrates with system-level assurance assumptions for mixed-criticality communication paths.
- Threats:
- Time-sync manipulation or drift amplification that breaks schedule assumptions and deterministic guarantees.
- Traffic-class abuse or schedule poisoning that starves critical streams under nominal network load.
- Interoperability profile drift across endpoints creating hidden failure modes and degraded resilience.
- Controls:
- Time-source integrity monitoring, holdover policy validation, and drift-threshold alerting.
- Configuration attestation for TSN schedules and profile-conformance checks in release pipelines.
- Continuous conformance tests for latency/jitter bounds and failover behavior under adversarial load.

### ARINC 429

- How it works: unidirectional point-to-point word-oriented avionics data bus.
- Threats: message injection from compromised transmitters and weak source trust assumptions.
- Controls: source integrity validation, plausibility checks, and interface gateway monitoring.

### ARINC 825

- How it works: aviation profile based on CAN semantics for distributed data exchange.
- Threats: arbitration abuse, identifier spoofing, and bus-flood denial of service.
- Controls: bus-load monitoring, identifier whitelisting, and partitioned gateway enforcement.

### MIL-STD-1553

- How it works: command-response multiplexed bus with Bus Controller, Remote Terminal, and Monitor roles.
- Threats: rogue command injection, role impersonation, and deterministic-timing disruption.
- Controls: controller command validation, strict terminal authorization, and anomaly detection on command cadence.

### RS-485

- How it works: differential physical layer for multi-drop serial communications over longer distances.
- Threats: physical-layer tap/injection, line contention abuse, and unauthorized device attachment.
- Controls: physical hardening, device authentication at higher layers, and line-integrity monitoring.

### CAN Bus

- How it works: broadcast message bus with ID-based arbitration and no native endpoint authentication.
- Threats: frame spoofing, priority starvation, and denial of service through high-priority flooding.
- Controls: gateway filtering, message-authentication overlays where feasible, and intrusion detection tuned to bus timing.

## Deterministic Ethernet Threat Mapping (ARINC 664 and 802.1DP)

- Critical assets:
- VL and TSN schedule artifacts, time-synchronization trust chain, switch policing configuration, and profile-conformance evidence.
- Common abuse paths:
- Timing manipulation, deterministic-bandwidth exhaustion, and unauthorized profile/configuration drift.
- Governance hooks:
- Require HITL review for deterministic network policy changes at `gate_2_boundary_approval` and `gate_3_stride_calibration`.
- Require evidence of conformance and runtime telemetry thresholds before `gate_5_mitigation_adequacy` acceptance.

## Threat-Model Mapping Hints

- STRIDE emphasis:
- Spoofing for unauthenticated endpoints and identifiers.
- Tampering for packet/frame injection and policy drift.
- Denial of Service for flood, starvation, and arbitration abuse.
- Information Disclosure for unencrypted or weakly segmented channels.
- ATT&CK ICS alignment:
- Command message abuse and protocol misuse patterns.
- Network service discovery, remote service exploitation, and control-channel manipulation.

## Confidence Notes

- This file is suitable for retrieval-augmented threat-model scaffolding.
- Certification-grade safety/security claims should be validated against controlled standards and program-authorized source baselines.
