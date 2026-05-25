# Functional Data Flow Reference

## Purpose

Define canonical high-level data flows between Aviate, Navigate, Communicate, and Operate functions.

## Core Data Flow Families

1. State and intent flows (sensor state, guidance intent, mode/state annunciation)
1. Command and control flows (pilot commands, automation commands, effector commands)
1. Mission/service flows (payload data, passenger-service data, operational service status)
1. Health and assurance flows (faults, maintenance state, integrity/confidence signals)

## Canonical Inter-Function Flows

- Navigate to Aviate: trajectory and guidance targets.
- Communicate to Navigate/Operate: external constraints, updates, and mission coordination.
- Operate to Communicate: mission or service output dissemination.
- Aviate services to all domains: health and availability constraints.

## Ownership and Enforcement Notes

- `../01_functional_decomposition/aviate/essential_flight_services/data_integrity_and_domain_isolation.md` owns cross-domain integrity validation and trust-boundary enforcement.
- Control-authority transitions remain governed by `control_authority_and_mode_management.md` even when data originates in mission or passenger-service functions.
- Detailed producer-consumer governance records are maintained in `../03_mapping_for_threat_alignment/interface_governance_matrix.csv`.

## Data Classification Hints

- Safety-critical control path data.
- Mission-sensitive intelligence/path data.
- Service and business operation data.
- Maintenance and health telemetry.

## Threat-Relevant Considerations

- Identify trust boundaries for every inter-function flow.
- Attach integrity and authenticity expectations to command-bearing data.
- Track confidence metadata for fused or transformed data products.
