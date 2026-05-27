# Navigate Functional Decomposition

## Scope

Functions that determine aircraft position, plan route and trajectory, and provide guidance intent.

## L1 Groups

1. Guidance and Trajectory Management
1. Route and Waypoint Management
1. Navigation Sensor Management
1. Route Planning and Replanning

## Current Files

- `guidance_and_trajectory_management.md`
- `route_and_waypoint_management.md`
- `navigation_sensor_management.md`
- `route_planning_and_replanning.md`

## Platform Placement

- Flight Controls: navigation intent and trajectory functions that directly support safe path execution.
- Vehicle Management: operational route coordination and navigation-service support functions.
- Mission Systems: mission-specific route constraints or overlays may feed Navigate functions through controlled interfaces.
