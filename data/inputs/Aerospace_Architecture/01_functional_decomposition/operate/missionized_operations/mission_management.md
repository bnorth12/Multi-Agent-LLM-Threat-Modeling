# Mission Management

## Purpose

Plan, coordinate, and adapt mission execution priorities across payload, communication, and flight-support functions.

## L2 Subfunctions

1. Manage Mission Objectives and Priorities
1. Coordinate Sensor Tasking with Mission Intent
1. Manage Mission Timeline and Dynamic Replanning
1. Coordinate Interactions Between Payload, Communications, and Crew

## Control-Authority Context

- Mission Management provides constraint and priority inputs but does not override pilot or flight-control authority.
- Route or trajectory requests flow to route-management and FMS functions, not directly to actuator-control functions.
- Mission-driven replanning must respect the authority and annunciation rules defined in `../../../02_cross_cutting/control_authority_and_mode_management.md`.

## Threat-Relevant Considerations

- Mission-priority tampering can redirect collection and decision focus.
- Timeline/replanning corruption can degrade mission effectiveness and survivability.
- Cross-domain coordination integrity is required to avoid hazardous mission-flight conflicts.
