# Propulsion

## Purpose

Provide controllable thrust required for takeoff, climb, cruise, descent, and go-around scenarios.

## L2 Subfunctions

1. Thrust Command Management
1. Engine/Propulsor Control and Monitoring
1. Start, Restart, and Shutdown Sequencing
1. Protection and Limit Management
1. Digital Engine Control Management (`DEEC`/`FADEC` authority and mode management)

## L3 Examples

- Full Authority Digital Engine Control (`FADEC`) for closed-loop thrust and protection logic.
- Digital Electronic Engine Control (`DEEC`) variants with bounded control authority and supervisory interfaces.
- Engine-control law mode transitions, reversion behavior, and pilot/automation interface handling.

## Threat-Relevant Considerations

- Invalid thrust command pathways can produce asymmetric or unsafe thrust states.
- Sensor/actuator data integrity is critical to limit enforcement.
- Degraded control-channel availability can create mission and safety impacts.
- DEEC/FADEC command-path tampering can directly affect thrust authority and envelope safety margins.
