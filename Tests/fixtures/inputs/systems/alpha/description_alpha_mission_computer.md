# Alpha Mission Computer

The Alpha Mission Computer is the mission-management core inside the Alpha air vehicle.
It receives approved mission packages from Bravo relay paths, executes mission logic, and
manages sensors, communication radios, data links, and EGI-informed navigation for the sortie.

## Supported Mission Profiles

- Strike missions with planned weapon-release geometry
- SEAD and DEAD missions with threat-avoidance and emitter-targeting constraints
- ISR missions with sensor coverage planning and retasking
- Peacetime ISR missions such as remote wildfire detection and monitoring

## Mission Package Content

The mission package consumed by Alpha includes:

- Waypoints and route plans
- Flight plans and timing constraints
- Communications frequencies and schedule windows
- Targeting information and weapon details to compute release or launch points
- Keep-out and threat-avoidance areas
- Sensor planning and ISR coverage objectives

## Trust and Interface Notes

Mission packages and status traffic cross the satellite-link boundary and must be
encrypted, authenticated, and replay-protected. EGI quality state is continuously
fused into mission execution decisions so degraded navigation can trigger safe
fallback routing and mission-mode constraints.
