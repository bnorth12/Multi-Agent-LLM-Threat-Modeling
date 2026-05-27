# Flight Control, Navigation, and Mission Function Stack

## Purpose

Provide explicit functional definitions and function-level data flows for:

- Flight Control System (FCS)
- Flight Management System (FMS)
- Flight Director (FD)
- Waypoint Manager
- Route Manager
- Mission Manager

This is a canonical functional model for architecture and threat mapping. It is not a vendor implementation baseline.

## Explicit Functional Definitions

## Flight Control System (FCS)

Primary role: stabilize and maneuver the aircraft by transforming control intent into actuator-level commands within authority and envelope constraints.

Core functions:

1. Sense flight state (attitude, rates, accelerations, air data inputs)
1. Execute control laws (longitudinal/lateral/directional)
1. Mix and allocate commands to effectors (surfaces, trim, thrust interfaces where applicable)
1. Apply envelope and limit protections
1. Monitor control loop health and reversion modes

## Flight Management System (FMS)

Primary role: manage flight intent across route, performance, constraints, and trajectory prediction.

Core functions:

1. Build and maintain flight plan and active route intent
1. Evaluate constraints (airspace, procedure, performance, weather/policy inputs)
1. Compute trajectory predictions and guidance references
1. Publish targets and constraints for guidance and automation functions
1. Manage revisions, alternates, and contingency plans

## Flight Director (FD)

Primary role: convert guidance intent into pilot-facing command cues and mode indications.

Core functions:

1. Select active guidance modes and armed modes
1. Generate lateral and vertical command cues
1. Annunciate mode state and transitions
1. Ensure cue continuity across captures and transitions

## Waypoint Manager

Primary role: maintain waypoint objects and procedure elements with validation.

Core functions:

1. Store and index waypoint data structures
1. Validate waypoint identity, coordinates, altitude/speed constraints, and procedure linkage
1. Support insert/delete/modify operations with integrity checks
1. Publish active/next waypoint context

## Route Manager

Primary role: maintain route graph and sequencing logic over waypoint and leg sets.

Core functions:

1. Build leg graph from waypoint/procedure elements
1. Sequence active leg and transition states
1. Resolve discontinuities and alternate path activation
1. Handle amendments and re-route operations with auditability

## Mission Manager

Primary role: coordinate mission objectives, priorities, and mission-driven constraints that may influence route/timeline and communication behavior.

Core functions:

1. Maintain mission objectives, priorities, and timeline
1. Request tasking-driven route/trajectory adjustments
1. Coordinate payload/sensor/communication task coupling
1. Manage dynamic replanning under mission context

## Relationship Model

## Primary Ownership Boundaries

- Waypoint Manager owns waypoint data integrity.
- Route Manager owns leg graph and sequencing integrity.
- FMS owns trajectory and performance intent generation using route and constraints.
- FD owns pilot cueing and mode annunciation from guidance intent.
- FCS owns closed-loop control and actuator command realization.
- Mission Manager owns mission-priority logic and mission-driven constraints.

## Functional Dependency Chain

1. Mission Manager provides mission context and priority constraints.
1. Waypoint Manager and Route Manager provide structured route intent to FMS.
1. FMS computes guidance targets and trajectory intent.
1. FD transforms guidance intent into crew command cues and mode state.
1. FCS executes control response (manual/automated authority path) to follow commanded intent.

## Function-Level Data Flows

## Flow Group A: Plan and Initialize

1. Mission Manager -> Route Manager: mission objectives, timing windows, restricted/priority areas.
1. Route Manager -> Waypoint Manager: resolve referenced waypoints and procedure elements.
1. Waypoint Manager -> Route Manager: validated waypoint set, constraints, and integrity status.
1. Route Manager -> FMS: active route graph, alternates, discontinuities, leg constraints.
1. FMS -> FD: computed lateral/vertical targets, mode recommendations, capture criteria.
1. FMS -> FCS: autopilot-coupled target set when automation authority is engaged.

## Flow Group B: Execute and Track

1. Sensors/State Estimation -> FCS: current state vector and rates.
1. FCS -> FD: achieved-versus-commanded response status and control mode status.
1. FCS -> FMS: conformance and performance deltas relevant to trajectory prediction.
1. FD -> Pilot/Crew Interface: command bars/cues and active/armed mode annunciation.
1. FMS -> Route Manager: leg-completion intent and transition triggers.
1. Route Manager -> FMS: next-leg activation and route-state update.

## Flow Group C: Replan and Recover

1. Mission Manager -> FMS: mission-priority change or retask event.
1. Communicate functions -> FMS/Route Manager: external constraint updates (airspace, ATC, operations).
1. FMS -> Route Manager: reroute proposal and alternate activation request.
1. Route Manager -> Waypoint Manager: validate injected waypoints/procedures.
1. FMS -> FD/FCS: revised targets and mode transition requirements.
1. FD -> FCS/Pilot path: managed transition or manual takeover cues based on authority rules.

## Control and Authority Notes

- FD cueing does not replace FCS control-law execution.
- FMS intent publication does not bypass Route/Waypoint integrity controls.
- Mission Manager can constrain intent but should not directly command actuator-level behavior.
- Manual override and mode annunciation integrity remain safety-critical across all flows.

## Mapping to Existing Decomposition Files

- FCS spans `../01_functional_decomposition/aviate/flight_stability_and_maneuvering.md` and `../01_functional_decomposition/aviate/flight_guidance_and_automation.md`.
- FD aligns primarily with `../01_functional_decomposition/aviate/flight_guidance_and_automation.md`.
- FMS aligns primarily with `../01_functional_decomposition/navigate/guidance_and_trajectory_management.md` and consumes route-state outputs from route-management functions.
- Route Manager and Waypoint Manager align with `../01_functional_decomposition/navigate/route_and_waypoint_management.md` and `../01_functional_decomposition/navigate/route_planning_and_replanning.md`.
- Mission Manager aligns with `../01_functional_decomposition/operate/missionized_operations/mission_management.md`.

## Function Aliasing Appendix

This cross-cutting stack defines canonical functional entities that may span more than one decomposition file.

| Canonical Entity | Decomposition Realization | Boundary Note |
| --- | --- | --- |
| FCS | `aviate/flight_stability_and_maneuvering.md` plus control-authority portions of `aviate/flight_guidance_and_automation.md` | Closed-loop control and actuator realization remain in the FCS scope. |
| FD | `aviate/flight_guidance_and_automation.md` | Pilot cueing, mode annunciation, and capture guidance stay distinct from FCS control-law execution. |
| FMS | `navigate/guidance_and_trajectory_management.md` plus route-state inputs from `navigate/route_and_waypoint_management.md` and `navigate/route_planning_and_replanning.md` | FMS owns trajectory intent, not raw waypoint integrity. |
| Waypoint Manager | waypoint-oriented L2 responsibilities in `navigate/route_and_waypoint_management.md` | Waypoint validation and publication remain distinct from leg sequencing. |
| Route Manager | route graph, sequencing, and replanning responsibilities in `navigate/route_and_waypoint_management.md` and `navigate/route_planning_and_replanning.md` | Route state drives FMS trajectory computation. |
| Mission Manager | `operate/missionized_operations/mission_management.md` | Mission logic may constrain route or timeline but does not directly command actuator behavior. |
