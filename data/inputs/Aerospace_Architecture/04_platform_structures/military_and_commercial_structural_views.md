# Military and Commercial Structural Views

## Purpose

Define practical top-level architecture structures aligned to platform purpose.

## Military-Oriented Structure

1. Flight Controls
1. Vehicle Management
1. Mission Systems

### Military Communication Placement

- Communication functions that are military-unique are located under Mission Systems.
- Examples include tactical data links, mission-network exchange, and mission-unique identification/surveillance integrations.

## Commercial Passenger-Oriented Structure

1. Flight Controls
1. Vehicle Management
1. Passenger Systems

### Commercial Communication Placement

- Core communication is located under Vehicle Management for aircraft operation and dispatch continuity.
- Passenger-facing connectivity and service data exchange are located under Passenger Systems.

## Grouping Notes

- Flight Controls generally includes the Aviate/Navigate control core.
- Vehicle Management generally includes utilities and operational communication infrastructure.
- Mission Systems replaces Passenger Systems for missionized platforms.

## Traceability to Canonical Decomposition

- Flight Controls maps primarily to Aviate and Navigate.
- Vehicle Management maps to essential flight services and selected communication/data-link functions.
- Mission Systems or Passenger Systems map to the Operate branch variants.
