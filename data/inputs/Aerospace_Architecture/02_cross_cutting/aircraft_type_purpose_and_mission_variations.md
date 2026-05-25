# Aircraft Type, Purpose, and Mission Variations

## Purpose

Capture decomposition overlays for different aircraft classes and mission purposes.

## Variation Axes

1. Aircraft type (transport, ISR missionized, mixed-role, rotary-wing).
1. Mission purpose (passenger transport, surveillance, command-and-control, special mission).
1. Operational environment (civil corridors, contested environment, remote/expeditionary).

## Functional Variation Examples

- Passenger transport: stronger emphasis on IFEC and cabin-service operational continuity.
- Missionized ISR: stronger emphasis on sensor management, correlation, and fusion quality.
- Mixed-role aircraft: concurrent management of service and mission payload boundaries.

## Baseline Integrity Rule

Variant overlays extend the canonical baseline; they do not redefine L0 function semantics.

## Threat-Relevant Considerations

- Variation-specific functions should inherit baseline threat controls plus mission-unique controls.
- Mixed-role aircraft require explicit segregation policies for service versus mission data domains.
