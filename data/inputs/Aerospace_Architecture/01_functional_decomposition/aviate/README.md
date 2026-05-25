# Aviate Functional Decomposition

## Scope

Functions required to control, stabilize, and physically sustain flight.

## L1 Groups

1. Flight Stability and Maneuvering
1. Flight Guidance and Automation
1. Essential Flight Services

## Current Files

- `flight_stability_and_maneuvering.md`
- `flight_guidance_and_automation.md`
- `essential_flight_services/`

## Platform Placement

- Flight Controls: primary placement for all Aviate functions.
- Vehicle Management: supporting placement for health, monitoring, and sustaining services under `essential_flight_services/`.
- Mission Systems and Passenger Systems: consume Aviate outputs but do not own Aviate control functions.
