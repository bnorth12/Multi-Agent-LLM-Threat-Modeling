# Route and Waypoint Management

## Purpose

Manage route structure, waypoint sequencing, and leg transitions across mission phases.

## L2 Subfunctions

1. Maintain Route Graph and Leg Definitions
1. Validate Waypoint and Procedure Integrity
1. Manage Active/Alternate Route Selection
1. Handle In-Flight Amendments

## Threat-Relevant Considerations

- Waypoint or leg tampering can misdirect aircraft trajectory.
- Transition logic corruption can trigger discontinuities and unstable path following.
- Alternate-route manipulation can degrade diversion safety.
