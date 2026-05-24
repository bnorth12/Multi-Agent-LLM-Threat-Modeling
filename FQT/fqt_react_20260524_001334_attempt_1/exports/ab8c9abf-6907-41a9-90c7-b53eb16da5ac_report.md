# Threat Model Report - UAS Weapon System

## Executive Summary
This report provides a comprehensive threat model for the UAS Weapon System, summarizing key risks and recommendations derived from canonical interface artifacts.

## System Scope and Description
- System Name: UAS Weapon System
- Major Components: UAS Air Vehicle Segment (SS-ALPHA-01), Mission Processing Ground Station (SS-BRAVO-01), Satellite Communications Terminal (SS-CHARLIE-01), Ground Maintenance System (SS-DELTA-01), Navigation Subsystem (SS-NAV-01), Command and Control Subsystem (SS-CMD-01), Mission Management Subsystem (SS-MSN-01), and supporting subsystems/components listed in canonical artifacts
- Diagram: See Data Flow Diagrams section

## Trust Boundaries
- Satellite Link Boundary (RF interfaces between air and ground segments)
- Ops Network Boundary (HTTPS/TLS interfaces between ground processing nodes)
- Maintenance Bus Boundary (MIL-STD-1553/RS-422 interfaces for diagnostics and loads)
- Maintenance LAN Boundary (Ethernet interfaces for software distribution)
- Key Management Authority Boundary (key provisioning interfaces)
- Planning Intelligence Boundary (intel ingest interfaces)
- External Radio Link (GCS operator command interfaces)

## Data Flow Diagrams
No diagrams were produced.

## STRIDE Findings
| Interface ID | Spoofing | Tampering | Repudiation | Information Disclosure | Denial of Service | Elevation of Privilege |
|--------------|----------|-----------|-------------|------------------------|-------------------|------------------------|
| IF-001      | 4       | 4        | 3          | 3                     | 4                | 3                     |
| IF-002      | 5       | 4        | 3          | 3                     | 4                | 4                     |
| IF-013      | 5       | 5        | 3          | 4                     | 4                | 4                     |
| IF-019      | 4       | 3        | 2          | 2                     | 4                | 3                     |
| IF-024      | 5       | 5        | 3          | 4                     | 4                | 4                     |

## Top Threats
- Command spoofing and replay on uplink (IF-002)
- Weapon package spoof and tampering (IF-013, IF-024)
- Malicious software load injection (IF-007)
- Key material spoofing and disclosure (IF-010)
- GCS command spoofing (IF-019)

## Mitigation Mapping and Residual Risk
- M-001/M-003/M-025/M-033: Challenge-response, threshold signatures, and sequence validation reduce spoofing residual risk to 2 across Satellite Link Boundary
- M-009/M-059/M-061: Hardware root-of-trust verification reduces malicious load residual risk to 2 on Maintenance Bus Boundary
- M-019/M-041: HSM-protected key transport reduces key disclosure residual risk to 2 on Key Management Authority Boundary
- M-029: Mutual TLS with certificate pinning reduces GCS spoofing residual risk to 2 on External Radio Link
- M-005/M-006/M-023/M-031: TLS pinning, signed packages, and end-to-end signature verification reduce tampering residual risk to 2 on Ops Network Boundary

## Appendix
- Messages captured: 9
- Mermaid diagram levels: 6
- STIX bundle present: yes
