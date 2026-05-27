# Data Link and Network Exchange

## Purpose

Provide structured digital exchange for operational and mission data between airborne and ground systems.

## L2 Subfunctions

1. Session Establishment and Trust Setup
1. Message Serialization and Validation
1. Link Health Monitoring and Recovery
1. Confidentiality and Integrity Protection
1. Manage Flight Plan and Operational Dispatch Data Links
1. Manage Passenger Flight and Gate Coordination Data Links [Passenger]
1. Manage Commercial Service Data Exchanges [Passenger]

## L3 Examples

- Establish mutual trust context and session lifecycle for operational exchanges.
- Serialize outbound flight, mission, and service data into approved interface formats.
- Validate inbound message schema, integrity metadata, and policy conformance.
- Reject malformed, replayed, stale, or unauthorized messages.
- Monitor link health, timeout, retry, and failover behavior.
- Protect confidentiality and integrity for operational and mission-sensitive exchanges.
- Flight plan uplink/downlink and dispatch update exchanges.
- Gate assignment, turnaround, and passenger-flight operations data-link exchange.
- Commercial operations data exchange with airline and airport service systems.

## Threat-Relevant Considerations

- Trust-setup compromise can enable adversary-in-the-middle behaviors.
- Message-validation failures can permit command/data injection.
- Link-health spoofing can trigger unsafe fallback behavior.
- Corruption of flight plan or gate/dispatch exchanges can create operational disruption and decision error.
