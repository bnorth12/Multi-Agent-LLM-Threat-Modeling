# Operate Functional Decomposition

## Scope

Purpose-specific operational functions beyond core flight control, navigation, and communication.

## Variants

- `passenger_transport/`
- `missionized_operations/`

## Rule

Select or blend variants based on platform purpose, mission profile, and payload configuration.

## Platform Placement

- Mission Systems: primary placement for `missionized_operations/` functions.
- Passenger Systems: primary placement for `passenger_transport/` functions.
- Flight Controls and Vehicle Management: may consume Operate outputs only through constrained interfaces and explicit authority rules.
