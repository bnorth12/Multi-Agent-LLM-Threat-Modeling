# Sensor Operations

## Purpose

Operate onboard payload sensors and coordinate collection modes with mission intent.

## L2 Subfunctions

1. Plan Sensor Collection Tasks
1. Control Sensor Modes and Pointing
1. Monitor Sensor Performance and Availability
1. Record Collection Metadata
1. Manage Mission Sensor Suite Operation
1. Manage Mission Data Link Reception and Transmission

## L3 Examples

- Multimode radar management (mode scheduling, waveform/mode selection, scan strategy).
- Hyperspectral sensor operation and collection control.
- Wide Area Motion Imagery (`WAMI`) collection management.
- `IRST` and `EO/IR` payload operation control.
- Missile-warning and radar-warning receiver operation.
- Electronic warfare (`EW`) and self-protection jamming mode control.
- Mission data-link ingest and dissemination for sensor-tasking and mission-product exchange.

## Threat-Relevant Considerations

- Unauthorized mode changes can degrade mission effectiveness.
- Collection-task tampering can alter mission priorities.
- Metadata integrity is required for downstream analysis trust.
- Compromise of multimode radar/EW mode management can degrade survivability and threat detection performance.
