# Charlie Mission Planning Computer

The Charlie Mission Planning Computer prepares executable mission packages that are
sent to Alpha through Bravo. It transforms multi-source planning inputs into a
single mission package aligned to UAS operational constraints.

## Planning Inputs

- All-source intelligence feeds
- Flight planning resources (airspace, terrain, weather, route constraints)
- Threat and keep-out area updates
- Communications spectrum constraints and scheduling windows
- Targeting and weapon data for release and launch-point calculations
- ISR sensor planning and coverage objectives

## Planning Outputs

The generated package includes waypoints, full flight plans, route plans,
communications frequencies and schedules, targeting details, weapon release
parameters, keep-out and threat-avoidance geometry, and ISR collection plans.

## Mission Types Supported

- Strike
- SEAD
- DEAD
- ISR (including peacetime ISR such as wildfire monitoring)

## Relay Path

Charlie planning output is sent to the Bravo mission-package broker for policy
validation and release control, then relayed to Alpha for execution.
