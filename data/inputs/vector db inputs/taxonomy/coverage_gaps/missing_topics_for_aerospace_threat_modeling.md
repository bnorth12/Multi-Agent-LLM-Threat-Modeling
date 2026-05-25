# Missing Topics for Aerospace Interface Threat Modeling

## Why This Exists

Current corpus has strong initial coverage of conference-derived patterns, core transport protocols, and selected avionics buses. Additional topics are needed for robust mission-system threat modeling.

## High-Priority Missing Topics

### 1) Deterministic Ethernet and Avionics Backbones

- ARINC 664 Part 7 (AFDX) baseline now covered in `../../Protocol Specifications/aerospace_interface_network_and_bus_standards.md`.
- IEEE 802.1DP aerospace TSN profile baseline now covered in `../../Protocol Specifications/aerospace_interface_network_and_bus_standards.md`.
- Time-Triggered Ethernet and additional TSN profile depth remain open for expanded coverage.
- Threat focus: virtual-link abuse, bandwidth policing bypass, timing integrity attacks.

### 2) Navigation and Timing Dependencies

- PTP/IEEE 1588, IRIG time distribution, GNSS timing inputs.
- Threat focus: time spoofing, holdover degradation, cross-domain time trust abuse.

### 3) Aircraft Data Network Management and Maintenance

- Configuration/control planes, maintenance laptops, secure update workflows.
- Threat focus: trusted maintenance pivot, unauthorized config push, supply-chain insertion.

### 4) Sensor and Actuator Interface Assurance

- ADC/DAC paths, serial peripheral channels, gatewayed legacy buses.
- Threat focus: sensor spoofing, command injection, integrity masking.

### 5) Wireless and RF Avionics Adjacent Paths

- SATCOM service channels, CPDLC/ACARS context, airport/ground wireless interfaces.
- Threat focus: message authenticity, replay, jamming and denial resiliency.

### 6) Cryptographic and Identity Operations

- PKI hierarchy, key lifecycle, revocation, offline root procedures.
- Threat focus: cert misuse, stale trust anchors, emergency key rollover failures.

### 7) Safety-Security Co-Engineering Constraints

- Interaction between safety monitors and cybersecurity controls.
- Threat focus: security control side effects on deterministic/safety behavior.

### 8) Non-Conference Threat Intelligence Inputs

- CISA ICS advisories, NIST CPS guidance, FAA/EASA cyber material, vendor PSIRTs.
- Threat focus: real-world exploitability, known vulnerable versions, mitigation maturity.

### 9) ISAC Intelligence in No-Membership Environments

- Public-facing ISAC content is available but lower fidelity than member streams.
- Threat focus: campaign plausibility, sector trend signals, and mitigation themes where IOC-level details are unavailable.
- Process control: use `../isac_public_ingestion_playbook.md` and `../../source_copies/manifests/manifest_isac_extension.csv` to track evidence quality and coverage gaps.

## Recommended Next Additions

- Expand deterministic Ethernet depth in `Protocol Specifications/aerospace_interface_network_and_bus_standards.md` with implementation-specific evidence examples and test vectors.
- `Aerospace CTI/advisories/aviation_and_ics_advisory_digest.md` created; continue source-authority strengthening.
- `Aerospace CTI/advisories/maintenance_and_update_chain_threats.md` created; expand with additional maintenance-chain case evidence.
- Begin source captures in `source_copies/raw/` and `source_copies/extracted/` with metadata.
