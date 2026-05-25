# Passenger Services and IFEC

## Purpose

Provide passenger-facing digital and media services while preserving separation from safety-critical domains.

## L2 Subfunctions

1. Manage Passenger Connectivity Services
1. Manage Inflight Entertainment Content
1. Enforce Service Domain Isolation
1. Monitor Passenger-Service Performance

## Control-Authority Context

- Passenger-service functions do not participate in flight-control authority decisions.
- Service-domain isolation must preserve separation from flight, navigation, and operational communication domains.
- Boundary expectations should be evaluated against `../../../02_cross_cutting/control_authority_and_mode_management.md` and `../../aviate/essential_flight_services/data_integrity_and_domain_isolation.md`.

## Threat-Relevant Considerations

- IFEC and passenger network pathways can be attractive lateral-movement targets.
- Isolation failure can expose avionics-adjacent services.
- Content or service update channels require strong integrity controls.
