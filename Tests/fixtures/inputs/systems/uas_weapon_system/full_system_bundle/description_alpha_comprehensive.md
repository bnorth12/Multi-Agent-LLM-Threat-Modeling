# Alpha UAV System - Comprehensive Threat Model

## System Role

Alpha is the airborne execution segment of the UAS Weapon System. It executes approved mission packages for strike, SEAD, DEAD, and ISR mission types, including peacetime ISR missions such as remote wildfire detection.

## Core Components

- Flight Control Computer for autonomous flight execution
- Payload Controller for ISR payload and mission sensor control
- Telemetry Router for encrypted command and status relay
- Aircraft Key Store for command-link and telemetry cryptographic material
- Mission Computer for mission execution logic, comms/radio/data-link management, and EGI-aware route control

## Mission Package Executed by Alpha

Alpha executes mission packages that include:

- Waypoints, route plans, and flight profiles
- Communications frequencies, schedules, and radio windows
- Targeting information and weapon details for release or launch-point calculation
- Keep-out zones and threat-avoidance constraints
- Sensor planning and ISR collection coverage

## Key Interfaces

- Mission package ingress from Bravo relay via encrypted satellite path
- EGI navigation quality input to mission execution decisions
- Mission status and sensor-collection feedback egress to Bravo

## Trust Boundaries

All mission package and mission status traffic crossing the satellite-link boundary is encrypted, authenticated, and replay-protected.

## Threat Modeling Context

Alpha is modeled as the mission executor. Mission-criticality scoring can later map directly to mission package elements such as weapon release points, threat-avoidance geometry, ISR coverage priority, and mission timeline windows.
