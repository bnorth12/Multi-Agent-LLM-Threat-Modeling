# Threat Model Report — Avionics Data Network

## Executive Summary

This report presents the results of a threat modeling analysis of the Avionics Data Network.
One high-risk interface was identified: the Ground to FMS Route Uplink over ACARS. The primary
threat is route spoofing via unauthenticated uplink. Technical and administrative mitigations are
recommended with residual risk ratings.

## System Scope and Description

The Avionics Data Network comprises the Flight Management Subsystem and the Ground Data Link
Subsystem. The FMS Core component receives route amendments from the VHF Data Radio via ACARS
uplink. The system is classified as mission-critical and safety-critical.

## Trust Boundaries

One trust boundary crossing was identified:

| Interface | Boundary Name | Crossing |
|-----------|--------------|---------|
| if-01 Ground to FMS Route Uplink | Air-Ground Boundary | Yes |

## Data Flow Diagrams

See Level 0, Level 1, and Level 2 diagrams produced by the Diagram Generator stage.

## STRIDE Findings

| Interface | S | T | R | I | D | E |
|-----------|---|---|---|---|---|---|
| if-01 | 4 | 3 | 2 | 3 | 2 | 2 |

Spoofing (4) and Tampering (3) are the dominant risk categories for the ACARS uplink interface.

## Top Threats

### Route Spoofing via Unauthenticated ACARS Uplink

- **Interface:** if-01 Ground to FMS Route Uplink
- **Likelihood:** 3/5
- **Impact:** 5/5
- **MITRE ATT&CK ICS:** T0856
- **CAPEC:** CAPEC-194
- **CWE:** CWE-290

An adversary transmits a forged ACARS uplink to alter the active flight route in the FMS without
aircrew awareness.

## Mitigation Mapping and Residual Risk

| Control ID | Title | Type | Residual Risk |
|-----------|-------|------|--------------|
| CTRL-T-01 | ACARS Message Authentication | Technical | 2/5 |
| CTRL-A-01 | Ground Station Access Control Review | Administrative | 3/5 |

## Appendix

- Analysis date: 2026-05-03
- Fixture run: golden-path avionics sample
- Schema version: canonical_graph v1
