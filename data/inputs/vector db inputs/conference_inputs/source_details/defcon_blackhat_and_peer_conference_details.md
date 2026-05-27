# DEF CON, Black Hat, and Peer Conference Presentation Details

## Scope

This document captures security-relevant details from DEF CON, Black Hat, and similar conference ecosystems for aerospace, satellite, transportation, and OT/ICS threat modeling.

## Black Hat - High-Value Entries

### 1) KA-SAT Cyberattack Lessons (Black Hat USA 2023)

- Title: `Lessons Learned from the KA-SAT Cyberattack: Response, Mitigation and Information Sharing`
- Source: https://www.blackhat.com/us-23/briefings/schedule/index.html#lessons-learned-from-the-ka-sat-cyberattack-response-mitigation-and--information-sharing-34478
- Key details:
- Malware targeted terminal devices and flash memory state.
- Parallel network-based denial actions persisted after initial malware phase.
- Viasat reported terminal forensic characterization within roughly 36 hours.
- NSA collaboration model emphasized rapid intel-sharing and cross-agency mitigation.
- Threat-model implications:
- Assets: satellite terminal firmware, management channels, terminal update path, SOC workflows.
- Attack preconditions: reachable terminal management/control path and malware delivery foothold.
- Impact classes: availability loss, service disruption, operational coordination stress.
- Defensive hooks:
- Pre-negotiated public-private incident coordination playbooks.
- Terminal firmware integrity and forensic telemetry baselines.
- Crisis-mode runbooks for parallel malware plus network-disruption campaigns.
- Confidence: High (direct conference abstract text).

### 2) Starlink User Terminal Fault Injection (Black Hat USA 2022)

- Title: `Glitched on Earth by Humans: A Black-Box Security Evaluation of the SpaceX Starlink User Terminal`
- Source: https://www.blackhat.com/us-22/briefings/schedule/index.html#glitched-on-earth-by-humans-a-black-box-security-evaluation-of-the-spacex-starlink-user-terminal-26982
- Slides: https://i.blackhat.com/USA-22/Wednesday/US-22-Wouters-Glitched-On-Earth.pdf
- Tool: https://github.com/KULeuven-COSIC/Starlink-FI
- Key details:
- Voltage fault injection used against boot verification flow.
- Reported extraction of ROM bootloader and eFuse contents after bypass.
- Attack chain moved from lab setup to custom hardware implementation.
- Threat-model implications:
- Assets: secure boot root of trust, ROM verification logic, terminal key material.
- Attack preconditions: physical access and specialized hardware skills.
- Impact classes: persistent compromise, trust-anchor defeat, downstream protocol exposure.
- Defensive hooks:
- Hardware fault attack resistance validation under realistic fault models.
- Tamper-evident hardware and anti-glitch monitoring.
- Risk tiering for terminals in untrusted physical environments.
- Confidence: High (direct abstract plus linked materials).

### 3) CoDe16 - CODESYS Framework (Black Hat USA 2023)

- Title: `CoDe16; 16 Zero-Day Vulnerabilities Affecting CODESYS Framework Leading to Remote Code Execution on Millions of Industrial Devices Across Industries`
- Source: https://www.blackhat.com/us-23/briefings/schedule/index.html#code16-16-zero-day-vulnerabilities-affecting-codesys-framework-leading-to-remote-code-execution-on-millions-of-industrial-devices-across-industries-31706
- Slides: https://i.blackhat.com/BH-US-23/Presentations/US-23-Tokarev-Code16-16-zero-day-vulnerabilities.pdf
- Key details:
- Multi-vulnerability chain in widespread PLC software framework.
- Cross-architecture and multi-vendor exposure was emphasized.
- Discussion included exploit chains and persistent malicious PLC logic.
- Threat-model implications:
- Assets: PLC runtime, engineering interfaces, proprietary protocol handlers.
- Attack preconditions: reachable CODESYS exposure and exploit chain maturity.
- Impact classes: process manipulation, persistent OT foothold, safety and production risk.
- Defensive hooks:
- Asset inventory for CODESYS-backed devices.
- Exposure reduction and strict segmentation for controller management services.
- PLC logic integrity checks and change governance.
- Confidence: High (direct conference abstract text).

