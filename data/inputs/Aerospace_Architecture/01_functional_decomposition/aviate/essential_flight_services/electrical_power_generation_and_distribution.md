# Electrical Power Generation and Distribution

## Purpose

Generate, condition, and distribute electrical power to flight-critical and mission-critical loads.

## L2 Subfunctions

1. Generate Electrical Power
1. Condition and Convert Power
1. Manage Bus and Load Distribution
1. Isolate Faults and Reconfigure Power Paths
1. Manage Electronic Control Circuit Breaker Units (`ECCBUs`) and controlled load-shed policies

## L3 Examples

- Electronic circuit-breaker command/telemetry control paths.
- Priority-based load shedding and restoration sequencing.
- Remote reset policy enforcement for critical and non-critical loads.

## Threat-Relevant Considerations

- Malicious or erroneous load-shed actions can remove critical function availability.
- Fault-isolation misbehavior can cascade into multi-domain outages.
- Distribution-state telemetry integrity is required for safe reconfiguration.
- Compromise of ECCBU command channels can create selective denial of power to safety or mission functions.