## DEF CON - High-Value Entries

### 4) Bluetooth Research Across Cars and Aircraft (DEF CON 32)

- Title: `Exploiting Bluetooth - from your car to the bank account$$`
- Source: https://defcon.org/html/defcon-32/dc-32-speakers.html
- Key details:
- Reported broad vulnerability findings across modern vehicles.
- Explicit mention of Garmin Flight Stream (aviation-relevant accessory ecosystem).
- Focus on Bluetooth Classic test/replay capability and account/MFA abuse potential.
- Threat-model implications:
- Assets: infotainment pairing paths, account-linked mobile bridges, cockpit-adjacent accessories.
- Attack preconditions: proximity and protocol-specific exploitability.
- Impact classes: confidentiality loss, account hijack vectoring, lateral trust abuse.
- Defensive hooks:
- Strong pairing policy and periodic key refresh.
- Telemetry for abnormal Bluetooth negotiation patterns.
- Hard separation between consumer pairing and safety-critical domains.
- Confidence: High (conference abstract text).

### 5) VSAT Modem Signal Injection (DEF CON 32)

- Title: `Breaking the Beam: Exploiting VSAT Satellite Modems from the Earth's Surface`
- Source: https://defcon.org/html/defcon-32/dc-32-speakers.html
- Key details:
- Demonstrates OTA signal injection against satellite modem workflows.
- Includes reverse engineering of software and network stack behavior.
- Highlights remote root-shell outcomes and bogus firmware update pathways in described scenarios.
- Threat-model implications:
- Assets: VSAT modem firmware update trust chain, SDR-exposed RF ingress, network control path.
- Attack preconditions: RF signal capability, protocol understanding, physical line-of-sight or equivalent access conditions.
- Impact classes: remote compromise, firmware trust breakdown, service integrity degradation.
- Defensive hooks:
- Strong authenticated update pipeline and anti-rollback.
- RF-layer anomaly monitoring and authenticated control channel design.
- Independent red-team exercises for SATCOM ground equipment.
- Confidence: High (conference abstract text).

### 6) Legacy Railroad Signaling Abuse (DEF CON 32)

- Title: `Abusing legacy railroad signaling systems`
- Source: https://defcon.org/html/defcon-32/dc-32-speakers.html
- Key details:
- Focuses on practical exploitation concepts for long-lived signaling stacks.
- Emphasizes low-cost hardware-assisted attack feasibility.
- Useful analog for avionics legacy protocol modernization risk.
- Threat-model implications:
- Assets: signaling channels, legacy safety logic assumptions, maintenance interfaces.
- Attack preconditions: protocol knowledge plus physical/radio foothold depending on deployment.
- Impact classes: disruption, unsafe state transitions, trust erosion in transport operations.
- Defensive hooks:
- Security overlays for legacy protocols.
- Integrity and authenticity checks on critical signaling messages.
- Segmented maintenance paths and stricter physical security controls.
- Confidence: High (conference abstract text).

### 7) Electronic Logging Device Wormability (DEF CON 32)

- Title: `Compromising an Electronic Logging Device and Creating a Truck2Truck Worm`
- Source: https://defcon.org/html/defcon-32/dc-32-speakers.html
- Key details:
- Highlights insecure defaults and weak security controls in transportation-connected embedded devices.
- Discusses worm-like propagation scenarios in fleet-connected environments.
- Strong transferability to aviation support vehicles and logistics network modeling.
- Threat-model implications:
- Assets: telematics/ELD stack, vehicle network interfaces, fleet update/management plane.
- Attack preconditions: vulnerable endpoint and reachable propagation path.
- Impact classes: distributed compromise, operational interruption, fleet-wide trust failures.
- Defensive hooks:
- Secure-by-default baseline requirements for connected transport devices.
- Signed updates and fleet-wide exposure scanning.
- Incident containment playbooks for worm behavior.
- Confidence: High (conference abstract text).

## DEF CON Ecosystem Signals (Village-Level)

### 8) Aerospace Village (DEF CON 32)

- Source: https://defcon.org/html/defcon-32/dc-32-villages.html
- Relevance:
- Explicitly frames collaborative aviation and space security outcomes.
- Useful for identifying practitioner communities and evolving issue clusters.
- Threat-model utility:
- Use as a source locator for emerging aviation and space vulnerabilities and mitigation patterns.
- Confidence: Medium-High (program-level, not single technical exploit paper).

### 9) ICS Village and Car Hacking Village (DEF CON 32)

- Source: https://defcon.org/html/defcon-32/dc-32-villages.html
- Relevance:
- Indicates sustained ecosystem focus on industrial and automotive security scenarios.
- Helps prioritize cross-domain patterns transferable to aerospace and transport systems.
- Confidence: Medium-High (program-level signal).

## Similar Group Entries (Peer Conference Ecosystem)

### 10) S4 (ICS/OT-Focused Conference Series)

- Source: https://s4xevents.com/
- Notable cues:
- Strong emphasis on OT and ICS operational security and incident thinking.
- Video release and agenda channels can be mined for case-study expansion.
- Threat-model use:
- Good secondary source for OT defensive architecture and incident response patterns.
- Confidence: Medium (landing page metadata captured; specific talk extraction should be expanded).

### 11) TROOPERS (European Security Conference)

- Source: https://troopers.de/troopers23/
- Notable cues:
- High-quality practitioner conference with archives and recurring advanced tracks.
- Threat-model use:
- Useful as a feed for protocol, identity, and infrastructure attack tradecraft that can transfer to aviation/OT models.
- Confidence: Medium (event-level metadata captured).

## Software Partitioning and Isolation Baseline (ARINC 653 + Separation Kernel)

### 12) ARINC 653 Core Concepts for Threat Modeling

- Source: https://en.wikipedia.org/wiki/ARINC_653
- Supporting context: https://en.wikipedia.org/wiki/Integrated_modular_avionics
- Key details:
- Defines APEX API and partitioned execution model for mixed-criticality avionics software.
- Time and space partitioning are core primitives.
- Two-level scheduling model uses fixed partition windows in a repeating major frame.
- Communication and error-handling services are explicit parts of the model.
- Threat-model implications:
- Assets: schedule table integrity, partition memory boundaries, inter-partition communication definitions, error-handler behavior.
- Attack preconditions: unauthorized configuration change, exploitable RTOS/service implementation flaw, or integration-level design mistake.
- Impact classes: deterministic timing loss, isolation weakening, unintended information flow.
- Defensive hooks:
- Configuration signing and traceable release process for partition/scheduling data.
- Verification that deployed partition schedule matches approved baseline.
- Explicit information-flow analysis for each communication object.
- Confidence: Medium-High (good technical summary source; use official ARINC documents for certification decisions).

### 13) Separation Kernel Assurance and Integration Caveats

- Source: https://en.wikipedia.org/wiki/Separation_kernel
- Additional source signal: https://www.lynx.com/products/lynxsecure-separation-kernel-hypervisor
- Key details:
- Separation kernels aim to isolate partitions and mediate allowed information flows.
- Historical SKPP-style evaluation context exists, but standalone conformance is not equivalent to full-system assurance.
- High-assurance claims depend on both kernel properties and system integration boundaries.
- Threat-model implications:
- Assets: kernel mediation logic, partition policy definitions, exported resource assignment, audit controls.
- Attack preconditions: integration defects, policy drift, bypass of expected mediation path, or covert-channel conditions.
- Impact classes: cross-domain leakage, privilege escalation, violation of mixed-criticality safety assumptions.
- Defensive hooks:
- Treat kernel assurance as one layer, not a complete security argument.
- Add system-level threat modeling for all partition interfaces and update channels.
- Include independent adversarial testing focused on boundary bypass.
- Confidence: Medium (authoritative conceptual alignment; vendor pages are product-level).

## Suggested Next Expansion

- Pull slide PDFs for each selected talk and append:
- CVE list
- affected versions
- preconditions
- exploitability qualifiers
- mitigation maturity status
- Add conference-to-framework mapping tags:
- `STRIDE`
- `MITRE ATT&CK ICS`
- `NIST CSF 2.0`
- Add confidence scoring field per extracted claim.
